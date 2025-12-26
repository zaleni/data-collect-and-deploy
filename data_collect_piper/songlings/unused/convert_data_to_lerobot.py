from pathlib import Path
import numpy as np
import torch
from converting_utils import organize_data_from_single_run
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
import cv2
import os

def convert_synced_data_format(joint, endpose, gripper, image_paths, folder):
    """将converting_utils的输出格式转换为与原syn_data相同的格式"""
    # 读取并处理图像
    images = []
    for img_name in image_paths:
        img_path = folder / 'imgs' / 'img_1_color' / img_name  # 根据实际路径调整
        img = cv2.imread(str(img_path))
        if img is None:
            raise ValueError(f"无法读取图像: {img_path}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 360))
        # 转换为PyTorch张量并归一化
        img_tensor = torch.from_numpy(img).float() / 255.0
        images.append(img_tensor)

    # 转换机械臂数据为tensor
    endpose_tensor = torch.tensor(
        [
            endpose.end_pose.X_axis,
            endpose.end_pose.Y_axis,
            endpose.end_pose.Z_axis,
            endpose.end_pose.RX_axis,
            endpose.end_pose.RY_axis,
            endpose.end_pose.RZ_axis,
        ],
        dtype=torch.int32,
    )

    joint_tensor = torch.tensor(
        [
            joint.joint_state.joint_1,
            joint.joint_state.joint_2,
            joint.joint_state.joint_3,
            joint.joint_state.joint_4,
            joint.joint_state.joint_5,
            joint.joint_state.joint_6,
        ],
        dtype=torch.int32,
    )

    gripper_tensor = torch.tensor(
        [gripper.gripper_state.grippers_angle],
        dtype=torch.int32,
    )

    return {
        "images": images,
        "endpose": endpose_tensor,
        "joint": joint_tensor,
        "gripper": gripper_tensor,
    }

def convert_data_to_lerobot():
    # 创建LeRobot数据集
    dataset = LeRobotDataset.create(
        repo_id='SongLinPickUpCup',
        robot_type="SongLing",
        fps=10,
        features={
            "img_1_color": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "img_1_depth": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "img_2_color": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "img_2_depth": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "joint": {
                "dtype": "float32",
                "shape": (6,),
                "names": ["joint"],
            },
            "endpose": {
                "dtype": "float32",
                "shape": (6,),
                "names": ["endpose"],
            },
            "gripper": {
                "dtype": "float32",
                "shape": (1,),
                "names": ["gripper"],
            },
            "task": {
                "dtype": "string",
                "shape": (1,),
                "names": ["task"],
            },
        },
    )

    # 指定数据根目录
    root_path = Path("/home/robot/mzk_workspace/data_collect/data/SimplePickUp")
    
    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    
    # 遍历每个数据文件夹
    for folder in data_folders:
        print(f"\n处理文件夹: {folder}")
        try:
            # 使用converting_utils中的函数获取同步后的数据
            synced_data = list(organize_data_from_single_run(folder))
            # 按要求裁剪数据
            synced_data = synced_data[3:-3:3]
            
            # 处理每一帧数据
            for joint, endpose, gripper, image_paths in synced_data:
                # 转换数据格式
                frame_data = convert_synced_data_format(joint, endpose, gripper, image_paths, folder)
                
                # 添加帧数据
                dataset.add_frame(
                    {
                        "img_1_color": frame_data["images"][0].numpy(),
                        "img_1_depth": frame_data["images"][1].numpy(),
                        "img_2_color": frame_data["images"][2].numpy(),
                        "img_2_depth": frame_data["images"][3].numpy(),
                        "joint": frame_data["joint"].float().numpy(),
                        "endpose": frame_data["endpose"].float().numpy(),
                        "gripper": frame_data["gripper"].float().numpy(),
                        "task": str(folder.name),
                    }
                )
            
            # 保存每个文件夹的数据为一个episode
            dataset.save_episode(task=folder.name)
            print(f"成功处理文件夹: {folder}")
            
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错: {str(e)}")
            continue
    
    # 整合数据集
    dataset.consolidate(run_compute_stats=False)
    print("数据集处理完成！")

if __name__ == "__main__":
    convert_data_to_lerobot() 