# -- coding: UTF-8
import os
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode='w', buffering=1)

from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    os.chdir(str(ROOT))

import time
import h5py
import argparse
import rclpy
import cv2
import yaml
import threading
import pyttsx3

import numpy as np

from copy import deepcopy
import select
import termios
import tty

from utils.ros_operator import Rate, RosOperator
from utils.setup_loader import setup_loader
from scipy.spatial.transform import Rotation as R  
try:
    from turbojpeg import TurboJPEG
    USE_TURBOJPEG = True
except ImportError:
    print("警告：未找到PyTurboJPEG库，将使用OpenCV编码")
    USE_TURBOJPEG = False

np.set_printoptions(linewidth=200)

voice_engine = pyttsx3.init()
voice_engine.setProperty('voice', 'en')
voice_engine.setProperty('rate', 120)  # 设置语速

voice_lock = threading.Lock()

init_eef=[-0.06067 ,0.00199,  0.25411]
init_range=0.01



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

def print_eef(eef):
    tips=['后','前','右','左','下','上']
    for i in range(3):
        if abs(eef[i]-init_eef[i])<init_range:
            print(f'\033[32m{eef[i]:.5f}\033[0m', end=' ')
        elif eef[i]>init_eef[i]+init_range:
            print(f'\033[31m{eef[i]:.5f} {tips[i*2]}\033[0m', end=' ')
        else:
            print(f'\033[31m{eef[i]:.5f} {tips[i*2+1]}\033[0m', end=' ')
    print('\n')



def voice_process(voice_engine, line):
    with voice_lock:
        voice_engine.say(line)
        voice_engine.runAndWait()
        print(line)

    return


def get_key():
    """非阻塞获取按键输入"""
    if select.select([sys.stdin], [], [], 0.01)[0]:
        return sys.stdin.read(1)
    return None

def setup_terminal():
    """设置终端为原始模式"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    return old_settings

def restore_terminal(old_settings):
    """恢复终端设置"""
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)




def collect_detect_with_key(args, start_episode, voice_engine, ros_operator):
    """带按键检测和实时可视化的准备阶段 - 双摄像头版本"""
    rate = Rate(args.frame_rate)
    print(f"\033[33mPreparing to record episode {start_episode}\033[0m")
    print(f"\033[36mPress 's' to start recording, 'q' to quit\033[0m")
    print(f"\033[36mLive camera preview is shown\033[0m")
    
    # 创建OpenCV窗口
    cv2.namedWindow('Camera Preview', cv2.WINDOW_NORMAL)
    
    # 持续检测按键，直到按下's'或'q'
    while rclpy.ok():
        key = get_key()
        
        if key == 's':
            print(f"\033[32m\nStarting recording...\033[0m")
            voice_process(voice_engine, "Start recording")
            cv2.destroyAllWindows()
            return True
        elif key == 'q':
            print(f"\033[31m\nQuitting...\033[0m")
            cv2.destroyAllWindows()
            return False
        
        # 显示当前状态和图像预览
        obs_dict = ros_operator.get_observation()
        if obs_dict:
            # 终端显示EEF状态
            print(f"\rWaiting for 's' key... EEF: ", end='')
            print_eef(obs_dict['eef'])
            
            # 图像预览 - 双摄像头并排显示
            if 'images' in obs_dict and obs_dict['images']:
                preview_images = []
                
                for cam_name in args.camera_names:
                    if cam_name in obs_dict['images']:
                        img = obs_dict['images'][cam_name]
                        if img is not None:
                            # 创建预览图像
                            preview_img = img.copy()
                            
                            # 添加摄像头标识
                            cam_label = f"{cam_name.upper()}"
                            cv2.putText(preview_img, cam_label, (10, 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                            
                            # 添加预览信息（只在第一个摄像头上显示）
                            if cam_name == args.camera_names[0]:
                                cv2.putText(preview_img, "PREVIEW MODE", (10, 60), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                                cv2.putText(preview_img, f"Episode: {start_episode}", (10, 90), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                                cv2.putText(preview_img, "Press 's' to start, 'q' to quit", (10, 120), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                                
                                # EEF位置
                                if 'eef' in obs_dict:
                                    eef_pos = obs_dict['eef'][:3]
                                    eef_text = f"EEF: [{eef_pos[0]:.3f}, {eef_pos[1]:.3f}, {eef_pos[2]:.3f}]"
                                    cv2.putText(preview_img, eef_text, (10, 150), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                            
                            preview_images.append(preview_img)
                
                # 合并图像（横向拼接）
                if len(preview_images) > 0:
                    # 确保所有图像高度一致
                    max_height = max(img.shape[0] for img in preview_images)
                    resized_images = []
                    for img in preview_images:
                        if img.shape[0] != max_height:
                            scale = max_height / img.shape[0]
                            new_width = int(img.shape[1] * scale)
                            img = cv2.resize(img, (new_width, max_height))
                        resized_images.append(img)
                    
                    # 横向拼接
                    combined_image = np.hstack(resized_images)
                    cv2.imshow('Camera Preview', combined_image)
                    
                    # 检查OpenCV窗口按键
                    cv_key = cv2.waitKey(1) & 0xFF
                    if cv_key == ord('s'):
                        print(f"\033[32m\nStarting recording...\033[0m")
                        voice_process(voice_engine, "Start recording")
                        cv2.destroyAllWindows()
                        return True
                    elif cv_key == ord('q'):
                        print(f"\033[31m\nQuitting...\033[0m")
                        cv2.destroyAllWindows()
                        return False
        
        rate.sleep()
    
    cv2.destroyAllWindows()
    return False

def create_and_write_mp4(args, data_dict, dataset_path, data_size):
    """
    从数据字典中提取图像并生成MP4视频文件
    """
    import cv2
    import os
    
    # 检查是否有图像数据
    print("Data dict keys:", data_dict.keys())
    if 'images' not in data_dict or not data_dict['images']:
        print("No image data found, skipping MP4 creation")
        return
    
    # 获取相机名称
    camera_names = args.camera_names if hasattr(args, 'camera_names') else ['left_wrist'] 
    for cam_name in camera_names:
        print(f"Processing camera: {cam_name}")
        # 从images列表中提取该相机的所有帧
        images_for_camera = []
        for frame_dict in data_dict['images']:
            if isinstance(frame_dict, dict) and cam_name in frame_dict:
                img = frame_dict[cam_name]
                if img is not None:
                    images_for_camera.append(img)
                else:
                    print(f"Warning: None image found for {cam_name}")
            else:
                print(f"Warning: Invalid frame structure or missing {cam_name}")
        
        if not images_for_camera:
            print(f"No valid images found for camera {cam_name}, skipping")
            continue
        
        print(f"Found {len(images_for_camera)} images for {cam_name}")
        
        # 创建视频文件路径
        video_path = f"{dataset_path}_{cam_name}.mp4"       
        try:
            # 获取第一帧图像来确定视频尺寸
            first_frame = images_for_camera[0]
            if first_frame is None:
                print(f"First frame is None for {cam_name}, skipping")
                continue
                
            height, width = first_frame.shape[:2]
            print(f"Video dimensions: {width}x{height}")
            
            # 设置视频编码器和参数
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或者使用 'XVID'
            fps = args.frame_rate if hasattr(args, 'frame_rate') else 10
            
            # 创建VideoWriter对象
            out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                print(f"Failed to open video writer for {video_path}")
                continue
            
            print(f"Creating MP4 for {cam_name}: {len(images_for_camera)} frames, {width}x{height}, {fps}fps")
            
            # 写入每一帧
            for i, frame in enumerate(images_for_camera):
                if frame is not None and len(frame.shape) == 3:
                    # 确保图像是BGR格式（OpenCV默认）
                    if frame.shape[2] == 3:
                        # OpenCV默认使用BGR，但如果你的图像是RGB格式，需要转换
                        # 根据你的数据，看起来是RGB格式，所以转换为BGR
                        # frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        out.write(frame)
                    else:
                        print(f"Warning: Invalid frame format at index {i} for {cam_name} - shape: {frame.shape}")
                else:
                    print(f"Warning: Invalid frame at index {i} for {cam_name}")
            
            # 释放资源
            out.release()
            
            # 验证文件是否创建成功
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / 1024 / 1024  # MB
                print(f"\033[32m✓ Successfully created {video_path} ({file_size:.1f}MB)\033[0m")
            else:
                print(f"\033[31m✗ Failed to create {video_path}\033[0m")
       
        except Exception as e:
            print(f"Error creating MP4 for {cam_name}: {e}")
            import traceback
            traceback.print_exc()
            if 'out' in locals():
                out.release()


# def create_and_write_hdf5(args, data_dict, dataset_path, data_size):
#     with h5py.File(dataset_path + '.hdf5', 'w', rdcc_nbytes=1024 ** 2 * 2) as root:
#         # 设置文件属性
#         # root.attrs['sim'] = False
#         # root.attrs['task'] = str(args.task)

#         # 创建 endpose 组
#         endpose_group = root.create_group('endpose')
        
#         # 创建 joint_action 组
#         joint_action_group = root.create_group('joint_action')
        
#         # 为 endpose 组创建数据集
#         endpose_datasets = {
#             'left_endpose': (data_size, 7),
#             'left_gripper': (data_size,),  # 注意这里是一维
#             'right_endpose': (data_size, 7),
#             'right_gripper': (data_size,)   # 注意这里是一维
#         }
        
#         for name, shape in endpose_datasets.items():
#             endpose_group.create_dataset(name, shape, dtype='float64')
        
#         # 为 joint_action 组创建数据集
#         joint_action_datasets = {
#             'left_arm': (data_size, 6),
#             'left_gripper': (data_size,),    # 注意这里是一维
#             'right_arm': (data_size, 6),
#             'right_gripper': (data_size,),   # 注意这里是一维
#             'vector': (data_size, 14)
#         }
        
#         for name, shape in joint_action_datasets.items():
#             joint_action_group.create_dataset(name, shape, dtype='float64')
        
#         # 填充数据
#         # 转换列表为numpy数组
#         for key, data_list in data_dict.items():
#             if key in root:
#                 # 确保数据维度正确
#                 data_array = np.array(data_list)
                
#                 # 对于一维数据集，确保正确的维度
#                 if key.endswith('gripper') and data_array.ndim > 1:
#                     # 如果gripper数据是多维的，取第一列或压平
#                     if data_array.shape[1] == 1:
#                         data_array = data_array.flatten()
#                     else:
#                         # 如果有多个gripper值，可能需要其他处理
#                         data_array = data_array[:, 0]  # 取第一列
                
#                 root[key][...] = data_array
#                 print(f"Saved {key}: shape={data_array.shape}, dtype={data_array.dtype}")

def encode_images_to_jpeg(images_list, camera_name, jpeg_quality=95):
    """
    将图像序列编码为JPEG格式
    
    Args:
        images_list: 图像数组列表
        camera_name: 相机名称
        jpeg_quality: JPEG压缩质量
        
    Returns:
        编码后的JPEG字节流列表和最大长度
    """
    if USE_TURBOJPEG:
        jpeg_encoder = TurboJPEG()
    
    encoded_frames = []
    max_len = 0
    
    print(f"开始编码 {camera_name} 图像...")
    for i, img in enumerate(images_list):
        if img is None:
            print(f"警告: 图像为空 {camera_name} frame {i}")
            # 创建空白图像
            blank_img = np.zeros((360, 640, 3), dtype=np.uint8)
            img = blank_img
        
        # 确保图像是正确的格式和尺寸
        if len(img.shape) != 3 or img.shape[2] != 3:
            print(f"警告: 图像格式不正确 {camera_name} frame {i}")
            blank_img = np.zeros((360, 640, 3), dtype=np.uint8)
            img = blank_img
        
        # 调整尺寸（如果需要）
        if img.shape[:2] != (360, 640):
            print(f"调整图像尺寸 {camera_name} frame {i} from {img.shape[:2]} to (360, 640)")
            img = cv2.resize(img, (640, 360))
        
        # 编码为JPEG
        if USE_TURBOJPEG:
            jpeg_bytes = jpeg_encoder.encode(img, quality=jpeg_quality)
        else:
            # 使用OpenCV编码
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
            _, jpeg_bytes = cv2.imencode('.jpg', img, encode_param)
            jpeg_bytes = jpeg_bytes.tobytes()
        
        encoded_frames.append(jpeg_bytes)
        max_len = max(max_len, len(jpeg_bytes))
    
    # 填充到相同长度
    padded_frames = []
    for jpeg_bytes in encoded_frames:
        padded_jpeg = jpeg_bytes.ljust(max_len, b'\0')
        padded_frames.append(padded_jpeg)
    
    print(f"完成编码 {camera_name}: {len(padded_frames)} 帧, 最大尺寸={max_len} bytes")
    return padded_frames, max_len


def create_and_write_hdf5(args, data_dict, dataset_path, data_size):
    with h5py.File(dataset_path + '.hdf5', 'w', rdcc_nbytes=1024 ** 2 * 2) as root:
        # 创建 observation 组
        obs_group = root.create_group('observation')
        
        # 创建 endpose 组
        endpose_group = root.create_group('endpose')
        
        # 创建 joint_action 组
        joint_action_group = root.create_group('joint_action')
        
        # 为 endpose 组创建数据集
        endpose_datasets = {
            'left_endpose': (data_size, 7),
            'left_gripper': (data_size,),
            'right_endpose': (data_size, 7),
            'right_gripper': (data_size,)
        }
        
        for name, shape in endpose_datasets.items():
            endpose_group.create_dataset(name, shape, dtype='float64')
        
        # 为 joint_action 组创建数据集
        joint_action_datasets = {
            'left_arm': (data_size, 6),
            'left_gripper': (data_size,),
            'right_arm': (data_size, 6),
            'right_gripper': (data_size,),
            'vector': (data_size, 14)
        }
        
        for name, shape in joint_action_datasets.items():
            joint_action_group.create_dataset(name, shape, dtype='float64')
        
        # 填充动作数据
        for key, data_list in data_dict.items():
            if key == 'images':
                continue  # 稍后处理图像
                
            if key in root:
                data_array = np.array(data_list)
                
                if key.endswith('gripper') and data_array.ndim > 1:
                    if data_array.shape[1] == 1:
                        data_array = data_array.flatten()
                    else:
                        data_array = data_array[:, 0]
                
                root[key][...] = data_array
                print(f"Saved {key}: shape={data_array.shape}, dtype={data_array.dtype}")
        
        # 处理图像数据
        if 'images' in data_dict and data_dict['images']:
            print("开始处理图像数据...")
            
            # 为每个相机提取图像
            camera_images = {}
            for cam_name in args.camera_names:
                camera_images[cam_name] = []
                
            # 从images列表中提取每个相机的图像
            for frame_dict in data_dict['images']:
                if isinstance(frame_dict, dict):
                    for cam_name in args.camera_names:
                        if cam_name in frame_dict:
                            camera_images[cam_name].append(frame_dict[cam_name])
                        else:
                            # 如果缺少某帧，添加空白图像
                            camera_images[cam_name].append(None)
            
            # 为每个相机编码并保存
            camera_mapping = {
                'left_wrist': 'left_camera',
                'head': 'head_camera'
            }
            
            for cam_name in args.camera_names:
                if cam_name in camera_images and camera_images[cam_name]:
                    hdf5_cam_name = camera_mapping.get(cam_name, cam_name)
                    
                    # 编码图像
                    encoded_frames, max_len = encode_images_to_jpeg(
                        camera_images[cam_name], 
                        cam_name,
                        jpeg_quality=95
                    )
                    
                    # 创建相机组并保存
                    cam_group = obs_group.create_group(hdf5_cam_name)
                    jpeg_array = np.array(encoded_frames, dtype=f'|S{max_len}')
                    cam_group.create_dataset('rgb', data=jpeg_array)
                    
                    print(f"Saved observation/{hdf5_cam_name}/rgb: "
                          f"shape={jpeg_array.shape}, dtype={jpeg_array.dtype}, "
                          f"max_size={max_len} bytes")
                else:
                    print(f"警告: 没有找到 {cam_name} 的图像数据")


# 保存数据函数
def save_data(args, timesteps, actions_eef, actions_joint, ros_operator, dataset_path):
    data_size = len(timesteps)

    # 数据字典
    data_dict = {
        'endpose/left_endpose': [],
        'endpose/left_gripper': [],
        'endpose/right_endpose': [],
        'endpose/right_gripper': [],
        'joint_action/left_arm': [],
        'joint_action/left_gripper': [],
        'joint_action/right_arm': [],
        'joint_action/right_gripper': [],
        'joint_action/vector': [],
        'images': [],
    }
#   - [Group] endpose
#   - [Dataset] endpose/left_endpose: shape=(140, 7), dtype=float64
#   - [Dataset] endpose/left_gripper: shape=(140,), dtype=float64
#   - [Dataset] endpose/right_endpose: shape=(140, 7), dtype=float64
#   - [Dataset] endpose/right_gripper: shape=(140,), dtype=float64
#   - [Group] joint_action
#   - [Dataset] joint_action/left_arm: shape=(140, 6), dtype=float64
#   - [Dataset] joint_action/left_gripper: shape=(140,), dtype=float64
#   - [Dataset] joint_action/right_arm: shape=(140, 6), dtype=float64
#   - [Dataset] joint_action/right_gripper: shape=(140,), dtype=float64
#   - [Dataset] joint_action/vector: shape=(140, 14), dtype=float64
    # 初始化相机字典
    # for cam_name in args.camera_names:
    #     data_dict[f'/observations/images/{cam_name}'] = []
    #     if args.use_depth_image:
    #         data_dict[f'/observations/images_depth/{cam_name}'] = []

    # 遍历并收集数据
    # print(actions_joint)
    
    while timesteps and rclpy.ok():
        action_eef = actions_eef.pop(0)
        action_joint = actions_joint.pop(0)
        ts = timesteps.pop(0)
        # print("ts",ts)
        # 填充数据
        # print("action_eef:", action_eef)
        quaternion = R.from_euler('xyz', [action_eef[3], action_eef[4], action_eef[5]]).as_quat()
        # print("euler:", [action_eef[3], action_eef[4], action_eef[5]])
        # print("quaternion:", quaternion)
        # print("combined:",np.concatenate([action_eef[:3], quaternion]))
        data_dict['endpose/left_endpose'].append(np.concatenate([action_eef[:3], quaternion]))
        data_dict['endpose/left_gripper'].append(action_eef[-1])
        data_dict['endpose/right_endpose'].append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        data_dict['endpose/right_gripper'].append(0.0)
        data_dict['joint_action/left_arm'].append(action_joint[:6])
        data_dict['joint_action/left_gripper'].append(action_joint[-1])
        data_dict['joint_action/right_arm'].append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        data_dict['joint_action/right_gripper'].append(0.0)
        data_dict['joint_action/vector'].append(np.concatenate([action_joint, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]))
        data_dict['images'].append(ts['images'])
        # 相机数据
        # for cam_name in args.camera_names:
        #     data_dict[f'/observations/images/{cam_name}'].append(ts['images'][cam_name])
        #     if args.use_depth_image:
        #         data_dict[f'/observations/images_depth/{cam_name}'].append(ts['images_depth'][cam_name])

    # 压缩图像数据
    # padded_size, padded_size_depth = compress_and_pad_images(data_dict, args.camera_names, args.use_depth_image)

    # 文本的属性：
    # 1 是否仿真
    # 2 图像是否压缩
    # print("Data validation:")
    # for key, data_list in data_dict.items():
    #     if data_list:
    #         sample = np.array(data_list[0])
    #         print(f"{key}: {len(data_list)} samples, shape per sample: {sample.shape}")
    t0 = time.time()
    create_and_write_mp4(args, data_dict, dataset_path, data_size)
    create_and_write_hdf5(args, data_dict, dataset_path, data_size)


    voice_process(voice_engine, "Save")
    print(f"\033[32m\nSaved in {time.time() - t0:.1f}s: {dataset_path}\033[0m\n")

    return


def collect_information_with_key(args, ros_operator, voice_engine):
    """带按键控制和实时图像可视化的数据收集 - 双摄像头版本"""
    timesteps = []
    actions_eef = []
    actions_joint = []

    count = 0
    rate = Rate(args.frame_rate)
    print(f"\033[32mRecording started! Press 'q' to stop recording\033[0m")
    print(f"\033[36mReal-time camera feed is displayed\033[0m")
    
    # 创建OpenCV窗口
    cv2.namedWindow('Live Camera Feed', cv2.WINDOW_NORMAL)
    
    while (count < args.max_timesteps) and rclpy.ok():
        # 检查是否按下q键停止录制
        key = get_key()
        if key == 'q':
            print(f"\033[33m\nStopping recording by user input...\033[0m")
            voice_process(voice_engine, "Stop recording")
            break
        
        obs_dict = ros_operator.get_observation()
        if obs_dict is None:
            print("Waiting for observation...")
            rate.sleep()
            continue
        
        # 实时显示图像 - 双摄像头并排显示
        if 'images' in obs_dict and obs_dict['images']:
            display_images = []
            
            for cam_name in args.camera_names:
                if cam_name in obs_dict['images']:
                    img = obs_dict['images'][cam_name]
                    if img is not None:
                        # 创建显示图像的副本
                        display_img = img.copy()
                        
                        # 添加摄像头标识
                        cam_label = f"{cam_name.upper()}"
                        cv2.putText(display_img, cam_label, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        
                        # 添加录制信息（只在第一个摄像头上显示）
                        if cam_name == args.camera_names[0]:
                            # 录制进度
                            progress_text = f"Recording: {count}/{args.max_timesteps}"
                            cv2.putText(display_img, progress_text, (10, 60), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            
                            # EEF位置信息
                            if 'eef' in obs_dict:
                                eef_pos = obs_dict['eef'][:3]
                                eef_text = f"EEF: [{eef_pos[0]:.3f}, {eef_pos[1]:.3f}, {eef_pos[2]:.3f}]"
                                cv2.putText(display_img, eef_text, (10, 90), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                            
                            # 关节信息（显示前3个关节）
                            if 'joint' in obs_dict:
                                joint_info = obs_dict['joint'][:3]
                                joint_text = f"Joint: [{joint_info[0]:.2f}, {joint_info[1]:.2f}, {joint_info[2]:.2f}]"
                                cv2.putText(display_img, joint_text, (10, 120), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                            
                            # 时间戳信息
                            if 'img_time' in obs_dict:
                                time_text = f"Time: {obs_dict['img_time']:.3f}"
                                cv2.putText(display_img, time_text, (10, 150), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                            
                            # 控制提示
                            control_text = "Press 'q' to stop"
                            cv2.putText(display_img, control_text, (10, display_img.shape[0] - 20), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        
                        display_images.append(display_img)
            
            # 合并图像（横向拼接）
            if len(display_images) > 0:
                # 确保所有图像高度一致
                max_height = max(img.shape[0] for img in display_images)
                resized_images = []
                for img in display_images:
                    if img.shape[0] != max_height:
                        scale = max_height / img.shape[0]
                        new_width = int(img.shape[1] * scale)
                        img = cv2.resize(img, (new_width, max_height))
                    resized_images.append(img)
                
                # 横向拼接
                combined_image = np.hstack(resized_images)
                cv2.imshow('Live Camera Feed', combined_image)
                
                # 检查OpenCV窗口的按键事件（非阻塞）
                cv_key = cv2.waitKey(1) & 0xFF
                if cv_key == ord('q'):
                    print(f"\033[33m\nStopping recording from camera window...\033[0m")
                    voice_process(voice_engine, "Stop recording")
                    break
        
        # 获取动作和观察值
        action_eef = deepcopy(obs_dict['eef'])
        action_joint = deepcopy(obs_dict['joint'])
        
        # 打印调试信息（每10帧打印一次）
        if count % 10 == 0:
            print(f"\033[36mFrame: {count}/{args.max_timesteps}\033[0m")
            print(f"action_joint: {action_joint}")
        
        # 收集数据
        timesteps.append(obs_dict)
        actions_eef.append(action_eef)
        actions_joint.append(action_joint)

        count += 1
        rate.sleep()
    
    # 关闭OpenCV窗口
    cv2.destroyAllWindows()
    
    print(f"\033[32m\nRecording completed!\033[0m")
    print(f"\033[32mlen(timesteps): {len(timesteps)}\033[0m")
    
    return timesteps, actions_eef, actions_joint

def main(args):
    # setup_loader(ROOT)
    
    # 设置终端
    old_settings = setup_terminal()
    
    try:
        rclpy.init()
        
        config = load_yaml(args.config)
        
        ros_operator = RosOperator(args, config, in_collect=True)
        
        spin_thread = threading.Thread(target=rclpy.spin, args=(ros_operator,), daemon=True)
        spin_thread.start()
        
        datasets_dir = Path(args.datasets)
        if not datasets_dir.is_absolute():
            datasets_dir = ROOT / args.datasets
        
        num_episodes = 1000 if args.episode_idx == -1 else 1
        current_episode = 0 if args.episode_idx == -1 else args.episode_idx
        
        # 查找最大episode序号
        max_episode = -1
        if datasets_dir.exists():
            for filename in datasets_dir.iterdir():
                if filename.name.startswith('episode_') and filename.name.endswith('.hdf5'):
                    try:
                        episode_num = int(filename.stem.split('_')[1])
                        max_episode = max(max_episode, episode_num)
                    except (ValueError, IndexError):
                        continue
        
        # 如果找到了已存在的episode，从最大序号的下一个开始
        if max_episode >= 0:
            current_episode = max_episode + 1
        
        episode_num = 0
        
        print(f"\033[34m{'='*50}\033[0m")
        print(f"\033[34mData Collection System Started\033[0m")
        print(f"\033[34m{'='*50}\033[0m")
        print(f"\033[36mControls:\033[0m")
        print(f"\033[36m  's' - Start recording episode\033[0m")
        print(f"\033[36m  'q' - Stop recording / Quit program\033[0m")
        print(f"\033[34m{'='*50}\033[0m")
        
        while episode_num < num_episodes and rclpy.ok():
            print(f'\n\033[35m{"="*30}\033[0m')
            print(f'\033[35mEpisode {current_episode}\033[0m')
            print(f'\033[35m{"="*30}\033[0m')
            
            # 等待按键开始录制
            should_record = collect_detect_with_key(args, current_episode, voice_engine, ros_operator)
            
            if not should_record:
                print(f"\033[31mExiting program...\033[0m")
                break
            
            # 开始数据收集
            result = collect_information_with_key(args, ros_operator, voice_engine)
            
            if result is None:
                print(f"\033[31mData collection failed, skipping episode\033[0m")
                continue
                
            timesteps, actions_eef, actions_joint = result
            
            if len(timesteps) == 0:
                print(f"\033[33mNo data collected, skipping save\033[0m")
                continue
            
            # 创建数据集目录
            if not datasets_dir.exists():
                datasets_dir.mkdir(parents=True, exist_ok=True)
            
            dataset_path = datasets_dir / f"episode_{current_episode}"
            
            # 启动保存线程
            print(f"\033[36mSaving episode {current_episode}...\033[0m")
            save_thread = threading.Thread(
                target=save_data,
                args=(args, timesteps, actions_eef, actions_joint, ros_operator, str(dataset_path))
            )
            save_thread.start()
            
            episode_num += 1
            current_episode += 1
        
        print(f"\033[32m\nData collection completed! Total episodes: {episode_num}\033[0m")
        
    except KeyboardInterrupt:
        print(f"\n\033[33mProgram interrupted by user\033[0m")
    except Exception as e:
        print(f"\n\033[31mError: {e}\033[0m")
    finally:
        # 恢复终端设置
        restore_terminal(old_settings)
        
        # 清理资源
        if 'ros_operator' in locals():
            ros_operator.destroy_node()
        if 'rclpy' in locals():
            rclpy.shutdown()
        if 'spin_thread' in locals():
            spin_thread.join(timeout=1.0)

def parse_arguments(known=False):
    parser = argparse.ArgumentParser()

    # 数据集配置
    parser.add_argument('--datasets', type=str, default=Path.joinpath(ROOT, '1022_umbrella'),
                        help='dataset dir')
    parser.add_argument('--episode_idx', type=int, default=0, help='episode index')
    parser.add_argument('--max_timesteps', type=int, default=6000, help='max timesteps')
    parser.add_argument('--frame_rate', type=int, default=30, help='frame rate')

    # 配置文件
    parser.add_argument('--config', type=str,
                        default='/home/go2/ARX_X5/main/config.yaml',
                        help='config file')

    # 图像处理选项
    parser.add_argument('--camera_names', type=str,
                    choices=['left_wrist','head'],
                    default=['left_wrist','head'], help='camera names')
    parser.add_argument('--use_depth_image', action='store_true', help='use depth image')

    # 机器人选项
    parser.add_argument('--record', choices=['Distance', 'Speed'], default='Distance',
                        help='record data')

    # 数据采集选项
    parser.add_argument('--key_collect', action='store_true', help='use key collect')

    parser.add_argument('--task', type=str, default='', help='task name')

    return parser.parse_known_args()[0] if known else parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    main(args)