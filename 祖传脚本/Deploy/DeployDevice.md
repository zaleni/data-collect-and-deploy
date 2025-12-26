#  设备启动指南

## 机械臂
- 启动主节点， 一台机器只能启动一个， 必须启动

    *启动后显示已启动则不用管*

```bash
roscore
```

### 启动机械臂（启动执行动作的ROS节点）

- 查看can设备是否激活成功
```bash
cd /home/pc3/deploy/Piper_ros
bash can_activate.sh
```
- 正常显示：
```bash
预期配置单个can模块，检测到接口 can0，对应的usb地址为 1-5:1.0
接口 can0 已经激活，并且比特率为 1000000
接口名称已经是 can0
```

- 运行机械臂ROS节点：
    - 1.订阅 需要发布给机械臂的action消息， 并通过机械臂sdk执行这个action. 
    - 2.不断发布自己获取到的观察（摄像机图片， 机械臂状态， 让需要的地方自己获取）
    ```bash
    cd /home/pc3/deploy/gui
    source /home/pc3/deploy/Piper_ros/devel/setup.bash
    conda activate deploy   
    roslaunch piper start_single_piper.launch can_port:=can0 auto_enable:=true
    ```
- 正常会出现：
    ```bash
    使能状态： True
    ```

    *如果使能状态一直为False，先关闭运行节点程序，再关闭机械臂电源，等待2s后重启机械臂电源，再等待2s后重新启动机械臂运行节点程序。*


## 摄像头

- 终端启动摄像头节点：
    ```bash
    conda activate deploy
    source /home/pc3/deploy/tmp/OrbbecSDK_develop/orbbec_ws/devel/setup.bash 
    roslaunch orbbec_camera multi_camera.launch
    ```
- 正常启动后，[INFO]信息不会一直刷新

     *如果一直刷新，检查摄像头USB连接，在***当前USB口***重新插拔*

     *如果要更换新的USB口或其余问题，请参考[step.txt](step.txt)*


## 远程按钮启动

### 启动语音输入按钮

- 启动远程语音输入控制按钮
    ```bash
    conda activate piper_clt
    cd /home/pc3/data_collect/voice_input_control_web
    uvicorn app:app --host 0.0.0.0 --port 1145
    ```
- 使用其他设备访问1145端口，如 http://172.40.1.201:1145

    如IP变动，终端查看本机ip：
    ```bash 
    ifconfig
    ```
- 网页上有一个录音按钮，按住录音，松开结束录音

    *语音输入时，先打开麦克风和接收器，正常情况下会常亮绿灯*

### 启动远程控制按钮
- 启动远程控制vllm web，桌面清理，sweep任务 
- 接受来自franka的http请求， 然后通过ros重新发布请求，这个启动就行（franka那边必须要通过44931请求）
```bash
conda activate piper_clt
cd /home/pc3/data_collect/arm_sys_control_web
uvicorn app:app --host 0.0.0.0 --port 44931
```

- 同语音输入，使用其他设备访问44931端口，如 http://172.40.1.201:44931

- 网页两个按钮，一个启动/暂停机械臂，一个return回原点/继续vla控制
