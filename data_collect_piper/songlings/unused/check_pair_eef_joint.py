from torch import ge
from utils import parser_joint_from_stream, parser_endpose_from_stream
# from piper_sdk.kinematics.piper_fk import C_PiperForwardKinematics
from utils import C_PiperForwardKinematics
from rich import print
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

joints = list(parser_joint_from_stream('data/ano/clean_remake/04-07AAA15:43/follower_joint'))
eefs = list(parser_endpose_from_stream('data/ano/clean_remake/04-07AAA15:43/follower_endpose'))
calc = C_PiperForwardKinematics()

def get_diff(joint, eef):
    joint = [
        joint.joint_state.joint_1,
        joint.joint_state.joint_2,
        joint.joint_state.joint_3,
        joint.joint_state.joint_4,
        joint.joint_state.joint_5,
        joint.joint_state.joint_6,
    ]
    
    eef = [
        eef.end_pose.X_axis,
        eef.end_pose.Y_axis,
        eef.end_pose.Z_axis,
        eef.end_pose.RX_axis,
        eef.end_pose.RY_axis,
        eef.end_pose.RZ_axis,
    ]
    
    j_to_eef = calc.arm_forward([item / 1000 for item in joint])
    
    return joint, eef, j_to_eef

def get_staticics():
    total_diff = 0
    partial_diff = [0] * 3

    diffs = []
    for i in range(len(joints)):
        select_joint = joints[i]
        select_eef = eefs[i]

        joint, eef, j_to_eef = get_diff(select_joint, select_eef)

        diff = [abs(j_to_eef[i] * 1000 - eef[i]) for i in range(3)]
        total_diff += sum(diff)
        for i in range(3):
            partial_diff[i] += diff[i]

        diffs.append(sum(diff))
    diff_std = np.std(diffs)
    diff_mean = np.mean(diffs)
    diff_max = np.max(diffs)
    diff_min = np.min(diffs)
    diff_median = np.median(diffs)
    
    print(f"diff_std: {diff_std}")
    print(f"diff_mean: {diff_mean}")
    print(f"diff_max: {diff_max}")
    print(f"diff_min: {diff_min}")
    print(f"diff_median: {diff_median}")
    print(f"total_diff: {total_diff}")
    print(f"partial_diff: {partial_diff}")
    return diffs
    
# temp = get_staticics()

# for index, item in enumerate(temp):
#     if item > 10000:
#         print(f"index: {index}, diff: {item}")
#         joint = joints[index]
#         eef = eefs[index]
        
#         joint, eef, j_to_eef = get_diff(joint, eef)
#         print(f"joint: {joint}")
#         print(f"eef: {eef}")
#         print(f"j_to_eef: {j_to_eef}")
        
j = [joint.joint_state.joint_5 for joint in joints]
j = np.array(j)
print(f'max: {np.max(j)}')
print(f'min: {np.min(j)}')
print(f'mean: {np.mean(j)}')
print(f'std: {np.std(j)}')
print(f'median: {np.median(j)}')

# fig = px.line(
#     y=np.array(temp) / 6,  # 数据点的y值
#     title="一维数组折线图（Plotly Express）",
#     labels={'x': 'index', 'y': 'diff'}  # 坐标轴标签
# )
# fig.show()
# fig.write_html("line_plot.html")