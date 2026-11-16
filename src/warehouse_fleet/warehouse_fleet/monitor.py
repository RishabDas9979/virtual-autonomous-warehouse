"""Live fleet table. Run: ros2 run warehouse_fleet monitor"""
import rclpy
from rclpy.node import Node
from warehouse_interfaces.msg import RobotStatus


class Monitor(Node):
    def __init__(self):
        super().__init__('fleet_monitor')
        self.rows = {}
        self.create_subscription(RobotStatus, '/fleet/status', self.on_status, 10)
        self.create_timer(1.0, self.show)

    def on_status(self, m):
        self.rows[m.robot] = m

    def show(self):
        lines = ['ROBOT   STATE        BATTERY             POSITION          ORDER']
        for name in sorted(self.rows):
            m = self.rows[name]
            pct = int(round(m.battery * 100))
            bar = '#' * (pct // 10) + '.' * (10 - pct // 10)
            order = '#%d' % m.order_id if m.order_id else '-'
            lines.append('%-7s %-12s [%s] %3d%%   (%6.1f, %6.1f)   %s'
                         % (m.robot, m.state, bar, pct, m.x, m.y, order))
        print('\033[2J\033[H' + '\n'.join(lines), flush=True)


def main():
    rclpy.init()
    node = Monitor()
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
