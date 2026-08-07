import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('reconfig_robot_description')
    rviz_config = os.path.join(pkg_path, 'rviz', 'view_robot.rviz')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        rviz
    ])