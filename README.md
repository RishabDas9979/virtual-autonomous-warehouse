# Virtual Autonomous Warehouse

A simulated warehouse with a fleet of up to 5 robots, built with ROS 2 and Gazebo.

## Features

- Gazebo warehouse world: shelves, loading and shipping docks, packing stations, sorting zone, charging pads, barrels and cones
- Differential drive robot model
- Multi-robot spawning from one launch file (max 5 robots)
- ROS 2 to Gazebo bridge
- Keyboard control of any selected robot

## Requirements

Ubuntu 24.04, ROS 2 Jazzy, Gazebo Sim (`ros-jazzy-ros-gz`), colcon, Python 3.

```bash
sudo apt update
sudo apt install ros-jazzy-desktop ros-jazzy-ros-gz python3-colcon-common-extensions
```

## Clone and build

```bash
git clone https://github.com/RishabDas9979/virtual-autonomous-warehouse.git
cd virtual-autonomous-warehouse
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

## Run

Open two terminals. In each, go to the project folder and run
`source /opt/ros/jazzy/setup.bash && source install/setup.bash`.

**Terminal 1:** start the warehouse and all 5 robots

```bash
ros2 launch warehouse_bringup warehouse_fleet.launch.py
```

**Terminal 2:** drive a robot with the keyboard

```bash
python3 scripts/fleet_teleop.py
```

On WSL, a `QStandardPaths: wrong permissions` warning is harmless.

## Project structure

```
virtual-autonomous-warehouse/
|-- scripts/
|   |-- fleet_teleop.py          Keyboard control
|   `-- make_world.py            Generates the warehouse world
`-- src/
    |-- warehouse_bringup/       Launch file: world + robot fleet
    |-- warehouse_description/   Robot model (robot.sdf)
    |-- warehouse_gazebo/        World (warehouse.sdf) and its launch file
    |-- warehouse_fleet/         Fleet package (Python)
    |-- warehouse_interfaces/    Custom interfaces (planned)
    `-- warehouse_navigation/    Navigation (planned)
```

## ROS 2 topics

| Topic | Purpose |
|-------|---------|
| `/robotN/cmd_vel` | Drive commands for robot N (1 to 5) |
| `/robotN/odom` | Position of robot N |

## Authors

- Rishab Das
- Divyanshu Majhi
