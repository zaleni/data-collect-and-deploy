from data_sample_interface.utils import (
    parser_joint_from_stream,
    parser_endpose_from_stream,
    parser_gripper_from_stream,
)
import os
from typing import List, Tuple, Any
import bisect
from pathlib import Path
from rich import print
import json

SpanExtendFrameNum = 15

def _extract_timestamp_from_image_name(name):
    try:
        name_clean = name
        if name.endswith('.png'):
            name_clean = name[:-4]
        name_clean = name_clean.replace("_", ".")
        return float(name_clean)
    except Exception as e:
        return 0.0

def _select_indices_within_range(nums: List[List[float]], range_limit: float) -> Tuple[List[List[int]], List[List[float]]]:
    argmin = lambda l: min(zip(l, range(len(l))))[1]
    res_indices = []
    res_values = []
    
    list_count = [len(n) for n in nums]
    
    # 只要 RGB 都不为空就能跑，不再检查深度图
    if any(c == 0 for c in list_count):
        print(f"[Debug] 警告：参与对齐的 RGB 文件夹中存在空文件夹！长度: {list_count}")
        return [], []

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
            res_indices.append(list(indexes))
            res_values.append(values)
            for i in range(len(list_count)):
                indexes[i] += 1
        else:
            min_index = argmin(values)
            indexes[min_index] += 1

    return res_indices, res_values

def _find_nearest_item_indexes(times, anchors):
    selected_indices = set()
    res = []
    last_selected_idx = 0

    for anchor in anchors:
        if not isinstance(anchor, float):
            mean_anchor = sum(anchor) / len(anchor) # 动态计算均值
        else:
            mean_anchor = anchor
        pos = bisect.bisect_left(times, mean_anchor, lo=last_selected_idx)

        best_index = None
        best_cost = float("inf")

        for i in range(pos, len(times)):
            if i in selected_indices:
                continue
            if not isinstance(anchor, float):
                # 只计算有效维度的距离
                cost = sum(abs(times[i] - bi) for bi in anchor)
            else:
                cost = abs(times[i] - anchor)
            if cost < best_cost:
                best_cost = cost
                best_index = i
            else:
                 if cost > best_cost: 
                     break

        if best_index is not None:
            selected_indices.add(best_index)
            last_selected_idx = best_index + 1
        else:
            if pos < len(times) and pos not in selected_indices:
                 selected_indices.add(pos)
                 last_selected_idx = pos + 1

    res = list(selected_indices)
    res.sort()
    return res

def _prepare_image_data(image_names_list: List[List[str]]) -> Tuple[List[List[float]], List[List[str]]]:
    sorted_timestamps = []
    sorted_filenames = []

    for names in image_names_list:
        pairs = []
        for name in names:
            ts = _extract_timestamp_from_image_name(name)
            if ts > 0:
                pairs.append((ts, name))
        
        pairs.sort(key=lambda x: x[0])
        
        if pairs:
            ts_list, name_list = zip(*pairs)
            sorted_timestamps.append(list(ts_list))
            sorted_filenames.append(list(name_list))
        else:
            sorted_timestamps.append([])
            sorted_filenames.append([])
            
    return sorted_timestamps, sorted_filenames

def sync_images(save_folder):
    """
    修改版：只同步 front_color 和 wrist_color。
    忽略深度图，深度图路径将填充为 ""。
    """
    save_folder = Path(save_folder)
    print(f"[Debug] 正在同步(仅RGB): {save_folder}")
    
    try:
        f_color = os.listdir(save_folder / "img" / "front_color")
        w_color = os.listdir(save_folder / "img" / "wrist_color")
        # 深度图即使报错或为空也不影响
    except FileNotFoundError as e:
        print(f"[Error] RGB 文件夹缺失，无法同步: {e}")
        return []

    # 1. 仅预处理 RGB 数据
    img_timestamps, img_filenames = _prepare_image_data([f_color, w_color])

    # 2. 对齐 (仅基于 RGB)
    # 阈值 0.05s (50ms)
    selected_indices, selected_timestamps = _select_indices_within_range(img_timestamps, 0.05)
    
    print(f"[Debug] RGB同步结果: 找到 {len(selected_indices)} 帧")

    # 3. 构造结果：[RGB1, RGB2, "", ""]
    final_images = []
    for idx_tuple in selected_indices:
        row = [
            img_filenames[0][idx_tuple[0]], # Front RGB
            img_filenames[1][idx_tuple[1]], # Wrist RGB
            "", # Front Depth (忽略)
            ""  # Wrist Depth (忽略)
        ]
        final_images.append(row)

    return zip(selected_timestamps, final_images)

# ---------------------------------------------------------------------
# 下面的函数是给采集脚本用的，如果采集脚本也需要忽略深度，可以类似修改
# 但为了标注工具(data_anno)能跑通，上面的 sync_images 是关键
# ---------------------------------------------------------------------

def sync_data(joints, eefs, grippers, image_1_color_names, image_2_color_names, image_1_depth_names, image_2_depth_names, sampling_frequency=0.03):
    # 这里保持原逻辑，或者也改成只用前两个列表
    # 为了保险，这里也改为只对齐 RGB
    img_timestamps, img_filenames = _prepare_image_data([image_1_color_names, image_2_color_names])
    selected_indices, selected_timestamps = _select_indices_within_range(img_timestamps, sampling_frequency)
    
    final_images = []
    for idx_tuple in selected_indices:
        row = [
            img_filenames[0][idx_tuple[0]], 
            img_filenames[1][idx_tuple[1]], 
            "", # Depth 占位
            ""  # Depth 占位
        ]
        final_images.append(row)
        
    to_time_stamp = lambda x: x.time_stamp
    make_time_stamp = lambda x: list(map(to_time_stamp, x))
    joint_indexes, eef_indexes, gripper_indexes = [_find_nearest_item_indexes(make_time_stamp(item), selected_timestamps) for item in [joints, eefs, grippers]]
    
    select = lambda x, inds: [x[i] for i in inds]
    joints = select(joints, joint_indexes)
    eefs = select(eefs, eef_indexes)
    grippers = select(grippers, gripper_indexes)
    return zip(joints, eefs, grippers, final_images)

def organize_data_from_single_run(save_folder):
    save_folder = Path(save_folder)
    joints = list(parser_joint_from_stream(save_folder / "follower_joint"))
    eefs = list(parser_endpose_from_stream(save_folder / "follower_endpose"))
    grippers = list(parser_gripper_from_stream(save_folder / "follower_gripper"))
    for i in range(len(grippers)): grippers[i].time_stamp /= 1e9
    
    # 读取文件列表
    try:
        image_1_color_names = os.listdir(save_folder / "img" / "front_color")
        image_2_color_names = os.listdir(save_folder / "img" / "wrist_color")
    except:
        image_1_color_names = []
        image_2_color_names = []
        
    return sync_data(joints, eefs, grippers, image_1_color_names, image_2_color_names, [], [])

def sync_data_by_spans(save_folder):
    # 此函数读取已有的 json，不需要修改对齐逻辑，但需注意文件读取
    save_folder = Path(save_folder)
    anno = save_folder / "ano.json"
    if not anno.exists(): return []
    with open(anno, "r") as f: data = json.load(f)
    
    spans = data.get("spans", [])
    frames = data.get("frames", [])
    if not frames: return []

    joints = list(parser_joint_from_stream(save_folder / "follower_joint"))
    eefs = list(parser_endpose_from_stream(save_folder / "follower_endpose"))
    grippers = list(parser_gripper_from_stream(save_folder / "follower_gripper"))
    for i in range(len(grippers)): grippers[i].time_stamp /= 1e9

    res = []
    to_time_stamp = lambda x: x.time_stamp
    make_time_stamp = lambda x: list(map(to_time_stamp, x))
    
    for span in spans:
        start_index, end_index, annotation = (span["start_index"], span["end_index"], span["annotation"])
        if start_index >= len(frames): continue
        
        # 使用 frame 中记录的时间戳 (第5个元素，索引4)
        time_stamps = [frames[i][4] for i in range(start_index, min(end_index + SpanExtendFrameNum + 1, len(frames)))]
        
        joint_indexes, eef_indexes, gripper_indexes = [
            _find_nearest_item_indexes(make_time_stamp(item), time_stamps)
            for item in [joints, eefs, grippers]
        ]
        
        select = lambda x, inds: [x[i] for i in inds]
        selected_joints = select(joints, joint_indexes)
        selected_eefs = select(eefs, eef_indexes)
        selected_grippers = select(grippers, gripper_indexes)

        img_folder = save_folder / "img"
        img_file_paths = []
        for i in range(start_index, min(len(frames), end_index + SpanExtendFrameNum + 1)):
            # 即使 frames[i][2] 是空字符串，路径拼接也不会报错，只是文件不存在
            f_rgb = str(img_folder / "front_color" / frames[i][0])
            w_rgb = str(img_folder / "wrist_color" / frames[i][1])
            # 对于深度图，如果文件名为空，我们就不生成路径或者生成个 dummy
            f_depth = str(img_folder / "front_depth" / frames[i][2]) if frames[i][2] else ""
            w_depth = str(img_folder / "wrist_depth" / frames[i][3]) if frames[i][3] else ""
            
            img_file_paths.append([f_rgb, w_rgb, f_depth, w_depth])

        res.append((selected_joints, selected_eefs, selected_grippers, img_file_paths, annotation))
    return res

if __name__ == "__main__":
    # 测试
    print("Test mode")