import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import SetEnvironmentVariable
from launch.conditions import IfCondition


def generate_launch_description():
    pkg_share = get_package_share_directory('sme_4wcl_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    # Process the URDF file
    urdf_file = os.path.join(pkg_share, 'urdf', 'sme-4wcl.gazebo.xacro')
    robot_description = Command(['xacro ', urdf_file])
    
    # Declaring arguments for rendering
    render_engine = DeclareLaunchArgument(
        'render_engine',
        default_value='ogre',
        description='Render engine for Gazebo (ogre or ogre2)'
    )
    
    use_software_rendering = LaunchConfiguration('use_software_rendering')
    declare_use_software_rendering = DeclareLaunchArgument(
        'use_software_rendering',
        default_value='true',
        description='Whether to force software rendering (LIBGL_ALWAYS_SOFTWARE=1)'
    )

    # Gazebo Sim (Ignition) launch
    world_file = os.path.join(pkg_share, 'world', 'test_world.sdf')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': [
            '-r ', world_file, ' --render-engine ', LaunchConfiguration('render_engine')
        ]}.items(),
    )

    # Spawn the robot
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'sme-4wcl',
            '-topic', 'robot_description',
            '-z', '0.1', # Spawn slightly above ground
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

    # Bridge between ROS 2 and Gazebo Sim
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/model/sme_4wcl/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/sme_4wcl/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        parameters=[{'use_sim_time': True}],
        remappings=[
            ('/model/sme_4wcl/tf', '/tf'),
            ('/model/sme_4wcl/joint_states', '/joint_states'),
        ],
        output='screen'
    )

    pkg_share_path = pkg_share

    return LaunchDescription([
        declare_use_software_rendering,
        
        # Software rendering - required for ogre2 on VMware SVGA
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
        
        SetEnvironmentVariable('IGN_GAZEBO_RENDER_ENGINE_GUESS', 'ogre'),
        SetEnvironmentVariable('GZ_RENDERING_ENGINE_GUESS', 'ogre'),
        SetEnvironmentVariable('QT_X11_NO_MITSHM', '1'),
        
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', [
            os.path.dirname(pkg_share),
            ':',
            pkg_share
        ]),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', [
            os.path.dirname(pkg_share),
            ':',
            pkg_share
        ]),
        render_engine,
        gazebo,
        robot_state_publisher,
        spawn,
        bridge,
    ])