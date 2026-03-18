#!/bin/bash

# ROS 2 Humble Installation Script (Source)
# Based on: https://docs.ros.org/en/humble/Installation/Alternatives/Ubuntu-Development-Setup.html

set -e

echo "Starting ROS 2 Humble source installation..."

# 1. Check OS Version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$UBUNTU_CODENAME" != "jammy" ]]; then
        echo "Error: This script is intended for Ubuntu 22.04 (Jammy)."
        exit 1
    fi
else
    echo "Error: Cannot determine OS version."
    exit 1
fi

echo "OS Version Check Passed: $PRETTY_NAME"

# 2. Set Locale
echo "Setting up locale..."
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 3. Add the ROS 2 apt repository
echo "Adding ROS 2 apt repository..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe

sudo apt update && sudo apt install -y curl
ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# Install ROS2
sudo apt update -y
sudo apt upgrade -y
sudo apt install ros-humble-desktop -y

# Set source
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Install packages
sudo apt install python3-pip -y
sudo apt install -y python3-colcon-common-extensions
sudo apt install -y ros-humble-joint-state-publisher-gui
sudo apt install -y ros-humble-gazebo-ros-pkgs 
sudo apt install -y ros-humble-gazebo-plugins 
sudo apt install -y ros-humble-ros-gz
sudo apt install -y ros-humble-xacro
sudo apt install -y ros-humble-teleop-twist-keyboard
sudo apt install -y ros-humble-rviz2
sudo apt install -y ros-humble-robot-state-publisher
sudo apt install -y ros-humble-navigation2 
sudo apt install -y ros-humble-nav2-bringup