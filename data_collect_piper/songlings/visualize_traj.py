import mediapy
from PIL import Image
from glob import glob
import numpy as np
from tqdm import tqdm
from pathlib import Path

data_path = "/home/pc3/data_collect/songlings/data/ano/clean_remake/04-07AAA16:19_异动"

frame_list = glob(f"{data_path}/img/front_color/*")
frame_list.sort()

video_frames = []
for item in tqdm(frame_list):
    img = Image.open(item)
    # print(img.size)
    img = np.array(img)
    
    video_frames.append(img)

mediapy.write_video(Path("./test.mp4"), video_frames, fps=10)