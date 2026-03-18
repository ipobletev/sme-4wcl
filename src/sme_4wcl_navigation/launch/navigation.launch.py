import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition

# ROS_DISTRO = os.environ.get('ROS_DISTRO', 'humble')

def generate_launch_description():
    # Parameters
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    # Packages
    pkg_mob_nav = get_package_share_directory('sme_4wcl_navigation')
    # Files
    nav2_params_file_path = os.path.join(pkg_mob_nav, 'param', 'nav2_params.yaml')
    rviz_config_path = os.path.join(pkg_mob_nav, 'rviz', 'navigation.rviz')
    nav2_launch_file_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    map_dir = LaunchConfiguration(
        'map',
        default=os.path.join(pkg_mob_nav, 'map', 'map.yaml'))

    nav2_params_dir = LaunchConfiguration(
        'params_file',
        default=nav2_params_file_path)
    
    return LaunchDescription([

        #Parameters
        ########################################################################
        
        # Map Server parameters
        DeclareLaunchArgument(
            'map',
            default_value=map_dir,
            description='Full path to map yaml file to load'
        ),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),

        # Navigation Nav2 parameters
        DeclareLaunchArgument(
            'params_file',
            default_value=nav2_params_dir,
            description='Full path to the ROS2 parameters file to use for all launched nodes'
        ),

        # RViz parameters
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Whether to start RViz'
        ),

        # Node Execution
        ########################################################################
        
        # Navigation Nav2 node execution
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([nav2_launch_file_dir, '/bringup_launch.py']),
            launch_arguments={
                'map': map_dir,
                'use_sim_time': use_sim_time,
                'params_file': nav2_params_dir}.items()
        ),
        
        # RViz node execution
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_path],
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            parameters=[{'use_sim_time': True}],
            output='screen'
        ),
    ])
