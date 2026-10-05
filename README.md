# Virtual Autonomous Warehouse

A simulated warehouse with a fleet of up to 5 robots, built with ROS 2 and Gazebo. One launch command starts the simulator, spawns the robots and connects them to ROS 2.

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Sim (installed with `ros-jazzy-ros-gz`)

## Build

```bash
cd ~/virtual-autonomous-warehouse
colcon build
source install/setup.bash
```

## Run

Use two terminals.

Terminal A: simulator (start first, leave running)

```bash
cd ~/virtual-autonomous-warehouse
source install/setup.bash
ros2 launch warehouse_bringup warehouse_fleet.launch.py
```

Terminal B: keyboard control

```bash
source ~/virtual-autonomous-warehouse/install/setup.bash
python3 ~/virtual-autonomous-warehouse/scripts/fleet_teleop.py
```

Keys: `1`-`5` select robot, `w`/`s` forward/back, `a`/`d` turn, `x` stop selected robot, Space stops all, `q` quits.

## Project layout

- `src/warehouse_bringup`: launch file (`warehouse_fleet.launch.py`)
- `src/warehouse_description`: robot model (`models/robot.sdf`)
- `src/warehouse_gazebo`: warehouse world (`worlds/warehouse.sdf`)
- `src/warehouse_fleet`, `src/warehouse_navigation`, `src/warehouse_interfaces`: empty placeholder packages
- `scripts/make_world.py`: generates the world (shelves, docks, pads, obstacles)
- `scripts/fleet_teleop.py`: keyboard control for all robots

## How it works

- Each robot has its own topics: `/robotN/cmd_vel` (drive) and `/robotN/odom` (position).
- The launch file spawns robots one second apart and bridges the topics between Gazebo and ROS 2.
- The robot count is the `ROBOTS` list in `warehouse_fleet.launch.py`, capped at 5 (`MAX_ROBOTS`).

## Changing the warehouse

Edit `scripts/make_world.py`, then run `python3 scripts/make_world.py` and `colcon build`.
