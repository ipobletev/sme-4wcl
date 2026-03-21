import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Packages
    pkg_sme_navigation = get_package_share_directory('sme_4wcl_navigation')
    pkg_sme_description = get_package_share_directory('sme_4wcl_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Files
    nav2_params_file_path = os.path.join(pkg_sme_navigation, 'param', 'nav2_params.yaml')
    rviz_config_path = os.path.join(pkg_sme_navigation, 'rviz', 'navigation.rviz')
    map_yaml_file = os.path.join(pkg_sme_navigation, 'map', 'map.yaml')
    urdf_file = os.path.join(pkg_sme_description, 'urdf', 'sme-4wcl.gazebo.xacro')
    bridge_params_file = os.path.join(pkg_sme_description, 'param', 'ign_bridge_parameters.yml')
    ekf_params_file = os.path.join(pkg_sme_description, 'param', 'ekf.yaml')


    # Simulation Time & Rendering
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    render_engine = LaunchConfiguration('render_engine', default='ogre')
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

    declare_render_engine_cmd = DeclareLaunchArgument(
        'render_engine',
        default_value='ogre',
        description='Render engine for Gazebo (ogre or ogre2)'
    )

    declare_use_software_rendering_cmd = DeclareLaunchArgument(
        'use_software_rendering',
        default_value='true',
        description='Whether to force software rendering (LIBGL_ALWAYS_SOFTWARE=1)'
    )

    # Gazebo Sim (Ignition) launch
    world_file = os.path.join(pkg_sme_description, 'world', 'test_world.sdf')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': [
            '-r ', world_file, ' --render-engine ', render_engine
        ]}.items(),
    )

    # Spawn the robot (delayed to give robot_state_publisher time to start)
    spawn = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-name', 'sme-4wcl',
                    '-topic', 'robot_description',
                    '-z', '0.1',
                ],
                output='screen',
            )
        ]
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

    # Robot Localization
    robot_localization = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params_file, {'use_sim_time': True}]
    )

    # Bridge between ROS 2 and Gazebo Sim
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_params_file,
            'use_sim_time': True
        }],
        output='screen'
    )

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
    ld.add_action(SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', [os.path.dirname(pkg_sme_description), ':', pkg_sme_description]))
    ld.add_action(SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', [os.path.dirname(pkg_sme_description), ':', pkg_sme_description]))
    ld.add_action(SetEnvironmentVariable('IGN_GAZEBO_RENDER_ENGINE_GUESS', 'ogre'))
    ld.add_action(SetEnvironmentVariable('GZ_RENDERING_ENGINE_GUESS', 'ogre'))
    ld.add_action(SetEnvironmentVariable('QT_X11_NO_MITSHM', '1'))
    ld.add_action(SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'))

    # Add declare arguments
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_render_engine_cmd)
    ld.add_action(declare_use_software_rendering_cmd)

    # Add nodes and included launch files
    ld.add_action(gazebo)                  # 1. Start Gazebo first
    ld.add_action(bridge)                  # 2. Start bridge immediately (provides /clock)
    ld.add_action(TimerAction(             # 3. Start RSP after 2s (clock must be available)
        period=2.0,
        actions=[robot_state_publisher]
    ))
    ld.add_action(TimerAction(             # 3.5 Start EKF after 3s
        period=3.0,
        actions=[robot_localization]
    ))
    ld.add_action(spawn)                   # 4. Spawn robot after 5s (RSP + Gazebo must be ready)
    ld.add_action(TimerAction(             # 5. Start Nav2 after 10s (bridge + Gazebo must supply /clock first)
        period=10.0,
        actions=[nav2_bringup]
    ))
    ld.add_action(TimerAction(             # 6. Start RViz after 8s
        period=8.0,
        actions=[rviz]
    ))

    return ld
