import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('reconfig_robot_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'wheel.xacro')
    controllers_yaml = os.path.join(pkg_path, 'config', 'controllers.yaml')  # which folder, which file?

    robot_description_content = os.popen(f'xacro {xacro_file}').read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description_content},
            controllers_yaml
        ],
        output='screen'
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'] 
   )

    front_diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['front_diff_drive_controller']  
    )

    four_wheel_diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['four_wheel_diff_drive_controller', '--inactive']
    )

    fold_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fold_position_controller']
    )

    return LaunchDescription([
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        front_diff_drive_spawner,
        four_wheel_diff_drive_spawner,
        fold_position_controller_spawner
    ])