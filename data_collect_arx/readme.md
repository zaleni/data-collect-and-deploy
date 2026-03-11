### data_collect

**方舟无限使用ros消息进行主从臂遥操数据采集**

1. 新开两个终端，激活主从臂can口，第一次需要设置can口位置，见[ARX-CAN手册](https://github.com/ARXroboticsX/ARX_X5/blob/main/00-readme/ARX-CAN手册.pdf)

   ```
   #从臂
   conda activate ARX
   cd /home/go2/ARX_X5/ARX_CAN/arx_can
   ./arx_can1.sh
   #主臂
   conda activate ARX
   cd /home/go2/ARX_X5/ARX_CAN/arx_can
   ./arx_can0.sh
   ```

2. 新开两个终端，主从臂采集遥操使能（先使能主臂再使能从臂，**注意：使能时保持主从臂位姿一样，以防开启同步后机械臂大幅度运动**）

   ```
   conda activate ARX
   cd /home/go2/ARX_X5/ROS2/X5_ws
   source install/setup.bash
   ros2 launch arx_x5_controller open_remote_master.launch.py
   
   conda activate ARX
   cd /home/go2/ARX_X5/ROS2/X5_ws
   source install/setup.bash
   ros2 launch arx_x5_controller open_remote_slave.launch.py
   ```

3. 新开一个终端，启动摄像ros程序

   ```
   #增加USB数据传输的内存缓冲区限制
   echo 256 | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb
   conda activate ARX
   . /home/go2/ARX_X5/ros2_ws/install/setup.bash
   ros2 launch orbbec_camera multi_camera.launch.py
   ```

4. 新开一个终端，启动采集程序

   采集时按‘s’开始采集，按‘q’结束当前数据采集

   采集时移动到预定位置后（所有提示为绿）开始采集

   修改代码--datasets 参数指定保存文件夹

   ```
   conda activate ARX
   source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
   python /home/go2/ARX_X5/main/collect_noop.py、
   ```

	采集的数据格式：/home/go2/ARX_X5/main/read_hdf5_all.py 进行hdf5文件查看

    ```
    - [Group] endpose
    - [Dataset] endpose/left_endpose: shape=(1051, 7), dtype=float64
    - [Dataset] endpose/left_gripper: shape=(1051,), dtype=float64
    - [Dataset] endpose/right_endpose: shape=(1051, 7), dtype=float64
    - [Dataset] endpose/right_gripper: shape=(1051,), dtype=float64
    - [Group] joint_action
    - [Dataset] joint_action/left_arm: shape=(1051, 6), dtype=float64
    - [Dataset] joint_action/left_gripper: shape=(1051,), dtype=float64
    - [Dataset] joint_action/right_arm: shape=(1051, 6), dtype=float64
    - [Dataset] joint_action/right_gripper: shape=(1051,), dtype=float64
    - [Dataset] joint_action/vector: shape=(1051, 14), dtype=float64
    - [Group] observation
    - [Group] observation/head_camera
    - [Dataset] observation/head_camera/rgb: shape=(1051,), dtype=|S58955
    - [Group] observation/left_camera
    - [Dataset] observation/left_camera/rgb: shape=(1051,), dtype=|S95319
    ```

**数据采集完成后，建议抽样进行轨迹复现，以防各种原因导致的数据错误**

 1. 主从臂先放回初始位置，再进行断电，然后只用从臂。

 2. 新建两个终端，分别使能can口以及启动机械臂推理ros程序（这里的启动的程序和推理阶段一样，不同于采集主从遥操的程序）

    ```
    /home/go2/ARX_X5/inference/scripts/can.sh
    /home/go2/ARX_X5/inference/scripts/arx.sh
    ```

3. 轨迹复现程序和移动初始位置程序（先让机械臂移动到初始位置，防止复现轨迹时机械臂大幅度运动

   To do: 融合2个代码为1个

   ```
   python /home/go2/ARX_X5/main/set_init.py #初始位置
   python replay.py /home/go2/ARX_X5/main/umbrella_1107/episode_0.hdf5 #复现指定轨迹
   ```

**（可选）**对采集的夹爪轨迹进行后处理，减少数据抖动

```
python3 process_gripper.py /home/go2/ARX_X5/main/umbrella_1108 --batch -o /home/go2/ARX_X5/main/umbrella_1108/processed_datasets/
```

