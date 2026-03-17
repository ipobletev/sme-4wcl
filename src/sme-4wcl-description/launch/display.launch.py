import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package directory
    pkg_description = get_package_share_directory('sme-4wcl-description')

    # Path to the URDF file
    # Note: We expect the file to be installed in share/sme-4wcl-description/on-shape-export-urdf/sme-4wcl/robot.urdf
    urdf_file = os.path.join(pkg_description, 'on-shape-export-urdf', 'sme-4wcl', 'robot.urdf')

    # Read the URDF file
    with open(urdf_file, 'r') as infp:
        robot_description_config = infp.read()

    # Path to the RViz config file
    rviz_config_file = os.path.join(pkg_description, 'config', 'robot_display.rviz')

    # Parameters
    params = {'robot_description': robot_description_config}

    # Robot State Publisher node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # Joint State Publisher GUI node (optional but helpful for visualization)
    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # RViz2 node
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen'
    )

    # Create the launch description
    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
        node_rviz
    ])
