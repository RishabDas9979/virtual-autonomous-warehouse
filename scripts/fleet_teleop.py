#!/usr/bin/env python3
import sys, termios, tty, select
import rclpy
from geometry_msgs.msg import Twist

ROBOTS = ['robot1', 'robot2', 'robot3', 'robot4', 'robot5']
LIN, ANG = 0.5, 1.0
KEYS = {'w': (LIN, 0.0), 's': (-LIN, 0.0), 'a': (0.0, ANG),
        'd': (0.0, -ANG), 'x': (0.0, 0.0)}

HELP = """
Fleet teleop
  1-5     : select robot (the previous one stops)
  w/s     : forward/back      a/d : turn left/right
  x       : stop selected robot
  SPACE   : STOP ALL robots
  q       : quit (stops all robots)
"""

def main():
    rclpy.init()
    node = rclpy.create_node('fleet_teleop')
    pubs = {n: node.create_publisher(Twist, '/' + n + '/cmd_vel', 10) for n in ROBOTS}

    def send(name, lin, ang):
        msg = Twist()
        msg.linear.x = lin
        msg.angular.z = ang
        pubs[name].publish(msg)
        rclpy.spin_once(node, timeout_sec=0.02)

    def stop_all():
        for _ in range(3):
            for n in ROBOTS:
                send(n, 0.0, 0.0)

    current = ROBOTS[0]
    old = termios.tcgetattr(sys.stdin)
    print(HELP)
    print('Driving: ' + current)
    try:
        tty.setcbreak(sys.stdin.fileno())
        stop_all()
        while rclpy.ok():
            if not select.select([sys.stdin], [], [], 0.1)[0]:
                continue
            k = sys.stdin.read(1).lower()
            if k == 'q':
                break
            if k == ' ':
                stop_all()
                print('ALL STOPPED')
            elif k.isdigit() and 1 <= int(k) <= len(ROBOTS):
                send(current, 0.0, 0.0)
                current = ROBOTS[int(k) - 1]
                print('Driving: ' + current)
            elif k in KEYS:
                send(current, *KEYS[k])
    finally:
        stop_all()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
