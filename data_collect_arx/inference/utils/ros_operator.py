import os
import threading
import collections
import cv2

import numpy as np
import matplotlib.pyplot as plt

from collections import deque

from scipy.spatial.transform import Rotation as R  # eef:ZXY

import rclpy

from rclpy.node import Node
from std_msgs.msg import Header
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, CompressedImage, Imu
from tf2_msgs.msg import TFMessage
from std_msgs.msg import Int32MultiArray

# from utils.controller import PIDController

import time


import argparse
import yaml



class Rate:
    def __init__(self, hz):
        self.period = 1.0 / hz
        self.last_time = time.time()

    def sleep(self):
        now = time.time()
        elapsed = now - self.last_time
        sleep_time = self.period - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
        self.last_time = time.time()


class RosOperator(Node):
    def __init__(self, args, config, in_collect=False):
        super().__init__('robot_operator')

        # from arm_control.msg._pos_cmd import PosCmd
        # from arm_control.msg._joint_control import JointControl
        from arx5_arm_msg.msg._robot_cmd import RobotCmd
        from arx5_arm_msg.msg._robot_status import RobotStatus

        # self.total=0
        self.args = args
        self.config = config

        self.in_collect = in_collect

        # 控制状态标志（带线程锁保护）
        self.ctrl_state = False
        self.ctrl_state_lock = threading.Lock()

        self.bridge = CvBridge()

        # 图像队列
        self.img_left_deque = deque()
        self.img_left_depth_deque = deque()
        self.img_head_deque = deque()
        self.img_head_depth_deque = deque()

        # 主从臂消息队列
        self.master_left_arm_deque = deque()
        self.follow_left_arm_deque = deque()
 
        # 控制器队列
        self.controller_left_deque = deque()

        
        # 跟随机械臂的关节/末端执行器状态
        self.follow_left_arm_joint_deque = deque()
        self.follow_left_arm_eef_deque = deque()

        # 跟随机械臂发布锁（避免冲突）
        self.follow_arm_publish_lock = threading.Lock()
        self.follow_arm_publish_lock.acquire()

        # 保存消息类型
        # self.pos_cmd = PosCmd
        # self.joint_control = JointControl
        self.robot_cmd = RobotCmd
        self.robot_status = RobotStatus

        # 摄像头订阅
        img_topics = {
            'img_left': 'img_left_topic',
            'img_head': 'img_head_topic',
        }
        for key, topic in img_topics.items():
            try:
                self.create_subscription(Image,
                                         self.config['camera_config'][topic],
                                         getattr(self, f"{key}_callback"),
                                         2)
            except KeyError as e:
                self.get_logger().error(f"Topic config missing: {e}")
            except AttributeError as e:
                self.get_logger().error(f"Callback not found for key: {key} -> {e}")

        if self.args.use_depth_image:
            depth_img_topics = {
                'img_left_depth': 'img_left_depth_topic',
                'img_head_depth': 'img_head_depth_topic',
            }
            for key, topic in depth_img_topics.items():
                try:
                    self.create_subscription(CompressedImage,
                                             self.config['camera_config'][topic],
                                             getattr(self, f"{key}_callback"),
                                             2)
                except KeyError as e:
                    self.get_logger().error(f"Topic config missing: {e}")
                except AttributeError as e:
                    self.get_logger().error(f"Callback not found for key: {key} -> {e}")

        # 机械臂订阅
        arm_topics = {
            # 'controller_left': ('controller_left_topic', self.pos_cmd),
            # 'arm_feedback_left': ('arm_feedback_left_topic', self.robot_status),
            'follow_arm_left_feedback': ('follow_arm_left_feedback_topic', self.robot_status),
        }
        for key, (topic_key, msg_type) in arm_topics.items():
            print( key, (self.config['arm_config'][topic_key], msg_type))
            try:
                self.create_subscription(msg_type,
                                         self.config['arm_config'][topic_key],
                                         getattr(self, f"{key}_callback"),
                                         2)
            except KeyError as e:
                self.get_logger().error(f"Topic config missing: {e}")
            except AttributeError as e:
                self.get_logger().error(f"Callback not found for key: {key} -> {e}")

        # 推理模式相关发布
        if not self.in_collect:
            self.follow_arm_left_publisher = self.create_publisher(
                self.robot_cmd,
                self.config['arm_config']['follow_arm_left_cmd_topic'],
                10
            )


    # 推理
    def follow_arm_publish(self, left):
        if len(left) == 7:
            msg = self.robot_cmd()
            msg.header = Header()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.joint_pos = left[:6].astype(np.float64)
            msg.gripper = left[6].astype(np.float64)
            #5 joint 4 eef 3 free
            msg.mode=5
            msg.end_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        else:
            print("\033[31mERROR action\033[0m")

            return
        
        self.follow_arm_left_publisher.publish(msg)  # /joint_control
        # joint_state_msg.joint_pos = left
        # self.follow_arm_left_publisher.publish(joint_state_msg)  # /joint_control
        # if len(right) != 0:
        #     joint_state_msg.joint_pos = right
        #     self.follow_arm_right_publisher.publish(joint_state_msg)  # /joint_control2


    def follow_arm_publish_continuous(self, left_target,step=None):
        arm_step = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.15]
        left_arm = None
     
        rate = self.create_rate(self.args.frame_rate)
        while rclpy.ok():
            if len(self.follow_left_arm_deque) != 0:
                print(len(self.follow_left_arm_deque))
                left_arm = list(self.follow_left_arm_deque[-1].joint_pos)

            if left_arm is not None:
                break
            # print(left_arm)

        # 计算方向标志位
        left_symbol = [1 if left_target[i] - left_arm[i] > 0 else -1 for i in range(len(left_target))]
        flag=True
        current_step = 0
        while rclpy.ok() and flag:
            print(current_step)
            current_step += 1
            if step!=None:
                if(current_step>=step):
                    return 
            if self.follow_arm_publish_lock.acquire(False):
                return
            left_diff = [abs(left_target[i] - left_arm[i]) for i in range(len(left_target))]
            flag=False
            for i in range(len(left_target)):
                if left_diff[i] < arm_step[i]:
                    left_arm[i] = left_target[i]
                else:
                    left_arm[i] += left_symbol[i] * arm_step[i]
                    flag=True

            # JointControl topic
            if len(left_arm) == 7:
                msg = self.robot_cmd()

            else:
                print("\033[31mInvalid joint length\033[0m")

                return

            msg.header = Header()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.joint_pos = left_arm[:6]
            msg.gripper = left_arm[6]
            #5 joint 4 eef 3 free
            msg.mode=5
            msg.end_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

            self.follow_arm_left_publisher.publish(msg)
            rate.sleep()

            print("follow_arm_publish_continuous:", current_step)
            rate.sleep()


    def visualize_pid_base(self, states, target, plot_path=None):
        STATE_NAMES = ["DX", "DY", "Yaw"]
        label1, label2 = 'states', 'target'
        states = np.array(states)
        target = np.array(target)

        num_ts, num_dim = states.shape
        fig, axs = plt.subplots(num_dim, 1, figsize=(8, 2 * num_dim))

        all_names = [f"{name}_left" for name in STATE_NAMES] + [f"{name}_right" for name in STATE_NAMES]

        for dim_idx, ax in enumerate(axs):
            ax.plot(states[:, dim_idx], label=label1, color='orangered')
            ax.plot(target[:, dim_idx], label=label2)
            ax.set_title(f'Joint {dim_idx}: {all_names[dim_idx]}')
            ax.legend()

        plt.tight_layout()
        if plot_path:
            plt.savefig(plot_path)
            print(f'Saved pid control plot to: {plot_path}')
        else:
            plt.show()

        plt.close()



    def _extract_eef_data(self, eef):
        return [eef.x, eef.y, eef.z, eef.roll, eef.pitch, eef.yaw]

    def get_observation(self):  # get the robot observation
        img_exsit=1
        img_data = {
            'left_wrist': None,
            'head': None,
            
        }
        img_depth_data = {
            'left_wrist': None,
            'head': None,
        }
        arm_data = {
            'follow_left_arm': self.robot_status(),
        }
        img_msg=None
        # 获取图像信息
        for cam_name in self.args.camera_names:
            if cam_name in img_data:
                deque_map = {
                    'left_wrist': self.img_left_deque,
                    'head': self.img_head_deque,
                }

                if len(deque_map[cam_name]) == 0:
                    print(f'there is no {cam_name}_deque')
                    img_exsit=0
                    return None

                # 是否压缩处理图像
              
                # img_data[cam_name] = self.bridge.compressed_imgmsg_to_cv2(deque_map[cam_name].pop(),
                #                                                           'passthrough')
                # img_msg=deque_map[cam_name].pop()
                img_msg=deque_map[cam_name][-1]
                img_data[cam_name] = self.bridge.imgmsg_to_cv2(img_msg,'bgr8')
                # print(img_data[cam_name])

            if self.args.use_depth_image:
                if cam_name in img_depth_data:
                    deque_map = {
                        'left_wrist_depth': self.img_left_depth_deque,
                        'head_depth': self.img_head_depth_deque,
                    }

                    key = cam_name + '_depth'

                    if len(deque_map[key]) == 0:
                        print(f'there is no {key}_deque')

                        return None

                    img_depth_data[key] = self.bridge.imgmsg_to_cv2(deque_map[key].pop(),
                                                                    'passthrough')

        # 获取机械臂状态
        for arm_name in ['follow_left_arm']:
            deque_map = {
                'follow_left_arm': self.follow_left_arm_deque,
            }

            if len(deque_map[arm_name]) == 0:
                print(f'there is no {arm_name}_deque')

                return None
            # self.total+=1
            # print(self.total)
            arm_data[arm_name] = deque_map[arm_name].pop()
            # arm_data[arm_name] = deque_map[arm_name][-1]

        obs_dict = collections.OrderedDict()  # 有序的字典

        # 保存图像
        obs_dict['images'] = {cam: img for cam, img in img_data.items() if cam in self.args.camera_names}

        if self.args.use_depth_image:
            obs_dict['images_depth'] = {cam: img_depth_data[cam] for cam in img_depth_data if
                                        cam in self.args.camera_names}

        # 保存机械臂状态
        left_eef = np.concatenate([
            arm_data['follow_left_arm'].end_pos,
            [arm_data['follow_left_arm'].joint_pos[-1]],
        ])


        # obs_dict['eef'] = np.concatenate((left_eef, right_eef), axis=0)
        obs_dict['img_time']=img_msg.header.stamp.sec + img_msg.header.stamp.nanosec*1e-9
        obs_dict['eef_time']= arm_data['follow_left_arm'].header.stamp.sec + arm_data['follow_left_arm'].header.stamp.nanosec*1e-9
        obs_dict['eef'] = np.array(left_eef)
        obs_dict['joint']=np.array(arm_data['follow_left_arm'].joint_pos)
        # obs_dict['qpos'] = np.concatenate((np.array(arm_data['follow_left_arm'].joint_pos),
        #                                    np.array(arm_data['follow_right_arm'].joint_pos)), axis=0)
        # obs_dict['qvel'] = np.concatenate((np.array(arm_data['follow_left_arm'].joint_vel),
        #                                    np.array(arm_data['follow_right_arm'].joint_vel)), axis=0)
        # obs_dict['effort'] = np.concatenate((np.array(arm_data['fsollow_left_arm'].joint_cur),
        #                                      np.array(arm_data['follow_right_arm'].joint_cur)), axis=0)
        obs_dict['qpos'] = np.array(arm_data['follow_left_arm'].joint_pos)
        obs_dict['qvel'] = np.array(arm_data['follow_left_arm'].joint_vel)
        obs_dict['effort'] = np.array(arm_data['follow_left_arm'].joint_cur)
        return obs_dict

    def get_action(self):
        joints_dim = 8

        action_dict = collections.OrderedDict()

        deque_map = {
            'control_left_arm_deque': self.controller_left_deque,
        }

        for name, deque in deque_map.items():
            if len(deque) == 0:
                print(f'there is no {name}')

                return None

        # 获取主臂状态
        left_frame = deque_map['control_left_arm_deque'].pop()
        
        control_left_arm = self._extract_eef_data(left_frame)
        
        control_left_arm_gripper = left_frame.gripper
        

        # 主臂保存状态
        control_left_arm_eef = np.concatenate([control_left_arm, [control_left_arm_gripper]])
       

        # 构建动作字典
        # action_dict['action'] = np.zeros((joints_dim * 2,))
        # action_dict['action_qvel'] = np.zeros((joints_dim * 2,))
        action_dict['action'] = np.zeros((joints_dim,))
        action_dict['action_qvel'] = np.zeros((joints_dim,))
        action_dict['action_eef'] = control_left_arm_eef
                                                 
    
        return action_dict


    def img_left_callback(self, msg):
        if len(self.img_left_deque) >= 2000:
            self.img_left_deque.popleft()
        self.img_left_deque.append(msg)

    def img_left_depth_callback(self, msg):
        if len(self.img_left_depth_deque) >= 2000:
            self.img_left_depth_deque.popleft()
        self.img_left_depth_deque.append(msg)

    # def master_left_arm_callback(self, msg):
    #     if len(self.master_left_arm_deque) >= 2000:
    #         self.master_left_arm_deque.popleft()
    #     self.master_left_arm_deque.append(msg)
    def img_head_callback(self, msg):
        if len(self.img_head_deque) >= 2000:
            self.img_head_deque.popleft()
        self.img_head_deque.append(msg)

    def img_head_depth_callback(self, msg):
        if len(self.img_head_depth_deque) >= 2000:
            self.img_head_depth_deque.popleft()
        self.img_head_depth_deque.append(msg)

    def follow_left_arm_callback(self, msg):
        if len(self.follow_left_arm_deque) >= 2000:
            self.follow_left_arm_deque.popleft()
        self.follow_left_arm_deque.append(msg)

    def controller_left_callback(self, msg):
        if len(self.controller_left_deque) >= 2000:
            self.controller_left_deque.popleft()
        self.controller_left_deque.append(msg)

    #主臂状态消息
    def arm_feedback_left_callback(self, msg):
        if len(self.follow_left_arm_deque) >= 2000:
            self.follow_left_arm_deque.popleft()
        self.follow_left_arm_deque.append(msg)

    #从臂状态消息
    def follow_arm_left_feedback_callback(self, msg):
        if len(self.follow_left_arm_deque) >= 2000:
            self.follow_left_arm_deque.popleft()
        self.follow_left_arm_deque.append(msg)

    def _update_arm_position(self, target, arm, symbol, steps_length):
        diff = [abs(target[i] - arm[i]) for i in range(len(target))]
        done = 0
        for i in range(len(target)):
            if diff[i] < steps_length[i]:
                arm[i] = target[i]
                done += 1
            else:
                arm[i] += symbol[i] * steps_length[i]

        return done,arm

def parse_arguments(known=False):
    parser = argparse.ArgumentParser()

    # 数据集配置
    # parser.add_argument('--datasets', type=str, default=Path.joinpath(ROOT, 'datasets'),
    # #                     help='dataset dir')
    # parser.add_argument('--episode_idx', type=int, default=0, help='episode index')
    # parser.add_argument('--max_timesteps', type=int, default=800, help='max timesteps')
    parser.add_argument('--frame_rate', type=int, default=30, help='frame rate')

    # 配置文件
    parser.add_argument('--config', type=str,
                        default='/home/go2/ARX_X5/inference/utils/config.yaml',
                        help='config file')

    # 图像处理选项
    # parser.add_argument('--camera_names', nargs='+', type=str,
    #                     choices=['head', 'left_wrist', 'right_wrist', ],
    #                     default=['head', 'left_wrist', 'right_wrist'], help='camera names')
    parser.add_argument('--camera_names', type=str,
                    choices=['left_wrist','head' ],
                    default=['left_wrist','head'], help='camera names')
    parser.add_argument('--use_depth_image', action='store_true', help='use depth image')

    # # 机器人选项
    # parser.add_argument('--use_base', action='store_true', help='use robot base')
    # parser.add_argument('--record', choices=['Distance', 'Speed'], default='Distance',
    #                     help='record data')

    # # 数据采集选项
    # parser.add_argument('--key_collect', action='store_true', help='use key collect')

    # parser.add_argument('--task', type=str, default='', help='task name')

    return parser.parse_known_args()[0] if known else parser.parse_args()


def load_yaml(yaml_file):
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: File not found - {yaml_file}")

        return None
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file - {e}")

        return None   

if __name__ == "__main__":
    rclpy.init()
    args = parse_arguments()   
    config = load_yaml(args.config)
    ros_operator = RosOperator(args, config, in_collect=False)
    spin_thread = threading.Thread(target=rclpy.spin, args=(ros_operator,), daemon=True)
    spin_thread.start()
    input("Press Enter to continue...\n")
    init_joint=[0.18520641,  0.11310768,  0.72270584, -1.15415382, -0.01811981,0.17299938,  0.01144505]
    ros_operator.follow_arm_publish_continuous(init_joint)
    while(1):
        print(ros_operator.get_observation())
        time.sleep(0.1)
        # print(ros_operator.img_left_deque[-1] if len(ros_operator.img_left_deque) > 0 else None)
    ros_operator.destroy_node()
    rclpy.shutdown()
    spin_thread.join()
