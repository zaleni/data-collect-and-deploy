import rclpy
from rclpy.node import Node
from std_msgs.msg import Header

# 假设 PosCmd 来自 piper_msgs
# 如果您的 PosCmd 消息在不同的包中，请修改这里的导入
from scipy.spatial.transform import Rotation as R
from geometry_msgs.msg import Pose
from sensor_msgs.msg import JointState
from arx5_arm_msg.msg import RobotCmd
from piper_msgs.msg import PosCmd
import numpy as np

gap=[-0.0557, 0.001895, -0.19555]
# gap=[0.0, 0.0, 0.0] 
# piper init 0.055 0.0019 0.196
# ARX init -0.0007 0.000005 0.0045  

#0.062,-0.003,0.203,
#piper_max=0.623,0.618,0.747


#piper -1.8 1.192 -2         2.2 1.3 1.9       -2.1  0.3  -2

#arx -1.74 0.786 -0.15    -0.14 0.83 -0.06     -1.7 0.74 0.02




class PosBridgeNode(Node):
    """
    该节点订阅一个机械臂的'pos_cmd'话题，
    然后将指令转换为'RobotCmd'消息格式，
    并发布给另一个机械臂。
    """
    def __init__(self):
        super().__init__('pos_cmd_to_robot_cmd_bridge')

        # 创建订阅者，接收来自第一个机械臂的指令
        # 话题名称和消息类型需要根据您的实际情况进行调整
        self.gripper_position=0.0
        self.init_piper_pos=[0.055,0.0019,0.196,0.118,1.424,1.127,0.0]
        self.init_piper(self.init_piper_pos)
        input("continue...")
        self.gripper_sub = self.create_subscription(
            JointState,
            'joint_states_single',
            self.gripper_cmd_callback,
            10)


        self.subscription = self.create_subscription(
            Pose,
            'end_pose',  # 订阅的话题名称
            self.pos_cmd_callback,
            10)
        self.get_logger().info('订阅 "pos_cmd" 话题...')

        # # 创建发布者，向第二个机械臂发送指令
        self.publisher = self.create_publisher(
            RobotCmd,
            'arm_cmd',  # 发布的话题名称
            10)
        self.get_logger().info('创建 "arm_cmd" 话题的发布者...')




    def gripper_cmd_callback(self, msg: JointState):
        print(msg.position)
        # 这里可以处理夹爪命令，例如存储最新的夹爪位置
        def cut_off_gripper(x):
            # 输入范围 [-0.071, 0.001] 映射到输出范围 [0, 5]
            in_min, in_max = -0.071, 0.001
            out_min, out_max = 0.0, 5.0
            # x = max(in_min, min(in_max, x))
            # 线性映射公式
            y = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
            # 限制范围
            y = max(out_min, min(out_max, y))
            return y

        self.gripper_position = cut_off_gripper(msg.position[6])
        print(msg.position, self.gripper_position)

    



    def pos_cmd_callback(self, msg: Pose):


        def cut_off(value):
            if value >0.5:
                return 0.5
            elif value <-0.5:
                return -0.5
            else:
                return value
        def cut_off_2(value):
            if value >1.3:
                return 1.3
            elif value <-1.3:
                return -1.3
            else:
                return value
        """
        接收到 Pose 消息后的回调函数。
        """
        self.get_logger().info(f'接收到 Pose: position=({msg.position.x:.3f}, {msg.position.y:.3f}, {msg.position.z:.3f}), orientation=({msg.orientation.x:.3f}, {msg.orientation.y:.3f}, {msg.orientation.z:.3f}, {msg.orientation.w:.3f})')
        
        # 1. 创建一个新的 RobotCmd 消息
        robot_cmd_msg = RobotCmd()
        robot_cmd_msg.header = Header()
        robot_cmd_msg.header.stamp = self.get_clock().now().to_msg()

        # 2. 将 Pose 的数据映射到 RobotCmd
        
        # 从四元数转换到欧拉角
        quat = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]
        rotation = R.from_quat(quat)
        # 使用 'xyz' 顺序获取 roll, pitch, yaw
        # roll, pitch, yaw = rotation.as_euler('xyz', degrees=False)
        roll, pitch, yaw = rotation.as_euler('xyz', degrees=True)
        roll=roll/57.3
        pitch=pitch/57.3
        yaw=yaw/57.3
        # roll, pitch, yaw = 0.0, 0.0, 0.0
        # 将末端位姿从 Pose 复制到 RobotCmd
        robot_cmd_msg.end_pos = [
            cut_off(msg.position.x+gap[0]),
            cut_off(msg.position.y+gap[1]),
            cut_off(msg.position.z+gap[2]),
            cut_off_2(roll),
            cut_off_2(pitch),
            cut_off_2(yaw)
        ]

        # PosCmd 中没有关节位置信息，设置为默认值
        robot_cmd_msg.joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # 复制夹爪指令
        robot_cmd_msg.gripper = self.gripper_position
        # robot_cmd_msg.gripper = 0.0

        # 设置控制模式。模式 '4' 通常对应末端位姿控制。
        # 您可能需要根据接收端节点的需要调整此值。
        robot_cmd_msg.mode = 4

        # 3. 发布转换后的消息
        self.publisher.publish(robot_cmd_msg)
        self.get_logger().info(f'已发布 RobotCmd: end_pos={robot_cmd_msg.end_pos},gripper={robot_cmd_msg.gripper}')


    def init_piper(self,init_piper_pos):
        init_piper_cmd=PosCmd()
        init_piper_cmd.x=init_piper_pos[0]
        init_piper_cmd.y=init_piper_pos[1]
        init_piper_cmd.z=init_piper_pos[2]
        init_piper_cmd.roll=init_piper_pos[3]
        init_piper_cmd.pitch=init_piper_pos[4]
        init_piper_cmd.yaw=init_piper_pos[5]
        init_piper_cmd.gripper=init_piper_pos[6]
        init_piper_cmd.mode1=0
        init_piper_cmd.mode2=0
        self.init_publisher_ = self.create_publisher(PosCmd, 'pos_cmd', 10)
        self.init_publisher_.publish(init_piper_cmd)

def main(args=None):
    rclpy.init(args=args)
    try:
        bridge_node = PosBridgeNode()
        rclpy.spin(bridge_node)
    except KeyboardInterrupt:
        pass
    finally:
        if 'bridge_node' in locals() and rclpy.ok():
            bridge_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()