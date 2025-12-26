# ⭐QuickStart

## 新开一个窗口 启动主节点， 一台机器只能启动一个
```bash
roscore
```

## 新开一个窗口启动摄像机节点
```bash
conda activate deploy
source /home/pc3/deploy/tmp/OrbbecSDK_develop/orbbec_ws/devel/setup.bash 
roslaunch orbbec_camera multi_camera.launch
```

## 新开一个窗口，启动执行动作的节点
### 查看can设备是否激活成功
```bash
cd /home/pc3/deploy/Piper_ros
bash can_activate.sh
```
### 运行节点
```bash
cd /home/pc3/deploy/gui
source /home/pc3/deploy/Piper_ros/devel/setup.bash
conda activate deploy
roslaunch piper start_single_piper.launch can_port:=can0 auto_enable:=true
```

## 新开一个窗口启动LLM
```bash
export CUDA_VISIBLE_DEVICES=0
proxy_on
conda activate vllm
API_PORT=8013 llamafactory-cli api /home/pc3/deploy/LLaMA-Factory/examples/inference/qwen2_5_7b_instruct.yaml
```

## 新开一个窗口，启动大脑VLM（启动一个就可以， 也可多个同时启动）
```bash
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


## 新开一个窗口 启动小脑VLA（启动一个就可以， 也可多个同时启动）
```bash

# snack
export CUDA_VISIBLE_DEVICES=2
source /home/pc3/deploy/openpi/.venv/bin/activate
XLA_PYTHON_CLIENT_PREALLOCATE=false python /home/pc3/deploy/openpi/scripts_/deploy_server.py  --checkpoint_bucket /mnt/ckpts/magic/snack_serve_0412/22500 --config_name pi0_bmlm_joint_snack 

# table clean and sweep
export CUDA_VISIBLE_DEVICES=3
source /home/pc3/deploy/openpi/.venv/bin/activate
XLA_PYTHON_CLIENT_PREALLOCATE=false python /home/pc3/deploy/openpi/scripts_/deploy_server.py --port 8010 --checkpoint_bucket /mnt/ckpts/magic/table_cleaning_0411_sweep/15000 --config_name pi0_bmlm_joint_sweep_and_table_clean 
```

## 新开一个窗口 远程语音输入控制按钮
```bash
conda activate piper_clt
cd /home/pc3/data_collect/voice_input_control_web
uvicorn app:app --host 0.0.0.0 --port 1145
```

## 新开一个窗口，语音输出tts
```bash
export CUDA_VISIBLE_DEVICES=1
conda activate cosyvoice
source /home/pc3/deploy/Piper_ros/devel/setup.bash
cd /home/pc3/deploy/CosyVoice
python chat.py
```

## 启动远程控制vllm web 以及转发来自franka的http请求
```bash
conda activate piper_clt
cd /home/pc3/data_collect/arm_sys_control_web
uvicorn app:app --host 0.0.0.0 --port 44931
```

## 新开一个窗口，启动主控流程的节点
```bash
export CUDA_VISIBLE_DEVICES=1
conda activate deploy
source /home/pc3/deploy/Piper_ros/devel/setup.bash
cd /home/pc3/deploy/gui_4_2
python main.py
```

