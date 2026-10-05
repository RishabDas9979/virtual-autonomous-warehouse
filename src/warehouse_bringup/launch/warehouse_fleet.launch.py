import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

MAX_ROBOTS = 5  # hard limit

# name, x, y  -- add or remove rows to change the number of robots
ROBOTS = [
    ('robot1', -3.0, -7.0),
    ('robot2', -1.5, -7.0),
    ('robot3', 0.0, -7.0),
    ('robot4', 1.5, -7.0),
    ('robot5', 3.0, -7.0),
]


def generate_launch_description():
    if len(ROBOTS) > MAX_ROBOTS:
        raise RuntimeError('Too many robots: %d (max %d)' % (len(ROBOTS), MAX_ROBOTS))
    gz_share = get_package_share_directory('warehouse_gazebo')
    desc_share = get_package_share_directory('warehouse_description')
    world = os.path.join(gz_share, 'worlds', 'warehouse.sdf')
    gz_sim = os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    with open(os.path.join(desc_share, 'models', 'robot.sdf')) as f:
        template = f.read()

    actions = [IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_sim),
        launch_arguments={'gz_args': '-r ' + world}.items())]

    bridge_args = []
    for i, (name, x, y) in enumerate(ROBOTS):
        path = '/tmp/warehouse_' + name + '.sdf'
        with open(path, 'w') as f:
            f.write(template.replace('__NAME__', name))
        actions.append(TimerAction(period=6.0 + i, actions=[Node(
            package='ros_gz_sim', executable='create', output='screen',
            arguments=['-file', path, '-name', name,
                       '-x', str(x), '-y', str(y), '-z', '0.05', '-Y', '1.5708'])]))
        bridge_args.append('/' + name + '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist')
        bridge_args.append('/' + name + '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry')

    actions.append(Node(package='ros_gz_bridge', executable='parameter_bridge',
                        arguments=bridge_args, output='screen'))
    return LaunchDescription(actions)
