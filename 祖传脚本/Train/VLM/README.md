# VLM-PaliGemma2 训练指南

本文档介绍基于Google的[Paligemma2-3B](https://huggingface.co/blog/paligemma2)模型进行无界大模型训练的注意事项和配置方法，代码基于[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)框架。

## 目录
- 环境准备
- 数据构造
- 模型训练

### ⚠️ 在广州服务器上需要做的事情
### 环境准备
```bash
cd MagicBot/Train/VLM/LLaMA-Factory
pip install -e ".[torch,metrics]"
```

Extra dependencies available: torch, torch-npu, metrics, deepspeed, liger-kernel, bitsandbytes, hqq, eetq, gptq, awq, aqlm, vllm, sglang, galore, apollo, badam, adam-mini, qwen, minicpm_v, modelscope, openmind, swanlab, quality

> Use `pip install --no-deps -e .` to resolve package conflicts.

### ⚠️ 在pc3上需要做的事情
### 数据构造
#### 训练数据格式遵循ShareGPT Format，具体可以参考👇

- [Example dataset](LLaMA-Factory/data/mllm_demo.json)

每个数据样本需要包含一个名为 `images` 的list，其中存放输入图像的路径。

图像的数量应与对话中的 `<image>` 标记数量完全一致。

- [order food]和[sweep the table]是双视角（wrist+front）

```json
[
    {
        "messages": [
            {
                "content": "<image> <image> [order food] obj_label 或者 [sweep the table]",
                "role": "user"
            },
            {
                "content": "pick up the plate",
                "role": "assistant"
            }
        ],
        "images": [
            "<QwQ>/00000000_wrist.png",
            "<QwQ>/00000000_front.png"
        ]
    },
]
```

- [table clean]是单视角（wrist）

```json
[
    {
        "messages": [
            {
                "content": "<image> [table clean]",
                "role": "user"
            },
            {
                "content": "pick up the plate",
                "role": "assistant"
            }
        ],
        "images": [
            "<QwQ>/00000000_wrist.png",
        ]
    },
]
```

为了生成上述的json数据，对应任务运行:
```python
cd Train/VLM/LLaMA-Factory/data/magic_bot
python build_vlm_snack.py
// python build_vlm_clean.py
// python build_vlm_sweep.py
```
.py中的data_root变量是数据采集组采集完后的数据文件夹

### ⚠️ 在pc3上需要做的事情
把build好的数据文件夹压缩打包
```bash
tar -cvf pc3上指定的压缩路径路径/文件.tar   pc3上文件的存放路径/文件
```
然后传输到广州服务器上
```bash
scp \
 -o StrictHostKeyChecking=no \
 -o UserKnownHostsFile=/dev/null \
 -P 8001 \
 -i /home/pc3/data_collect/tmp/uestc_jksong_1.id \
 -r \
 /home/pc3/data_collect/openpi/tmp_vlm/bmlm_snack_v4.tar \  这是pc3上压缩好的文件路径
 uestc_jksong_1@121.46.19.4:/HOME/uestc_jksong/uestc_jksong_1/zhanghaonan/code/LLaMA-Factory/bmlm_vlm_data/robot_data_3/data && \ 这是广州服务器指定要存放的路径，最好放在HDD_POLL下面，建一个自己名字的文件夹
```

### ⚠️ 在广州服务器上需要做的事情
解压缩传输过来的文件
```bash
tar -xvf 广州服务器上压缩文件的存放路径/文件名.tar
```

把解压缩文件里面的vlm.json数据中的图像符号"\<QwQ\>"替换成正确的图像路径，然后放到Train/VLM/LLaMA-Factory/data路径下，并在Train/VLM/LLaMA-Factory/data/dataset_info.json中添加数据信息
```json
  "vlm": {
    "file_name": "vlm.json",
    "formatting": "sharegpt",
    "columns": {
      "messages": "messages",
      "images": "images"
    },
    "tags": {
      "role_tag": "role",
      "content_tag": "content",
      "user_tag": "user",
      "assistant_tag": "assistant"
    }
  }
```
### 模型训练

模型配置文件在
```
Train/VLM/LLaMA-Factory/examples/train_full/paligemma_full_sft.yaml
```
需要修改的基础地方分别是
```
model_name_or_path: 原始的预训练模型权重路径，需要用huggingface下载下来
dataset: 数据集名，如果是vlm.json的数据，则这里填入vlm
output_dir: 指定模型保存路径
```
然后运行:
```bash
run_vlm.sh
```
### 模型权重传输
把模型的数据存在一个文件夹下，然后传到pc3上用于部署调用
```bash
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 8001 -i /home/pc3/data_collect/tmp/uestc_jksong_1.id -r uestc_jksong_1@121.46.19.4:/HOME/uestc_jksong/uestc_jksong_1/zhanghaonan/code/LLaMA-Factory/saves/paligemma-3b-224/full/bmlm_demo_v9/vllm_0403 /home/pc3/deploy/vllm_model_ckpt
```
