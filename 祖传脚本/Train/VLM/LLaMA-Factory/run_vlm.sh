#!/bin/bash

#SBATCH -J paligemma
#SBATCH -p hx
#SBATCH -N 1 # <一个节点>
#SBATCH --ntasks=1 # <任务数：作业进程数>
#SBATCH --cpus-per-task=8 # <每个任务 cpu 核心数>
#SBATCH --gres=gpu:8 # 调用多少张卡，这里是 8 张
#SBATCH --output=/HOME/uestc_jksong/uestc_jksong_1/zhanghaonan/code/LLaMA-Factory/logs/paligemma_v2_%j.out # 作业控制台输出，路
径/名字可以随便改
#SBATCH --error=/HOME/uestc_jksong/uestc_jksong_1/zhanghaonan/code/LLaMA-Factory/logs/paligemma_v2_%j.err # 作业报错输出，路径/名字可以随便改

# ntask should be equal to N

# 激活使用对应版本的 cuda （`module av` 可以查询）
module load CUDA/12.2 # 激活使用对应版本的 cuda

# 以下为两种激活环境的方法，二选一即可
# 使用 python venv 管理环境
# source .venv/bin/activate # 激活环境

# 使用 conda 管理环境
source /HOME/uestc_jksong/uestc_jksong_1/miniconda3/etc/profile.d/conda.sh
conda activate llama-factory # 换成自己的环境

# 以下代码仅为举例，请换成自己的（单机多卡训练）
HF_ENDPOINT=https://hf-mirror.com llamafactory-cli train examples/train_full/paligemma_full_sft.yaml
# HF_ENDPOINT=https://hf-mirror.com llamafactory-cli train examples/train_full/qwen2_5_7b_instruct.yaml