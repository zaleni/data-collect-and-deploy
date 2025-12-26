import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import time
import os

class ImageSaver(Node):
    def __init__(self, save_dir="images", freq=1):
        super().__init__('image_saver')
        self.subscription = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.listener_callback,
            10)
        self.bridge = CvBridge()
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        self.freq = freq
        self.last_time = 0

    def listener_callback(self, msg):
        now = time.time()
        if now - self.last_time >= 1.0 / self.freq:  # 控制保存频率
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # 用 ROS2 的时间戳命名（秒 + 纳秒）
            stamp = msg.header.stamp
            filename = os.path.join(
                self.save_dir,
                f"{stamp.sec}_{stamp.nanosec}.jpg"
            )

            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f"Saved {filename}")
            self.last_time = now

def main(args=None):
    rclpy.init(args=args)
    node = ImageSaver(save_dir="/home/go2/ARX_X5/run/Images", freq=2)  # 每秒 2 张
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
