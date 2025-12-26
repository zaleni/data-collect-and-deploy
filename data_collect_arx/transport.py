import shutil
import os

# 源文件夹列表（可以手动填写，也可以用tkinter等方式弹窗选择）
source_folders = [
    '/home/go2/ARX_X5/00-sh',
    '/home/go2/ARX_X5/ARX_CAN',
    '/home/go2/ARX_X5/ARX_VR',
    '/home/go2/ARX_X5/ARX_VR_SDK',
    '/home/go2/ARX_X5/inference',
    '/home/go2/ARX_X5/py',
    '/home/go2/ARX_X5/ROS',
    '/home/go2/ARX_X5/ROS2',
    '/home/go2/ARX_X5/ros2_ws',
    '/home/go2/ARX_X5/run'
]

# 目标目录
target_dir = '/home/pc3/backup/data_collect_arx/'

for folder in source_folders:
    folder_name = os.path.basename(folder)
    dest_path = os.path.join(target_dir, folder_name)
    shutil.copytree(folder, dest_path)
    print(f'已复制 {folder} 到 {dest_path}')