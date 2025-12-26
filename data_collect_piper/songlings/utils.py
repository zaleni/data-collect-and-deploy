import struct
from collections import defaultdict
from itertools import islice
from piper_interface_v2 import (
    ArmJoint,
    ArmGripper,
    ArmEndPose,
    ArmJointCtrl,
    ArmGripperCtrl,
)
from io import BufferedReader
import math
from typing import Generator, Union, Iterator, Callable, Literal
import time
from rich import print
import os
import torch
import cv2
from glob import glob

joint_struct = struct.Struct(">ddiiiiii")
gripper_struct = struct.Struct(">ddiii")
endpose_struct = struct.Struct(">ddiiiiii")


def enable_fun(piper):
    """
    使能机械臂并检测使能状态,尝试5s,如果使能超时则退出程序
    """
    piper.EnableArm(7)
    enable_flag = False
    # 设置超时时间（秒）
    timeout = 5
    # 记录进入循环前的时间
    start_time = time.time()
    elapsed_time_flag = False
    while not (enable_flag):
        elapsed_time = time.time() - start_time
        print("--------------------")
        enable_flag = (
            piper.GetArmLowSpdInfoMsgs().motor_1.foc_status.driver_enable_status
            and piper.GetArmLowSpdInfoMsgs().motor_2.foc_status.driver_enable_status
            and piper.GetArmLowSpdInfoMsgs().motor_3.foc_status.driver_enable_status
            and piper.GetArmLowSpdInfoMsgs().motor_4.foc_status.driver_enable_status
            and piper.GetArmLowSpdInfoMsgs().motor_5.foc_status.driver_enable_status
            and piper.GetArmLowSpdInfoMsgs().motor_6.foc_status.driver_enable_status
        )
        print("使能状态:", enable_flag)
        piper.EnableArm(7)
        piper.GripperCtrl(0, 1000, 0x01, 0)
        print("--------------------")
        # 检查是否超过超时时间
        if elapsed_time > timeout:
            print("超时....")
            elapsed_time_flag = True
            enable_flag = True
            break
        time.sleep(1)
        pass
    if elapsed_time_flag:
        print("程序自动使能超时,退出程序")
        exit(0)


class MockTimer:
    def __init__(self, based_time):
        self.start_time = None
        self.elapsed = 0
        self.running = False
        self.based_time = based_time

    def start(self):
        if not self.running:
            self.start_time = time.time() - self.elapsed
            self.running = True

    def pause(self):
        if self.running:
            self.elapsed = time.time() - self.start_time
            self.running = False

    def reset(self):
        self.start_time = None
        self.elapsed = 0
        self.running = False

    def time(self):
        if self.running:
            return time.time() - self.start_time + self.based_time
        return self.based_time + self.elapsed


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


parser_joint_from_stream: Callable[[str], Iterator[ArmJoint]] = _parse_from_stream(
    8 * 2 + 4 * 6, _bytes_to_joint
)

parser_gripper_from_stream: Callable[[str], Iterator[ArmGripper]] = _parse_from_stream(
    8 * 2 + 4 * 3, _byte_to_gripper
)

parser_endpose_from_stream: Callable[[str], Iterator[ArmEndPose]] = _parse_from_stream(
    8 * 2 + 4 * 6, _byte_to_endpose
)

parser_joint_ctrl_from_stream: Callable[[str], Iterator[ArmJointCtrl]] = _parse_from_stream(
    8 * 2 + 4 * 6, _bytes_to_joint_ctrl
)

parser_gripper_ctrl_from_stream: Callable[[str], Iterator[ArmGripperCtrl]] = _parse_from_stream(
    8 * 2 + 4 * 3, _byte_to_gripper_ctrl
)


# safe_eef_range = [
#     [-43964, 240761],  # x
#     [-226757, 38866],  # y
#     [161286, 413472],  # z
#     [-179879, 180000],  # rx
#     [436, 90000],  # ry
#     [-179844, 180000],  # rz
# ]

safe_eef_range = [
    [-60000000, 60000000],  # x
    [-15000000, 70000000],  # y
    [-13400000, 60000000],  # z 133894 [-161286, 4134720]
    [-17987900, 18000000],  # rx
    [-30000000, 90000000],  # ry
    [-17984400, 18000000],  # rz
]


def check_eef(x, y, z, rx, ry, rz):
    return (
        True
        and safe_eef_range[0][0] <= x <= safe_eef_range[0][1]
        and safe_eef_range[1][0] <= y <= safe_eef_range[1][1]
        and safe_eef_range[2][0] <= z <= safe_eef_range[2][1]
        and safe_eef_range[3][0] <= rx <= safe_eef_range[3][1]
        and safe_eef_range[4][0] <= ry <= safe_eef_range[4][1]
        and safe_eef_range[5][0] <= rz <= safe_eef_range[5][1]
    )


def print_check_eef(x, y, z, rx, ry, rz):
    valid_x = safe_eef_range[0][0] <= x <= safe_eef_range[0][1]
    valid_y = safe_eef_range[1][0] <= y <= safe_eef_range[1][1]
    valid_z = safe_eef_range[2][0] <= z <= safe_eef_range[2][1]
    valid_rx = safe_eef_range[3][0] <= rx <= safe_eef_range[3][1]
    valid_ry = safe_eef_range[4][0] <= ry <= safe_eef_range[4][1]
    valid_rz = safe_eef_range[5][0] <= rz <= safe_eef_range[5][1]

    tag_x = "[green] X [/green]" if valid_x else "[red] X [/red]"
    tag_y = "[green] Y [/green]" if valid_y else "[red] Y [/red]"
    tag_z = "[green] Z [/green]" if valid_z else "[red] Z [/red]"
    tag_rx = "[green] RX [/green]" if valid_rx else "[red] RX [/red]"
    tag_ry = "[green] RY [/green]" if valid_ry else "[red] RY [/red]"
    tag_rz = "[green] RZ [/green]" if valid_rz else "[red] RZ [/red]"

    print(f"safe low : {[safe_eef_range[i][0] for i in range(6)]}")
    print(f"current  : {[x, y, z, rx, ry, rz]}")
    print(f"safe high: {[safe_eef_range[i][1] for i in range(6)]}")
    print(f"{[tag_x, tag_y, tag_z, tag_rx, tag_ry, tag_rz]}")


def _clip(min_value, value, max_value):
    return min(max_value, max(min_value, value))


def _clip_range(boundary, value):
    return _clip(boundary[0], value, boundary[1])


def rectily_eef(x, y, z, rx, ry, rz):
    return (
        _clip_range(safe_eef_range[0], x),
        _clip_range(safe_eef_range[1], y),
        _clip_range(safe_eef_range[2], z),
        _clip_range(safe_eef_range[3], rx),
        _clip_range(safe_eef_range[4], ry),
        _clip_range(safe_eef_range[5], rz),
    )


def load_images(img_path):
    """
    读取指定路径下的所有图片
    Args:
        img_path: 图片文件夹路径
    Returns:
        list: 按文件名排序的图片列表
    """
    # 获取所有jpg和png图片
    image_files = sorted(glob(os.path.join(img_path, "*.jpg")))
    images = []

    for img_file in image_files:
        # 读取图片
        img = cv2.imread(img_file)
        if img is not None:
            # 转换为RGB格式（OpenCV默认是BGR）
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)

    return images


def load_images_as_tensors(img_path):
    """
    读取指定路径下的所有图片并转换为PyTorch张量
    Args:
        img_path: 图片文件夹路径
    Returns:
        list: 包含所有图片张量的列表
    """
    images = load_images(img_path)
    # 转换为PyTorch张量，并归一化到[0,1]范围
    tensor_images = [torch.from_numpy(img).float() / 255.0 for img in images]
    return tensor_images


def process_data(basepath):
    img1c_path = os.path.join(basepath, "imgs/img_1_color")
    img1d_path = os.path.join(basepath, "imgs/img_1_depth")
    img2c_path = os.path.join(basepath, "imgs/img_2_color")
    img2d_path = os.path.join(basepath, "imgs/img_2_depth")
    fe_path = os.path.join(basepath, "follower_endpose")
    fg_path = os.path.join(basepath, "follower_gripper")
    fj_path = os.path.join(basepath, "follower_joint")
    original_freq = 200
    target_freq = 1
    downsample_interval = int(original_freq / target_freq)

    endpose_iter = parser_endpose_from_stream(fe_path)
    joint_iter = parser_joint_from_stream(fj_path)
    gripper_iter = parser_gripper_from_stream(fg_path)

    endpose_iter = islice(
        parser_endpose_from_stream(fe_path), 0, None, downsample_interval
    )
    joint_iter = islice(parser_joint_from_stream(fj_path), 0, None, downsample_interval)
    gripper_iter = islice(
        parser_gripper_from_stream(fg_path), 0, None, downsample_interval
    )
    tensor_images_1c = load_images_as_tensors(img1c_path)
    tensor_images_1d = load_images_as_tensors(img1d_path)
    tensor_images_2c = load_images_as_tensors(img2c_path)
    tensor_images_2d = load_images_as_tensors(img2d_path)
    return (
        endpose_iter,
        joint_iter,
        gripper_iter,
        tensor_images_1c,
        tensor_images_1d,
        tensor_images_2c,
        tensor_images_2d,
    )


def data_to_tensor(endpose, joint, gripper):
    # 提取并转换endpose数据
    endpose_tensor = torch.tensor(
        [
            endpose.end_pose.X_axis,  # 转换到米级单位
            endpose.end_pose.Y_axis,
            endpose.end_pose.Z_axis,
            endpose.end_pose.RX_axis,
            endpose.end_pose.RY_axis,
            endpose.end_pose.RZ_axis,
        ],
        dtype=torch.int32,
    )

    # 提取并转换joint数据
    joint_tensor = torch.tensor(
        [
            joint.joint_state.joint_1,
            joint.joint_state.joint_2,
            joint.joint_state.joint_3,
            joint.joint_state.joint_4,
            joint.joint_state.joint_5,
            joint.joint_state.joint_6,
        ],
        dtype=torch.int32,
    )

    # 提取并转换gripper数据
    gripper_tensor = torch.tensor(
        [
            gripper.gripper_state.grippers_angle,
        ],
        dtype=torch.int32,
    )
    return endpose_tensor, joint_tensor, gripper_tensor


def syn_data(basepath):

    count = 0
    synced_data = []

    (
        endpose_iter,
        joint_iter,
        gripper_iter,
        tensor_images_1c,
        tensor_images_1d,
        tensor_images_2c,
        tensor_images_2d,
    ) = process_data(basepath)

    while True:
        try:
            img_index = count // 3
            if img_index >= len(tensor_images_1c):
                break

            # 获取当前图片组
            current_img_1c = tensor_images_1c[img_index]
            current_img_1d = tensor_images_1d[img_index]
            current_img_2c = tensor_images_2c[img_index]
            current_img_2d = tensor_images_2d[img_index]

            endpose = next(endpose_iter)
            joint = next(joint_iter)
            # 每个gripper数据要用三次
            if count % 3 == 0:
                current_gripper = next(gripper_iter)
            endpose_tensor, joint_tensor, gripper_tensor = data_to_tensor(
                endpose, joint, current_gripper
            )
            synced_data.append(
                {
                    "images": [
                        current_img_1c,
                        current_img_1d,
                        current_img_2c,
                        current_img_2d,
                    ],
                    "endpose": endpose_tensor,
                    "joint": joint_tensor,
                    "gripper": gripper_tensor,
                }
            )
            count += 1

        except StopIteration:
            break
    return synced_data


if __name__ == "__main__":
    basepath = "/home/robot/mzk_workspace/data_collect/data/03-04@11:07:27"
    # synced_data = syn_data(basepath)

    # print(len(tensor_images_1d))
    length = 0
    synced_data = syn_data(basepath)
    for step in synced_data:
        # print(step["images"], step["endpose"], step["joint"], step["gripper"], "\n")
        # print(
        #     step["images"][0].shape,
        #     step["images"][1].shape,
        #     step["images"][2].shape,
        #     step["images"][3].shape,
        # )
        length += 1
        # break
    print("length", length)




class C_PiperForwardKinematics():
    def __init__(self):
        self.RADIAN = 57.295777
        self.PI_2 = math.pi / 2
        # DH参数矩阵（Denavit-Hartenberg）
        self.DH_matrix = [
            [0.0, 0.123, 0.0, -self.PI_2],
            [-self.PI_2, 0.0, 0.28503, 0.0],
            [self.PI_2, 0.02198, 0.0, self.PI_2],
            [0.0, 0.25075, 0.0, -self.PI_2],
            [0.0, 0.0, 0.0, self.PI_2],
            [0.0, 0.091, 0.0, 0.0]
        ]
    
    def __arm_rotmat_to_eulerangle(self, rotationM, eulerAngles):
        # 旋转矩阵转换为欧拉角
        if abs(rotationM[6]) >= 1.0 - 0.0001:
            if rotationM[6] < 0:
                A = 0.0
                B = self.PI_2
                C = math.atan2(rotationM[1], rotationM[4])
            else:
                A = 0.0
                B = -self.PI_2
                C = -math.atan2(rotationM[1], rotationM[4])
        else:
            B = math.atan2(-rotationM[6], math.sqrt(rotationM[0] ** 2 + rotationM[3] ** 2))
            cb = math.cos(B)
            A = math.atan2(rotationM[3] / cb, rotationM[0] / cb)
            C = math.atan2(rotationM[7] / cb, rotationM[8] / cb)

        eulerAngles[0] = C
        eulerAngles[1] = B
        eulerAngles[2] = A

    # 矩阵相乘函数
    def __matrix_multiply(self, A, B, m, p, n, C):
        for i in range(m):
            for j in range(n):
                C[i * n + j] = 0
                for k in range(p):
                    C[i * n + j] += A[i * p + k] * B[k * n + j]
    
    # 正向运动学函数
    def arm_forward(self, joint_states:list, joint_index:Literal[1, 2, 3, 4, 5, 6]=6):
        q_in = [0.0] * 6
        q = [0.0] * 6
        cosq = sinq = cosa = sina = 0.0
        P06 = [0.0] * 6
        R06 = [0.0] * 9
        R = [[0.0] * 9 for _ in range(6)]
        R02 = [0.0] * 9
        R03 = [0.0] * 9
        R04 = [0.0] * 9
        R05 = [0.0] * 9
        L0_bs = [0.0] * 3
        L0_se = [0.0] * 3
        L0_ew = [0.0] * 3
        L0_wt = [0.0] * 3

        L1_base = [0.0, -0.123, 0.0]
        L2_arm = [0.28503, 0.0, 0.0]
        L3_elbow = [-0.02198, 0.0, 0.25075]
        L6_wrist = [0.0, 0.0, 0.091]
        migration_val = [0, 84.22, -169.22, 0, 0, 0]

        # 将输入关节角度转换为弧度
        for i in range(6):
            q_in[i] = (joint_states[i] - migration_val[i]) / self.RADIAN

        # 计算每个关节的旋转矩阵
        for i in range(joint_index):
            q[i] = q_in[i] + self.DH_matrix[i][0]
            cosq = math.cos(q[i])
            sinq = math.sin(q[i])
            cosa = math.cos(self.DH_matrix[i][3])
            sina = math.sin(self.DH_matrix[i][3])

            R[i][0] = cosq
            R[i][1] = -cosa * sinq
            R[i][2] = sina * sinq
            R[i][3] = sinq
            R[i][4] = cosa * cosq
            R[i][5] = -sina * cosq
            R[i][6] = 0.0
            R[i][7] = sina
            R[i][8] = cosa

        # 矩阵相乘
        self.__matrix_multiply(R[0], R[1], 3, 3, 3, R02)
        self.__matrix_multiply(R02, R[2], 3, 3, 3, R03)
        self.__matrix_multiply(R03, R[3], 3, 3, 3, R04)
        self.__matrix_multiply(R04, R[4], 3, 3, 3, R05)
        self.__matrix_multiply(R05, R[5], 3, 3, 3, R06)

        self.__matrix_multiply(R[0], L1_base, 3, 3, 1, L0_bs)
        self.__matrix_multiply(R02, L2_arm, 3, 3, 1, L0_se)
        self.__matrix_multiply(R03, L3_elbow, 3, 3, 1, L0_ew)
        self.__matrix_multiply(R06, L6_wrist, 3, 3, 1, L0_wt)

        for i in range(3):
            P06[i] = L0_bs[i] + L0_se[i] + L0_ew[i] + L0_wt[i]

        # 计算旋转矩阵对应的欧拉角
        euler = [0.0] * 3
        self.__arm_rotmat_to_eulerangle(R06, euler)
        P06[3:] = euler

        # 更新输出
        pos_rot = [ P06[0] * 1000, P06[1] * 1000, P06[2] * 1000,
                    P06[3] * self.RADIAN, P06[4] * self.RADIAN, P06[5] * self.RADIAN]
        return pos_rot