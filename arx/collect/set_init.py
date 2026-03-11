#!/usr/bin/env python3
import argparse
import numpy as np
from typing import List, Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from sensor_msgs.msg import JointState
from arx5_arm_msg.msg import RobotCmd,RobotStatus

class JointInterpolator(Node):
    def __init__(self, topic: str, rate_hz: float, target: List[float], steps: int):
        super().__init__('joint_interpolator')

        self.topic = topic
        self.rate_hz = max(1.0, rate_hz)
        # self.target = [-0.041771888732910156,1.9907302856445312,1.0782403945922852,-0.5842294692993164, -0.09060001373291016,-0.01506805419921875]
        # self.target = [1.5314340591430664,-0.00934600830078125,0.01468658447265625,-0.00782012939453125,-0.00438690185546875,0.01392364501953125]
        self.target = [-1.4860382080078125, 0.6830320358276367, 1.3399324417114258, -1.2991151809692383, 0.08258914947509766,-0.07648563385009766, 0.007248878479003906]
       
        # self.target=[-0.00362396240234375,1.2197685241699219,0.7551307678222656,-0.5849924087524414,-0.17605113983154297,-0.059319496154785156]
        # self.target=[0.00209808349609375,2.701418876647949,2.599946975708008,-0.5628671646118164,-0.01201629638671875,-0.06389713287353516]
        


        self.steps = steps

        self.current_pos: Optional[List[float]] = None
        self.trajectory: Optional[np.ndarray] = None
        self.idx = 0

        # 订阅当前关节状态
        self.sub = self.create_subscription(RobotStatus, '/arm_status', self._on_joint_state, 10)


        self.RobotCmd = RobotCmd
        self.pub = self.create_publisher(RobotCmd, self.topic, 10)
        self.get_logger().info(f"发布 RobotCmd -> {self.topic}")


        self.timer = self.create_timer(1.0 / self.rate_hz, self._tick)

    def _on_joint_state(self, msg: RobotStatus):
        # 只在第一次获取时记录当前位置
        
        if self.current_pos is None and msg.joint_pos.all():
            print(1)
            self.current_pos = list(msg.joint_pos[:len(self.target)])
            self.get_logger().info(f"已获取当前位置: {self.current_pos}")
            self._build_trajectory()

    def _build_trajectory(self):
        if self.current_pos is None:
            return
        start = np.array(self.current_pos)
        end = np.array(self.target)
        self.trajectory = np.linspace(start, end, self.steps)
        self.get_logger().info(f"插值轨迹生成: {self.steps} steps")
        self.idx = 0

    def _tick(self):
        if self.trajectory is None:
            return  # 等待当前位置初始化

        if self.idx >= len(self.trajectory):
            self.get_logger().info("已到达目标位置")
            self.timer.cancel()
            return

        pos = self.trajectory[self.idx]
        self.idx += 1
        
        self._publish_robot_cmd(pos)


    def _publish_robot_cmd(self, positions: List[float]):
        RobotCmd = self.RobotCmd
        msg = RobotCmd()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        six = list(positions[:6]) + [0.0] * max(0, 6 - len(positions))
        msg.joint_pos = six
        msg.gripper = float(positions[6]) if len(positions) > 6 else 0.0
        msg.mode = 5
        self.pub.publish(msg)

        self.pub.publish(msg)
        self.get_logger().info(f'Published RobotCmd: {msg.joint_pos}')


def main():
    parser = argparse.ArgumentParser(description='Interpolate from current position to target position')
    parser.add_argument('--topic', default='/arm_cmd', help='Topic to publish')
    parser.add_argument('--rate', type=float, default=30.0, help='Publish rate Hz (default 10)')
    parser.add_argument('--steps', type=int, default=150, help='Number of interpolation steps')
    parser.add_argument('--target', type=float,default=[0,0,0,0,0,0],help='Target joint positions, space separated')
    args = parser.parse_args()

    rclpy.init()
    try:
        node = JointInterpolator(args.topic, args.rate, args.target, args.steps)
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
