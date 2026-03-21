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
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Files
    nav2_params_file_path = os.path.join(pkg_sme_navigation, 'param', 'nav2_params.yaml')
    rviz_config_path = os.path.join(pkg_sme_navigation, 'rviz', 'navigation.rviz')
    map_yaml_file = os.path.join(pkg_sme_navigation, 'map', 'map.yaml')
    bridge_params_file = os.path.join(pkg_sme_description, 'param', 'ign_bridge_parameters.yml')
    navigation_launch_file = os.path.join(pkg_sme_navigation, 'launch', 'navigation.launch.py')

    # Simulation Time & Rendering
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    render_engine = LaunchConfiguration('render_engine', default='ogre')
    
    # Launch Configurations to pass to navigation
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

    # Bridge between ROS 2 and Gazebo Sim
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_params_file,
            'use_sim_time': use_sim_time
        }],
        output='screen'
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

    # Navigation (RSP, EKF, Nav2) node execution
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(navigation_launch_file),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_yaml,
            'params_file': params_file
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
    
    # We delay navigation by 2s so it doesn't crash from clock issues, 
    # and it makes /robot_description available before spawn at 3s
    ld.add_action(TimerAction(             
        period=2.0,
        actions=[navigation]
    ))
    
    ld.add_action(spawn)                   # 3. Spawn robot after 3s
    
    ld.add_action(TimerAction(             # 4. Start RViz after 8s
        period=8.0,
        actions=[rviz]
    ))

    return ld
