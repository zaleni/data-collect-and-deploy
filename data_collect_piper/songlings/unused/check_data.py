import os
from pathlib import Path
from converting_utils import organize_data_from_single_run, _extract_timestamp_from_image_name

def check_all_data_folders():
    # 指定数据根目录
    root_path = "/home/robot/mzk_workspace/data_collect/data/SimplePickUp"
    root_path = Path(root_path)

    # 获取所有子文件夹
    data_folders = [f for f in root_path.iterdir() if f.is_dir()]
    
    # 遍历每个数据文件夹
    for folder in data_folders:
        print(f"\n正在处理文件夹: {folder}")
        try:
            # 获取同步后的数据
            u = list(organize_data_from_single_run(folder))
            # 按要求裁剪数据
            u = u[3:-3:3]
            
            print(f"数据长度: {len(u)}")
            print(f"时间跨度: {u[-1][0].time_stamp - u[0][0].time_stamp}")
            
            # 打印每组数据的时间戳
            for j, e, g, (i1, i2, d1, d2) in u:
                print(f'joint  : {j.time_stamp}')
                print(f'eef    : {e.time_stamp}')
                print(f'gripper: {g.time_stamp}')
                print(f'i1     : {_extract_timestamp_from_image_name(i1)}')
                print(f'i2     : {_extract_timestamp_from_image_name(i2)}')
                print(f'd1     : {_extract_timestamp_from_image_name(d1)}')
                print(f'd2     : {_extract_timestamp_from_image_name(d2)}')
                
                user_input = input('按回车继续，输入q退出:')
                if user_input.lower() == 'q':
                    return
                
        except Exception as e:
            print(f"处理文件夹 {folder} 时出错: {str(e)}")
            continue

if __name__ == '__main__':
    check_all_data_folders() 