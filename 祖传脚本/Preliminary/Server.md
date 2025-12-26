# Server

## Slurm 作业调度系统

### 常用指令

- 查看分区信息：`sinfo`
- 查看作业队列：`squeue`
- 查看作业详情：`scontrol show job <jobid>`
- 查看节点信息：`scontrol show node <hostname>`
- 提交作业：`sbatch <script.sh>`
- 取消作业：`scancel <jobid>`
- 交互式运行作业：`srun`
- 查看 GPU 信息：`nvidia-smi`
- 查看 CPU 信息：`top` / `htop`

更多细节查看 slurm 官方文档：[https://slurm.schedmd.com/documentation.html](https://slurm.schedmd.com/documentation.html)

### 提交作业脚本样例

```bash
#!/bin/bash

#SBATCH -J <job 名字>
#SBATCH -p <分区名>
#SBATCH -N 1 # <一个节点>
#SBATCH --ntasks=1 # <任务数：作业进程数>
#SBATCH --cpus-per-task=24 # <每个任务 cpu 核心数>
#SBATCH --output=slurm_logs/<job 名字>-%j.out # 作业控制台输出，路径/名字可以随便改
#SBATCH --error=slurm_logs/<job 名字>-%j.err # 作业报错输出，路径/名字可以随便改

# ntask should be equal to N

# 激活使用对应版本的 cuda
module load CUDA/12.4

# 以下为两种激活环境的方法，二选一即可
# 使用 python venv 管理环境
# source .venv/bin/activate # 激活环境

# 使用 conda 管理环境
source /HOME/uestc_jksong/uestc_jksong_1/miniconda3/etc/profile.d/conda.sh
conda activate <env name> # 换成自己的环境

# 以下代码仅为举例，请换成自己的（单机多卡训练）
NCCL_P2P_LEVEL=NVL OMP_NUM_THREADS=8 srun torchrun \
    --standalone \
    --nnodes 1 \
    --nproc_per_node 8 \
    vla-scripts/train.py \
    ...

```

请注意：不同的集群设置会所区别，但基本上大同小异，只有很小的变化。实际使用的时候需要看计算服务供应商提供的文档来调整。
