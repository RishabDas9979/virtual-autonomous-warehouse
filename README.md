# Virtual Autonomous Warehouse

A simulated warehouse with a fleet of up to 5 robots, built with ROS 2 and Gazebo.

## What it includes

- A Gazebo warehouse world with floor, walls, shelves, loading dock, shipping dock, packing stations, sorting zone, charging pads, barrels and cones
- A differential drive robot model
- Multi-robot spawning from a single launch file (maximum 5 robots)
- A ROS 2 to Gazebo bridge
- Keyboard control of any selected robot

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Sim (`ros-jazzy-ros-gz`)
- colcon
- Python 3

Install the ROS and Gazebo packages if you do not have them:

```bash
sudo apt update
sudo apt install ros-jazzy-desktop ros-jazzy-ros-gz python3-colcon-common-extensions
```

## How to clone

```bash
git clone https://github.com/RishabDas9979/virtual-autonomous-warehouse.git
cd virtual-autonomous-warehouse
```

## How to build

Run this from the project folder:

```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

## How to run

You need two terminals. In each one, start from the project folder and source ROS first:

```bash
cd ~/virtual-autonomous-warehouse
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

**Terminal 1: start the warehouse and spawn all 5 robots**

```bash
ros2 launch warehouse_bringup warehouse_fleet.launch.py
```

**Terminal 2: drive a robot with the keyboard**

```bash
python3 scripts/fleet_teleop.py
```

Follow the on-screen instructions to pick a robot and drive it.

To open only the empty warehouse world (no robots):

```bash
ros2 launch warehouse_gazebo warehouse.launch.py
```

On WSL you may see a `QStandardPaths: wrong permissions` warning. It is harmless.

## Project structure

```
virtual-autonomous-warehouse/
├── scripts/
│   ├── fleet_teleop.py        Keyboard control for the robots
│   └── make_world.py          Script that generates the warehouse world
├── src/
│   ├── warehouse_bringup/     Launch file that starts the world and the robot fleet
│   ├── warehouse_description/ Robot model (robot.sdf)
│   ├── warehouse_gazebo/      Warehouse world (warehouse.sdf) and its launch file
│   ├── warehouse_fleet/       Fleet package (Python)
│   ├── warehouse_interfaces/  Custom ROS 2 interfaces (planned)
│   └── warehouse_navigation/  Navigation (planned)
├── .gitignore
└── README.md
```

## ROS 2 topics

| Topic | Purpose |
|-------|---------|
| `/robotN/cmd_vel` | Drive commands for robot N |
| `/robotN/odom` | Position of robot N |

`N` is the robot number, from 1 to 5.

## Authors

- Rishab Das
- Divyanshu Majhi# Virtual Autonomous Warehouse

A simulated warehouse with a fleet of up to 5 robots, built with ROS 2 and Gazebo.

## What it includes

- A Gazebo warehouse world with floor, walls, shelves, loading dock, shipping dock, packing stations, sorting zone, charging pads, barrels and cones
- A differential drive robot model
- Multi-robot spawning from a single launch file (maximum 5 robots)
- A ROS 2 to Gazebo bridge
- Keyboard control of any selected robot

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Sim (`ros-jazzy-ros-gz`)
- colcon
- Python 3

Install the ROS and Gazebo packages if you do not have them:

```bash
sudo apt update
sudo apt install ros-jazzy-desktop ros-jazzy-ros-gz python3-colcon-common-extensions
```

## How to clone

```bash
git clone https://github.com/RishabDas9979/virtual-autonomous-warehouse.git
cd virtual-autonomous-warehouse
```

## How to build

Run this from the project folder:

```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

## How to run

You need two terminals. In each one, start from the project folder and source ROS first:

```bash
cd ~/virtual-autonomous-warehouse
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

**Terminal 1: start the warehouse and spawn all 5 robots**

```bash
ros2 launch warehouse_bringup warehouse_fleet.launch.py
```

**Terminal 2: drive a robot with the keyboard**

```bash
python3 scripts/fleet_teleop.py
```

Follow the on-screen instructions to pick a robot and drive it.

To open only the empty warehouse world (no robots):

```bash
ros2 launch warehouse_gazebo warehouse.launch.py
```

On WSL you may see a `QStandardPaths: wrong permissions` warning. It is harmless.

## Project structure

```
virtual-autonomous-warehouse/
├── scripts/
│   ├── fleet_teleop.py        Keyboard control for the robots
│   └── make_world.py          Script that generates the warehouse world
├── src/
│   ├── warehouse_bringup/     Launch file that starts the world and the robot fleet
│   ├── warehouse_description/ Robot model (robot.sdf)
│   ├── warehouse_gazebo/      Warehouse world (warehouse.sdf) and its launch file
│   ├── warehouse_fleet/       Fleet package (Python)
│   ├── warehouse_interfaces/  Custom ROS 2 interfaces (planned)
│   └── warehouse_navigation/  Navigation (planned)
├── .gitignore
└── README.md
```

## ROS 2 topics

| Topic | Purpose |
|-------|---------|
| `/robotN/cmd_vel` | Drive commands for robot N |
| `/robotN/odom` | Position of robot N |

`N` is the robot number, from 1 to 5.

## Authors

- Rishab Das
- Divyanshu Majhi
