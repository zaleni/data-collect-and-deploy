import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
import numpy as np

from geometry_msgs.msg import Pose
from arx5_arm_msg.msg import RobotCmd
# 假设X5的状态消息类型为ArmStatus，您需要根据实际情况修改
# 您可以通过 `ros2 topic info /arm_status -v` 命令查看其确切类型
from arx5_arm_msg.msg import RobotStatus
from scipy.spatial.transform import Rotation as R

class PosBridgeNode(Node):
    def __init__(self):
        super().__init__('pos_cmd_to_robot_cmd_bridge')

        # --- 新增状态变量 ---
        self.initial_piper_pose = None
        self.initial_x5_pose = None
        self.position_offset = None
        self.orientation_offset = None # 用于姿态偏移
        self.is_ready = False

        # 1. 订阅 Piper (Master) 的位姿
        self.piper_subscription = self.create_subscription(
            Pose,
            'end_pose',
            self.piper_pose_callback,
            10)
        
        # 2. 订阅 X5 (Slave) 的状态以获取其初始位姿
        self.x5_status_subscription = self.create_subscription(
            RobotStatus,  # <--- 请确认此消息类型
            'arm_status',
            self.x5_status_callback,
            10)

        # 3. 创建到 X5 (Slave) 的指令发布者
        self.x5_publisher = self.create_publisher(
            RobotCmd,
            'arm_cmd',
            10)
            
        self.get_logger().info('桥接节点已启动，正在等待主从臂的初始位姿...')

    def x5_status_callback(self, msg: RobotStatus):
        # 仅在尚未记录初始位姿时执行
        if self.initial_x5_pose is None:
            # X5的end_pos是 [x, y, z, r, p, y]
            pos = msg.end_pos[0:3]
            # 将欧拉角转为四元数
            rot = R.from_euler('xyz', msg.end_pos[3:6], degrees=False)
            self.initial_x5_pose = {'position': np.array(pos), 'orientation': rot}
            self.get_logger().info(f'已捕获X5机械臂初始位置: {pos}')
            self.try_calculate_offset()

    def piper_pose_callback(self, msg: Pose):
        # 仅在尚未记录初始位姿时执行
        if self.initial_piper_pose is None:
            pos = np.array([msg.position.x, msg.position.y, msg.position.z])
            quat = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]
            rot = R.from_quat(quat)
            self.initial_piper_pose = {'position': np.array(pos), 'orientation': rot}
            self.get_logger().info(f'已捕获Piper机械臂初始位置: {pos}')
            self.try_calculate_offset()
        
        # 如果已经准备就绪，则执行主从控制
        if self.is_ready:
            self.control_x5(msg)

    def try_calculate_offset(self):
        # 当两个机械臂的初始位姿都已捕获时，计算偏移量
        if self.initial_piper_pose is not None and self.initial_x5_pose is not None:
            # 计算位置偏移
            self.position_offset = self.initial_x5_pose['position'] - self.initial_piper_pose['position']
            
            # 计算姿态偏移: Offset = Initial_Slave * Inverse(Initial_Master)
            self.orientation_offset = self.initial_x5_pose['orientation'] * self.initial_piper_pose['orientation'].inv()

            self.is_ready = True
            self.get_logger().info('--- 主从臂初始位姿对齐完成，已计算偏移量 ---')
            self.get_logger().info(f'位置偏移 (Offset): {self.position_offset}')
            self.get_logger().info('--- 现在可以开始主从控制 ---')

    def control_x5(self, piper_msg: Pose):
        # 1. 获取Piper当前位姿
        current_piper_pos = np.array([piper_msg.position.x, piper_msg.position.y, piper_msg.position.z])
        current_piper_quat = [piper_msg.orientation.x, piper_msg.orientation.y, piper_msg.orientation.z, piper_msg.orientation.w]
        current_piper_rot = R.from_quat(current_piper_quat)

        # 2. 应用偏移量计算X5的目标位姿
        target_x5_pos = current_piper_pos + self.position_offset
        # 应用姿态偏移: Target_Slave = Offset * Current_Master
        target_x5_rot = self.orientation_offset * current_piper_rot

        # 3. 准备发送给X5的指令
        robot_cmd_msg = RobotCmd()
        robot_cmd_msg.header.stamp = self.get_clock().now().to_msg()
        
        # 将姿态从旋转对象转回欧拉角
        roll, pitch, yaw = target_x5_rot.as_euler('xyz', degrees=False)
        
        # 填充末端位姿指令 [cite: 130]
        robot_cmd_msg.end_pos = [
            target_x5_pos[0],
            target_x5_pos[1],
            target_x5_pos[2],
            roll,
            pitch,
            yaw
        ]
        
        # 设置为末端位姿控制模式 [cite: 131]
        robot_cmd_msg.mode = 4

        # 4. 发布指令
        self.x5_publisher.publish(robot_cmd_msg)
        # self.get_logger().info(f'发布X5目标指令: {robot_cmd_msg.end_pos}')


def main(args=None):
    rclpy.init(args=args)
    bridge_node = PosBridgeNode()
    rclpy.spin(bridge_node)
    bridge_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()