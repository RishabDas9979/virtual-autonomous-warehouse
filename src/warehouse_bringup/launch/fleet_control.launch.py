from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    args = [DeclareLaunchArgument('start_battery', default_value='1.0'),
            DeclareLaunchArgument('speedup', default_value='1.0')]
    nodes = [Node(package='warehouse_fleet', executable='driver',
                  name='driver_robot%d' % i, output='screen',
                  parameters=[{'robot': 'robot%d' % i}]) for i in range(1, 6)]
    nodes.append(Node(package='warehouse_fleet', executable='manager',
                      name='fleet_manager', output='screen',
                      parameters=[{'start_battery': LaunchConfiguration('start_battery'),
                                   'speedup': LaunchConfiguration('speedup')}]))
    nodes.append(Node(package='warehouse_fleet', executable='gz_labels',
                      name='gz_labels', output='screen'))
    return LaunchDescription(args + nodes)
