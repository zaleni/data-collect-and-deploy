import json
import os
from tqdm import tqdm
import copy
from pathlib import Path
import shutil
import re
import random

data_root = "dir_buffer/snack"
output_folder = Path("vlm_clean/bmlm_snack")
StrangePrefix = Path("<QwQ>")

def obj_extractor(task, first_instruction=None):

    # 目标物品列表
    TARGET_OBJECTS = [
        "coffee",
        "cookie",
        "tea",
        "milk",
        "popcorn",
        "water",
        "gum",
        "chocolate",
        "cola",
        "oreo",
        "biscuits",
    ]

    OBJECT_PATTERN = r"\b(" + "|".join(TARGET_OBJECTS) + r")\b"

    """
    从任务描述中提取目标物品
    
    :param task: str, 任务描述
    :return: list, 提取的目标物品
    """
    if (
        task == "pick up the plate"
        or task == "put the plate on the table"
        or task == "push the plate closer to the customer"
    ):
        return "[order food] plate"

    if (
        task == "return to the initial state"
        and first_instruction == "return to the initial state"
    ):
        # print("[order food] " + random.sample(TARGET_OBJECTS, 1)[0])
        return "[order food] " + random.sample(TARGET_OBJECTS, 1)[0]

    if task == "return to the initial state" and first_instruction is not None:
        return obj_extractor(first_instruction)

    matches = re.findall(OBJECT_PATTERN, task.lower())

    if len(list(set(matches))) == 1:
        return "[order food] " + str(list(set(matches))[0])

    return task


def process_folder(folder_path):
    json_path = os.path.join(folder_path, "ano.json")
    if not os.path.exists(json_path):
        print("ano.json not exist!")
        return []

    paligemma = []
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except:
        return paligemma

    temp = []

    ood_task = []
    print(folder_path)

    if len(data.get("spans", [])) == 0:
        return None, None

    first_instruction = data.get("spans", [])[0].get("annotation", "").lower()

    for sample in data.get("spans", []):

        instruction = sample.get("annotation", "").lower()

        vlm_input = obj_extractor(instruction, first_instruction)

        if vlm_input == "<image> <image> [order food]":
            print(instruction, first_instruction)

        if "[order food]" not in vlm_input:
            ood_task.append(instruction)

        if not sample.get("used_for_vlm", False):
            continue

        downsampling_ratio = 15
        for i in range(sample["start_index"], sample["end_index"], downsampling_ratio):

            high_level_instruct = vlm_input
            low_level_instruct = sample["annotation"].lower()

            img_path_wrist_path = os.path.join(
                folder_path, "img", "wrist_color", data["frames"][i][1]
            )
            img_path_front_path = os.path.join(
                folder_path, "img", "front_color", data["frames"][i][0]
            )

            temp.append(
                {
                    "messages": [
                        {
                            "content": "<image> <image> " + high_level_instruct,
                            "role": "user",
                        },
                        {"content": low_level_instruct, "role": "assistant"},
                    ],
                    "images": [img_path_wrist_path, img_path_front_path],
                }
            )

    shift = True
    shift_ratio = 100
    if shift:
        temp_deep = copy.deepcopy(temp)
        shift_data = []
        shift_num = int(shift_ratio // downsampling_ratio)

        for idx in range(shift_num, len(temp_deep)):
            temp_deep[idx]["images"] = temp[idx - shift_num]["images"]
            shift_data.append(temp_deep[idx])

        if len(shift_data) == 0:
            return paligemma

        last_instruct = shift_data[-1]["messages"][0]["content"]
        last_response = shift_data[-1]["messages"][-1]["content"]
        if "return to" not in last_response:
            for k in range(idx - shift_num + 1, len(temp)):
                shift_data.append(
                    {
                        "messages": [
                            {
                                "content": last_instruct,
                                "role": "user",
                            },
                            {
                                "content": "return to the initial state",
                                "role": "assistant",
                            },
                        ],
                        "images": temp[k]["images"],
                    }
                )
        paligemma.extend(shift_data)
    else:
        paligemma.extend(temp)

    return paligemma, ood_task


def main():
    all_data = []
    all_ood_task = []

    for folder_name in tqdm(os.listdir(data_root)):
        # if "3-17@" in folder_name: # "3-20@" not in folder_name and "3-19@16:" not in folder_name and "3-19@15:49:53" not in folder_name and "3-19@" not in folder_name:
        folder_path = os.path.join(data_root, folder_name)
        if os.path.isdir(folder_path):
            sss, ood_task = process_folder(folder_path)
            if sss is None:
                print(f"Skipping folder {folder_path} due to empty data.")
                continue
            all_data.extend(sss)
            all_ood_task.extend(ood_task)
            # all_data.extend(process_folder(folder_path))
    print("ood_task:", set(all_ood_task))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file = os.path.join(output_folder, "vlm_data.json")
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"Processed {len(all_data)} samples. Output saved to {output_folder}")

    # Copy the images to the output folder
    img_folder = output_folder / "images"
    if not img_folder.exists():
        img_folder.mkdir(parents=True, exist_ok=True)

    """
    {
        "messages": [
            {
                "content": "<image> <image> table clean",
                "role": "user"
            },
            {
                "content": "pick up the empty water bottle",
                "role": "assistant"
            }
        ],
        "images": [
            "temp_vlm/04-07AAA17:05/img/wrist_color/1744016755_340741900.png",
            "temp_vlm/04-07AAA17:05/img/front_color/1744016755_338861000.png"
        ]
    },
    """

    counter = 0
    for item in tqdm(all_data):
        wrist_image = item["images"][0]
        front_image = item["images"][1]

        new_wrist_image = img_folder / f"{str.rjust(str(counter), 8, '0')}_wrist.png"
        new_front_image = img_folder / f"{str.rjust(str(counter), 8, '0')}_front.png"

        shutil.copy(wrist_image, new_wrist_image)
        shutil.copy(front_image, new_front_image)
        counter += 1

        item["images"] = [
            str(StrangePrefix / str(new_wrist_image.name)),
            str(StrangePrefix / str(new_front_image.name)),
        ]
    print(f"Copied images to {img_folder}")

    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"Updated image paths in {output_file}")


if __name__ == "__main__":
    main()
