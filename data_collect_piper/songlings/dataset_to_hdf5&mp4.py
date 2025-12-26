import numpy as np
import h5py
import cv2
import os
from pathlib import Path
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R
from converting_utils import organize_data_from_single_run

try:
    from turbojpeg import TurboJPEG
    USE_TURBOJPEG = True
except ImportError:
    print("警告：未找到PyTurboJPEG库，将使用OpenCV编码")
    USE_TURBOJPEG = False


def encode_images_to_jpeg(image_paths, jpeg_quality=95):
    """
    将图像序列编码为JPEG格式
    
    Args:
        image_paths: 图像路径列表
        jpeg_quality: JPEG压缩质量
        
    Returns:
        编码后的JPEG字节流列表和最大长度
    """
    if USE_TURBOJPEG:
        jpeg_encoder = TurboJPEG()
    
    encoded_frames = []
    max_len = 0
    
    for img_path in tqdm(image_paths, desc="编码图像", leave=False):
        if not img_path.exists():
            print(f"警告: 图像不存在 {img_path}")
            # 创建空白图像
            blank_img = np.zeros((360, 640, 3), dtype=np.uint8)
            img_bgr = blank_img
        else:
            img_bgr = cv2.imread(str(img_path))
            if img_bgr is None:
                print(f"警告: 无法读取图像 {img_path}")
                blank_img = np.zeros((360, 640, 3), dtype=np.uint8)
                img_bgr = blank_img
            else:
                # 调整尺寸
                img_bgr = cv2.resize(img_bgr, (640, 360))
        
        # 编码为JPEG
        if USE_TURBOJPEG:
            jpeg_bytes = jpeg_encoder.encode(img_bgr, quality=jpeg_quality)
        else:
            # 使用OpenCV编码
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
            _, jpeg_bytes = cv2.imencode('.jpg', img_bgr, encode_param)
            jpeg_bytes = jpeg_bytes.tobytes()
        
        encoded_frames.append(jpeg_bytes)
        max_len = max(max_len, len(jpeg_bytes))
    
    # 填充到相同长度
    padded_frames = []
    for jpeg_bytes in encoded_frames:
        padded_jpeg = jpeg_bytes.ljust(max_len, b'\0')
        padded_frames.append(padded_jpeg)
    
    return padded_frames, max_len


def create_and_write_hdf5(args, data_dict, dataset_path, data_size, 
                          front_images, wrist_images, jpeg_quality=95):
    """
    创建HDF5文件并写入数据
    
    Args:
        args: 参数(可为None)
        data_dict: 动作数据字典
        dataset_path: 输出HDF5文件路径(不含后缀)
        data_size: 数据长度
        front_images: front_color图像路径列表
        wrist_images: wrist_color图像路径列表
        jpeg_quality: JPEG压缩质量
    """
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
        print("开始处理front_color图像...")
        front_encoded, front_max_len = encode_images_to_jpeg(front_images, jpeg_quality)
        
        print("开始处理wrist_color图像...")
        wrist_encoded, wrist_max_len = encode_images_to_jpeg(wrist_images, jpeg_quality)
        
        # 创建相机组并保存图像
        # front_camera (head_camera)
        front_camera_group = obs_group.create_group('head_camera')
        front_jpeg_array = np.array(front_encoded, dtype=f'|S{front_max_len}')
        front_camera_group.create_dataset('rgb', data=front_jpeg_array)
        print(f"Saved head_camera/rgb: shape={front_jpeg_array.shape}, "
              f"dtype={front_jpeg_array.dtype}, max_size={front_max_len} bytes")
        
        # wrist_camera
        wrist_camera_group = obs_group.create_group('wrist_camera')
        wrist_jpeg_array = np.array(wrist_encoded, dtype=f'|S{wrist_max_len}')
        wrist_camera_group.create_dataset('rgb', data=wrist_jpeg_array)
        print(f"Saved wrist_camera/rgb: shape={wrist_jpeg_array.shape}, "
              f"dtype={wrist_jpeg_array.dtype}, max_size={wrist_max_len} bytes")


if __name__ == "__main__":
    folder_path = "/home/pc3/data_collect/songlings/data/tmp/1"
    save_path = "/home/pc3/data_collect/songlings/data/tmp/hdf5_test"
    os.makedirs(save_path, exist_ok=True)
    
    for subfolder in tqdm(os.listdir(folder_path), desc="Processing folders", unit="folder"):
        traj_path = os.path.join(folder_path, subfolder)
        u = list(organize_data_from_single_run(traj_path))
        print(f"处理 {subfolder}: {len(u)} 帧")
        
        # 准备数据字典
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
        }
        
        # 收集图像路径
        front_images = []
        wrist_images = []
        
        for (j, e, g, (i1, i2)) in u:
            img1_path = Path(os.path.join(traj_path, "img", "front_color", f"{i1}"))
            img2_path = Path(os.path.join(traj_path, "img", "wrist_color", f"{i2}"))
            
            front_images.append(img1_path)
            wrist_images.append(img2_path)
            
            action_eef = form_eef_state_action([e], [g])[0]
            action_joint = form_joint_state_action([j], [g])[0]
            
            quaternion = R.from_euler('xyz', [action_eef[3], action_eef[4], action_eef[5]]).as_quat()
            
            data_dict['endpose/left_endpose'].append(np.concatenate([action_eef[:3], quaternion]))
            data_dict['endpose/left_gripper'].append(float(action_eef[-1]))
            data_dict['endpose/right_endpose'].append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            data_dict['endpose/right_gripper'].append(0.0)
            data_dict['joint_action/left_arm'].append(np.array(action_joint[:6], dtype=np.float64))
            data_dict['joint_action/left_gripper'].append(float(action_joint[-1]))
            data_dict['joint_action/right_arm'].append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            data_dict['joint_action/right_gripper'].append(0.0)
            data_dict['joint_action/vector'].append(
                np.concatenate([action_joint, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]).astype(np.float64)
            )
        
        # 创建HDF5文件(包含图像数据)
        create_and_write_hdf5(
            None, 
            data_dict, 
            os.path.join(save_path, subfolder), 
            len(data_dict['endpose/left_endpose']),
            front_images,
            wrist_images,
            jpeg_quality=95
        )
        
        print(f"✓ 完成 {subfolder}")