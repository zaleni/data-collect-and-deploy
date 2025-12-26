import sys

# import datasets

from utils import syn_data

import shutil

from lerobot.common.datasets.lerobot_dataset import HF_LEROBOT_HOME
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

# import tensorflow_datasets as tfds
# import tyro
import os

def main():
    # Clean up any existing dataset in the output directory
    output_path = ''

    # Create LeRobot dataset, define features to store
    # OpenPi assumes that proprio is stored in `state` and actions in `action`
    # LeRobot assumes that dtype of image data is `image`
    dataset = LeRobotDataset.create(
        repo_id='SongLinPickUpCup',
        robot_type="SongLing",
        fps=10,
        features={
            "img_1_color": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "img_1_depth": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "img_2_color": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "img_2_depth": {
                "dtype": "image",
                "shape": (360, 640, 3),
                "names": ["height", "width", "channel"],
            },
            "joint": {
                "dtype": "int32",
                "shape": (6,),
                "names": ["joint"],
            },
            "endpose": {
                "dtype": "int32",
                "shape": (6,),
                "names": ["endpose"],
            },
            "gripper": {
                "dtype": "int32",
                "shape": (1,),
                "names": ["gripper"],
            },
            "task": {
                "dtype": "string",
                "shape": (1,),
                "names": ["task"],
            },
        },
        # image_writer_threads=10,
        # image_writer_processes=5,
    )

    base_path = "/home/robot/mzk_workspace/data_collect/data"
    # for item in os.listdir(base_path):
    item = "03-04@11:07:27"
    item_path = "/home/robot/mzk_workspace/data_collect/data/03-04@11:07:27"
    dic = syn_data(item_path)
    # current_episode_index = dataset.meta.total_episodes
    for step in dic:

        dataset.add_frame(
            {
                "img_1_color": step["images"][0],
                "img_1_depth": step["images"][1],
                "img_2_color": step["images"][2],
                "img_2_depth": step["images"][3],
                "joint": step["joint"],
                "endpose": step["endpose"],
                "gripper": step["gripper"],
                "task": item,
                # "index": global_index,
                # "episode_index": current_episode_index,
                # "timestamp": timestamp,
                # "task_index": task_index,
            }
        )
    print("done")
    # dataset.save_episode(task=step["language_instruction"].decode())
    dataset.save_episode(task=item)
    dataset.consolidate(run_compute_stats=False)


if __name__ == "__main__":
    # tyro.cli(main)
    main()
