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


class HDF5JointReplayer(Node):
    def __init__(self, hdf5_path: str, topic: str, rate_hz: float, loop: bool, publish_robot_cmd: bool, init_interpolation: bool = False):
        super().__init__('hdf5_joint_replayer')
        self.hdf5_path = hdf5_path
        self.topic = topic
        self.rate_hz = rate_hz
        self.loop = loop
        self.publish_robot_cmd = publish_robot_cmd
        self.count=0
        self.init_interpolation = init_interpolation
        self.interpolation_complete = not init_interpolation

        # 加载HDF5数据
        self.joint_data = self._load_hdf5_joints(hdf5_path)
        if len(self.joint_data) == 0:
            raise RuntimeError(f"HDF5文件中没有有效的关节数据: {hdf5_path}")

        # 发布者
        if self.publish_robot_cmd:
            # 懒导入，避免在未 source ROS2 工作区时语法检查失败
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

        # 插值数据
        if self.init_interpolation:
            before_init = [-1.4860382080078125, 0.6830320358276367, 1.3399324417114258, -1.2991151809692383, 0.08258914947509766,-0.07648563385009766, 0.007248878479003906]
            # init_joint = [-0.10128211975097656, 0.7059202194213867,1.457045555114746, -1.2983522415161133, -0.039101600646972656, -0.055123329162597656, 0.020600318908691406]
            init_joint = [-1.4860382080078125, 0.6830320358276367, 1.3399324417114258, -1.2991151809692383, 0.08258914947509766,-0.07648563385009766, 0.007248878479003906]
            
            self.interpolation_data = self._generate_interpolation(before_init, init_joint, num_steps=30)
            self.interpolation_idx = 0
            self.get_logger().info(f"生成了 {len(self.interpolation_data)} 个插值点，将在 2 秒内完成初始化")

        self.idx = 0
        self.timer = self.create_timer(1.0 / self.rate_hz, self._tick)
        self.get_logger().info(f"已加载 {len(self.joint_data)} 帧关节数据，频率 {self.rate_hz} Hz，loop={self.loop}")

    def _generate_interpolation(self, start: List[float], end: List[float], num_steps: int) -> List[List[float]]:
        """生成线性插值轨迹"""
        start_arr = np.array(start)
        end_arr = np.array(end)
        
        interpolation = []
        for i in range(num_steps + 1):  # +1 确保包含终点
            alpha = i / num_steps
            point = start_arr + alpha * (end_arr - start_arr)
            interpolation.append(point.tolist())
        
        return interpolation

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
                self.get_logger().info(f"左臂夹爪数据: {left_gripper_data.shape}")
                
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
        # 如果还在执行初始化插值
        if not self.interpolation_complete:
            if self.interpolation_idx < len(self.interpolation_data):
                positions = self.interpolation_data[self.interpolation_idx]
                self.interpolation_idx += 1
                
                # 发布插值位置
                if self.publish_robot_cmd:
                    self._publish_robot_cmd(positions)
                else:
                    names = [f'joint_{j}' for j in range(6)] + ['gripper']
                    self._publish_joint_state(positions, names)
                
                # 显示进度
                progress = (self.interpolation_idx / len(self.interpolation_data)) * 100
                print(f"\r初始化进度: {progress:.1f}% ({self.interpolation_idx}/{len(self.interpolation_data)})", end='')
                
                return
            else:
                # 插值完成
                self.interpolation_complete = True
                print("\n\033[32m初始化插值完成！开始播放数据...\033[0m")
                return
        
        # 正常播放HDF5数据
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
        self.count+=1
        print(self.count)
        print(msg.joint_pos)
        self.pub.publish(msg)


def main():
    parser = argparse.ArgumentParser(description='Replay joints from HDF5 file collected by collect.py')
    parser.add_argument('hdf5', help='Path to HDF5 file (e.g., episode_0.hdf5)')
    parser.add_argument('--topic', default='/arm_cmd', help='Topic to publish to (default: /arm_cmd)')
    parser.add_argument('--rate', type=float, default=15, help='Publish rate Hz (default: 15 for 2s interpolation)')
    parser.add_argument('--loop', action='store_true', help='Loop playback indefinitely')
    parser.add_argument('--joint-state', action='store_true', 
                       help='Publish sensor_msgs/JointState instead of arx5_arm_msg/RobotCmd')
    parser.add_argument('--init-interpolation', action='store_true',
                       help='Enable initialization interpolation from before_init to init_joint')
    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.hdf5):
        print(f"\033[31m错误: 文件不存在 - {args.hdf5}\033[0m")
        return

    # 决定发布消息类型
    publish_robot_cmd = not args.joint_state

    print(f"\033[36m{'='*50}\033[0m")
    print(f"\033[36mHDF5 Joint Replay System\033[0m")
    print(f"\033[36m{'='*50}\033[0m")
    print(f"\033[32mFile: {args.hdf5}\033[0m")
    print(f"\033[32mTopic: {args.topic}\033[0m")
    print(f"\033[32mRate: {args.rate} Hz\033[0m")
    print(f"\033[32mLoop: {args.loop}\033[0m")
    print(f"\033[32mInit Interpolation: {args.init_interpolation}\033[0m")
    print(f"\033[32mMessage Type: {'RobotCmd' if publish_robot_cmd else 'JointState'}\033[0m")
    print(f"\033[36m{'='*50}\033[0m")
    print(f"\033[33mPress Ctrl+C to stop\033[0m")

    rclpy.init()
    try:
        node = HDF5JointReplayer(args.hdf5, args.topic, args.rate, args.loop, publish_robot_cmd, args.init_interpolation)
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

#python3 replay.py /home/go2/ARX_X5/main/datasets/episode_22.hdf5

# python3 replay.py /home/go2/ARX_X5/main/1021_dataset/episode_1.hdf5

# 使用初始化插值：
# python3 replay.py /home/go2/ARX_X5/main/umbrella_1107/processed/processed_episode_2.hdf5 --init-interpolation --rate 15