import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from controller_manager_msgs.srv import SwitchController



class ReconfigNode(Node):
    def __init__(self):
        super().__init__('reconfig_node')
        self.fold_pub = self.create_publisher(
            Float64MultiArray,
            '/fold_position_controller/commands',
            10
        )
        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        self.switch_client = self.create_client(SwitchController, '/controller_manager/switch_controller')
        self.latest_joint_state = None
        self.get_logger().info('Reconfig node started')

    def joint_state_callback(self, msg):
        self.latest_joint_state = msg

    def command_fold(self, left_target, right_target):
        msg = Float64MultiArray()
        msg.data = [left_target, right_target]
        self.fold_pub.publish(msg)
        self.get_logger().info(f'Published fold command: {msg.data}')

    def is_fold_complete(self, left_target, right_target, tolerance=0.03):
        if self.latest_joint_state is None:
            return False
        names = self.latest_joint_state.name
        positions = self.latest_joint_state.position

        if 'rear_left_fold_joint' not in names or 'rear_right_fold_joint' not in names:
            return False

        left_pos = positions[names.index('rear_left_fold_joint')]
        right_pos = positions[names.index('rear_right_fold_joint')]

        left_done = abs(left_pos - left_target) < tolerance
        right_done = abs(right_pos - right_target) < tolerance

        return left_done and right_done

    def switch_controllers(self, activate, deactivate):
        while not self.switch_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for switch_controller service...')

        request = SwitchController.Request()
        request.activate_controllers = activate
        request.deactivate_controllers = deactivate
        request.strictness = SwitchController.Request.STRICT

        future = self.switch_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        
        if future.result() is not None:
            self.get_logger().info(f'Switched controllers — activated: {activate}, deactivated: {deactivate}')
        else:
            self.get_logger().error('Switch controller call failed')


def main(args=None):
    rclpy.init(args=args)
    node = ReconfigNode()

    # Step 1: deactivate the current drive controller (4-wheel mode)
    node.switch_controllers(activate=[], deactivate=['four_wheel_diff_drive_controller'])

    # Step 2: command the fold joints to "folded"
    node.command_fold(1.5708, 1.5708)  # Example target positions for folded state

    # Step 3: wait until folding is complete
    while not node.is_fold_complete(1.5708, 1.5708):
        rclpy.spin_once(node, timeout_sec=0.1)

    # Step 4: activate the new drive controller (2-wheel mode)
    node.switch_controllers(activate= ['front_diff_drive_controller'], deactivate= [])

    node.get_logger().info('Reconfiguration complete.')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()