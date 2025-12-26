import time
import numpy as np
import math
from scipy.spatial.transform import Rotation as R

# 假设你的SDK文件都在同一个目录下或Python路径中
from piper_interface_v2 import C_PiperInterface_V2
from utils import enable_fun  # 从utils.py导入使能函数

class RobotController:
    """
    一个封装了Piper机械臂控制的类，用于手眼标定。
    """
    def __init__(self, can_name="can0"):
        """
        初始化机械臂接口。
        :param can_name: CAN设备名称。
        """
        print(f"正在初始化机械臂接口，使用CAN设备: {can_name}...")
        self.piper = C_PiperInterface_V2(can_name=can_name)
        self.piper.ConnectPort()
        print("CAN端口已连接，数据线程已启动。")
        time.sleep(1) # 等待一下，确保有初始数据流

    def enable_robot(self):
        """
        使能机械臂。
        """
        print("正在使能机械臂...")
        enable_fun(self.piper)
        print("[成功] 机械臂已使能。")
        
    def enter_drag_teach_mode(self):
        """
        发送指令使机械臂进入拖动示教模式
        """
        print("正在进入拖动示教模式...")
        # 调用 MotionCtrl_1，将 grag_teach_ctrl 参数设为 0x01

        #self.piper.MotionCtrl_1(emergency_stop=0, track_ctrl=0, grag_teach_ctrl=0x01)
        time.sleep(0.5) # 等待指令生效
        print("[成功] 机械臂现在可以被拖动。")
    
    def exit_drag_teach_mode(self):
        """
        发送指令使机械臂退出拖动示教模式，并锁定当前位置。
        """
        print("正在退出拖动示教模式...")


        # 调用 MotionCtrl_1，将 grag_teach_ctrl 参数设为 0x02

        #self.piper.MotionCtrl_1(emergency_stop=0, track_ctrl=0, grag_teach_ctrl=0x02)
        time.sleep(0.5) # 等待指令生效
        print("[成功] 机械臂已锁定当前位置。")
    
    
    def get_eef_pose_raw(self):
        """
        从SDK获取原始的末端位姿数据。
        返回的是一个包含6个整数的列表 [x, y, z, rx, ry, rz]。
        单位: x,y,z 为 0.001mm; rx,ry,rz 为 0.001度。
        """
        end_pose_msg = self.piper.GetArmEndPoseMsgs()
        pose = end_pose_msg.end_pose
        
        raw_pose = [
            pose.X_axis,
            pose.Y_axis,
            pose.Z_axis,
            pose.RX_axis,
            pose.RY_axis,
            pose.RZ_axis
        ]
        #print("raw_pose:", raw_pose)

        return raw_pose

    def get_eef_pose_matrix(self):
        """
        获取末端位姿，并将其转换为手眼标定所需的4x4齐次变换矩阵。
        :return: 一个4x4的NumPy数组 (T_base^tool)，平移单位为毫米(mm)。
        """
        # 1. 获取原始数据
        raw_pose = self.get_eef_pose_raw()
        
        # 2. 单位转换
        # 平移: 从 0.001mm 转换为 mm
        t_mm = np.array([
            raw_pose[0] / 1000.0,
            raw_pose[1] / 1000.0,
            raw_pose[2] / 1000.0
        ]).reshape(3, 1)

        # 旋转: 从 0.001度 转换为 弧度
        # 注意: 欧拉角的旋转顺序非常重要！这里假设是'xyz'，你需要根据机器人文档确认。
        # 'xyz'表示先绕固定的X轴，再绕固定的Y轴，最后绕固定的Z轴旋转。
        # 如果是 'ZYX' (Roll-Pitch-Yaw)，顺序是'zyx'。这更常见。
        # 我们假设是 'xyz'，单位为度
        angles_deg = np.array([
            raw_pose[3] / 1000.0,
            raw_pose[4] / 1000.0,
            raw_pose[5] / 1000.0
        ])
        print("机器人6位姿:", raw_pose[0] / 1000.0,raw_pose[1] / 1000,raw_pose[2] / 1000.0,raw_pose[3] / 1000.0,raw_pose[4] / 1000.0,raw_pose[5]/1000 )
        # 3. 姿态转换 (欧拉角 -> 旋转矩阵)
        # 重要：需要确认机器人的欧拉角定义顺序
        # 大多数工业机器人使用 ZYX (Roll-Pitch-Yaw) 顺序
        print(f"欧拉角 (度): RX={angles_deg[0]:.3f}, RY={angles_deg[1]:.3f}, RZ={angles_deg[2]:.3f}")
        try:
            # 使用 ZYX 顺序 (Roll-Pitch-Yaw)，这是最常见的工业机器人约定
            rotation = R.from_euler('ZYX', angles_deg, degrees=True)
            rotation_matrix = rotation.as_matrix()
        except ImportError:
            print("[警告] 未找到scipy库，将使用手动计算。请运行 'pip install scipy' 以获得更稳健的转换。")
            rotation_matrix = self._euler_to_rotation_matrix(np.deg2rad(angles_deg), 'zyx')

        # 4. 构建4x4齐次变换矩阵
        T_base_tool = np.eye(4)
        T_base_tool[0:3, 0:3] = rotation_matrix
        T_base_tool[0:3, 3:4] = t_mm

        # 设置NumPy打印格式：保留小数点后3位
        np.set_printoptions(precision=3, suppress=True)  # suppress=True 禁用科学计数法
        print("原始机器人位姿矩阵:")
        print(T_base_tool)
        #print("原始机器人位姿矩阵:", T_base_tool)


        return T_base_tool   # 返回原始4x4齐次位姿变换矩阵

    def _euler_to_rotation_matrix(self, angles_rad, order='xyz'):
        """
        手动将欧拉角转换为旋转矩阵的备用方法。
        """
        rx, ry, rz = angles_rad
        
        Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
        Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
        Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])

        if order.lower() == 'xyz':
            # R = Rz * Ry * Rx
            R_mat = Rz @ Ry @ Rx
        elif order.lower() == 'zyx':
            # R = Rx * Ry * Rz
            R_mat = Rx @ Ry @ Rz
        else:
            raise ValueError(f"不支持的欧拉角顺序: {order}")
            
        return R_mat

    def stop(self):
        """
        关闭与机械臂的连接。
        """
        # SDK中没有明确的stop或disconnect方法，通常是程序结束时自动清理。
        # 如果有，应该在这里调用。
        print("正在关闭机械臂接口...")
        self.piper.running = False # 停止CAN读取线程
        
# ==============================================================================
# 拖动到指定位置 得到该位置的EEF
# ==============================================================================
if __name__ == '__main__':
    
    robot_controller = None
    try:
        # 0. 初始化并使能机器人
        robot_controller = RobotController(can_name="can0")
        robot_controller.enable_robot()
        # 1. 进入拖动模式
        # robot_controller.enter_drag_teach_mode()  改接口不能用 

        # 2. 等待用户操作
        print("\n按机械臂头部的按钮 变为常绿然后将机械臂拖动到一个新的姿态。")
        input("摆放好后，请按 Enter 键来锁定位置并采集数据...")
        # 3. 退出拖动模式，锁定位置
        #robot_controller.exit_drag_teach_mode()
        # 4. 等待机械臂稳定
        time.sleep(1) # 锁定后等待1秒，确保机器人完全静止

        # 2. 获取一次末端位姿矩阵
        print("正在获取当前末端位姿...")
        pose_matrix = robot_controller.get_eef_pose_matrix()
        
        # 3. 打印结果
        print("\n获取到的4x4位姿矩阵 (T_base^tool) 为:")
        np.set_printoptions(precision=3, suppress=True) # 设置打印格式
        print(pose_matrix)

        # 验证平移和旋转部分
        translation = pose_matrix[:3, 3]
        print(f"\n平移向量 (mm): [x={translation[0]:.3f}, y={translation[1]:.3f}, z={translation[2]:.3f}]")
        
        rotation_check = R.from_matrix(pose_matrix[:3,:3])
        euler_angles_check = rotation_check.as_euler('xyz', degrees=True)
        print(f"转换回的欧拉角 (度): [rx={euler_angles_check[0]:.3f}, ry={euler_angles_check[1]:.3f}, rz={euler_angles_check[2]:.3f}]")

    except Exception as e:
        print(f"[主程序发生错误]: {e}")
    finally:
        if robot_controller:
            robot_controller.stop()