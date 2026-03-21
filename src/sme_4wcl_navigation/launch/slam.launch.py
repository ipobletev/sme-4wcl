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
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')

    # Default Files
    urdf_file_path = os.path.join(pkg_sme_description, 'urdf', 'sme-4wcl.gazebo.xacro')
    ekf_params_file_path = os.path.join(pkg_sme_description, 'param', 'ekf.yaml')
    slam_params_file_path = os.path.join(pkg_sme_navigation, 'param', 'slam_toolbox_params.yaml')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    urdf_file = LaunchConfiguration('urdf_file')
    ekf_params_file = LaunchConfiguration('ekf_params_file')
    slam_params_file = LaunchConfiguration('slam_params_file')

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
            'urdf_file',
            default_value=urdf_file_path,
            description='Full path to the URDF/Xacro file'
        ),
        
        DeclareLaunchArgument(
            'ekf_params_file',
            default_value=ekf_params_file_path,
            description='Full path to the EKF parameters file'
        ),

        DeclareLaunchArgument(
            'slam_params_file',
            default_value=slam_params_file_path,
            description='Full path to the slam_toolbox parameters file'
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

        # SLAM Toolbox node execution
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'slam_params_file': slam_params_file}.items()
        ),
        
    ])
