
import os
import sys
import argparse
import time
import numpy as np
import rclpy
import threading
from utils.ros_operator import RosOperator,load_yaml


import cv2
project_root = "/home/pc3/deploy/RoboTwin/policy/ACT"
sys.path.append(project_root)

from act_policy_real import ACT

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frame_rate', type=int, default=15, help='frame rate')

    # ros配置文件
    parser.add_argument('--config', type=str,
                        default='/home/go2/ARX_X5/inference/utils/config.yaml',
                        help='config file')
    #model配置文件
    parser.add_argument('--lang_embeddings_path', type=str, default='/home/go2/ARX_X5/checkpoint/arrange_umbrella/umb_hrdt_14d_finetune_norm/lang_embeddings/arrange_the_umbrellas.pt', help='Path to language embeddings')
    parser.add_argument('--stat_file_path', type=str, default='/home/go2/ARX_X5/checkpoint/arrange_the_umbrellas_14d.json',help='Path to statistics file for action normalization')
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
    parser.add_argument('--momentum', type=float, default=0.5)
    parser.add_argument('--prompt', type=str, default='Use the robotic arm to pick up the beverage and place it on the mat.')
    parser.add_argument('--config_path', type=str, default='/home/pc3/deploy/act/act_config.yaml', help='Path to ACT model configuration file')
     
        # 模型服务器配置
    return parser.parse_args()


class ACTInference:
    def __init__(self, args):
        self.args = args
        self.cfg = load_yaml(args.config_path)
        assert self.cfg is not None, f"配置文件无效: {args.config_path}"
        # 确保有必要字段
        default_stub = {
            "policy_class": "ACT",
            "task_name": "deploy-dummy",
            "seed": 0,
            "num_epochs": 1,
            "save_freq": 1,
            "device": "cuda:0",
        }
        # 训练时 action_dim 等于 14
        merged = {**default_stub, **self.cfg}
        # camera_names
        self.camera_names = merged.get("camera_names", ["cam_high", "cam_left_wrist"])
        self.model_chunk_size = int(merged.get("chunk_size", self.args.chunk_size))
        # 创建模型（传 dict 而非路径）
        self.model = ACT(merged)
        if hasattr(self.model, "stats") and self.model.stats:
            print("已加载数据集统计，将执行反归一化")
        else:
            print("未找到 dataset_stats.pkl，动作为未反归一化原值")

    def predict_action(self, observation):
        # 固定返回整段动作，不推进内部 self.t，避免与外部 t 失配
        return self.model.get_chunk(observation)


def save_camera_views(observation, save_dir='visualization'):
    """保存相机视图到文件"""
    if observation is None or 'images' not in observation:
        return
    
    images = observation['images']
    camera_configs = [
        ('cam_left_wrist', 'left_wrist_view.jpg'),
        ('cam_high', 'head_view.jpg')
    ]
    
    for camera_name, filename in camera_configs:
        camera_image = images.get(camera_name, None)
        if camera_image is None:
            continue
        save_path = os.path.join(save_dir, filename)
        cv2.imwrite(save_path, camera_image)



# def encode_obs(observation):
#     obs={}
#     obs['images'] = {}  
#     obs['images']['head_cam'] = observation['images']['head']
#     # obs['images']['head_cam'] = None
#     obs['images']['left_cam'] = observation['images']['left_wrist']
#     # obs['images']['left_cam'] = None
#     obs['images']['right_cam'] = None
#     obs['puppet_left']=observation['joint']
#     obs['puppet_right']=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#     # obs['agent_pos']=np.concatenate([observation['joint'], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
#     return obs



def post_process_action(action):
    min_action=[-1.34,0.35,0.5,-1.29,-1.1,-1.73,0.1]
    max_action=[ 0.97, 2.2,2.6,0.32,0.78,1.73,5.3]
    if action[6]>1.5:
        action[6]+=3.0
    for i in range(len(action)):
        if action[i]>max_action[i]:
            action[i]=max_action[i]
        if action[i]<min_action[i]:
            action[i]=min_action[i] 
    return action

MODEL_TO_REAL_CAM = {
    "cam_high": "head",
    "cam_left_wrist": "left_wrist",
    # 如需扩展在此继续添加
}



def encode_obs(observation, camera_names, model2real_map):
    obs = {}
    images = observation.get("images", {})
    # 按模型配置的 camera_names 顺序取图像，并转为 [3,H,W], float32 [0,1]
    for cam in camera_names:
        real_key = model2real_map.get(cam, cam)
        img = images[real_key]  # [H,W,3] RGB or BGR，按你的 RosOperator 输出而定
        if img.dtype != np.float32:
            img = img.astype(np.float32) / 255.0
        chw = np.transpose(img, (2, 0, 1))
        obs[cam] = chw
    # qpos: 拼到 14 维（左臂 7 + 右臂 7，右臂此处补 0）
    qpos7 = np.asarray(observation["qpos"], dtype=np.float32)
    if qpos7.shape[0] == 7:
        qpos = np.concatenate([qpos7, np.zeros(7, dtype=np.float32)], axis=0)
    else:
        qpos = qpos7
    obs["qpos"] = qpos
    return obs



if __name__ == '__main__':
    rclpy.init()
    args = get_arguments()
    config = load_yaml(args.config)
    input("Press Enter to start ROS operator...")
    ros_operator = RosOperator(args, config, in_collect=False)
    spin_thread = threading.Thread(target=rclpy.spin, args=(ros_operator,), daemon=True)
    spin_thread.start()

    act_inference = ACTInference(args)
        # 保险起见，重置模型内部时间步
    if hasattr(act_inference.model, "reset"):
        act_inference.model.reset()
    print("ACT model initialized.")
    
    # init_joint=[0.18520641,  0.11310768,  0.72270584, -1.15415382, -0.01811981,0.17299938,  0.01144505]
    # init_joint=[-0.10128211975097656, 0.7059202194213867,1.457045555114746, -1.2983522415161133, -0.039101600646972656, -0.055123329162597656, 0.020600318908691406]
    init_joint=[-0.09098148345947266,1.2834749221801758,2.1738386154174805,-1.3014039993286133,-0.02422332763671875, -0.00782012939453125, 0.020981788635253906]


    ros_operator.follow_arm_publish_continuous(init_joint)
    save_dir = '/home/go2/ARX_X5/inference/visualization'
    os.makedirs(save_dir, exist_ok=True)
    input("Robot to initial joint state")
    rate=ros_operator.create_rate(args.frame_rate)
    t=0
    action_buffer=None
    prev_action = None
    momentum = args.momentum
    while rclpy.ok():

        ros_observation=ros_operator.get_observation()
        if ros_observation is None:
            rate.sleep()
            continue
        # print("ros_observation",ros_observation)
        observation = encode_obs(
            ros_observation,
            act_inference.camera_names,
            MODEL_TO_REAL_CAM
        )
        
        if t%args.chunk_size==0:
             action_buffer =act_inference.predict_action(observation)
             print(action_buffer)
        
        print("current:", observation['qpos'])
        save_camera_views(observation, save_dir)


        if action_buffer is not None:
            current_action = action_buffer[t % args.chunk_size][:7]

            if prev_action is None:
                prev_action = current_action
            else:
                smoothed_joints = momentum * prev_action[:6] + (1 - momentum) * current_action[:6]
                current_action = np.concatenate([smoothed_joints, [current_action[6]]])
                prev_action = current_action


            print("predict action:", current_action)
            current_action=post_process_action(current_action)
            print("post action:", current_action)
            ros_operator.follow_arm_publish(current_action)
           
        # print(observation)

        t+=1
        rate.sleep()
