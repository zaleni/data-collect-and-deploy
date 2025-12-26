
import os
import sys
import argparse
import time
import numpy as np
import rclpy
import threading
from utils.ros_operator import RosOperator,load_yaml
from utils.model_inference import HRDTInference

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frame_rate', type=int, default=15, help='frame rate')

    # ros配置文件
    parser.add_argument('--config', type=str,
                        default='/home/go2/ARX_X5/inference/utils/config.yaml',
                        help='config file')
    #model配置文件
    parser.add_argument('--config_path', type=str, default='/home/go2/ARX_X5/checkpoint/hrdt_pick-rubbish/hrdt.yaml', help='Path to model config file')
    parser.add_argument('--pretrained_model_path', type=str, default='/home/go2/ARX_X5/checkpoint/hrdt_pick-rubbish', help='Path to pretrained model')
    parser.add_argument('--lang_embeddings_path', type=str, default='/home/go2/ARX_X5/checkpoint/hrdt_pick-rubbish/lang_embeddings/pick_trash_exp.pt', help='Path to language embeddings')
    parser.add_argument('--stat_file_path', type=str, default='/home/go2/ARX_X5/checkpoint/hrdt_pick-rubbish/stats.json',help='Path to statistics file for action normalization')
    parser.add_argument('--training_mode', type=str, default='lang')
    parser.add_argument('--chunk_size', type=int, default=16)
    # 图像处理选项
    # parser.add_argument('--camera_names', nargs='+', type=str,
    #                     choices=['head', 'left_wrist', 'right_wrist', ],
    #                     default=['head', 'left_wrist', 'right_wrist'], help='camera names')
    parser.add_argument('--camera_names', type=str,
                    choices=['left_wrist' ],
                    default=['left_wrist'], help='camera names')
    parser.add_argument('--use_depth_image', action='store_true', help='use depth image')
    return parser.parse_args()

def encode_obs(observation):
    obs={}
    obs['images'] = {}  
    obs['images']['head_cam'] = None
    obs['images']['left_cam'] = observation['images']['left_wrist']
    obs['images']['right_cam'] = None
    obs['puppet_left']=observation['joint']
    obs['puppet_right']=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    # obs['agent_pos']=np.concatenate([observation['joint'], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    return obs

def post_process_action(action):
    max_action=[2.0,2.8,2.0,1.3,1.5,2.0,5.0]
    min_action=[-2.0,-0.01,-0.0,-1.6,-2.0,-1.6,0.03]
    for i in range(len(action)):
        if action[i]>max_action[i]:
            action[i]=max_action[i]
        if action[i]<min_action[i]:
            action[i]=min_action[i] 
    return action

def main():
    rclpy.init()
    args = get_arguments()
    config = load_yaml(args.config)
    hrdt_inference = HRDTInference(args)
    input("Press Enter to start ROS operator...")
    ros_operator = RosOperator(args, config, in_collect=False)
    spin_thread = threading.Thread(target=rclpy.spin, args=(ros_operator,), daemon=True)
    spin_thread.start()
    init_joint=[0.18520641,  0.11310768,  0.72270584, -1.15415382, -0.01811981,0.17299938,  0.01144505]
    ros_operator.follow_arm_publish_continuous(init_joint)
    
    input("Robot to initial joint state")
    rate=ros_operator.create_rate(args.frame_rate)
    t=0
    action_buffer=None
    prev_action=np.zeros(14)
    while rclpy.ok():
        ros_observation=ros_operator.get_observation()
        if ros_observation is None:
            rate.sleep()
            continue
        
        observation=encode_obs(ros_observation)
        hrdt_inference.update_obs(observation)
        
        if t%args.chunk_size==0:
             action_buffer = hrdt_inference.predict_action(observation)
             print(action_buffer)
        
        print("current:", observation['puppet_left'])
        # print("right:", observation['puppet_right'])
        print("head_cam:", type(observation['images']['head_cam']))
        print("left_cam shape:", observation['images']['left_cam'].shape if observation['images']['left_cam'] is not None else None)
        import cv2
        cv2.imshow("Left Cam", observation['images']['left_cam'])
        cv2.waitKey(1)  # 1ms刷新窗口
        print("right_cam:", type(observation['images']['right_cam']))


        if action_buffer is not None:
            current_action = action_buffer[t % args.chunk_size][:7]
            print("predict action:", current_action)
            current_action=post_process_action(current_action)
            print("post action:", current_action)
            ros_operator.follow_arm_publish(current_action)
           
        # print(observation)

        t+=1
        rate.sleep()


if __name__ == '__main__':
    main()