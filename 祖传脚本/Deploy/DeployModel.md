# 模型部署指南

## 端口说明

| 端口号 | 模型 |
| -----  | -----| 
| 8001  | VLLM (pick snack) |
| 8009  | VLLM (sweep the table) |
| 8011  | VLLM (table clean) |
| 8000  | VLA (pick snack) |
| 8010  | VLA(table clean+sweep) |
| 8013  | LLM |
| 1145  | Web conttrol record audio|
| 44931  | Web control robotic arm |


***如果更改端口号，同时修改启动模型port参数以及gui/lib中(\*)_inference.py文件，如：[vla_inference.py](./gui_4_2/lib/vla_inference.py)，[vllm_inference.py](./gui_4_2/lib/vllm_inference.py)***

## LLM模型
- 使用LLaMA-Factor部署qwen2_5_7b_instruct模型，和标准流程一样没有特殊的。（没有微调，只是指定了系统prompt）
```bash
export CUDA_VISIBLE_DEVICES=0
proxy_on
conda activate vllm
API_PORT=8013 llamafactory-cli api /home/pc3/deploy/LLaMA-Factory/examples/inference/qwen2_5_7b_instruct.yaml
```

## VLLM模型

- 使用LLaMA-Factor部署微调后的paligemma
```bash
#三个vllM， pick snack 端口号:8001(两张图片)     sweep 端口号：8009（两张图片）， table clean 端口号8011(只接受一张图片)
# pick snack 对应一个 8000端口， sweep 对应 8009端口 ,table clean 对应8010端口
#主程序会通过vllm instruct 自动选取要使用的模型， 三种instruct:①"[sweep the table]" ② "[table clean]" ③不是以上两种的都默认为零食抓取

# snack 
export CUDA_VISIBLE_DEVICES=2
conda activate vllm
API_PORT=8001 llamafactory-cli api --model_name_or_path /home/pc3/deploy/vllm_model_ckpt/vllm_snack_0410 --template paligemma --infer_backend huggingface --trust_remote_code true

#sweep
export CUDA_VISIBLE_DEVICES=1
conda activate vllm
API_PORT=8009 llamafactory-cli api --model_name_or_path /home/pc3/deploy/vllm_model_ckpt/vllm_sweep_0413 --template paligemma --infer_backend huggingface --trust_remote_code true

#table clean
export CUDA_VISIBLE_DEVICES=3
conda activate vllm
API_PORT=8011 llamafactory-cli api --model_name_or_path /home/pc3/deploy/vllm_model_ckpt/vllm_clean_0412_v3 --template paligemma --infer_backend huggingface --trust_remote_code true
```
## VLA模型
- 部署VLA模型， **需要将--checkpoint_bucket 和 --config_name相对应， 训练checkpoint_bucket模型的数据集名称一定要在config中的和--config_name 相对应的trainconfig 的data项。**（使用新的数据集训练时才需要注意这个）  
config.py是指：/home/pc3/deploy/openpi/src/openpi/training/config.py  
数据集名称是指：/mnt/ckpts/magic/snack_serve_0402/10000/assets/datasets/SongLin-tp17435951900472827/ 中的 SongLin-tp17435951900472827
```bash
export CUDA_VISIBLE_DEVICES=2 #自行决定用那些卡
# snack
source /home/pc3/deploy/openpi/.venv/bin/activate #这pi激活环境的方式
source /home/pc3/deploy/Piper_ros/devel/setup.bash #增加与机械臂ros节点相关的导包路径
XLA_PYTHON_CLIENT_PREALLOCATE=false python /home/pc3/deploy/openpi/scripts_/deploy_server.py  --checkpoint_bucket /mnt/ckpts/magic/snack_serve_0412/22500 --config_name pi0_bmlm_joint_snack #默认端口8000

# table clean and sweep
export CUDA_VISIBLE_DEVICES=3
source /home/pc3/deploy/openpi/.venv/bin/activate #这pi激活环境的方式
source /home/pc3/deploy/Piper_ros/devel/setup.bash #增加与机械臂ros节点相关的导包路径
XLA_PYTHON_CLIENT_PREALLOCATE=false python /home/pc3/deploy/openpi/scripts_/deploy_server.py --port 8010 --checkpoint_bucket /mnt/ckpts/magic/table_cleaning_0411_sweep/15000 --config_name pi0_bmlm_joint_sweep_and_table_clean 
```
## TTS模型
- 使用cosyvoice作为TTS语音输出模型
- 启动后，语音输出会作为一个ROS节点一直运行，收到ROS消息后会自动tts语音播放
```bash
export CUDA_VISIBLE_DEVICES=1
conda activate cosyvoice
source /home/pc3/deploy/Piper_ros/devel/setup.bash
cd /home/pc3/deploy/CosyVoice
python chat.py
```

## YOLO检测
- yolo检测，GUI可视化
```bash
export CUDA_VISIBLE_DEVICES=0
conda activate mmyolo
source /home/pc3/deploy/Piper_ros/devel/setup.bash
cd /home/pc3/mmyolo/Deploy
python my_image_demo_wrist.py
```