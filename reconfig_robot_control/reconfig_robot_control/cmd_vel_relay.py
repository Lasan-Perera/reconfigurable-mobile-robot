import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import JointState


class CmdVelRelay(Node):
    def __init__(self):
        super().__init__('cmd_vel_relay')

        self.front_pub = self.create_publisher(TwistStamped, '/front_diff_drive_controller/cmd_vel', 10)
        self.four_wheel_pub = self.create_publisher(TwistStamped, '/four_wheel_diff_drive_controller/cmd_vel', 10)

        self.cmd_vel_sub = self.create_subscription(TwistStamped, '/cmd_vel', self.cmd_vel_callback, 10)
        self.joint_sub = self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)

        self.current_mode = None  # 'front', 'four_wheel', or None (transitioning/unknown)
        self.get_logger().info('cmd_vel relay started')

    def joint_state_callback(self, msg):
        names = msg.name
        positions = msg.position
        tolerance = 0.05

        if 'rear_left_fold_joint' not in names:
            return

        fold_pos = positions[names.index('rear_left_fold_joint')]

        if abs(fold_pos - 0.0) < tolerance:
            self.current_mode = 'four_wheel'
        elif abs(fold_pos - 1.5708) < tolerance:
            self.current_mode = 'front'
        else:
            self.current_mode = None  # mid-transition — don't forward

    def cmd_vel_callback(self, msg):
        if self.current_mode == 'front':
            self.front_pub.publish(msg)
        elif self.current_mode == 'four_wheel':
            self.four_wheel_pub.publish(msg)
        # else: mid-transition or unknown — drop the command


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()