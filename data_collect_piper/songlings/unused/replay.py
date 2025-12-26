import time
from utils import parser_gripper_from_stream, parser_joint_from_stream, enable_fun
from piper_interface_v2 import C_PiperInterface_V2
from rich import print

piper = C_PiperInterface_V2()
piper.ConnectPort()
enable_fun(piper)

g_joint = parser_joint_from_stream(
    open('data/03-05@11:02:44/follower_joint_downsample_10hz', 'rb')
)
g_gripper = parser_gripper_from_stream(
    open('data/03-05@11:02:44/follower_gripper_downsample_10hz', 'rb')
)

g_joint = iter(g_joint)
g_gripper = iter(g_gripper)

joint = next(g_joint, None)
gripper = next(g_gripper, None)
if gripper is not None:
    gripper.time_stamp /= 1e9

start_time = float('inf')
if joint is not None:
    start_time = min(start_time, joint.time_stamp)
if gripper is not None:
    start_time = min(start_time, gripper.time_stamp)

program_start_time = time.time()
piper.MotionCtrl_2(0x01, 0x01, 100, 0x00)
while False \
    or g_joint is not None \
    or g_gripper is not None:
        current_time_stamp = time.time() - program_start_time + start_time
        if joint is not None and joint.time_stamp < current_time_stamp:
            # print(f'execute joint')
            piper.JointCtrl(
                joint.joint_state.joint_1,
                joint.joint_state.joint_2,
                joint.joint_state.joint_3,
                joint.joint_state.joint_4,
                joint.joint_state.joint_5,
                joint.joint_state.joint_6,
            )
            print(joint)
            joint = next(g_joint, None)
        if gripper is not None and gripper.time_stamp < current_time_stamp:
            # print(f'{current_time_stamp} ---> {gripper.time_stamp}')
            # print(gripper)
            # print(f'execute gripper')
            piper.GripperCtrl(
                abs(gripper.gripper_state.grippers_angle),
                1000,
                0x01,
                0
            )
            gripper = next(g_gripper, None)
            if gripper is not None:
                gripper.time_stamp /= 1e9

    