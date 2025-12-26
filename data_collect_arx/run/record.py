import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from arx5_arm_msg.msg import RobotStatus
import message_filters

import os
import csv
import sys
import tty
import cv2
import time
import termios
import select
import threading
from datetime import datetime
from cv_bridge import CvBridge, CvBridgeError


class SyncSaver(Node):
    def __init__(self):
        super().__init__('sync_saver')

        # 订阅器与近似时间同步
        sub_img = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        sub_arm = message_filters.Subscriber(self, RobotStatus, 'arm_slave_l_status')
        ts = message_filters.ApproximateTimeSynchronizer(
            [sub_img, sub_arm],
            queue_size=20,
            slop=0.5
        )
        ts.registerCallback(self.callback)

        # 定时器：10Hz，从最新同步数据里按键控逻辑采样保存
        self.timer = self.create_timer(1.0 / 10, self.save_data_tick)

        # 状态与缓存
        self.latest_data = None             # (img_msg, arm_msg)
        self.is_recording = False
        self.bridge = CvBridge()
        self.lock = threading.Lock()

        # 录制缓存
        self.frames = []                    # list[np.ndarray BGR]
        self.arm_rows = []                  # list[dict | (sec, nsec, joints)]
        self.joint_count = None
        self.output_dir = "/home/go2/ARX_X5/run/save"
        self.target_fps = 10.0            # 与定时器一致，作为兜底

        self.get_logger().info("就绪：按 's' 开始/停止录制，停止时自动保存；按 'q' 退出。")

    # 同步回调：只缓存最新一对消息
    def callback(self, img_msg, arm_msg):
        self.get_logger().info(
            f"Saved synchronized data: img_time={img_msg.header.stamp}, arm_time={arm_msg.header.stamp}"
        )
        self.latest_data = (img_msg, arm_msg)

    # 定时器：在录制中则从最新同步数据取一帧并缓存
    def save_data_tick(self):
        if not self.is_recording:
            return
        if self.latest_data is None:
            return

        img_msg, arm_msg = self.latest_data
        try:
            frame = self.bridge.imgmsg_to_cv2(img_msg, desired_encoding='bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge error: {e}')
            return

        # 关节数量按第一帧推断
        joints = list(getattr(arm_msg, 'joint_pos', []))
        if self.joint_count is None:
            self.joint_count = len(joints)

        row = {
            'sec': arm_msg.header.stamp.sec,
            'nsec': arm_msg.header.stamp.nanosec,
            'joints': joints,
        }

        with self.lock:
            self.frames.append(frame)
            self.arm_rows.append(row)

    # 键控：切换录制
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_and_save()

    def start_recording(self):
        with self.lock:
            self.frames.clear()
            self.arm_rows.clear()
            self.joint_count = None
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = os.path.join(self.output_dir, f"record_{timestamp}")
            os.makedirs(self.output_dir, exist_ok=True)
            self.is_recording = True
        self.get_logger().info(f"开始录制 -> {self.output_dir}")

    def stop_and_save(self):
        with self.lock:
            if not self.is_recording:
                return
            self.is_recording = False
            frames = self.frames[:]
            arm_rows = self.arm_rows[:]
            joint_count = self.joint_count or 0
            output_dir = self.output_dir

        if not frames or not arm_rows:
            self.get_logger().warn("无数据，跳过保存。")
            return

        # 保存关节CSV
        csv_path = os.path.join(output_dir, "joints.csv")
        with open(csv_path, "w", newline="") as f:
            fieldnames = ['sec', 'nsec'] + [f'joint_{i}' for i in range(joint_count)]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in arm_rows:
                row = {'sec': r['sec'], 'nsec': r['nsec']}
                for i in range(joint_count):
                    row[f'joint_{i}'] = r['joints'][i] if i < len(r['joints']) else ''
                writer.writerow(row)

        # 估算帧率（优先按时间戳计算）
        # if len(arm_rows) >= 2:
        #     t0 = arm_rows[0]['sec'] + arm_rows[0]['nsec'] * 1e-9
        #     t1 = arm_rows[-1]['sec'] + arm_rows[-1]['nsec'] * 1e-9
        #     dur = max(0.0, t1 - t0)
        #     fps = (len(frames) / dur) if dur > 0 else self.target_fps
        # else:
        #     fps = self.target_fps
        fps = self.target_fps

        # 保存为 MP4 视频
        h, w = frames[0].shape[:2]
        video_path = os.path.join(output_dir, "video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 通用 mp4v 编码
        writer = cv2.VideoWriter(video_path, fourcc, fps, (w, h))
        for fr in frames:
            writer.write(fr)
        writer.release()

        self.get_logger().info(f"已保存: {csv_path}")
        self.get_logger().info(f"已保存: {video_path} (fps≈{fps:.2f}, frames={len(frames)})")

    # 退出时若仍在录制，先保存
    def cleanup(self):
        if self.is_recording:
            self.get_logger().info("检测到退出，先停止并保存录制数据...")
            self.stop_and_save()


def keyboard_thread(node: SyncSaver):
    # Linux 终端按键监听（无需回车）
    fd = sys.stdin.fileno()
    if not os.isatty(fd):
        node.get_logger().warn("stdin 非 TTY，按键控制不可用。")
        return

    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while rclpy.ok():
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if not rlist:
                continue
            ch = sys.stdin.read(1)
            if ch == 's':
                node.toggle_recording()
            elif ch == 'q':
                node.cleanup()
                rclpy.shutdown()
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main(args=None):
    rclpy.init(args=args)
    node = SyncSaver()

    # 启动按键监听线程
    t = threading.Thread(target=keyboard_thread, args=(node,), daemon=True)
    t.start()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cleanup()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        t.join(timeout=1.0)


if __name__ == '__main__':
    main()