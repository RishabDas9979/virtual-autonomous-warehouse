# Virtual Autonomous Warehouse

A simulated warehouse with a fleet of up to 5 robots, built with ROS 2 and Gazebo.

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Sim (`ros-jazzy-ros-gz`)
- colcon (ROS 2 build tool)
- Python 3

## Topics covered in the project

- Gazebo warehouse world: floor, walls, shelves, loading dock, shipping dock, packing stations, sorting zone, charging pads, barrels and cones
- Robot model (differential drive robot)
- Multi-robot spawning from a single launch file (hard limit of 5 robots)
- ROS 2 and Gazebo bridge
- Keyboard control of any selected robot

## ROS 2 topics used

- `/robotN/cmd_vel`: drive commands for each robot
- `/robotN/odom`: position of each robot
