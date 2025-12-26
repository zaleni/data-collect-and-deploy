import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from arx5_arm_msg.msg import RobotCmd
import time

class RobotCmdPublisher(Node):
    def __init__(self):
        super().__init__('robot_cmd_publisher')
        self.publisher_ = self.create_publisher(RobotCmd, 'arm_cmd', 10)
        self.timer_period = 2.0  # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.pos_a = [0.0, 0.0, 0.05, 0.0, 0.0, 0.0]
        self.pos_b = [0.0, 0.02, 0.05, 0.0, 0.0, 0.0]
        self.toggle = True

    def timer_callback(self):
        msg = RobotCmd()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        if self.toggle:
            msg.end_pos = self.pos_a
            msg.joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            msg.end_pos = self.pos_b
            msg.joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        msg.gripper = 0.0
        msg.mode = 4
        self.publisher_.publish(msg)
        self.toggle = not self.toggle
        self.get_logger().info(f'Published RobotCmd: {msg.end_pos}')

def main(args=None):
    rclpy.init(args=args)
    node = RobotCmdPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()