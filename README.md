# SME-4WCL Robot Description

This repository contains the URDF description and visualization tools for the **SME-4WCL** robot.

## Prerequisites

Before starting, ensure you have **ROS 2 Humble** installed and **Ubuntu 22.04**. You can follow the [Official ROS 2 Humble Installation Guide](https://docs.ros.org/en/humble/Installation.html) or use the provided script:

```bash
# Optional: Use the included installation script
chmod +x install_ros2_humble.sh
./install_ros2_humble.sh
```

## Building

1. From the root of your workspace, build the package:

```bash
colcon build
```

2. Source the environment to make the package available:

```bash
source install/setup.bash
```
## Packages

### sme-4wcl-description - Robot Visualization & Gazebo
---
This package contains the robot's URDF description and launch files for visualization and simulation.

#### RViz Visualization
To visualize the robot in **RViz2** and interactively move its joints:
```bash
# Launch the robot in RViz2
ros2 launch sme-4wcl-description display.launch.py

# Publish the wheel joint states
ros2 run joint_state_publisher_gui joint_state_publisher_gui 
```

#### Gazebo Simulation
To launch the robot in **Gazebo** for physics simulation:

**Gazebo Sim (Ignition - Recommended)**
```bash
# Launch the robot in Gazebo Ignition
ros2 launch sme-4wcl-description gazebo.launch.py
```

**Gazebo Classic**
```bash
# Launch the robot in Gazebo Classic
ros2 launch sme-4wcl-description gazebo_classic.launch.py
```

```bash
# Control the robot using the keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

#### Features
- **Robot Model**: 3D visualization based on the URDF exported from Onshape.
- **Gazebo Support**: Physics-based simulation with a 4-wheel differential drive plugin (`libgazebo_ros_diff_drive`).
- **Joint State Publisher GUI**: Interactive sliders to control joints in RViz.

## Assets - Robot Meshes
To update the robot model when it is modified in the cloud (Onshape)

```bash
# Launch the Onshape API to export the URDF and update meshes (./assets) and urdf (./urdf)
./src/sme-4wcl-description/on-shape-export-urdf/launch_app.sh
```