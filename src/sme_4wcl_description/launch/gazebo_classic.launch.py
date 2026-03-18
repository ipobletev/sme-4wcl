import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('sme_4wcl_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    
    # Process the URDF file (Gazebo Classic version)
    urdf_file = os.path.join(pkg_share, 'urdf', 'sme-4wcl_classic.gazebo.xacro')
    robot_description = Command(['xacro ', urdf_file])
    
    # Launch Arguments
    use_software_rendering = LaunchConfiguration('use_software_rendering')
    declare_use_software_rendering = DeclareLaunchArgument(
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
            '-timeout', '120', # Increased timeout for slow software rendering/model loading
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

    # Prepare the launch description
    return LaunchDescription([
        declare_use_software_rendering,
        
        # Enable software rendering only if requested (useful for some VMs)
        SetEnvironmentVariable(
            'LIBGL_ALWAYS_SOFTWARE', '1',
            condition=IfCondition(use_software_rendering)
        ),
        SetEnvironmentVariable('QT_X11_NO_MITSHM', '1'),
        
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', [
            os.path.dirname(pkg_share), # For sme_4wcl_description
        ]),
        
        gazebo,
        robot_state_publisher,
        spawn, 
    ])
