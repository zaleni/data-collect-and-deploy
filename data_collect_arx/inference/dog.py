#!/usr/bin/env python3
import os
import sys
import argparse
import time
import numpy as np
import rclpy
from rclpy.node import Node
import threading
from utils.ros_operator import RosOperator, load_yaml
from utils.pi0_inference import PI0Inference
from std_msgs.msg import String

import cv2

project_root = "/home/go2/ARX_X5/H_RDT"
sys.path.append(project_root)

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frame_rate', type=int, default=15, help='frame rate')

    # ros配置文件
    parser.add_argument('--config', type=str,
                        default='/home/go2/ARX_X5/inference/utils/config.yaml',
                        help='config file')
    #model配置文件
    parser.add_argument('--config_path', type=str, default='/home/go2/ARX_X5/checkpoint/hrdt_finetune_real_robot_14d.yaml', help='Path to model config file')
    parser.add_argument('--pretrained_model_path', type=str, default='/home/go2/ARX_X5/checkpoint/arrange_umbrella/hrdt_14d_norm/checkpoint-15000', help='Path to pretrained model')
    parser.add_argument('--lang_embeddings_path', type=str, default='/home/go2/ARX_X5/checkpoint/arrange_umbrella/umb_hrdt_14d_finetune_norm/lang_embeddings/arrange_the_umbrellas.pt', help='Path to language embeddings')
    parser.add_argument('--stat_file_path', type=str, default='/home/go2/ARX_X5/checkpoint/arrange_the_umbrellas_14d.json',help='Path to statistics file for action normalization')
    parser.add_argument('--training_mode', type=str, default='lang')
    parser.add_argument('--chunk_size', type=int, default=50)
    # 图像处理选项
    # parser.add_argument('--camera_names', nargs='+', type=str,
    #                     choices=['head', 'left_wrist', 
    # 'right_wrist', ],
    #                     default=['head', 'left_wrist', 'right_wrist'], help='camera names')
    parser.add_argument('--camera_names', type=str,
                    choices=['left_wrist' 'head'],
                    default=['left_wrist','head'], help='camera names')
    parser.add_argument('--use_depth_image', action='store_true', help='use depth image')
    parser.add_argument('--runner_type', type=str, default='default',choices=['default', '7d_selective', '14d_selective'])
    parser.add_argument('--model_dimension', type=int, default=14, choices=[7, 14, 62])
    parser.add_argument('--noise_strategy', type=str, default='gaussian', choices=['zero', 'gaussian', 'uniform'],help='Strategy for generating human action noise')
    parser.add_argument('--noise_scale', type=float, default=1.0, help='Scale of the noise to be added to human actions')
    parser.add_argument('--normalize_actions', action='store_true')
    parser.add_argument('--momentum', type=float, default=0)
    parser.add_argument('--prompt', type=str, default='Pick up the McDonald bag and place it into the box on the robot dog.')
    return parser.parse_args()

class RobotController(Node):
    def __init__(self, args):
        super().__init__('robot_controller')
        self.args = args
        self.ros_operator = RosOperator(args, load_yaml(args.config), in_collect=False)
        spin_thread = threading.Thread(target=rclpy.spin, args=(self.ros_operator,), daemon=True)
        spin_thread.start()
        self.pi0_inference = PI0Inference(args)
        self.init_joint = [-1.4860382080078125, 0.6830320358276367, 1.3399324417114258, -1.2991151809692383, 0.08258914947509766, -0.07648563385009766, 0.007248878479003906]
        self.current_prompt = args.prompt
        self.current_object_type = None  # 当前抓取物体类型
        self.action_buffer = None
        self.prev_action = None
        self.action_delta = None
        self.momentum = args.momentum
        self.t = 0
        self.model_control = False
        self.rate = self.ros_operator.create_rate(args.frame_rate)

        # ROS2 订阅器
        self.subscription = self.create_subscription(
            String,
            '/robot_command',
            self.command_callback,
            10
        )
        # 初始化机械臂到初始位置
        self.get_logger().info("Moving robot to initial joint position...")
        self.ros_operator.follow_arm_publish_continuous(self.init_joint)
        self.get_logger().info("Robot initialized to home position.")

        self.get_logger().info("Robot Controller Initialized. Waiting for commands...")

    def command_callback(self, msg):
        """处理接收到的 ROS2 指令"""
        command = msg.data.lower()
        self.get_logger().info(f"Received command: {command}")
        print(f"Received command: {command}")
        if command == "initialize":
            self.get_logger().info("Initializing robot to home position...")
            self.model_control = False
            self.current_object_type = None
            self.ros_operator.follow_arm_publish_continuous(self.init_joint)
        elif command == "pick_mcdonald":
            self.current_prompt = "Pick up the McDonald bag and place it into the box on the robot dog."
            self.current_object_type = "mcdonald"
            self.model_control = True
        elif command == "pick_tissue":
            self.current_prompt = "Pick up the tissue and place it into the box on the robot dog."
            self.current_object_type = "tissue"
            self.model_control = True
        elif command == "pick_bottle":
            self.current_prompt = "Pick up the water bottle and place it into the box on the robot dog."
            self.current_object_type = "bottle"
            self.model_control = True
        elif command == "pick_gum":
            self.current_prompt = "Pick up the chewing gum and place it into the box on the robot dog."
            self.current_object_type = "gum"
            self.model_control = True
        else:
            self.get_logger().warning(f"Unknown command: {command}")

    def run(self):
        """主循环，控制机械臂"""
        while rclpy.ok():
            print(1)
            ros_observation = self.ros_operator.get_observation()
            if ros_observation is None:
                self.rate.sleep()
                continue
            print(2)
            observation = self.encode_obs(ros_observation)
           
            if self.model_control:
                if self.t % self.args.chunk_size == 0:
                    self.get_logger().info(f"Infer observation: {observation['state']}")
                    self.action_buffer = self.pi0_inference.predict_action(observation)
                    self.action_buffer[0][:7] = observation['state'][:7]  # 对齐第一个动作
                    for i in range(1, self.args.chunk_size):
                        self.action_buffer[i][:7] += self.action_buffer[i - 1][:7]  # 增量变化
                    self.action_delta = observation['state'] - self.action_buffer[0][:7]

                current_action = self.action_buffer[self.t % self.args.chunk_size][:7]
                if self.prev_action is None:
                    self.prev_action = current_action
                else:
                    smoothed_joints = self.momentum * self.prev_action[:6] + (1 - self.momentum) * current_action[:6]
                    current_action = np.concatenate([smoothed_joints, [current_action[6]]])
                    self.prev_action = current_action

                current_action += self.action_delta
                current_action = self.post_process_action(current_action, self.current_object_type)
                self.ros_operator.follow_arm_publish(current_action)

            self.t += 1
            self.rate.sleep()

    def encode_obs(self, observation):
        """编码观测数据"""
        obs = {
            'images': {
                'cam_high': np.transpose(observation['images']['head'], (2, 0, 1)),
                'cam_left_wrist': np.transpose(observation['images']['left_wrist'], (2, 0, 1))
            },
            'state': observation['joint'],
            'prompt': self.current_prompt
        }
        return obs

    def post_process_action(self, action, object_type):
        """后处理动作，限制范围"""
        min_action = [-2.11, -0.00, 0.52, -1.29, -1.14, -1.57, 0.00]
        max_action = [2.38, 2.60, 2.23, 0.25, 1.47, 1.69, 5.31]
            # 根据物体类型应用特定的后处理逻辑
        if object_type == "mcdonald":
            if action[6] > 1.5:
                action[6] += 3.0
        elif object_type == "tissue":
            pass
        elif object_type == "bottle":
            pass
        elif object_type == "gum":
            pass
        for i in range(len(action)):
            action[i] = max(min(action[i], max_action[i]), min_action[i])
        return action

def main(args=None):
    rclpy.init(args=args)
    args = get_arguments()
    robot_controller = RobotController(args)

    try:
        robot_controller.run()
    except KeyboardInterrupt:
        robot_controller.get_logger().info("Shutting down robot controller...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()