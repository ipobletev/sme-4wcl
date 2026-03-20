import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Packages
    pkg_sme_navigation = get_package_share_directory('sme_4wcl_navigation')
    pkg_sme_description = get_package_share_directory('sme_4wcl_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Files
    nav2_params_file_path = os.path.join(pkg_sme_navigation, 'param', 'nav2_params.yaml')
    rviz_config_path = os.path.join(pkg_sme_navigation, 'rviz', 'navigation.rviz')
    map_yaml_file = os.path.join(pkg_sme_navigation, 'map', 'map.yaml')
    urdf_file = os.path.join(pkg_sme_description, 'urdf', 'sme-4wcl_classic.gazebo.xacro')

    # Simulation Time
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_software_rendering = LaunchConfiguration('use_software_rendering', default='false')

    # Robot Description
    robot_description = Command(['xacro ', urdf_file])

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
        default_value='false',
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

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(robot_description, value_type=str),
            'use_sim_time': True
        }]
    )

    # Note: No bridge needed for Gazebo Classic as plugins publish directly to ROS topics.

    # Navigation Nav2 node execution
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': use_sim_time,
            'params_file': LaunchConfiguration('params_file')}.items()
    )

    # RViz node execution
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        parameters=[{'use_sim_time': True}],
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
    ld.add_action(spawn)
    ld.add_action(robot_state_publisher)
    ld.add_action(nav2_bringup)
    ld.add_action(rviz)

    return ld
