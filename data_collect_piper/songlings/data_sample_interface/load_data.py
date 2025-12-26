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
from typing import List
from piper_datastructures import ArmJoint, ArmGripper, ArmEndPose

# 具体的数据说明可以点到类型定义里面看
# 文件名里带follower的是从臂的数据，带leader的是主臂的数据
# 注意： grippers数据里的timestamp是正常数据的1e9倍，使用时记得先放缩
# Gripper数据只会用到grippers_angle

joints  : List[ArmJoint]   = list(parser_joint_from_stream('data/03-04@11:07:27/follower_joint_downsample'))
gripper : List[ArmGripper] = list(parser_gripper_from_stream('data/03-04@11:07:27/follower_gripper_downsample'))
eefs    : List[ArmEndPose] = list(parser_endpose_from_stream('data/03-04@11:07:27/follower_endpose_downsample'))

print(gripper[2])
