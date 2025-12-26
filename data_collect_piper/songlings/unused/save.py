# from piper_sdk import C_PiperInterface_V2
from piper_interface_v2 import C_PiperInterface_V2, MessageSaver

from utils import ( ArmEndPose,
    joint_to_bytes, gripper_to_bytes, endpose_to_bytes, joint_ctrl_to_bytes, gripper_ctrl_to_bytes, enable_fun)
from rich import print
import os
import rospy
from pathlib import Path
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import datetime
import time

class EEFRecorder:
    def __init__(self):
        self.last_eef = None
        self.current_eef= None
        self.counter = 0 
        
    def record(self, eef: ArmEndPose):
        if self.counter % 300 == 0:
            self.last_eef = self.current_eef
            self.counter += 1
        self.current_eef = [
            eef.end_pose.X_axis,
            eef.end_pose.Y_axis,
            eef.end_pose.Z_axis,
        ]
    
    def get_neigber_distance(self):
        if self.last_eef is None:
            return -1
        return sum([(p - n) * (p - n) for p, n in zip(self.last_eef, self.current_eef)])
    
    def get_neigber_distance_l1(self):
        if self.last_eef is None:
            return [-1, -1, -1]
        return [abs(p - n) for p, n in zip(self.last_eef, self.current_eef)]
    
    

class SimpleSaver(MessageSaver):
    def __init__(self, recorder : EEFRecorder, save_dir, task_name=None):
        self.recorder = recorder
        assert save_dir is not None, '提供一个文件夹来保存此次采集的数据先'
        
        save_dir = Path(save_dir)
        if task_name is not None:
            save_dir = save_dir / task_name
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(save_dir / 'imgs', exist_ok=True)
        
        self.leader_joint_f = open(save_dir / 'leader_joint', 'wb')
        self.leader_gripper_f = open(save_dir / 'leader_gripper', 'wb')
        self.follower_joint_f = open(save_dir / 'follower_joint', 'wb')
        self.follower_gripper_f = open(save_dir / 'follower_gripper', 'wb')
        self.follower_ep_f = open(save_dir / 'follower_endpose', 'wb')
        
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
        rospy.Subscriber('/ob_camera_01/color/image_raw', Image, self.save_image_to(self.img_1_color, counter_name='img_1_color_count'))
        rospy.Subscriber('/ob_camera_02/color/image_raw', Image, self.save_image_to(self.img_2_color, counter_name='img_2_color_count'))
        rospy.Subscriber('/ob_camera_01/depth/image_raw', Image, self.save_image_to(self.img_1_depth, is_rgb=False, counter_name='img_1_depth_count'))
        rospy.Subscriber('/ob_camera_02/depth/image_raw', Image, self.save_image_to(self.img_2_depth, is_rgb=False, counter_name='img_2_depth_count'))
        
        
        self.leader_joint_count = 0
        self.leader_gripper_count = 0
        self.follower_joint_count = 0
        self.follower_gripper_count = 0
        self.follower_eef_count = 0
        
        self.img_1_color_count = 0
        self.img_2_color_count = 0
        self.img_1_depth_count = 0
        self.img_2_depth_count = 0
        
    def save_leader_joint(self, joint):
        self.leader_joint_f.write(joint_ctrl_to_bytes(joint))
        self.leader_joint_f.flush()
        self.leader_joint_count += 1
    
    def save_leader_gripper(self, gripper):
        self.leader_gripper_f.write(gripper_ctrl_to_bytes(gripper))
        self.leader_gripper_f.flush()
        self.leader_gripper_count += 1
    
    def save_follower_joint(self, joint):
        self.follower_joint_f.write(joint_to_bytes(joint))
        self.follower_joint_f.flush()
        self.follower_joint_count += 1
    
    def save_follower_gripper(self, gripper):
        self.follower_gripper_f.write(gripper_to_bytes(gripper))
        self.follower_gripper_f.flush()
        self.follower_gripper_count += 1
        
    def save_follower_endpose(self, ep):
        self.follower_ep_f.write(endpose_to_bytes(ep))
        self.follower_ep_f.flush()
        self.follower_eef_count += 1
        self.recorder.record(ep)
    
    def save_image_to(self, folder, is_rgb=True, counter_name=None):
        def save_image(msg: Image):
            # print(f'save image to {folder}')
            timestamp = msg.header.stamp
            timestamp_str = str(timestamp.to_sec()).replace('.', '_')            
            if is_rgb:
                cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            else:
                cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            image_filename = os.path.join(folder, f"{timestamp_str}.png")
            cv2.imwrite(image_filename, cv_image)
            
            if counter_name is not None:
                setattr(self, counter_name, getattr(self, counter_name) + 1)
        return save_image
    
    def stop(self):
        self.follower_joint_f.close()
        self.follower_gripper_f.close()
        self.follower_ep_f.close()
        self.leader_gripper_f.close()
        self.leader_joint_f.close()

if __name__ == '__main__':
    recorder = EEFRecorder()
    saver = SimpleSaver(recorder, f'data/MixClean_gjq', f'{datetime.datetime.now().strftime("%m-%d@%H:%M:%S")}')
    piper = C_PiperInterface_V2(saver=saver)
    piper.ConnectPort()
    
    ros = rospy.init_node('data_collator', anonymous=True)

    
    start_time = time.time()
    try:
        while not rospy.core.is_shutdown():
            os.system('clear')
            print(f'Leader Joint Count:     {saver.leader_joint_count}')
            print(f'Leader Gripper Count:   {saver.leader_gripper_count}')
            print(f'Follower Joint Count:   {saver.follower_joint_count}')
            print(f'Follower Gripper Count: {saver.follower_gripper_count}')
            print(f'Follower EEF Count:     {saver.follower_eef_count}')
            
            print(f'Image 1 RGB Count:      {saver.img_1_color_count}')
            print(f'Image 1 Depth Count:    {saver.img_1_depth_count}')
            print(f'Image 2 RGB Count:      {saver.img_2_color_count}')
            print(f'Image 2 Depth Count:    {saver.img_2_depth_count}')
            
            print(f'Passed Time :           {int(time.time() - start_time)}')
            
            # print(f'Move Dist :             {recorder.get_neigber_distance_l1()}')
            # print(f'Move Dist (All) :       {recorder.get_neigber_distance()}')
            # print(f'last eef :              {recorder.last_eef}')
            # print(f'current eef :           {recorder.current_eef}')
            
            
            rospy.rostime.wallsleep(0.1)
    except KeyboardInterrupt:
        rospy.core.signal_shutdown('keyboard interrupt')
    
    
    piper.running = False
    # piper.can_deal_th.setDaemon(False)
    piper.can_deal_th.join()
    saver.stop()
    