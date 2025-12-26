from data_sample_interface.utils import (
    parser_joint_from_stream,
    parser_endpose_from_stream,
    parser_gripper_from_stream,
)
import os
from typing import List
import bisect
from pathlib import Path
from rich import print
import json


"""
    从实际的情况来看，机械臂的数据采集速率为200~600HZ，并且开始时间和结束之间与图像采集的开始时间和结束时间相近，可以完全覆盖图像的时间戳分布
    所以只需要对图像进行对齐就行，然后从机械臂里面找相近的数据就行
"""

SpanExtendFrameNum = 15  # 每个span的前后扩展帧数


def _extract_timestamp_from_image_name(name):
    """
    从图像文件名中提取时间戳，该函数是下面那个函数的反函数
    id = _extract_timestamp_from_image_name . _format_image_names_make
    """
    name = name[:-4].replace("_", ".")
    time_stamp = float(name)
    return time_stamp


def _format_image_names_make(time_stamp):
    """
    根据时间戳生成对应的图像名，该函数是上面那个函数的反函数
    id = _format_image_names_make . _extract_timestamp_from_image_name
    """
    return f'{str(time_stamp).replace(".", "_").ljust(20, "0")}.png'


def _format_image_names(name_list: List[List[float]]):
    return [list(map(_format_image_names_make, item)) for item in name_list]


def _select_items_within_range(nums: List[List[float]], range_limit: float):
    argmin = lambda l: min(zip(l, range(len(l))))[1]

    res = []
    list_count = [len(n) for n in nums]
    indexes = [0 for _ in list_count]
    while True:
        stop = False
        for i, c in zip(indexes, list_count):
            if i >= c:
                stop = True
                break
        if stop:
            break

        values = [num[i] for i, num in zip(indexes, nums)]
        if max(values) - min(values) < range_limit:
            res.append(values)
            for i in range(len(list_count)):
                indexes[i] += 1
        else:
            min_index = argmin(values)
            indexes[min_index] += 1

    return res


def _find_nearest_item_indexes(times, anchors):
    selected_indices = set()  # 存储已选索引，确保选取不同的元素
    res = []
    last_selected_idx = 0  # 记录上一次选择的索引，初始化为 0

    for anchor in anchors:
        if not isinstance(anchor, float):
            mean_anchor = sum(anchor) / 4  # 计算当前元组 b 的均值
        else:
            mean_anchor = anchor
        pos = bisect.bisect_left(
            times, mean_anchor, lo=last_selected_idx
        )  # 仅从 last_selected_idx 之后查找

        # 在 s 附近寻找未被选择的元素
        best_index = None
        best_cost = float("inf")

        # 向右搜索，确保索引递增
        for i in range(pos, len(times)):
            if i in selected_indices:
                continue
            if not isinstance(anchor, float):
                cost = sum(abs(times[i] - bi) for bi in anchor)
            else:
                cost = abs(times[i] - anchor)
            if cost < best_cost:
                best_cost = cost
                best_index = i
            break  # 选到一个合适的就退出

        # 记录选择的索引
        if best_index is not None:
            selected_indices.add(best_index)
            last_selected_idx = best_index + 1  # 记录上一次选择的位置

    res = list(selected_indices)
    res.sort()
    return res


def sync_data(
    joints,
    eefs,
    grippers,
    image_1_color_names,
    image_2_color_names,
    image_1_depth_names,
    image_2_depth_names,
    sampling_frequency=0.03,
):
    make = lambda x: list(sorted(map(_extract_timestamp_from_image_name, x)))
    img_time_stamp = [
        make(item)
        for item in [
            image_1_color_names,
            image_2_color_names,
            image_1_depth_names,
            image_2_depth_names,
        ]
    ]

    img_time_stamp = _select_items_within_range(img_time_stamp, sampling_frequency)

    to_time_stamp = lambda x: x.time_stamp
    make_time_stamp = lambda x: list(map(to_time_stamp, x))
    joint_indexes, eef_indexes, gripper_indexes = [
        _find_nearest_item_indexes(make_time_stamp(item), img_time_stamp)
        for item in [joints, eefs, grippers]
    ]

    select = lambda x, inds: [x[i] for i in inds]
    joints = select(joints, joint_indexes)
    eefs = select(eefs, eef_indexes)
    grippers = select(grippers, gripper_indexes)

    images = _format_image_names(img_time_stamp)
    return zip(joints, eefs, grippers, images)


def organize_data_from_single_run(save_folder):
    """
    从一个文件夹下读取并按照30Hz同步数据，此处的文件夹即先前实验保存的文件夹
    返回一个迭代器，可通过
        for joint, eef, gripper, (img1_color_path, img2_color_path, depth1_path, depth2_path) in xxx取出
    """
    save_folder = Path(save_folder)

    joints = list(parser_joint_from_stream(save_folder / "follower_joint"))
    eefs = list(parser_endpose_from_stream(save_folder / "follower_endpose"))
    grippers = list(parser_gripper_from_stream(save_folder / "follower_gripper"))

    for i in range(len(grippers)):
        grippers[i].time_stamp /= 1e9

    image_1_color_names = os.listdir(save_folder / "img" / "front_color")
    image_2_color_names = os.listdir(save_folder / "img" / "wrist_color")
    image_1_depth_names = os.listdir(save_folder / "img" / "front_depth")
    image_2_depth_names = os.listdir(save_folder / "img" / "wrist_depth")

    res = sync_data(
        joints,
        eefs,
        grippers,
        image_1_color_names,
        image_2_color_names,
        image_1_depth_names,
        image_2_depth_names,
    )
    return res


def sync_images(save_folder):
    save_folder = Path(save_folder)
    image_1_color_names = os.listdir(save_folder / "img" / "front_color")
    image_2_color_names = os.listdir(save_folder / "img" / "wrist_color")
    image_1_depth_names = os.listdir(save_folder / "img" / "front_depth")
    image_2_depth_names = os.listdir(save_folder / "img" / "wrist_depth")

    make = lambda x: list(sorted(map(_extract_timestamp_from_image_name, x)))
    img_time_stamp = [
        make(item)
        for item in [
            image_1_color_names,
            image_2_color_names,
            image_1_depth_names,
            image_2_depth_names,
        ]
    ]

    img_time_stamp = _select_items_within_range(img_time_stamp, 0.03)
    images = _format_image_names(img_time_stamp)
    # res = images
    # res.append(img_time_stamp)
    return zip(img_time_stamp, images)


def sync_data_by_spans(save_folder):
    save_folder = Path(save_folder)
    anno = save_folder / "ano.json"
    with open(anno, "r") as f:
        data = json.load(f)
    spans = data["spans"]
    frames = data["frames"]
    joints = list(parser_joint_from_stream(save_folder / "follower_joint"))
    eefs = list(parser_endpose_from_stream(save_folder / "follower_endpose"))
    grippers = list(parser_gripper_from_stream(save_folder / "follower_gripper"))
    for i in range(len(grippers)):
        grippers[i].time_stamp /= 1e9

    res = []
    to_time_stamp = lambda x: x.time_stamp
    make_time_stamp = lambda x: list(map(to_time_stamp, x))
    for span in spans:
        start_index, end_index, annotation = (
            span["start_index"],
            span["end_index"],
            span["annotation"],
        )
        time_stamps = [
            frames[i][4]
            for i in range(
                start_index, min(end_index + SpanExtendFrameNum + 1, len(frames))
            )
        ]

        joint_indexes, eef_indexes, gripper_indexes = [
            _find_nearest_item_indexes(make_time_stamp(item), time_stamps)
            for item in [joints, eefs, grippers]
        ]

        select = lambda x, inds: [x[i] for i in inds]
        selected_joints = select(joints, joint_indexes)
        selected_eefs = select(eefs, eef_indexes)
        selected_grippers = select(grippers, gripper_indexes)

        img_folder = save_folder / "img"
        img_file_paths = [
            [
                str(img_folder / "front_color" / frames[i][0]),
                str(img_folder / "wrist_color" / frames[i][1]),
                str(img_folder / "front_depth" / frames[i][2]),
                str(img_folder / "wrist_depth" / frames[i][3]),
            ]
            for i in range(
                start_index, min(len(frames), end_index + SpanExtendFrameNum + 1)
            )
        ]
        res.append(
            (
                selected_joints,
                selected_eefs,
                selected_grippers,
                img_file_paths,
                annotation,
            )
        )
    return res


if __name__ == "__main__":

    u= list(organize_data_from_single_run("/home/pc3/data_collect/songlings/data/tmp/1/10-17AAA12:10:01"))
    print(len(u))
    # u = list(sync_images("/home/pc3/data_collect/songlings/data/tmp/1/10-17AAA12:10:01"))
    # # u = u[3:-3:3]
    # print(len(u))
    # # print(u[-1][0].time_stamp - u[0][0].time_stamp)
    # for t, (i1, i2, d1, d2) in u:
    #     # print(f'joint  : {j.time_stamp}')
    #     # print(f'eef    : {e.time_stamp}')
    #     # # print(f'gripper: {g.time_stamp}')
    #     print(f"time   : {t}")
    #     print(f"i1     : imgs/front_color/{(i1)}")
    #     print(f"i2     : imgs/wrist_color/{(i2)}")
    #     print(f"d1     : imgs/front_depth/{(d1)}")
    #     print(f"d2     : imgs/wrist_depth/{(d2)}")
    #     # print(i1)
    #     print(f"----------------------------------------------------")
    #     input(":")
