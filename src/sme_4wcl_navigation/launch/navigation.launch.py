import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Packages
    pkg_sme_navigation = get_package_share_directory('sme_4wcl_navigation')
    pkg_sme_description = get_package_share_directory('sme_4wcl_description')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Default Files
    nav2_params_file_path = os.path.join(pkg_sme_navigation, 'param', 'nav2_params.yaml')
    map_yaml_file = os.path.join(pkg_sme_navigation, 'map', 'map.yaml')
    urdf_file_path = os.path.join(pkg_sme_description, 'urdf', 'sme-4wcl.gazebo.xacro')
    ekf_params_file_path = os.path.join(pkg_sme_description, 'param', 'ekf.yaml')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    urdf_file = LaunchConfiguration('urdf_file')
    ekf_params_file = LaunchConfiguration('ekf_params_file')

    # Robot Description
    robot_description = Command(['xacro ', urdf_file])

    return LaunchDescription([

        # Parameters
        ########################################################################
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true'
        ),
        
        DeclareLaunchArgument(
            'map',
            default_value=map_yaml_file,
            description='Full path to map yaml file to load'
        ),

        DeclareLaunchArgument(
            'params_file',
            default_value=nav2_params_file_path,
            description='Full path to the ROS2 parameters file to use for all launched nodes'
        ),
        
        DeclareLaunchArgument(
            'urdf_file',
            default_value=urdf_file_path,
            description='Full path to the URDF/Xacro file'
        ),
        
        DeclareLaunchArgument(
            'ekf_params_file',
            default_value=ekf_params_file_path,
            description='Full path to the EKF parameters file'
        ),

        # Node Execution
        ########################################################################
        
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': ParameterValue(robot_description, value_type=str),
                'use_sim_time': use_sim_time
            }]
        ),

        # Robot Localization (EKF)
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_params_file, {'use_sim_time': use_sim_time}]
        ),

        # Navigation Nav2 node execution
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'map': map_yaml,
                'use_sim_time': use_sim_time,
                'params_file': params_file}.items()
        ),
        
    ])
