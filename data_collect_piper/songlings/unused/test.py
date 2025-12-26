import time
from utils import parser_gripper_from_stream, parser_endpose_from_stream, print_check_eef, rectily_eef
from piper_interface_v2 import C_PiperInterface_V2
from rich import print

import os
from converting_utils import _extract_timestamp_from_image_name
import numpy as np
import pickle
from typing import List

# folder = 'data/SimplePickUp/03-05@11:40:28/imgs/img_2_color'
# files = os.listdir(folder)
# out = []
# for file in files:
#     time_stamp = _extract_timestamp_from_image_name(file)
#     new_file = f'camera2_color_{str(time_stamp).replace(".", "_")}.jpg'
#     out.append((file, new_file, file == new_file))
# print(out)
# new_out = [x for x in out if not x[2]]
# print(new_out)

# files = [
#     '03-10@16:17:28',
#     '03-10@19:16:05',
#     '03-10@17:22:09',
#     '03-10@17:25:39',
#     # '03-10@18:57:14_有点快',
#     '03-10@19:17:20',
#     '03-10@16:54:32',
#     # '03-10@17:30:19_丢橘子不流畅（没有一次性对准）',
#     # '03-10@19:10:35_exception',
#     '03-10@17:31:59',
#     '03-10@17:21:08',
#     '03-10@17:16:11',
#     '03-10@16:55:26',
#     # '03-10@19:02:27_夹橘子不流畅',
#     '03-10@17:08:54',
#     '03-10@16:38:11',
#     '03-10@16:39:25',
#     '03-10@16:30:25',
#     '03-10@17:03:55',
#     '03-10@17:12:23',
#     '03-10@19:06:19',
#     # '03-10@19:04:51_丢橘子不流畅',
#     '03-10@18:55:41',
#     '03-10@16:34:48',
#     '03-10@17:20:05',
#     '03-10@17:23:25',
#     '03-10@17:13:24',
#     # '03-10@18:54:24_重复抓取',
#     '03-10@19:09:18',
#     # '03-10@19:13:34_夹橘子夹歪了',
#     '03-10@16:31:33',
#     '03-10@15:56:43',
#     '03-10@19:07:23',
#     '03-10@17:11:26',
#     '03-10@16:58:37',
#     '03-10@17:02:52',
#     # '03-10@16:36:15_exceptioin',
#     # '03-10@17:05:24_从臂抽搐',
#     '03-10@19:12:29',
#     '03-10@19:14:50',
#     '03-10@17:19:03',
#     '03-10@19:01:24',
#     # '03-10@17:26:42_有点快',
#     '03-10@17:24:21',
#     # '03-10@16:28:27_imp',
#     '03-10@19:08:18',
#     '03-10@17:33:14',
#     '03-10@16:33:08',
#     '03-10@16:26:01',
#     # '03-10@17:09:42_丢橘子不流畅（没有一次性对准）',
#     '03-10@19:03:50',
#     # '03-10@17:17:36_丢橘子不流畅（没有一次性对准）',
#     '03-10@18:52:56',
#     # '03-10@16:56:30_夹子打开时碰到了橘子',
#     '03-10@17:28:58',
#     '03-10@18:59:54',
#     '03-10@17:14:22'
# ]

# states = []
# for f in files:
#     eef_file = f'data/orange_in_bowl/{f}/follower_endpose'
#     gripper = f'data/orange_in_bowl/{f}/leader_gripper'

#     eefs = parser_endpose_from_stream(eef_file)
#     grippers = parser_gripper_from_stream(gripper)
    
#     temp = []

#     for eef, gripper in zip(eefs, grippers):
#         temp.append([
#             eef.end_pose.X_axis,
#             eef.end_pose.Y_axis,
#             eef.end_pose.Z_axis,
#             eef.end_pose.RX_axis,
#             eef.end_pose.RY_axis,
#             eef.end_pose.RZ_axis,
#             gripper.gripper_state.grippers_angle
#         ])
#     temp = np.array(temp)
#     states.append(temp)

# # states = np.array(states)
# # np.save('tmp/verify_data/data.np', states)
# pickle.dump(states, open('tmp/verify_data/data.npy.pickle', 'wb'))

# /home/robot/mzk_workspace/data_collect/tmp/verify_data/data.npy.pickle
# import pickle
# import numpy as np
# doc : List[np.ndarray] = pickle.load(open('/home/robot/mzk_workspace/data_collect/tmp/verify_data/data.npy.pickle', 'rb'))

import torch

doc = parser_endpose_from_stream('data/test/test_move/follower_endpose')
doc = list(doc)[::60]
res = []
for item in doc:
    res.append(torch.tensor([
        item.end_pose.X_axis,
        item.end_pose.Y_axis,
        item.end_pose.Z_axis,
        item.end_pose.RX_axis,
        item.end_pose.RY_axis,
        item.end_pose.RZ_axis,
    ]))

dist = [torch.sum(torch.abs(p - n)).item() for p, n in zip(res, res[1:])]
from rich import print

print(dist)
