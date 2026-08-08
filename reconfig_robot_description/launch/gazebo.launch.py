import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('reconfig_robot_description')
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')
    xacro_file = os.path.join(pkg_path, 'urdf', 'wheel.xacro')

    robot_description_content = os.popen(f'xacro {xacro_file}').read()

    # 1. Start Gazebo (server + client)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': os.path.join(pkg_path, 'worlds', 'reconfig_warehouse.world')}.items()
    )

    # 2. Publish robot_description (same as before)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }]
    )

    # 3. Spawn the robot into the running Gazebo world
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'reconfig_robot',
           '-x', '0.0', '-y', '1.5', '-z', '0.1'],
        output='screen'
    )

    # 4. Controller spawners (same as your existing control.launch.py)
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster']
    )

    front_diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['front_diff_drive_controller', '--inactive']
    )

    four_wheel_diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['four_wheel_diff_drive_controller']
    )

    fold_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fold_position_controller']
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        joint_state_broadcaster_spawner,
        front_diff_drive_spawner,
        four_wheel_diff_drive_spawner,
        fold_position_controller_spawner
    ])