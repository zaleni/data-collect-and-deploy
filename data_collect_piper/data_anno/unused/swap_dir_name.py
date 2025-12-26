from pathlib import Path
import json 
import os
from rich import print

base_dir = Path('data/ano')

def reorder_json(json_content):
    # original order of a frame : color_front, color_wrist, depth_front, depth_wrist, mean
    # new order of a frame : color_wrist, color_front, depth_wrist, depth_front, mean
    json_content['frames'] = [
        [frame[1], frame[0], frame[3], frame[2], frame[4]]
        for frame in json_content['frames']
    ]
    return json_content

def swap_directories(dir_a, dir_b):
    # 检查目录是否存在
    if not os.path.isdir(dir_a):
        raise FileNotFoundError(f"目录 '{dir_a}' 不存在。")
    if not os.path.isdir(dir_b):
        raise FileNotFoundError(f"目录 '{dir_b}' 不存在。")
    
    # 生成唯一的临时目录名
    temp_dir = f"temp_swap"
    while os.path.exists(temp_dir):
        temp_dir = f"temp_swap"
    
    try:
        # 将A重命名为临时目录
        os.rename(dir_a, temp_dir)
        # 将B重命名为A
        os.rename(dir_b, dir_a)
        # 将临时目录重命名为B
        os.rename(temp_dir, dir_b)
        print(f"成功交换目录 {dir_a} 和 {dir_b}。")
    except Exception as e:
        print(f"错误发生: {e}")
        print("部分操作可能已完成，请检查以下目录状态:")
        print(f"临时目录: {temp_dir}")
        print(f"当前 {dir_a} 是否存在: {os.path.exists(dir_a)}")
        print(f"当前 {dir_b} 是否存在: {os.path.exists(dir_b)}")
        print("请手动处理目录重命名。")
        raise

def check_if_inversed(dir_name):
    anno = dir_name / 'ano.json'
    doc = json.load(open(anno))
    frames = doc['frames']
    
    front_color_files = os.listdir(dir_name / 'img' / 'front_color')
    wrist_color_files = os.listdir(dir_name / 'img' / 'wrist_color')
    front_color_files = set(front_color_files)
    wrist_color_files = set(wrist_color_files)
    
    is_swapped = False
    for front_color, wrist_color, _, _, _ in frames:
        if front_color not in front_color_files or \
            wrist_color not in wrist_color_files:
                is_swapped = True
                break
    
    if not is_swapped:
        return False
    
    if is_swapped:
        for front_color, wrist_color, _, _, _ in frames:
            if front_color not in wrist_color_files or \
                wrist_color not in front_color_files:
                    raise Exception('ERROR')
    return True

for task_series in base_dir.iterdir():
    for task_dir in task_series.iterdir():
        is_reversed = check_if_inversed(task_dir)
        if is_reversed:
            print(f'{is_reversed} : {task_dir}')
            doc = json.load(open(task_dir / 'ano.json'))
            doc = reorder_json(doc)
            with open(task_dir / 'ano.json', 'w') as f:
                json.dump(doc, f, indent=2)
        # # rename the directory
        # dir_front_color = task_dir / 'img' / 'front_color'
        # dir_front_depth = task_dir / 'img' / 'front_depth'
        # dir_wrist_color = task_dir / 'img' / 'wrist_color'
        # dir_wrist_depth = task_dir / 'img' / 'wrist_depth'
        
        # swap_directories(dir_front_color, dir_wrist_color)
        # swap_directories(dir_front_depth, dir_wrist_depth)