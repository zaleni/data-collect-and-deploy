import os
from pathlib import Path
import tqdm 

base_dir = Path('data/stage2_bk')

def do(img_folder):
    for img_name in os.listdir(img_folder):
        time_stamp = img_name[:-4].replace('_', '.')
        time_stamp = float(time_stamp)
        time_stamp = str(time_stamp).ljust(20, '0')
        time_stamp = time_stamp.replace('.', '_')
        os.rename(img_folder / img_name, img_folder / f'{time_stamp}.png')

for save in os.listdir(base_dir):
    record_base_dir = base_dir / save
    for record in tqdm.tqdm(os.listdir(record_base_dir)):
        do(record_base_dir / record / 'img' / 'front_color')
        do(record_base_dir / record / 'img' / 'front_depth')
        do(record_base_dir / record / 'img' / 'wrist_color')
        do(record_base_dir / record / 'img' / 'wrist_depth')
