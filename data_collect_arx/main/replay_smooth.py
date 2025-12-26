#!/usr/bin/env python3
# filepath: /home/go2/ARX_X5/run/replay_hdf5.py

import os
import h5py
import time
import argparse
from typing import List, Dict
import numpy as np

import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from sensor_msgs.msg import JointState


class GripperSmoother:
    """夹爪数据平滑处理器"""
    def __init__(self, 
                 window_size=5,
                 threshold_ratio=0.05,
                 min_stable_frames=5,
                 open_value=None,
                 closed_value=None):
        """
        Args:
            window_size: 滑动窗口大小
            threshold_ratio: 阈值比例(相对于开合范围)
            min_stable_frames: 最少稳定帧数
            open_value: 打开状态值(自动检测)
            closed_value: 闭合状态值(自动检测)
        """
        self.window_size = window_size
        self.threshold_ratio = threshold_ratio
        self.min_stable_frames = min_stable_frames
        self.open_value = open_value
        self.closed_value = closed_value
        self.threshold = None
    
    def auto_detect_values(self, data):
        """自动检测开合值"""
        self.closed_value = float(np.min(data))
        self.open_value = float(np.max(data))
        
        # 计算阈值
        gripper_range = abs(self.open_value - self.closed_value)
        self.threshold = gripper_range * self.threshold_ratio
        
        return self.closed_value, self.open_value, self.threshold
    
    def smooth_sliding_window(self, data):
        """滑动窗口平滑"""
        if len(data) < self.window_size:
            return data
        
        kernel = np.ones(self.window_size) / self.window_size
        smoothed = np.convolve(data, kernel, mode='same')
        
        # 处理边界
        edge = self.window_size // 2
        smoothed[:edge] = data[:edge]
        smoothed[-edge:] = data[-edge:]
        
        return smoothed
    
    def stabilize_threshold(self, data):
        """阈值稳定化 - 将接近闭合/打开值的数据统一设置"""
        stabilized = data.copy()
        
        # 检测闭合状态
        is_closed = np.abs(data - self.closed_value) < self.threshold
        stabilized[is_closed] = self.closed_value
        
        # 检测打开状态
        is_open = np.abs(data - self.open_value) < self.threshold
        stabilized[is_open] = self.open_value
        
        return stabilized
    
    def lock_stable_states(self, data):
        """状态锁定"""
        locked = data.copy()
        changes = np.abs(np.diff(data, prepend=data[0]))
        
        stable_value = data[0]
        stable_count = 0
        
        for i in range(len(data)):
            if changes[i] < self.threshold:
                stable_count += 1
                if stable_count >= self.min_stable_frames:
                    locked[i] = stable_value
            else:
                stable_value = data[i]
                stable_count = 0
        
        return locked
    
    def process(self, gripper_data):
        """完整处理流程"""
        # 如果没有预设值，自动检测
        if self.closed_value is None or self.open_value is None:
            self.auto_detect_values(gripper_data)
        
        processed = gripper_data.copy()
        
        # 步骤1: 滑动窗口平滑
        processed = self.smooth_sliding_window(processed)
        
        # 步骤2: 阈值稳定化
        processed = self.stabilize_threshold(processed)
        
        # 步骤3: 状态锁定
        processed = self.lock_stable_states(processed)
        
        return processed


class HDF5JointReplayer(Node):
    def __init__(self, hdf5_path: str, topic: str, rate_hz: float, loop: bool, 
                 publish_robot_cmd: bool, smooth_gripper: bool,
                 window_size: int, threshold_ratio: float):
        super().__init__('hdf5_joint_replayer')
        self.hdf5_path = hdf5_path
        self.topic = topic
        self.rate_hz = rate_hz
        self.loop = loop
        self.publish_robot_cmd = publish_robot_cmd
        self.smooth_gripper = smooth_gripper
        self.count = 0

        # 创建夹爪平滑器
        if self.smooth_gripper:
            self.gripper_smoother = GripperSmoother(
                window_size=window_size,
                threshold_ratio=threshold_ratio
            )
            self.get_logger().info(f"夹爪平滑已启用: window={window_size}, threshold_ratio={threshold_ratio}")

        # 加载HDF5数据
        self.joint_data = self._load_hdf5_joints(hdf5_path)
        if len(self.joint_data) == 0:
            raise RuntimeError(f"HDF5文件中没有有效的关节数据: {hdf5_path}")

        # 发布者
        if self.publish_robot_cmd:
            try:
                from arx5_arm_msg.msg import RobotCmd  # type: ignore
                self.RobotCmd = RobotCmd
                self.pub = self.create_publisher(RobotCmd, self.topic, 10)
                self.get_logger().info(f"发布 RobotCmd -> {self.topic}")
            except ImportError:
                self.get_logger().error("无法导入 arx5_arm_msg.msg.RobotCmd，请检查工作区")
                raise
        else:
            self.pub = self.create_publisher(JointState, self.topic, 10)
            self.get_logger().info(f"发布 JointState -> {self.topic}")

        self.idx = 0
        self.timer = self.create_timer(1.0 / self.rate_hz, self._tick)
        self.get_logger().info(f"已加载 {len(self.joint_data)} 帧关节数据，频率 {self.rate_hz} Hz，loop={self.loop}")

    def _load_hdf5_joints(self, path: str) -> List[Dict]:
        """从HDF5文件中加载关节数据"""
        joint_data = []
        
        try:
            with h5py.File(path, 'r') as f:
                self.get_logger().info("HDF5文件结构:")
                self._print_hdf5_structure(f)
                
                # 检查数据结构
                if 'joint_action' not in f:
                    raise RuntimeError("HDF5文件中未找到 'joint_action' 组")
                
                joint_group = f['joint_action']
                
                # 获取左臂关节数据
                if 'left_arm' not in joint_group:
                    raise RuntimeError("未找到 'joint_action/left_arm' 数据集")
                
                left_arm_data = joint_group['left_arm'][:]  # shape: (N, 6)
                left_gripper_data = joint_group['left_gripper'][:] if 'left_gripper' in joint_group else np.zeros(len(left_arm_data))
                
                self.get_logger().info(f"左臂关节数据: {left_arm_data.shape}")
                self.get_logger().info(f"左臂夹爪原始数据:")
                self.get_logger().info(f"  Shape: {left_gripper_data.shape}")
                self.get_logger().info(f"  Range: [{left_gripper_data.min():.6f}, {left_gripper_data.max():.6f}]")
                self.get_logger().info(f"  Mean: {left_gripper_data.mean():.6f}")
                self.get_logger().info(f"  Std: {left_gripper_data.std():.6f}")
                
                # 平滑夹爪数据
                if self.smooth_gripper:
                    # 自动检测开合值
                    closed_val, open_val, threshold = self.gripper_smoother.auto_detect_values(left_gripper_data)
                    
                    self.get_logger().info(f"\n自动检测夹爪参数:")
                    self.get_logger().info(f"  闭合值 (最小值): {closed_val:.6f}")
                    self.get_logger().info(f"  打开值 (最大值): {open_val:.6f}")
                    self.get_logger().info(f"  开合范围: {abs(open_val - closed_val):.6f}")
                    self.get_logger().info(f"  稳定化阈值: {threshold:.6f}")
                    
                    # 处理数据
                    left_gripper_data_smoothed = self.gripper_smoother.process(left_gripper_data)
                    
                    self.get_logger().info(f"\n左臂夹爪平滑后:")
                    self.get_logger().info(f"  Range: [{left_gripper_data_smoothed.min():.6f}, {left_gripper_data_smoothed.max():.6f}]")
                    self.get_logger().info(f"  Mean: {left_gripper_data_smoothed.mean():.6f}")
                    self.get_logger().info(f"  Std: {left_gripper_data_smoothed.std():.6f}")
                    self.get_logger().info(f"  标准差降低: {(1 - left_gripper_data_smoothed.std()/left_gripper_data.std())*100:.1f}%")
                    
                    # 统计稳定帧数
                    closed_frames = np.sum(np.abs(left_gripper_data_smoothed - closed_val) < 1e-6)
                    open_frames = np.sum(np.abs(left_gripper_data_smoothed - open_val) < 1e-6)
                    self.get_logger().info(f"  闭合状态帧数: {closed_frames}/{len(left_gripper_data_smoothed)} ({closed_frames/len(left_gripper_data_smoothed)*100:.1f}%)")
                    self.get_logger().info(f"  打开状态帧数: {open_frames}/{len(left_gripper_data_smoothed)} ({open_frames/len(left_gripper_data_smoothed)*100:.1f}%)")
                    
                    left_gripper_data = left_gripper_data_smoothed
                
                # 组合数据
                for i in range(len(left_arm_data)):
                    joint_positions = list(left_arm_data[i])  # 6个关节
                    gripper_pos = float(left_gripper_data[i]) 
                    
                    joint_data.append({
                        'joint_positions': joint_positions + [gripper_pos],  # 6个关节 + 1个夹爪
                        'joint_names': [f'joint_{j}' for j in range(6)] + ['gripper']
                    })
                
        except Exception as e:
            self.get_logger().error(f"加载HDF5文件失败: {e}")
            raise
        
        return joint_data

    def _print_hdf5_structure(self, h5_file, prefix=""):
        """递归打印HDF5文件结构"""
        for key in h5_file.keys():
            item = h5_file[key]
            if isinstance(item, h5py.Group):
                self.get_logger().info(f"{prefix}- [Group] {key}")
                self._print_hdf5_structure(item, prefix + "  ")
            elif isinstance(item, h5py.Dataset):
                self.get_logger().info(f"{prefix}- [Dataset] {key}: shape={item.shape}, dtype={item.dtype}")

    def _tick(self):
        """定时器回调函数"""
        if self.idx >= len(self.joint_data):
            if self.loop:
                self.idx = 0
                self.get_logger().info('重新开始播放...')
            else:
                self.get_logger().info('播放完成，停止计时器。')
                self.timer.cancel()
                return

        joint_info = self.joint_data[self.idx]
        self.idx += 1

        if self.publish_robot_cmd:
            self._publish_robot_cmd(joint_info['joint_positions'])
        else:
            self._publish_joint_state(joint_info['joint_positions'], joint_info['joint_names'])

    def _publish_joint_state(self, positions: List[float], names: List[str]):
        """发布JointState消息"""
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = positions
        self.pub.publish(msg)

    def _publish_robot_cmd(self, positions: List[float]):
        """发布RobotCmd消息"""
        RobotCmd = self.RobotCmd
        msg = RobotCmd()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()

        # 前6个作为关节位置
        joint_pos = positions[:6] + [0.0] * max(0, 6 - len(positions))
        msg.joint_pos = joint_pos
        
        # 第7个作为夹爪位置（如存在）
        msg.gripper = float(positions[6]) if len(positions) > 6 else 0.0
        
        # 关节控制模式
        msg.mode = 5  # 关节位置控制模式
        
        # 末端位姿字段保持默认（如果不需要末端控制）
        msg.end_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.count += 1
        
        # 每100帧打印一次
        if self.count % 100 == 0:
            print(f"[{self.count}] Gripper: {msg.gripper:.6f}")
        
        self.pub.publish(msg)


def main():
    parser = argparse.ArgumentParser(
        description='Replay joints from HDF5 file with gripper smoothing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本播放(不平滑)
  python3 replay.py episode_0.hdf5
  
  # 启用夹爪平滑(自动检测开合值)
  python3 replay.py episode_0.hdf5 --smooth-gripper
  
  # 自定义平滑参数
  python3 replay.py episode_0.hdf5 --smooth-gripper --window-size 7 --threshold-ratio 0.08
  
  # 循环播放 + 平滑
  python3 replay.py episode_0.hdf5 --smooth-gripper --loop
  
说明:
  - threshold-ratio: 阈值比例(相对于开合范围), 默认0.05 (5%)
    例如: 范围0.01, 阈值=0.01*0.05=0.0005
  - window-size: 滑动窗口大小, 越大越平滑但响应越慢
        """
    )
    
    parser.add_argument('hdf5', help='Path to HDF5 file (e.g., episode_0.hdf5)')
    parser.add_argument('--topic', default='/arm_cmd', help='Topic to publish to (default: /arm_cmd)')
    parser.add_argument('--rate', type=float, default=30, help='Publish rate Hz (default: 30)')
    parser.add_argument('--loop', action='store_true', help='Loop playback indefinitely')
    parser.add_argument('--joint-state', action='store_true', 
                       help='Publish sensor_msgs/JointState instead of arx5_arm_msg/RobotCmd')
    
    # 夹爪平滑参数
    parser.add_argument('--smooth-gripper', action='store_true',
                       help='Enable gripper smoothing (auto-detect open/closed values)')
    parser.add_argument('--window-size', type=int, default=5,
                       help='Sliding window size for smoothing (default: 5)')
    parser.add_argument('--threshold-ratio', type=float, default=0.05,
                       help='Threshold ratio relative to gripper range (default: 0.05 = 5%%)')
    
    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.hdf5):
        print(f"\033[31m错误: 文件不存在 - {args.hdf5}\033[0m")
        return

    # 决定发布消息类型
    publish_robot_cmd = not args.joint_state

    print(f"\033[36m{'='*60}\033[0m")
    print(f"\033[36mHDF5 Joint Replay System\033[0m")
    print(f"\033[36m{'='*60}\033[0m")
    print(f"\033[32mFile: {args.hdf5}\033[0m")
    print(f"\033[32mTopic: {args.topic}\033[0m")
    print(f"\033[32mRate: {args.rate} Hz\033[0m")
    print(f"\033[32mLoop: {args.loop}\033[0m")
    print(f"\033[32mMessage Type: {'RobotCmd' if publish_robot_cmd else 'JointState'}\033[0m")
    print(f"\033[32mGripper Smoothing: {args.smooth_gripper}\033[0m")
    if args.smooth_gripper:
        print(f"\033[33m  - Window Size: {args.window_size}\033[0m")
        print(f"\033[33m  - Threshold Ratio: {args.threshold_ratio*100:.1f}%\033[0m")
        print(f"\033[33m  - Auto-detect open/closed values from data\033[0m")
    print(f"\033[36m{'='*60}\033[0m")
    print(f"\033[33mPress Ctrl+C to stop\033[0m\n")

    rclpy.init()
    try:
        node = HDF5JointReplayer(
            args.hdf5, 
            args.topic, 
            args.rate, 
            args.loop, 
            publish_robot_cmd,
            args.smooth_gripper,
            args.window_size,
            args.threshold_ratio
        )
    except Exception as e:
        print(f"\033[31m初始化失败: {e}\033[0m")
        rclpy.shutdown()
        return

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print(f"\n\033[33m用户中断播放\033[0m")
    finally:
        node.destroy_node()
        rclpy.shutdown()
        print(f"\033[32m播放结束\033[0m")


if __name__ == '__main__':
    main()

# 使用示例:
# python3 replay_smooth.py /home/go2/ARX_X5/main/1022_umbrella/episode_21.hdf5--smooth-gripper
# python3 replay.py /home/go2/ARX_X5/main/1021_dataset/episode_1.hdf5 --smooth-gripper --loop