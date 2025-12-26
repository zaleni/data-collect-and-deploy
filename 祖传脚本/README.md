# 🦾 MagicBot

MagicBot 是一个基于 ROS (Robot Operating System) 的智能机器人系统，集成了先进的视觉语言模型（VLM）和视觉语言动作模型（VLA），能够实现智能化的机器人控制和交互。使用了 system-1 和 system-2 的架构，能够实现多模态的机器人控制和交互。

## 🌟 特性

- 🤖 基于 ROS 的分布式机器人控制系统
- 👁️ 多模态视觉语言模型集成
- 🎯 精确的机械臂控制
- 🗣️ 语音交互能力
- 📊 完整的数据采集和训练流程
- 🔄 模块化设计，易于扩展

## 📋 系统要求

- Ubuntu 操作系统
- ROS 环境
- CUDA 支持的 GPU
- Python 3.10
- Conda 环境管理

## 🚀 快速开始

系统启动需要按以下顺序初始化各个组件：

1. **ROS 核心服务**：启动 ROS 主节点，作为整个系统的通信中心
2. **感知系统**：启动相机节点，获取环境视觉信息
3. **控制系统**：初始化机械臂控制节点，建立与硬件的连接
4. **AI 模型服务**：
   - 启动 LLM 服务，处理自然语言指令
   - 启动 VLM 服务，处理视觉语言任务
   - 启动 VLA 服务，执行具体的动作控制
5. **交互系统**：启动语音输入输出和远程控制界面

详细的启动步骤和配置说明请参考 [QuickStart](Deploy/QuickStart.md)

## 📁 项目结构

### 📁 Preliminary

- [README](Preliminary/README.md) - 项目基础设置和 ROS 环境配置
- [Server](Preliminary/Server.md) - 服务器配置说明

### 📁 Deploy

- [Quick Start](Deploy/QuickStart.md) - 快速启动指南
- [Deploy Model](Deploy/DeployModel.md) - 模型部署说明
- [Deploy Device](Deploy/DeployDevice.md) - 设备部署指南
- [Deploy System](Deploy/DeploySystem.md) - 系统部署文档
- [ROS Instruction](Deploy/ROSInstruction.md) - ROS 使用说明

### 📁 Train

- VLM/VLA - 视觉语言动作模型训练相关文档
- [VLM] - 视觉语言模型tutorial
- [VLA] - 视觉语言动作模型tutorial

### 📁 DataCollection

- [README](DataCollection/README.md) - 数据采集说明
- [Data Collection](DataCollection/DataCollect.md) - 数据采集流程
- [Data Annotation](DataCollection/DataAnno.md) - 数据标注指南
- [Software and Format Convert](DataCollection/SoftwareAndFormatConvert.md) - 软件使用和格式转换说明
- 数据收集软件说明/ - 数据采集软件详细文档

### 📁 Algorithm

- [README](Algo/GR00T/readme.md) - 在GR00T上微调LIBERO数据集

## 📞 联系方式

如有问题，请提交issue.
