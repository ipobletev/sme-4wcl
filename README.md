# SME-4WCL Robot Description

This repository contains the URDF description and visualization tools for the **SME-4WCL** robot.

## Prerequisites

Before starting, ensure you have **ROS 2 Humble** installed. You can follow the [Official ROS 2 Humble Installation Guide](https://docs.ros.org/en/humble/Installation.html) or use the provided script:

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

### sme-4wcl-description - Robot Visualization
---
To visualize the robot in **RViz2** and interactively move its joints, run the following command:

```bash
ros2 launch sme-4wcl-description display.launch.py
```

To update the robot model when it is modified in the cloud (Onshape), ensuring you have `onshape-to-robot` installed:

```bash
# Update from Onshape (one-liner)
./src/sme-4wcl-description/on-shape-export-urdf/launch_app.sh
```

#### Features
- **Robot Model**: 3D visualization based on the URDF exported from Onshape.
- **Joint State Publisher GUI**: Interactive sliders to control wheels and other joints.
- **TF Display**: Visualization of the robot's coordinate frames.