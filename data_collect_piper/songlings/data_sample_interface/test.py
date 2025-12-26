from typing import List, Iterator
from piper_datastructures import ArmJoint, ArmGripper, ArmEndPose
from utils import (
    # 从从臂中读数据的函数
    parser_joint_from_stream,
    parser_endpose_from_stream,
    parser_gripper_from_stream,
    
    # 从主臂中读数据的函数
    parser_joint_ctrl_from_stream,
    parser_gripper_ctrl_from_stream,
    
    # 用于存储各类数据的函数
    joint_to_bytes,
    endpose_to_bytes,
    gripper_to_bytes,
    joint_ctrl_to_bytes,
    gripper_ctrl_to_bytes
    
    # 函数名中带有ctrl的都是主臂相关的，没有的都是从臂相关的
)

# 关节角度迭代器：每次返回6个关节角度
def joint_iterator(joints: List[ArmJoint]) -> Iterator[List[float]]:
    for joint in joints:
        yield [
            joint.joint_state.joint_1,
            joint.joint_state.joint_2,
            joint.joint_state.joint_3,
            joint.joint_state.joint_4,
            joint.joint_state.joint_5,
            joint.joint_state.joint_6
        ]

# 夹爪角度迭代器：每次返回1个夹爪角度
def gripper_iterator(grippers: List[ArmGripper]) -> Iterator[float]:
    for gripper in grippers:
        yield gripper.gripper_state.grippers_angle

# 末端姿态迭代器：每次返回6个末端姿态的坐标和角度
def eef_iterator(eefs: List[ArmEndPose]) -> Iterator[List[float]]:
    for eef in eefs:
        yield [
            eef.end_pose.X_axis,
            eef.end_pose.Y_axis,
            eef.end_pose.Z_axis,
            eef.end_pose.RX_axis,
            eef.end_pose.RY_axis,
            eef.end_pose.RZ_axis
        ]

# 使用示例
joints: List[ArmJoint] = list(parser_joint_from_stream('data/03-04@11:07:27/follower_joint_downsample'))
gripper: List[ArmGripper] = list(parser_gripper_from_stream('data/03-04@11:07:27/follower_gripper_downsample'))
eefs: List[ArmEndPose] = list(parser_endpose_from_stream('data/03-04@11:07:27/follower_endpose_downsample'))

# 迭代示例
joint_iter = joint_iterator(joints)
gripper_iter = gripper_iterator(gripper)
eef_iter = eef_iterator(eefs)

# 遍历每个迭代器
for joint_angles in joint_iter:
    print("Joint Angles:", joint_angles)

for gripper_angle in gripper_iter:
    print("Gripper Angle:", gripper_angle)

for eef_pose in eef_iter:
    print("End-Effector Pose:", eef_pose)
    
    
'''
图像在对应文件夹下的imgs文件夹下，共4个子文件夹,img_[1/2]_[color/depth]，表示第1/2个摄像头的数据，分别是rgb图像和深度图像
上面展示的数据对应的图像在data_sample_interface/data/03-04@11:07:27/imgs里面
'''
