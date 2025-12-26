import json
import os
from tqdm import tqdm
import copy
from pathlib import Path
import shutil

data_root = "clean_remake"
output_folder = Path("tmp_vlm/bmlm_demo_v1")
StrangePrefix = Path("<QwQ>")

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
    for sample in data.get("spans", []):

        if not sample.get("used_for_vlm", False):
            continue

        for i in range(sample["start_index"], sample["end_index"], 15):

            high_level_instruct = "table clean".lower()
            low_level_instruct = sample["annotation"].lower()

            if low_level_instruct == "transparent snack wrapper":
                print(json_path)

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
                            "content": "<image> " + high_level_instruct,
                            "role": "user",
                        },
                        {"content": low_level_instruct, "role": "assistant"},
                    ],
                    "images": [img_path_wrist_path],
                }
            )

    shift = True

    if shift:
        temp_deep = copy.deepcopy(temp)
        shift_data = []
        shift_num = int(50 // 15)

        for idx in range(shift_num, len(temp_deep)):
            temp_deep[idx]["images"] = temp[idx - shift_num]["images"]
            shift_data.append(temp_deep[idx])

        if len(shift_data) == 0:
            return paligemma

        if "return to" not in shift_data[-1]["messages"][-1]["content"]:
            for k in range(idx - shift_num + 1, len(temp)):
                shift_data.append(
                    {
                        "messages": [
                            {
                                "content": "<image> " + high_level_instruct,
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

    return paligemma


def main():
    all_data = []

    for folder_name in tqdm(os.listdir(data_root)):
        # if "3-17@" in folder_name: # "3-20@" not in folder_name and "3-19@16:" not in folder_name and "3-19@15:49:53" not in folder_name and "3-19@" not in folder_name:
        folder_path = os.path.join(data_root, folder_name)
        if os.path.isdir(folder_path):
            all_data.extend(process_folder(folder_path))

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
        # front_image = item["images"][1]

        new_wrist_image = img_folder / f"{str.rjust(str(counter), 8, '0')}_wrist.png"
        new_front_image = img_folder / f"{str.rjust(str(counter), 8, '0')}_front.png"

        shutil.copy(wrist_image, new_wrist_image)
        # shutil.copy(front_image, new_front_image)
        counter += 1

        item["images"] = [
            str(StrangePrefix / str(new_wrist_image.name)),
            # str(StrangePrefix / str(new_front_image.name)),
        ]
    print(f"Copied images to {img_folder}")

    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"Updated image paths in {output_file}")


if __name__ == "__main__":
    main()


# import json
# from collections import Counter

# # 假设你的 JSON 文件名为 data.json
# with open("/HOME/uestc_jksong/uestc_jksong_1/zhanghaonan/code/LLaMA-Factory/data/bmlm_demo_v14.json", "r") as f:
#     data_list = json.load(f)

# # 要统计的关键词
# keywords = ['return', 'put', 'dump', 'move', 'pick']
# counter = Counter()

# # 遍历每个数据项，仅统计 messages[1]['content']
# for item in data_list:
#     messages = item.get("messages", [])
#     if len(messages) > 1:  # 确保有第二个元素
#         content = messages[1].get("content", "").lower()
#         for word in keywords:
#             counter[word] += content.count(word)

# # 输出统计结果
# print(dict(counter))
