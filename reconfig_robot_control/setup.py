from setuptools import find_packages, setup

package_name = 'reconfig_robot_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lasan-perera',
    maintainer_email='lasanperera.lsp@gmail.com',
    description='Reconfiguration sequencing node for the reconfigurable mobile robot',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'reconfig_node = reconfig_robot_control.reconfig_node:main',
            'cmd_vel_relay = reconfig_robot_control.cmd_vel_relay:main',
        ],
    },
)
