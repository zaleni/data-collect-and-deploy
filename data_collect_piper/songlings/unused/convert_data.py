from pathlib import Path
import numpy as np
import torch
from converting_utils import organize_data_from_single_run, _extract_timestamp_from_image_name, sync_data
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
# from lerobot.common.datasets.lerobot_dataset import HF_LEROBOT_HOME
import cv2
import os
from rich import print
import time

# 仅对数据进行同步和查看
def sync_all_data_folders(root_path):
    # 指定数据根目录
    # root_path = "/home/robot/mzk_workspace/data_collect/data/SimplePickUp"
    root_path = Path(root_path)

    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    
    # 遍历每个数据文件夹
    for folder in data_folders:
        print(f"\n#############正在同步文件夹: {folder}")
        try:
            # 获取同步后的数据
            u = list(organize_data_from_single_run(folder))
            # 按要求裁剪数据
            u = u[3:-3:3]
            
            print(f"数据长度: {len(u)}")
            print(f"时间跨度: {u[-1][0].time_stamp - u[0][0].time_stamp}")
            
            # 打印每组数据的时间戳
            for j, e, g, (i1, i2, d1, d2) in u:
                print(f'joint  : {j.time_stamp}')
                print(f'eef    : {e.time_stamp}')
                print(f'gripper: {g.time_stamp}')
                print(f'i1     : {_extract_timestamp_from_image_name(i1)}')
                print(f'i2     : {_extract_timestamp_from_image_name(i2)}')
                print(f'd1     : {_extract_timestamp_from_image_name(d1)}')
                print(f'd2     : {_extract_timestamp_from_image_name(d2)}')
                print(f'i1_path: {i1}')
                print(f'i2_path: {i2}')
                print(f'd1_path: {d1}')
                print(f'd2_path: {d2}')
                print('y')
                user_input = input('按回车继续，输入q退出，输入j跳过当前文件夹进入下一个:')
                if user_input.lower() == 'q':
                    return
                if user_input.lower() == 'j':
                    break
                
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错: {str(e)}")
            continue

# 对数据进行同步和转换
def convert_data_to_lerobot(root_path):
    # 创建LeRobot数据集
    dataset = LeRobotDataset.create(
        repo_id='SongLinPickUpCup1',
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
    root_path = Path(root_path)
    
    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    
    # 遍历每个数据文件夹
    for folder in data_folders:
        print(f"\n############正在同步并转换文件夹: {folder}")
        try:
            # 使用converting_utils中的函数获取同步后的数据
            synced_data = list(organize_data_from_single_run(folder))
            # 按要求裁剪数据
            synced_data = synced_data[3:-3:3]

            print(f"数据长度: {len(synced_data)}")
            print(f"时间跨度: {synced_data[-1][0].time_stamp - synced_data[0][0].time_stamp}")
            
            # 处理每一帧数据
            for joint, endpose, gripper, (img1_color, img2_color, img1_depth, img2_depth) in synced_data:
                # print(f'joint  : {joint.time_stamp}')
                # print(f'eef    : {endpose.time_stamp}')
                # print(f'gripper: {gripper.time_stamp}')
                # print(f'i1     : {_extract_timestamp_from_image_name(img1_color)}')
                # print(f'i2     : {_extract_timestamp_from_image_name(img2_color)}')
                # print(f'd1     : {_extract_timestamp_from_image_name(img1_depth)}')
                # print(f'd2     : {_extract_timestamp_from_image_name(img2_depth)}')
                # user_input = input('按回车继续，输入q退出，输入j跳过当前文件夹进入下一个:')
                # if user_input.lower() == 'q':
                #     return
                # if user_input.lower() == 'j':
                #     break

                # 读取图像
                img_paths = {
                    'img_1_color': folder / 'imgs' / 'img_1_color' / img1_color,
                    'img_2_color': folder / 'imgs' / 'img_2_color' / img2_color,
                    'img_1_depth': folder / 'imgs' / 'img_1_depth' / img1_depth,
                    'img_2_depth': folder / 'imgs' / 'img_2_depth' / img2_depth
                }
                
                images = {}
                for key, path in img_paths.items():
                    img = cv2.imread(str(path))
                    if img is None:
                        raise ValueError(f"无法读取图像: {path}")
                    img = cv2.resize(img, (640, 360))
                    images[key] = img

                # 添加帧数据
                dataset.add_frame(
                    {
                        "img_1_color": images['img_1_color'],
                        "img_1_depth": images['img_1_depth'],
                        "img_2_color": images['img_2_color'],
                        "img_2_depth": images['img_2_depth'],
                        "joint": np.array(joint.joint_values, dtype=np.float32),
                        "endpose": np.array(endpose.pose_values, dtype=np.float32),
                        "gripper": np.array([gripper.gripper_value], dtype=np.float32),
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
    

def convert_synced_data_format(joint, endpose, gripper, image_paths, folder):
    """将converting_utils的输出格式转换为与原syn_data相同的格式"""
    # 读取并处理图像
    images = []
    image_paths = {
        'img_1_color_path' : folder / 'imgs' / 'img_1_color' / image_paths[0],
        'img_2_color_path' : folder / 'imgs' / 'img_2_color' / image_paths[1],
        'img_1_depth_path' : folder / 'imgs' / 'img_1_depth' / image_paths[2],
        'img_2_depth_path' : folder / 'imgs' / 'img_2_depth' / image_paths[3]
    }

    for img_name, img_path in image_paths.items():
        # img_path = folder / 'imgs' / 'img_1_color' / img_name  # 根据实际路径调整
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

def convert_data_to_lerobot_v2(root_path):
    # 创建LeRobot数据集
    dataset = LeRobotDataset.create(
        repo_id='SongLinPickUpCup04',
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
            }
        },
    )

    # 指定数据根目录
    root_path = Path(root_path)
    
    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    
    # 遍历每个数据文件夹
    for index, folder in enumerate(data_folders):
        print(f"\n处理文件夹: {folder}")
        try:
            # 使用converting_utils中的函数获取同步后的数据
            synced_data = list(organize_data_from_single_run(folder))
            # 按要求裁剪数据
            synced_data = synced_data[3:-3:3]
            
            # 处理每一帧数据
            for joint, endpose, gripper, image_paths in synced_data:

                # 读取图像并转换数据格式
                frame_data = convert_synced_data_format(joint, endpose, gripper, image_paths, folder)
                
                # 添加帧数据
                dataset.add_frame(
                    {
                        "img_1_color": frame_data["images"][0],
                        "img_1_depth": frame_data["images"][1],
                        "img_2_color": frame_data["images"][2],
                        "img_2_depth": frame_data["images"][3],
                        "joint": frame_data["joint"].float(),
                        "endpose": frame_data["endpose"].float(),
                        "gripper": frame_data["gripper"].float(),
                    }
                )
            
            # 保存每个文件夹的数据为一个episode
            dataset.save_episode(task=f'Pick up the cup')
            print(f"成功处理文件夹: {folder}")
            
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错: {str(e)}")
            continue
    
    # 整合数据集
    dataset.consolidate(run_compute_stats=True)
    print("数据集处理完成！")

def form_eef_state_action(eef_list, gripper_list):
    res = []
    for eef, gripper in zip(eef_list, gripper_list):
        res.append(torch.tensor([
                eef.end_pose.X_axis,
                eef.end_pose.Y_axis,
                eef.end_pose.Z_axis,
                eef.end_pose.RX_axis,
                eef.end_pose.RY_axis,
                eef.end_pose.RZ_axis,
                gripper.gripper_state.grippers_angle
            ],
            dtype=torch.float32,
        ))
    return res

def load_image(image_path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"无法读取图像: {image_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 360))
    # 转换为PyTorch张量并归一化
    img_tensor = torch.from_numpy(img).float() / 255.0
    return img_tensor

def is_noops(state, action, arm_threshold=1000, gripper_threshold=50) -> bool:
    """
    Formal noops filter. Consider to removing noops operation arm state and gripper state, respectively.
    (WIP) without testing, do not use this function, by junlin xie (2025-03-20, 17:09)
    
    Modifies:
        1. add gripper_threshold=20
        2. change arm_threshold=1000
    """
    arm_state_diff = torch.sum(torch.abs(state[:6] - action[:6]))
    
    gripper_state_diff = torch.abs(state[6] - action[6])
    return (arm_state_diff < arm_threshold) and (gripper_state_diff < gripper_threshold)

def is_too_close(state, action) -> bool :
    return (torch.sum(torch.abs(state - action)) < 500).item()

def is_too_far(state, action) -> bool: 
    return (torch.sum(torch.abs(state - action)[:3]) > 100000).item()

def convert_data_to_lerobot_with_action_and_state(root_path, repo_id):
    # 创建LeRobot数据集
    dataset = LeRobotDataset.create(
        # repo_id=f'{repo_id}@{str(time.time()).replace(".", "")}',
        repo_id=f'{repo_id}-Resample',
        robot_type="Piper",
        fps=10,
        features={
            "wrist_rgb": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "wrist_depth": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "front_rgb": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "front_depth": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "action": {
                "dtype": "float32",
                "shape": (7,),
                "names": ["eef", "gripper"]
            },
            "state": {
                "dtype": "float32",
                "shape": (7,),
                "names": ["eef", "gripper"]
            }
        },
    )

    # 指定数据根目录
    root_path = Path(root_path)
    
    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    data_folders.sort()
    
    # 遍历每个数据文件夹
    for index, folder in enumerate(data_folders):
        print(f"\n[{index}/{len(data_folders)}]处理文件夹: {folder}")

        # 使用converting_utils中的函数获取同步后的数据
        synced_data = list(organize_data_from_single_run(folder))
        # 按要求裁剪数据
        synced_data = synced_data[1::3]

        jt, eef, gp, imgs = list(zip(*synced_data))
        
        state_seq = form_eef_state_action(eef, gp)
        
        for action, state, img in zip(state_seq[1:], state_seq, imgs):
            # print(torch.abs(state - action))
            # print(torch.sum(torch.abs(state - action)))
            if is_too_close(state, action) or is_noops(state, action):
                continue
            if is_too_far(state, action):
                break
            dataset.add_frame(
                {
                    # （已解决）这里的腕部数据和第三人称数据保存时反了！！！！！！转换时请确认摄像头位置！！！！！
                    "front_rgb":   load_image(root_path / folder.name  / 'img' / 'front_color' / img[0]),
                    "wrist_rgb":   load_image(root_path / folder.name  / 'img' / 'wrist_color' / img[1]),
                    "front_depth": load_image(root_path / folder.name  / 'img' / 'front_depth' / img[2]),
                    "wrist_depth": load_image(root_path / folder.name  / 'img' / 'wrist_depth' / img[3]),
                    "action": action,
                    "state": state
                }
            )
        
        # 保存每个文件夹的数据为一个episode
        dataset.save_episode(task=f'Table bussing')
        print(f"成功处理文件夹: {folder}")
    
    # 整合数据集
    dataset.consolidate(run_compute_stats=False)
    print("数据集处理完成！")

def __test_do_not_use_this_funtion(root_path):
    root_path = Path(root_path)
    
    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    
    res = []
    # 遍历每个数据文件夹
    for index, folder in enumerate(data_folders):
        print(f"\n处理文件夹: {folder}")
        try:
            synced_data = list(organize_data_from_single_run(folder))
            synced_data = synced_data[3:-3:3]

            jt, eef, gp, imgs = list(zip(*synced_data))
            state_seq = form_eef_state_action(eef, gp)
            temp = []
            for action, state, img in zip(state_seq[1:], state_seq, imgs):
                temp.append(
                    {
                        # "wrist_rgb":   str(root_path / folder.name  / 'imgs' / 'img_1_color' / img[0]),
                        # "front_rgb":   str(root_path / folder.name  / 'imgs' / 'img_2_color' / img[1]),
                        # "wrist_depth": str(root_path / folder.name  / 'imgs' / 'img_1_depth' / img[2]),
                        # "front_depth": str(root_path / folder.name  / 'imgs' / 'img_2_depth' / img[3]),
                        "action": str(action),
                        "state": str(state)
                    }
                )
            print(f"成功处理文件夹: {folder}")
            res.append(temp)
            
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错: {str(e)}")
            continue
    import json
    json.dump(res, open('./files_state.json', 'w'), indent=2)

def __test_to_remove_nop(root_path):
    # 指定数据根目录
    root_path = Path(root_path)
    
    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    
    res = []
    # 遍历每个数据文件夹
    for index, folder in enumerate(data_folders):
        print(f"\n处理文件夹: {folder}")
        try:
            # 使用converting_utils中的函数获取同步后的数据
            synced_data = list(organize_data_from_single_run(folder))
            # 按要求裁剪数据
            synced_data = synced_data[1::3]

            jt, eef, gp, imgs = list(zip(*synced_data))
            
            state_seq = form_eef_state_action(eef, gp)
            
            temp = []
            for action, state, img in zip(state_seq[1:], state_seq, imgs):
                if is_too_close(state, action):
                    continue
                temp.append(
                    {
                        # "wrist_rgb":   load_image(root_path / folder.name  / 'imgs' / 'img_1_color' / img[0]),
                        # "front_rgb":   load_image(root_path / folder.name  / 'imgs' / 'img_2_color' / img[1]),
                        # "wrist_depth": load_image(root_path / folder.name  / 'imgs' / 'img_1_depth' / img[2]),
                        # "front_depth": load_image(root_path / folder.name  / 'imgs' / 'img_2_depth' / img[3]),
                        "action": action,
                        "state": state
                    }
                )
            res.append(temp)
            
            # 保存每个文件夹的数据为一个episode
            
            print(f"成功处理文件夹: {folder}")
            
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错: {str(e)}")
            continue
    
    # 整合数据集
    
    print("数据集处理完成！")
    import pickle
    pickle.dump(res, open('/home/robot/mzk_workspace/data_collect/tmp/verify_data/vd.pickle', 'wb'))


if __name__ == "__main__":
    # sync_all_data_folders(root_path="/home/robot/mzk_workspace/data_collect/data/SimplePickUp")
    # convert_data_to_lerobot(root_path="/home/robot/mzk_workspace/data_collect/data/SimplePickUp")
    # convert_data_to_lerobot_v2(root_path="/home/robot/mzk_workspace/data_collect/data/SimplePickUp")
    convert_data_to_lerobot_with_action_and_state(root_path='/home/robot/mzk_workspace/data_collect/data/stage2/resample_data_by_gjq-03-17', repo_id='SongLin')
    # __test_do_not_use_this_funtion(root_path='/home/robot/mzk_workspace/data_collect/data/SimplePickUp')
    # __test_to_remove_nop('/home/robot/mzk_workspace/data_collect/data/orange_in_bowl')