# PI0 训练指南

本文档介绍基于Physical Intelligence的Pi0模型进行无界大模型训练的注意事项和配置方法。

## 目录
- [模型概述](#模型概述)
- [主要修改点](#主要修改点)
  - [训练配置](#1-训练配置)
  - [数据读取配置](#2-数据读取配置)
  - [输入输出配置](#3-输入输出配置)
- [训练流程](#训练流程)

## 模型概述
当前无界大模型训练基于[Physical Intelligence的PI0模型](https://github.com/Physical-Intelligence/openpi)实现

## 广州集群项目路径
`/HOME/uestc_jksong/uestc_jksong_1/workspace/openpi`

## 数据集传输和模型传输脚本
在PC3上运行下面两个脚本完成数据集的传输以及训练完成的模型ckpt传输
### 从pc3传输数据集到超算集群
```bash
scp \
 -o StrictHostKeyChecking=no \
 -o UserKnownHostsFile=/dev/null \
 -P 8001 \
 -i /home/pc3/data_collect/tmp/uestc_jksong_1.id \
 -r \
 dataset_dir \ # 修改为build好的lerobot数据集目录
 uestc_jksong_1@121.46.19.4:/HOME/uestc_jksong/uestc_jksong_1/workspace/openpi/datasets 
```

### 将训练好的checkpoint从超算集群传输到
```bash
rsync -avz --info=progress2 -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 8001 -i /home/pc3/data_collect/tmp/uestc_jksong_1.id" \
--exclude 'train_state' \
-r uestc_jksong_1@121.46.19.4:/HOME/uestc_jksong/uestc_jksong_1/workspace/openpi/snack_serve/pi0_bmlm_joint_v2/exp_0411_joint_add_snack/22500 \
/mnt/ckpts/magic/snack_serve_0412
```

## 主要修改点

### 1. 训练配置
修改文件：[`openpi/src/openpi/training/config.py`](./openpi/src/openpi/training/config.py)

```python
TrainConfig(
    name="pi0_bmlm",   # 配置名称
    batch_size=256,   
    num_workers=16,
    model=pi0.Pi0Config(action_horizon=20),  # action_horizon: 模型一次预测的动作数量
    data=LeRobotCFMDataConfig(
        repo_id="datasets/SongLin-Remake",  # LeRobot数据集名称
        base_config=DataConfig(
            local_files_only=True,  # 设为True表示仅使用本地数据集
            prompt_from_task=True,
            action_sequence_keys=("action", )  # LeRobot原始数据中action字段的键值
        ),
    ),
    weight_loader=weight_loaders.CheckpointWeightLoader("ckpts/pi0_base/params"),
    num_train_steps=30_000,  # 默认训练30000步（简单任务5000步即可）
    wandb_enabled=True,
    lr_schedule=_optimizer.CosineDecaySchedule(
        warmup_steps=1_000,
        peak_lr=2.5e-5,
        decay_steps=30_000,
        decay_lr=2.5e-6
    )
)
```
### 2. 数据读取配置
修改文件：[`openpi/src/openpi/training/config.py`](./openpi/src/openpi/training/config.py)
```python
class LeRobotCFMDataConfig(DataConfigFactory):
    @override
    def create(self, assets_dirs: pathlib.Path, model_config: _model.BaseModelConfig) -> DataConfig:
        # 数据重映射配置
        repack_transform = _transforms.Group(
            inputs=[
                _transforms.RepackTransform({
                    "image": "front_rgb",    # 键名对应关系：左边为训练数据键，右边为原始数据键
                    "wrist_image": "wrist_rgb",
                    "state": "state",
                    "actions": "action",
                    "prompt": "prompt"
                })
            ]
        )

        # 数据转换配置
        data_transforms = _transforms.Group(
            inputs=[cfm_policy.BmlmInputs(action_dim=model_config.action_dim, 
                                         model_type=model_config.model_type)],
            outputs=[cfm_policy.BmlmOutputs()],
        )

        # Delta Action转换配置（最后一维gripper通常不转换）
        delta_action_mask = _transforms.make_bool_mask(6, -1)
        data_transforms = data_transforms.push(
            inputs=[_transforms.DeltaActions(delta_action_mask)],
            outputs=[_transforms.AbsoluteActions(delta_action_mask)],
        )

        model_transforms = ModelTransformFactory()(model_config)

        return dataclasses.replace(
            self.create_base_config(assets_dirs),
            repack_transforms=repack_transform,
            data_transforms=data_transforms,
            model_transforms=model_transforms,
        )
```

### 3. 输入输出配置
修改文件：[`openpi/src/openpi/policies/cfm_policy.py`](./openpi/src/openpi/policies/cfm_policy.py)
```python
class BmlmInputs(transforms.DataTransformFn):
    action_dim: int
    model_type: _model.ModelType = _model.ModelType.PI0

    def __call__(self, data: dict) -> dict:
        mask_padding = self.model_type == _model.ModelType.PI0
        state = transforms.pad_to_dim(data["state"], self.action_dim)
        
        # 图像处理
        base_image = _parse_image(data["image"])  # 第三人称视角
        wrist_image = _parse_image(data["wrist_image"])  # 腕部视角

        inputs = {
            "state": state,
            "image": {
                "base_0_rgb": base_image,
                "left_wrist_0_rgb": wrist_image,
                "right_wrist_0_rgb": np.zeros_like(base_image),  # 无数据时填充
            },
            "image_mask": {
                "base_0_rgb": np.True_,
                "left_wrist_0_rgb": np.True_,
                "right_wrist_0_rgb": np.False_ if mask_padding else np.True_, # 无数据时填充np.False_
            },
        }

        if "actions" in data:
            inputs["actions"] = transforms.pad_to_dim(data["actions"], self.action_dim)
        if "prompt" in data:
            inputs["prompt"] = data["prompt"]

        return inputs
```
## 训练流程
### 1. 计算统计量
```bash
uv run scripts/compute_norm_stats.py --config-name pi0_bmlm
```
### 2. 启动训练
```bash
XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
uv run scripts/train.py pi0_bmlm \
    --exp-name=exp_0410 \
    --save_interval=5000 \ # 每5000步保存一次ckpt
    --keep_period=5000 \ # 只保留step%5000 == 0的ckpt
    --checkpoint_base_dir=./table_cleaning \ # 模型ckpt保存文件夹路径
    --overwrite
```
### 3. 恢复训练
在命令后添加`--resume`参数，会自动导入`checkpoint_base_dir`文件夹下的最近一个step的训练状态继续训练
> 更多参数说明请参考：`openpi/src/openpi/training/config.py` 中的 `TrainConfig`