"""Fleet manager: takes orders, picks robots, simulates batteries.

  sub  /orders             warehouse_interfaces/Order
  srv  /set_priority       warehouse_interfaces/SetPriority
  sub  /robotN/world_pose  geometry_msgs/Point
  sub  /robotN/arrived     std_msgs/String
  pub  /robotN/goto        std_msgs/String
  pub  /robotN/battery     sensor_msgs/BatteryState   (percentage 0.0 to 1.0)
  pub  /fleet/status       warehouse_interfaces/RobotStatus
"""
import math
import os

import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import String
from warehouse_interfaces.msg import Order, RobotStatus
from warehouse_interfaces.srv import SetPriority

from warehouse_fleet.allocator import RobotInfo, choose_robot
from warehouse_fleet.battery import Battery, BatteryParams
from warehouse_fleet.graph import Graph
from warehouse_fleet.orders import ACTIVE, DONE, OrderQueue, PENDING

IDLE, TO_PICKUP, TO_DROPOFF = 'IDLE', 'TO_PICKUP', 'TO_DROPOFF'
TO_CHARGER, CHARGING = 'TO_CHARGER', 'CHARGING'


class Robot:
    def __init__(self, name, params, level):
        self.name = name
        self.idx = ''.join(c for c in name if c.isdigit())
        self.state = IDLE
        self.battery = Battery(params, level)
        self.order = None
        self.pose = None
        self.last = None
        self.delivered = 0
        self.held = []
        self.want = None
        self.wait_since = None


class Manager(Node):
    def __init__(self):
        super().__init__('fleet_manager')
        count = min(5, max(1, int(self.param('robots', 5))))
        speedup = float(self.param('speedup', 1.0))
        start = float(self.param('start_battery', 1.0))
        aging = float(self.param('aging_sec', 60.0))
        share = get_package_share_directory('warehouse_navigation')
        self.graph = Graph.from_yaml(os.path.join(share, 'config', 'locations.yaml'))
        self.params = BatteryParams(speedup=speedup)
        self.queue = OrderQueue(aging_sec=aging)
        self.robots, self.goto_pubs, self.batt_pubs = {}, {}, {}
        self.owner = {}
        for i in range(1, count + 1):
            name = 'robot%d' % i
            r = '/' + name
            self.robots[name] = Robot(name, self.params, start)
            self.goto_pubs[name] = self.create_publisher(String, r + '/goto', 10)
            self.batt_pubs[name] = self.create_publisher(BatteryState, r + '/battery', 10)
            self.create_subscription(
                Point, r + '/world_pose', lambda m, k=name: self.on_pose(k, m), 10)
            self.create_subscription(
                String, r + '/arrived', lambda m, k=name: self.on_arrived(k, m), 10)
        self.status_pub = self.create_publisher(RobotStatus, '/fleet/status', 10)
        self.create_subscription(Order, '/orders', self.on_order, 10)
        self.create_service(SetPriority, '/set_priority', self.on_set_priority)
        self.last_t = self.now()
        self.n_done = 0
        self.n_late = 0
        self.create_timer(0.1, self.tick)
        self.create_timer(1.0, self.publish_status)
        self.create_timer(10.0, self.summary)
        self.get_logger().info('manager ready: %d robots, speedup %.1f, start battery %.0f%%'
                               % (count, speedup, start * 100))

    def param(self, name, default):
        desc = ParameterDescriptor(dynamic_typing=True)
        return self.declare_parameter(name, default, desc).value

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_pose(self, name, msg):
        r = self.robots[name]
        r.pose = (msg.x, msg.y)
        if r.last is None:
            r.last = r.pose
            home = self.graph.nearest(r.pose[0], r.pose[1])
            r.held = [home]
            self.owner[home] = name

    def goto(self, r, place):
        r.want = place
        r.wait_since = None
        self.try_move(r)

    def at_home(self, r):
        return (r.want is None and len(r.held) == 1
                and r.held[0].startswith(('parking_', 'charger_')))

    def release_behind(self, r):
        # free the nodes the robot has already left
        while len(r.held) > 1:
            nx, ny = self.graph.nodes[r.held[1]]
            if math.hypot(r.pose[0] - nx, r.pose[1] - ny) >= 0.5:
                break
            if self.owner.get(r.held[0]) == r.name:
                del self.owner[r.held[0]]
            r.held.pop(0)

    def try_move(self, r):
        # start a move only when every node on the route is free
        if r.want is None or r.pose is None:
            return
        start = self.graph.nearest(r.pose[0], r.pose[1])
        path, _ = self.graph.path(start, r.want)
        if path is None:
            self.get_logger().warn('%s: no route to %s' % (r.name, r.want))
            r.want = None
            return
        blocker = next((self.owner[n] for n in path
                        if self.owner.get(n, r.name) != r.name), None)
        if blocker:
            now = self.now()
            if r.wait_since is None:
                r.wait_since = now
                self.get_logger().info('%s waits for a free route to %s (blocked by %s)'
                                       % (r.name, r.want, blocker))
            elif now - r.wait_since > 60.0:
                self.get_logger().warn('%s has waited %.0f s for %s (blocked by %s)'
                                       % (r.name, now - r.wait_since, r.want, blocker))
                r.wait_since = now
            return
        for n in r.held:
            if self.owner.get(n) == r.name:
                del self.owner[n]
        for n in path:
            self.owner[n] = r.name
        r.held = list(path)
        place, r.want, r.wait_since = r.want, None, None
        self.goto_pubs[r.name].publish(String(data=place))

    def send_to_charger(self, r):
        r.state = TO_CHARGER
        self.goto(r, 'charger_' + r.idx)
        self.get_logger().info('%s -> charger (battery %.0f%%)' % (r.name, r.battery.level * 100))

    def on_order(self, msg):
        ok = self.graph.orderable
        if msg.pickup not in ok or msg.dropoff not in ok or msg.pickup == msg.dropoff:
            self.get_logger().warn('rejected order %s -> %s (valid places: %s)'
                                   % (msg.pickup, msg.dropoff, ', '.join(ok)))
            return
        prio = msg.priority if msg.priority in (1, 2, 3) else 2
        rec = self.queue.submit(msg.pickup, msg.dropoff, prio, self.now(), msg.deadline_sec)
        self.get_logger().info('order #%d queued: %s -> %s, priority %d'
                               % (rec.id, rec.pickup, rec.dropoff, rec.priority))

    def on_set_priority(self, req, res):
        res.ok = self.queue.set_priority(req.order_id, req.priority)
        res.message = 'updated' if res.ok else 'order not waiting, not found, or bad priority'
        self.get_logger().info('set_priority #%d -> %d: %s'
                               % (req.order_id, req.priority, res.message))
        return res

    def on_arrived(self, name, msg):
        r, place, now = self.robots[name], msg.data, self.now()
        o = r.order
        if r.state == TO_PICKUP and o and place == o.pickup:
            r.state = TO_DROPOFF
            self.goto(r, o.dropoff)
            self.get_logger().info('%s picked up order #%d' % (name, o.id))
        elif r.state == TO_DROPOFF and o and place == o.dropoff:
            self.queue.complete(o.id, now)
            late = ' LATE' if now > o.deadline else ''
            self.n_done += 1
            self.n_late += 1 if late else 0
            self.get_logger().info('%s delivered order #%d in %.0f s%s'
                                   % (name, o.id, now - o.submitted, late))
            r.order = None
            r.delivered += 1
            if r.battery.is_low:
                self.send_to_charger(r)
            else:
                r.state = IDLE
                self.goto(r, 'parking_' + r.idx)
        elif r.state == TO_CHARGER and place == 'charger_' + r.idx:
            r.state = CHARGING
            self.get_logger().info('%s charging' % name)

    def tick(self):
        now = self.now()
        dt, self.last_t = now - self.last_t, now
        for r in self.robots.values():
            if r.pose is None:
                continue
            metres = math.hypot(r.pose[0] - r.last[0], r.pose[1] - r.last[1])
            r.last = r.pose
            r.battery.step(dt, metres, carrying=(r.state == TO_DROPOFF),
                           charging=(r.state == CHARGING))
            self.publish_battery(r)
            self.update_robot(r)
            self.release_behind(r)
            self.try_move(r)
        self.dispatch(now)

    def update_robot(self, r):
        b = r.battery
        if r.state == CHARGING and b.is_charged:
            r.state = IDLE
            self.get_logger().info('%s charged (%.0f%%), back in service'
                                   % (r.name, b.level * 100))
        elif r.state == IDLE and b.is_low:
            self.send_to_charger(r)
        elif r.state == TO_PICKUP and b.is_critical:
            self.get_logger().warn('%s battery critical, order #%d back in queue'
                                   % (r.name, r.order.id))
            self.queue.requeue(r.order.id)
            r.order = None
            self.send_to_charger(r)

    def dispatch(self, now):
        for order in self.queue.pending(now):
            infos = [RobotInfo(r.name, r.pose[0], r.pose[1], r.battery.level,
                               r.state if self.at_home(r) else 'BUSY')
                     for r in self.robots.values() if r.pose is not None]
            name = choose_robot(order, infos, self.graph, self.params)
            if name is None:
                continue
            r = self.robots[name]
            self.queue.assign(order.id, name, now)
            r.order, r.state = order, TO_PICKUP
            self.goto(r, order.pickup)
            self.get_logger().info('order #%d -> %s (battery %.0f%%)'
                                   % (order.id, name, r.battery.level * 100))

    def publish_battery(self, r):
        m = BatteryState()
        m.header.stamp = self.get_clock().now().to_msg()
        m.percentage = float(r.battery.level)
        m.present = True
        m.power_supply_status = (BatteryState.POWER_SUPPLY_STATUS_CHARGING
                                 if r.state == CHARGING
                                 else BatteryState.POWER_SUPPLY_STATUS_DISCHARGING)
        self.batt_pubs[r.name].publish(m)

    def publish_status(self):
        for r in self.robots.values():
            if r.pose is None:
                continue
            self.status_pub.publish(RobotStatus(
                robot=r.name, state=r.state, x=float(r.pose[0]), y=float(r.pose[1]),
                battery=float(r.battery.level), order_id=r.order.id if r.order else 0))

    def summary(self):
        recs = list(self.queue.orders.values())
        if self.n_done:
            ok = self.n_done - self.n_late
            self.get_logger().info('on time: %d of %d delivered (%.0f%%)'
                                   % (ok, self.n_done, 100.0 * ok / self.n_done))
        self.get_logger().info('orders: %d waiting, %d active, %d delivered' % (
            sum(o.status == PENDING for o in recs),
            sum(o.status == ACTIVE for o in recs),
            sum(o.status == DONE for o in recs)))


def main():
    rclpy.init()
    node = Manager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
