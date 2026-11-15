"""Driver node: drives one robot along the waypoint graph.

robotN = value of the 'robot' parameter.
  sub  /robotN/odom        nav_msgs/Odometry
  sub  /robotN/goto        std_msgs/String       a location name from locations.yaml
  pub  /robotN/cmd_vel     geometry_msgs/Twist
  pub  /robotN/arrived     std_msgs/String       location name, once on arrival
  pub  /robotN/world_pose  geometry_msgs/Point   x, y in world frame, z = heading (rad)

Each robot's odometry starts at (0, 0) where it spawned, so the driver adds the
spawn pose (the robot's parking spot, facing +y) to get world coordinates.
"""
import math
import os

import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import String

from warehouse_fleet.graph import Graph

MAX_LIN = 0.4        # m/s
MAX_ANG = 1.0        # rad/s
TURN_FIRST = 0.35    # rad: rotate in place when the heading error is bigger
WAYPOINT_TOL = 0.25  # m
GOAL_TOL = 0.15      # m


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def yaw_of(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


class Driver(Node):
    def __init__(self):
        super().__init__('driver')
        self.robot = self.declare_parameter('robot', 'robot1').value
        share = get_package_share_directory('warehouse_navigation')
        self.graph = Graph.from_yaml(os.path.join(share, 'config', 'locations.yaml'))
        idx = ''.join(c for c in self.robot if c.isdigit())
        sx, sy = self.graph.nodes.get('parking_' + idx, (0.0, 0.0))
        self.sx = self.declare_parameter('spawn_x', float(sx)).value
        self.sy = self.declare_parameter('spawn_y', float(sy)).value
        self.syaw = self.declare_parameter('spawn_yaw', math.pi / 2).value
        self.pose = None          # (x, y, yaw) in world frame
        self.route = []
        self.goal = ''
        r = '/' + self.robot
        self.cmd_pub = self.create_publisher(Twist, r + '/cmd_vel', 10)
        self.arr_pub = self.create_publisher(String, r + '/arrived', 10)
        self.pose_pub = self.create_publisher(Point, r + '/world_pose', 10)
        self.create_subscription(Odometry, r + '/odom', self.on_odom, 10)
        self.create_subscription(String, r + '/goto', self.on_goto, 10)
        self.create_timer(0.1, self.loop)
        self.get_logger().info('%s driver ready, spawn (%.1f, %.1f)'
                               % (self.robot, self.sx, self.sy))

    def on_odom(self, msg):
        ox, oy = msg.pose.pose.position.x, msg.pose.pose.position.y
        c, s = math.cos(self.syaw), math.sin(self.syaw)
        self.pose = (self.sx + c * ox - s * oy,
                     self.sy + s * ox + c * oy,
                     wrap(self.syaw + yaw_of(msg.pose.pose.orientation)))

    def on_goto(self, msg):
        goal = msg.data.strip()
        if self.pose is None:
            self.get_logger().warn('no odometry yet, ignoring goto')
            return
        if goal not in self.graph.nodes:
            self.get_logger().warn('unknown location: ' + goal)
            return
        start = self.graph.nearest(self.pose[0], self.pose[1])
        path, _ = self.graph.path(start, goal)
        if path is None:
            self.get_logger().warn('no route to ' + goal)
            return
        self.route, self.goal = path, goal
        self.get_logger().info('route: ' + ' -> '.join(path))

    def stop(self):
        self.cmd_pub.publish(Twist())

    def loop(self):
        if self.pose is None:
            return
        x, y, yaw = self.pose
        self.pose_pub.publish(Point(x=x, y=y, z=yaw))
        if not self.route:
            return
        tx, ty = self.graph.nodes[self.route[0]]
        tol = GOAL_TOL if len(self.route) == 1 else WAYPOINT_TOL
        dx, dy = tx - x, ty - y
        if math.hypot(dx, dy) < tol:
            self.route.pop(0)
            if not self.route:
                self.stop()
                self.arr_pub.publish(String(data=self.goal))
                self.get_logger().info('arrived at ' + self.goal)
            return
        err = wrap(math.atan2(dy, dx) - yaw)
        cmd = Twist()
        if abs(err) > TURN_FIRST:
            cmd.angular.z = max(-MAX_ANG, min(MAX_ANG, 2.0 * err))
        else:
            cmd.linear.x = MAX_LIN
            cmd.angular.z = max(-MAX_ANG, min(MAX_ANG, 1.5 * err))
        self.cmd_pub.publish(cmd)


def main():
    rclpy.init()
    node = Driver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.stop()
        except Exception:
            pass
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
