#!/usr/bin/env python3
import os
import csv
import time
import argparse
from typing import List, Dict

import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from sensor_msgs.msg import JointState


class JointCSVReplayer(Node):
    def __init__(self, csv_path: str, topic: str, rate_hz: float, loop: bool, publish_robot_cmd: bool):
        super().__init__('joint_csv_replayer')
        self.csv_path = csv_path
        self.topic = topic
        self.rate_hz = max(0.1, rate_hz)
        self.loop = loop
        self.publish_robot_cmd = publish_robot_cmd

        self.rows: List[Dict] = self._load_csv(csv_path)
        if not self.rows:
            raise RuntimeError(f"CSV 中没有有效数据: {csv_path}")

        # 识别关节列
        self.joint_cols = [c for c in self.rows[0].keys() if c.startswith('joint_')]
        self.joint_cols.sort(key=lambda s: int(s.split('_')[1]) if '_' in s and s.split('_')[1].isdigit() else 1e9)
        if not self.joint_cols:
            raise RuntimeError('CSV 未发现 joint_ 列')

        # 发布者
        if self.publish_robot_cmd:
            # 懒导入，避免在未 source ROS2 工作区时语法检查失败
            from arx5_arm_msg.msg import RobotCmd  # type: ignore
            self.RobotCmd = RobotCmd
            self.pub = self.create_publisher(RobotCmd, self.topic, 10)
            self.get_logger().info(f"发布 RobotCmd -> {self.topic}")
        else:
            self.pub = self.create_publisher(JointState, self.topic, 10)
            self.get_logger().info(f"发布 JointState -> {self.topic}")

        self.idx = 0
        self.timer = self.create_timer(1.0 / self.rate_hz, self._tick)
        self.get_logger().info(f"已加载 {len(self.rows)} 行，频率 {self.rate_hz} Hz，loop={self.loop}")

    def _load_csv(self, path: str) -> List[Dict]:
        rows: List[Dict] = []
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
        return rows

    def _tick(self):
        if self.idx >= len(self.rows):
            if self.loop:
                self.idx = 0
            else:
                self.get_logger().info('播放完成，停止计时器。')
                self.timer.cancel()
                return

        r = self.rows[self.idx]
        self.idx += 1

        # 解析关节值
        positions: List[float] = []
        for c in self.joint_cols:
            try:
                positions.append(float(r[c]))
            except Exception:
                positions.append(0.0)

        if self.publish_robot_cmd:
            self._publish_robot_cmd(positions)
        else:
            self._publish_joint_state(positions)

    def _publish_joint_state(self, positions: List[float]):
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_cols
        msg.position = positions
        self.pub.publish(msg)

    def _publish_robot_cmd(self, positions: List[float]):
        # RobotCmd: 6个关节 + gripper（如存在）
        RobotCmd = self.RobotCmd
        msg = RobotCmd()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()

        # 前6个作为关节
        six = positions[:6] + [0.0] * max(0, 6 - len(positions))
        msg.joint_pos = six
        # 第7个作为夹爪（如存在）
        msg.gripper = float(positions[6]) if len(positions) > 6 else 0.0
        # 关节控制模式（如需末端位姿，请修改）
        msg.mode = 5
        # 末端位姿字段保持默认

        self.pub.publish(msg)


def main():
    parser = argparse.ArgumentParser(description='Replay joints.csv at a fixed frequency')
    parser.add_argument('csv', help='Path to joints.csv')
    parser.add_argument('--topic', default='/arm_cmd', help='Topic to publish')
    parser.add_argument('--rate', type=float, default=10.0, help='Publish rate Hz (default 10)')
    parser.add_argument('--loop', action='store_true', help='Loop playback')
    parser.add_argument('--robot-cmd', action='store_false', help='Publish arx5_arm_msg/RobotCmd instead of JointState')
    args = parser.parse_args()

    rclpy.init()
    try:
        node = JointCSVReplayer(args.csv, args.topic, args.rate, args.loop, args.robot_cmd)
    except Exception as e:
        print(f"初始化失败: {e}")
        rclpy.shutdown()
        return

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
