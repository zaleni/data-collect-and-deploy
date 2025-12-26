import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from arx5_arm_msg.msg import RobotStatus  # 你的arm_status消息类型
import message_filters
from builtin_interfaces.msg import Time

class SyncSaver(Node):
    def __init__(self):
        super().__init__('sync_saver')

        self.record=False

        # 定义订阅器
        sub_img = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        sub_arm = message_filters.Subscriber(self, RobotStatus, '/arm_status')
        # sub_img.registerCallback(self.img_callback)
        # sub_arm.registerCallback(self.arm_callback)
        # 近似时间同步（允许时间差）
        ts = message_filters.ApproximateTimeSynchronizer(
            [sub_img, sub_arm], 
            queue_size=20, 
            slop=0.2   # 允许50ms偏差
        )
        ts.registerCallback(self.callback)

        # 15Hz 定时器
        self.timer = self.create_timer(1.0/10, self.save_data)
        self.latest_data = None

    def img_callback(self, img):
        self.get_logger().debug(f"收到图像消息，时间戳: {img.header.stamp.sec}.{img.header.stamp.nanosec}")

    def arm_callback(self, arm):
        self.get_logger().debug(f"收到手臂消息，时间戳: {arm.header.stamp.sec}.{arm.header.stamp.nanosec}")

    def callback(self, img, arm):
        # 缓存最新的一对同步消息
        print(1)
        self.latest_data = (img, arm)

    def save_data(self):
        if self.latest_data is not None:
            img, arm = self.latest_data
            # TODO: 在这里保存图像和状态
            self.get_logger().info(
                f"Saved synchronized data: img_time={img.header.stamp}, arm_time={arm.header.stamp}"
            )
    def start_record(self):
        self.record=True

def main(args=None):
    rclpy.init(args=args)
    node = SyncSaver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
