from utils import parser_endpose_from_stream, parser_endpose_from_stream
from piper_sdk.kinematics.piper_fk import C_PiperForwardKinematics
from rich import print

joints = list(parser_endpose_from_stream(open('data/03-04@11:07:27/follower_joint', 'rb')))
eefs = list(parser_endpose_from_stream(open('data/03-04@11:07:27/follower_endpose', 'rb')))
calc = C_PiperForwardKinematics()

for i in range(len(joints)):
    select_joint = joints[i]
    select_eef = eefs[i]

    joint = [
        select_joint.joint_state.joint_1,
        select_joint.joint_state.joint_2,
        select_joint.joint_state.joint_3,
        select_joint.joint_state.joint_4,
        select_joint.joint_state.joint_5,
        select_joint.joint_state.joint_6,
    ]
    eef = [
        select_eef.end_pose.X_axis,
        select_eef.end_pose.Y_axis,
        select_eef.end_pose.Z_axis,
        select_eef.end_pose.RX_axis,
        select_eef.end_pose.RY_axis,
        select_eef.end_pose.RZ_axis,
    ]
    joint = [item / 1000 for item in joint]
    j_to_eef = calc.arm_forward(joint)

    print(f'joint 0 stamp: {select_joint.time_stamp}')
    print(f'eef 0 stamp: {select_eef.time_stamp}')

    print(f'joint: {joint}')
    print(f'eef: {eef}')
    print(f'------------------------------------------------')
    print(f'joint to eef: {j_to_eef}')
    print(f'eef:{eef}')

    print(f'diff: {[a * 1000 - b for a, b in zip(j_to_eef, eef)]}')
    input('>')