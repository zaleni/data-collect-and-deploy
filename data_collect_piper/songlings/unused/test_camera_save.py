# from piper_sdk import C_PiperInterface_V2
from piper_interface_v2 import MessageSaver

from rich import print
import os
import rospy
from pathlib import Path
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import datetime

class SimpleSaver(MessageSaver):
    def __init__(self, save_dir, task_name=None):
        assert save_dir is not None, '提供一个文件夹来保存此次采集的数据先'
        
        save_dir = Path(save_dir)
        if task_name is not None:
            save_dir = save_dir / task_name
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(save_dir / 'imgs', exist_ok=True)
        
        self.img_1_color = save_dir / 'imgs' / 'img_1_color'
        self.img_2_color = save_dir / 'imgs' / 'img_2_color'
        self.img_1_depth = save_dir / 'imgs' / 'img_1_depth'
        self.img_2_depth = save_dir / 'imgs' / 'img_2_depth'
        
        for folder in [
            self.img_1_color,
            self.img_2_color,
            self.img_1_depth,
            self.img_2_depth
        ]:
            os.makedirs(folder, exist_ok=True)
        
        self.bridge = CvBridge()
        rospy.Subscriber('/ob_camera_01/color/image_raw', Image, self.save_image_to(self.img_1_color))
        rospy.Subscriber('/ob_camera_02/color/image_raw', Image, self.save_image_to(self.img_2_color))
        rospy.Subscriber('/ob_camera_01/depth/image_raw', Image, self.save_image_to(self.img_1_depth, is_rgb=False))
        rospy.Subscriber('/ob_camera_02/depth/image_raw', Image, self.save_image_to(self.img_2_depth, is_rgb=False))
        

    
    def save_image_to(self, folder, is_rgb=True):
        def save_image(msg: Image):
            print(f'save image to {folder}')
            timestamp = msg.header.stamp
            timestamp_str = str(timestamp.to_sec()).replace('.', '_')            
            if is_rgb:
                cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            else:
                cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            image_filename = os.path.join(folder, f"camera2_color_{timestamp_str}.jpg")
            cv2.imwrite(image_filename, cv_image)
        return save_image


if __name__ == '__main__':
    saver = SimpleSaver(f'tmp/{datetime.datetime.now().strftime("%m-%d@%H:%M:%S")}')
    ros = rospy.init_node('data_collator', anonymous=True)

    rospy.spin()
    