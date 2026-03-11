#### Deploy

方舟无限ARX X5真机模型推理部署

1. 新建两个终端，分别使能can口以及启动机械臂推理ros程序

   ```
   /home/go2/ARX_X5/inference/scripts/can.sh
   /home/go2/ARX_X5/inference/scripts/arx.sh
   ```

2. 新开一个终端，启动摄像ros程序

   ```
   #增加USB数据传输的内存缓冲区限制
   echo 256 | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb
   conda activate ARX
   . /home/go2/ARX_X5/ros2_ws/install/setup.bash
   ros2 launch orbbec_camera multi_camera.launch.py
   ```

3. 选择指定模型启动推理server服务

    ```
    /home/go2/ARX_X5/inference/scripts/mip_hrdt_server.sh #mivla
    /home/go2/ARX_X5/inference/scripts/hrdt_server.sh #hrdt
    /home/go2/ARX_X5/inference/scripts/pi0_server.sh #pi0
    /home/go2/ARX_X5/inference/scripts/pi05_server.sh #pi05
    ```

    | args (mivla, hrdt)           | description                      |
    | ---------------------------- | -------------------------------- |
    | lang_embeddings_path         | 指令文本pt文件                   |
    | config_path                  | 训练配置文件                     |
    | pretrained_model_path        | 权重                             |
    | stat_file_path               | 归一化文件(最大值和最小值)       |
    | model_dimension, runner_type | 共同决定模型输入输出维度，默认14 |
    | normalize_actions            | 是否归一化和反归一化             |
    | host, port                   | 对齐server                       |

    | args (pi0, pi05)  | description                                                 |
    | ----------------- | ----------------------------------------------------------- |
    | checkpoint_bucket | 权重文件夹                                                  |
    | config_name       | 添加并与/openpi/src/openpi/training/config.py中repo_id 对齐 |
    
	
	
1. 推理部署启动

   ```
   /home/go2/ARX_X5/inference/scripts/hrdt_run.sh #mivla，hrdt
   /home/go2/ARX_X5/inference/scripts/pi0_run.sh #pi0，pi05
   ```

   | args       | description                     |
   | ---------- | ------------------------------- |
   | chunk_size | 使用模型一个chunk多少步发布     |
   | frame_rate | 推理发布的频率                  |
   | momentum   | 对模型推理加冲量，为0则为原始值 |
   
   



