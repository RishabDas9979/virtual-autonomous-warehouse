import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = get_package_share_directory('warehouse_bringup')
    sim = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        os.path.join(share, 'launch', 'warehouse_fleet.launch.py')))
    control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, 'launch', 'fleet_control.launch.py')),
        launch_arguments={'start_battery': LaunchConfiguration('start_battery'),
                          'speedup': LaunchConfiguration('speedup'),
                          'aging_sec': LaunchConfiguration('aging_sec')}.items())
    return LaunchDescription([
        DeclareLaunchArgument('start_battery', default_value='1.0'),
        DeclareLaunchArgument('speedup', default_value='1.0'),
        DeclareLaunchArgument('aging_sec', default_value='60.0'),
        sim,
        TimerAction(period=15.0, actions=[control]),
    ])
