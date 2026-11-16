"""Floating battery labels above each robot in Gazebo.

  sub  /fleet/status  warehouse_interfaces/RobotStatus
  calls Gazebo service /marker (text markers, redrawn at 2 Hz)
"""
import rclpy
from gz.msgs10.empty_pb2 import Empty
from gz.msgs10.marker_pb2 import Marker
from gz.msgs10.marker_v_pb2 import Marker_V
from gz.transport13 import Node as GzNode
from rclpy.node import Node
from warehouse_interfaces.msg import RobotStatus


class GzLabels(Node):
    def __init__(self):
        super().__init__('gz_labels')
        self.gz = GzNode()
        self.rows = {}
        self.warned = False
        self.create_subscription(RobotStatus, '/fleet/status', self.on_status, 10)
        self.create_timer(0.5, self.draw)
        self.get_logger().info('battery labels ready')

    def on_status(self, m):
        self.rows[m.robot] = m

    H, W, T = 0.30, 0.16, 0.04
    SEGMENTS = {'0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
                '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
    LAYOUT = {'a': (0.0, H / 2, True), 'g': (0.0, 0.0, True), 'd': (0.0, -H / 2, True),
              'f': (-W / 2, H / 4, False), 'b': (W / 2, H / 4, False),
              'e': (-W / 2, -H / 4, False), 'c': (W / 2, -H / 4, False)}

    def segment(self, mv, mid, x, y, z, horizontal, rgb, on):
        mk = mv.marker.add()
        mk.ns = 'battery'
        mk.id = mid
        mk.action = Marker.ADD_MODIFY
        mk.type = Marker.BOX
        mk.lifetime.sec = 0
        if horizontal:
            mk.scale.x, mk.scale.y, mk.scale.z = self.W, self.T, self.T
        else:
            mk.scale.x, mk.scale.y, mk.scale.z = self.T, self.T, self.H / 2
        mk.pose.position.x = x
        mk.pose.position.y = y
        mk.pose.position.z = z if on else -5.0
        for c in (mk.material.ambient, mk.material.diffuse, mk.material.emissive):
            c.r, c.g, c.b, c.a = rgb[0], rgb[1], rgb[2], 1.0

    def draw(self):
        mv = Marker_V()
        for name, m in self.rows.items():
            n = int(''.join(c for c in name if c.isdigit()) or 0)
            pct = int(round(min(1.0, max(0.0, float(m.battery))) * 100))
            if m.state == 'CHARGING':
                rgb = (0.2, 0.5, 1.0)
            elif pct > 50:
                rgb = (0.1, 0.9, 0.1)
            elif pct >= 30:
                rgb = (1.0, 0.6, 0.0)
            else:
                rgb = (1.0, 0.1, 0.1)
            text = str(pct)
            step = self.W + 0.08
            for i in range(3):
                digit = text[i] if i < len(text) else None
                cx = float(m.x) + (i - (len(text) - 1) / 2.0) * step
                for k, seg in enumerate('abcdefg'):
                    ox, oz, horiz = self.LAYOUT[seg]
                    on = digit is not None and seg in self.SEGMENTS[digit]
                    self.segment(mv, n * 30 + i * 7 + k, cx + ox, float(m.y),
                                 1.0 + self.H / 2 + oz, horiz, rgb, on)
        self.gz.request('/marker_array', mv, Marker_V, Empty, 30)


def main():
    rclpy.init()
    node = GzLabels()
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
