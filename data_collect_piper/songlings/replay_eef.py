import time
from utils import parser_gripper_from_stream, parser_endpose_from_stream, enable_fun
from piper_interface_v2 import C_PiperInterface_V2
from rich import print

# piper = C_PiperInterface_V2()
# piper.ConnectPort()
# enable_fun(piper)

dataset_path = "/home/pc3/data_collect/songlings/data/tmp/1/10-17AAA12:10:01"
g_endpose = parser_endpose_from_stream(
    open(f"{dataset_path}/follower_endpose", "rb")
)
g_gripper = parser_gripper_from_stream(
    open(f"{dataset_path}/follower_gripper", "rb")
)

g_endpose = iter(g_endpose)
g_gripper = iter(g_gripper)

eef = next(g_endpose, None)
gripper = next(g_gripper, None)
if gripper is not None:
    gripper.time_stamp /= 1e9

start_time = float("inf")
if eef is not None:
    start_time = min(start_time, eef.time_stamp)
if gripper is not None:
    start_time = min(start_time, gripper.time_stamp)

program_start_time = time.time()
# piper.MotionCtrl_2(0x01, 0x00, 100, 0x00)
# input(':')
while False or g_endpose is not None or g_gripper is not None:
    current_time_stamp = time.time() - program_start_time + start_time
    if eef is not None and eef.time_stamp < current_time_stamp:
        # piper.MotionCtrl_2(0x01, 0x00, 100, 0x00)

        x, y, z, rx, ry, rz = [
            eef.end_pose.X_axis,
            eef.end_pose.Y_axis,
            eef.end_pose.Z_axis,
            eef.end_pose.RX_axis,
            eef.end_pose.RY_axis,
            eef.end_pose.RZ_axis,
        ]
        print(
            f"Time:{current_time_stamp:.3f}|EEF: {x:.2f}, {y:.2f}, {z:.2f}, {rx:.2f}, {ry:.2f}, {rz:.2f}"
        )
        # piper.EndPoseCtrl(
        #     x, y, z, rx, ry, rz

        # )

        eef = next(g_endpose, None)
    if gripper is not None and gripper.time_stamp < current_time_stamp:
        # print(f"execute gripper")
        # piper.GripperCtrl(abs(gripper.gripper_state.grippers_angle), 1000, 0x01, 0)
        # print(f'Gripper: {gripper.gripper_state.grippers_angle}')
        gripper = next(g_gripper, None)
        if gripper is not None:
            gripper.time_stamp /= 1e9
        print(f"Time:{current_time_stamp:.3f}|Gripper: {gripper.gripper_state.grippers_angle}")
    # input(':')
