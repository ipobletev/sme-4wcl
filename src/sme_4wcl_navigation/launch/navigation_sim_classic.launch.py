import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    # Packages
    pkg_sme_navigation = get_package_share_directory('sme_4wcl_navigation')
    pkg_sme_description = get_package_share_directory('sme_4wcl_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Files
    nav2_params_file_path = os.path.join(pkg_sme_navigation, 'param', 'nav2_params.yaml')
    rviz_config_path = os.path.join(pkg_sme_navigation, 'rviz', 'navigation.rviz')
    map_yaml_file = os.path.join(pkg_sme_navigation, 'map', 'map.yaml')
    urdf_file = os.path.join(pkg_sme_description, 'urdf', 'sme-4wcl_classic.gazebo.xacro')
    navigation_launch_file = os.path.join(pkg_sme_navigation, 'launch', 'navigation.launch.py')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_software_rendering = LaunchConfiguration('use_software_rendering', default='false')
    
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    # Declare Launch Arguments
    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=map_yaml_file,
        description='Full path to map yaml file to load'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=nav2_params_file_path,
        description='Full path to the ROS2 parameters file to use for all launched nodes'
    )

    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether to start RViz'
    )

    declare_use_software_rendering_cmd = DeclareLaunchArgument(
        'use_software_rendering',
        default_value='true',
        description='Whether to force software rendering (LIBGL_ALWAYS_SOFTWARE=1)'
    )

    # Gazebo Classic launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(pkg_gazebo_ros, 'worlds', 'empty.world'),
            'verbose': 'true',
        }.items(),
    )

    # Spawn the robot
    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'sme-4wcl',
            '-topic', 'robot_description',
            '-z', '0.1',
            '-timeout', '120',
        ],
        output='screen',
    )

    # Navigation (RSP, EKF, Nav2) node execution
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(navigation_launch_file),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_yaml,
            'params_file': params_file,
            'urdf_file': urdf_file
        }.items()
    )

    # RViz node execution
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Create Launch Description
    ld = LaunchDescription()

    # Add environment variables
    ld.add_action(SetEnvironmentVariable('QT_X11_NO_MITSHM', '1'))
    ld.add_action(SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1', condition=IfCondition(use_software_rendering)))
    
    # Required for Gazebo Classic to find models if they are in the pkg_share
    ld.add_action(SetEnvironmentVariable('GAZEBO_MODEL_PATH', [os.path.dirname(pkg_sme_description)]))

    # Add declare arguments
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_use_software_rendering_cmd)

    # Add nodes and included launch files
    ld.add_action(gazebo)
    
    # We delay navigation by 2s so /robot_description is ready before spawn
    ld.add_action(TimerAction(             
        period=2.0,
        actions=[navigation]
    ))
    
    # We delay spawn to 3s because it waits for /robot_description from navigation.launch.py
    ld.add_action(TimerAction(
        period=3.0,
        actions=[spawn]
    ))
    
    ld.add_action(TimerAction(             
        period=8.0,
        actions=[rviz]
    ))

    return ld
