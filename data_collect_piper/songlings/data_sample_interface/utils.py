import struct
from .piper_datastructures import (
    ArmJoint,
    ArmJointCtrl,
    ArmGripper,
    ArmGripperCtrl,
    ArmEndPose
)
from typing import Union, Iterator
from io import BufferedReader
import math

joint_struct = struct.Struct(">ddiiiiii")
gripper_struct = struct.Struct(">ddiii")
endpose_struct = struct.Struct(">ddiiiiii")


def joint_to_bytes(joint: ArmJoint):
    return joint_struct.pack(
        joint.time_stamp,
        joint.Hz,
        joint.joint_state.joint_1,
        joint.joint_state.joint_2,
        joint.joint_state.joint_3,
        joint.joint_state.joint_4,
        joint.joint_state.joint_5,
        joint.joint_state.joint_6,
    )


def _bytes_to_joint(byte):
    joint = ArmJoint()
    ts, hz, j1, j2, j3, j4, j5, j6 = joint_struct.unpack(byte)
    joint.time_stamp = ts
    joint.Hz = hz
    joint.joint_state.joint_1 = j1
    joint.joint_state.joint_2 = j2
    joint.joint_state.joint_3 = j3
    joint.joint_state.joint_4 = j4
    joint.joint_state.joint_5 = j5
    joint.joint_state.joint_6 = j6
    return joint


def gripper_to_bytes(gripper: ArmGripper):
    return gripper_struct.pack(
        gripper.time_stamp,
        gripper.Hz,
        gripper.gripper_state.grippers_angle,
        gripper.gripper_state.grippers_effort,
        gripper.gripper_state.status_code,
    )


def _byte_to_gripper(byte):
    gripper = ArmGripper()
    ts, hz, ang, eff, code = gripper_struct.unpack(byte)
    gripper.time_stamp = ts
    gripper.Hz = hz
    gripper.gripper_state.grippers_angle = ang
    gripper.gripper_state.grippers_effort = eff
    gripper.gripper_state.status_code = code
    return gripper


def endpose_to_bytes(ep: ArmEndPose):
    return endpose_struct.pack(
        ep.time_stamp,
        ep.Hz,
        ep.end_pose.X_axis,
        ep.end_pose.Y_axis,
        ep.end_pose.Z_axis,
        ep.end_pose.RX_axis,
        ep.end_pose.RY_axis,
        ep.end_pose.RZ_axis,
    )


def _byte_to_endpose(byte):
    ep = ArmEndPose()
    ts, hz, x, y, z, rx, ry, rz = endpose_struct.unpack(byte)
    ep.time_stamp = ts
    ep.Hz = hz
    ep.end_pose.X_axis = x
    ep.end_pose.Y_axis = y
    ep.end_pose.Z_axis = z
    ep.end_pose.RX_axis = rx
    ep.end_pose.RY_axis = ry
    ep.end_pose.RZ_axis = rz
    return ep


def joint_ctrl_to_bytes(joint: ArmJointCtrl):
    return joint_struct.pack(
        joint.time_stamp,
        joint.Hz,
        joint.joint_ctrl.joint_1,
        joint.joint_ctrl.joint_2,
        joint.joint_ctrl.joint_3,
        joint.joint_ctrl.joint_4,
        joint.joint_ctrl.joint_5,
        joint.joint_ctrl.joint_6,
    )


def _bytes_to_joint_ctrl(byte):
    joint = ArmJointCtrl()
    ts, hz, j1, j2, j3, j4, j5, j6 = joint_struct.unpack(byte)
    joint.time_stamp = ts
    joint.Hz = hz
    joint.joint_ctrl.joint_1 = j1
    joint.joint_ctrl.joint_2 = j2
    joint.joint_ctrl.joint_3 = j3
    joint.joint_ctrl.joint_4 = j4
    joint.joint_ctrl.joint_5 = j5
    joint.joint_ctrl.joint_6 = j6
    return joint


def gripper_ctrl_to_bytes(gripper: ArmGripperCtrl):
    return gripper_struct.pack(
        gripper.time_stamp,
        gripper.Hz,
        gripper.gripper_ctrl.grippers_angle,
        gripper.gripper_ctrl.grippers_effort,
        gripper.gripper_ctrl.status_code,
    )


def _byte_to_gripper_ctrl(byte):
    gripper = ArmGripperCtrl()
    ts, hz, ang, eff, code = gripper_struct.unpack(byte)
    gripper.time_stamp = ts
    gripper.Hz = hz
    gripper.gripper_ctrl.grippers_angle = ang
    gripper.gripper_ctrl.grippers_effort = eff
    gripper.gripper_ctrl.status_code = code
    return gripper


def _parse_from_stream(block_size, parse_func):
    def func(f: Union[BufferedReader, str]):
        is_file = True
        if not isinstance(f, BufferedReader):
            f = open(f, "rb")
            is_file = False

        f.seek(0, 2)
        file_size = f.tell()
        item_count = math.ceil(file_size / block_size)
        f.seek(0, 0)
        for _ in range(item_count):
            data = f.read(block_size)
            yield parse_func(data)

        if not is_file:
            f.close()

    return func


parser_joint_from_stream: Iterator[ArmJoint] = _parse_from_stream(
    8 * 2 + 4 * 6, _bytes_to_joint
)

parser_gripper_from_stream: Iterator[ArmGripper] = _parse_from_stream(
    8 * 2 + 4 * 3, _byte_to_gripper
)

parser_endpose_from_stream: Iterator[ArmEndPose] = _parse_from_stream(
    8 * 2 + 4 * 6, _byte_to_endpose
)

parser_joint_ctrl_from_stream: Iterator[ArmJointCtrl] = _parse_from_stream(
    8 * 2 + 4 * 6, _bytes_to_joint_ctrl
)

parser_gripper_ctrl_from_stream: Iterator[ArmGripperCtrl] = _parse_from_stream(
    8 * 2 + 4 * 3, _byte_to_gripper_ctrl
)
