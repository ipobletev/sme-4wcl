import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Packages
    pkg_sme_navigation = get_package_share_directory('sme_4wcl_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Default Files
    nav2_params_file_path = os.path.join(pkg_sme_navigation, 'param', 'nav2_params.yaml')
    slam_launch_file = os.path.join(pkg_sme_navigation, 'launch', 'slam.launch.py')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([

        # Parameters
        ########################################################################
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true'
        ),

        DeclareLaunchArgument(
            'params_file',
            default_value=nav2_params_file_path,
            description='Full path to the ROS2 parameters file to use for all launched nodes'
        ),

        # SLAM (RSP, EKF, slam_toolbox)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch_file),
            launch_arguments={
                'use_sim_time': use_sim_time
            }.items()
        ),

        # Navigation 2 (planners, controllers, behavior servers, without AMCL)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': params_file}.items()
        ),
        
    ])
