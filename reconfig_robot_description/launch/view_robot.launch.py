import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    pkg_path = get_package_share_directory('reconfig_robot_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'wheel.xacro')
    rviz_config = os.path.join(pkg_path, 'rviz', 'view_robot.rviz')

    robot_description = ExecuteProcess(
        cmd=['xacro', xacro_file],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': os.popen(f'xacro {xacro_file}').read()}]
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz
    ])