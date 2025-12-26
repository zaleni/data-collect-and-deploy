## 数据采集和部署框架

具身智能机器人真机数据采集、标注和部署运行框架。

主要功能：
- 📊 **数据采集**：从 ARX VR 设备实时获取机械臂关节数据  
- 🔄 **数据处理**：清洗、转换、分析、标注
- 🤖 **模型部署**：pi0、pi05、MiVLA等方法的模型部署


## **简介**
### 🤖 支持的机械臂
- **松灵agilex PiPER 机械臂**  
  - ROS1通信  
  - 6+1 自由度  
  - 主从臂控制
- **方舟无限ARX X5 机械臂**  
  - ROS2通信  
  - 6+1 自由度  
  - 主从臂ROS2控制
- **Locoman（自建宇树GO1双臂机器人）**  
  - 使用 Apple Vision Pro 遥操作采集  
  - 双臂 4+4 自由度  
  - 机械臂由 8 枚 ROBOTIS XC330-T288-T 舵机构成
  
### 🧠 支持的 VLA 模型
- π0
- π0.5
- H-RDT
- ACT

---

- **MiVLA**
- 

## **目录**

```bash
祖传脚本/                       # 早期readme集合
data_collect_arx/               # ARX X5
data_collect_piper/             # Piper
locoman/                        # locoman
readme.md                       # 本文件
```

---

## **使用方法**

详情请见各个文件夹下的readme！！

---

<!--## **联系方式**

- 作者：**你的名字**
- 邮箱：your@email.com -->
