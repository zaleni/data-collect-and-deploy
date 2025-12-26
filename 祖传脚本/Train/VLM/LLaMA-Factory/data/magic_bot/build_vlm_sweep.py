import json
import os
from tqdm import tqdm
import copy
from pathlib import Path
import shutil

data_root = "dir_buffer/sweep"
output_folder = Path("vlm_clean/bmlm_sweep")
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
        # assert len(data["frames"]) == len(data["spans"])
        # print(folder_path, len(data["frames"]), len(data["spans"]))
    except:
        print("Failed to load JSON file.")
        return paligemma

    temp = []

    downsampling_ratio = 15

    for sample in data.get("spans", []):

        if not sample.get("used_for_vlm", False):
            continue

        for i in range(sample["start_index"], sample["end_index"], downsampling_ratio):

            high_level_instruct = "[sweep the table]".lower()
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
    if len(temp) == 0:
        print("empety file {}".format(folder_path))
        return paligemma

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

    return paligemma


def main():
    all_data = []

    for folder_name in tqdm(os.listdir(data_root)):
        # if "04-10AAA04:26:53" not in folder_name:
        #     continue
        folder_path = os.path.join(data_root, folder_name)
        if os.path.isdir(folder_path):
            all_data.extend(process_folder(folder_path))
        # print(folder_name)
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
                "content": "<image> <image> [sweep the table]",
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
