import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('reconfig_robot_description')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_path, 'launch', 'gazebo.launch.py')
        )
    )

    cmd_vel_relay = Node(
        package='reconfig_robot_control',
        executable='cmd_vel_relay',
        output='screen'
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': os.path.join(pkg_path, 'config', 'slam_params.yaml')
        }.items()
    )

    rviz_config = os.path.join(pkg_path, 'rviz', 'view_robot.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        gazebo,
        cmd_vel_relay,
        slam,
        rviz
    ])
