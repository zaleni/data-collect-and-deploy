# 部署文档

完整执行顺序参考 [启动步骤.md](启动步骤.md)

## 1.机械臂
启动主节点， 一台机器只能启动一个， 必须启动

*启动后显示已启动则不用管*

```bash
roscore
```

### 1.1启动机械臂（启动执行动作的ROS节点）

- 查看can设备是否激活成功
```bash
cd /home/pc3/deploy/Piper_ros
bash can_activate.sh
```
正常显示：
```bash
预期配置单个can模块，检测到接口 can0，对应的usb地址为 1-5:1.0
接口 can0 已经激活，并且比特率为 1000000
接口名称已经是 can0
```

-  运行机械臂ROS节点：1.订阅 需要发布给机械臂的action消息， 并通过机械臂sdk执行这个action. 2.不断发布自己获取到的观察（摄像机图片， 机械臂状态， 让需要的地方自己获取）
```bash
cd /home/pc3/deploy/gui
source /home/pc3/deploy/Piper_ros/devel/setup.bash
conda activate deploy   
roslaunch piper start_single_piper.launch can_port:=can0 auto_enable:=true
```
正常会出现：
```bash
使能状态： True
```
*如果使能状态一直为False，先关闭运行节点程序，再关闭机械臂电源，等待2s后重启机械臂电源，再等待2s后重新启动机械臂运行节点程序。*


### 1.2摄像头

- 终端启动摄像头节点：
```bash
conda activate deploy
source /home/pc3/deploy/tmp/OrbbecSDK_develop/orbbec_ws/devel/setup.bash 
roslaunch orbbec_camera multi_camera.launch
```
- 正常启动后，[INFO]信息不会一直刷新

     *如果一直刷新，检查摄像头USB连接，在***当前USB口***重新插拔*

     *如果要更换新的USB口或其余问题，请参考[step.txt](tmp/OrbbecSDK_develop/step.txt)*


## 2.模型启动

### LLM模型
- 使用LLaMA-Factor部署qwen2_5_7b_instruct模型，和标准流程一样没有特殊的。（没有微调，只是指定了系统prompt）
```bash
conda activate vllm
API_PORT=8005 llamafactory-cli api /home/pc3/deploy/LLaMA-Factory/examples/inference/qwen2_5_7b_instruct.yaml
```

### VLLM模型
- 使用LLaMA-Factor部署微调后的paligemma
```bash
API_PORT=8001 llamafactory-cli api --model_name_or_path /home/pc3/deploy/vllm_model_ckpt/vllm_snack_0409_v2 --template paligemma --infer_backend huggingface --trust_remote_code true
```
### VLA模型
- 部署VLA模型， **需要将--checkpoint_bucket 和 --config_name相对应， 训练checkpoint_bucket模型的数据集名称一定要在config中体现**， config.py是指：/home/pc3/deploy/openpi/src/openpi/training/config.py
```bash
export CUDA_VISIBLE_DEVICES=0,1 #自行决定用那些卡
source /home/pc3/deploy/openpi/.venv/bin/activate #这pi激活环境的方式
source /home/pc3/deploy/Piper_ros/devel/setup.bash #增加与机械臂ros节点相关的导包路径
XLA_PYTHON_CLIENT_PREALLOCATE=false python /home/pc3/deploy/openpi/scripts_/deploy_server.py  --checkpoint_bucket /mnt/ckpts/magic/snack_serve_0402/10000 --config_name pi0_bmlm 
```

## 3.通信相关：

### ROS

ROS主要通过**节点**(node)间**发布/订阅**(pub/sub)**话题**(topic)的方式实现通信

| 核心节点  | 说明 |
| ------------- | ------------- |
| piper_ctrl_single_node  | 机械臂执行动作节点  |
| joint_state_publisher | 系统控制节点 |
| chat_subscriber | 语音输出节点  |

| 主要话题 | 说明 |
| ------- | -------- |
| /ob_camera_01/color/image_raw | 机械臂摄像头图像话题 | 
| /ob_camera_02/color/image_raw | 第三视角摄像头图像话题 | 
| joint_states_single | 当前机械joint state状态话题 |
| js_cmd | 系统控制机械臂joint state话题 |
| /arm_control/franka_msg/ | franka完成当前[order food]消息话题 |
| /chat/| 语音文本消息话题 |

#### ros发布和订阅示例：

系统控制节点，发布系统控制机械臂js_cmd话题
```python
#创捷一个Publisher
self.puppet_arm_left_publisher_joint = rospy.Publisher('js_cmd', JointState, queue_size=10)

#设置JointState类型消息
joint_state_msg = JointState()
joint_state_msg.header = Header()
joint_state_msg.header.stamp = rospy.Time.now()  
joint_state_msg.name = ['joint0', 'joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']  
joint_state_msg.position = left_arm

#使用Publisher pub消息
if(self.ctrl_mode):
    self.puppet_arm_left_publisher_joint.publish(joint_state_msg)

```
机械臂执行动作节点，订阅js_cmd话题并调用sdk执行
```python

"""机械臂关节订阅"""
#创建一个Subscriber
#Subsriber创建后，收到一个ros消息，会执行一次回调函数
rospy.Subscriber("js_cmd",JointState,self.joint_callback,queue_size=1,tcp_nodelay=True,)
rospy.spin()

"""机械臂关节角回调函数
Args:
    joint_data ():
"""
def joint_callback(self, joint_data):



```




### HTTP

### QT信号响应

## 4. 语音输入输出

### 语音输入

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

### 语音输出
启动后，语音输出会作为一个ROS节点一直运行

收到ROS消息后会自动tts语音播放
```bash
export CUDA_VISIBLE_DEVICES=2
conda activate cosyvoice
source /home/pc3/deploy/Piper_ros/devel/setup.bash
cd /home/pc3/deploy/CosyVoice
python chat.py
```

## 5. 远程界面按钮控制

- 启动远程控制vllm web

```bash
conda activate piper_clt
cd /home/pc3/data_collect/arm_sys_control_web
uvicorn app:app --host 0.0.0.0 --port 44931
```

- 同语音输入，使用其他设备访问44931端口，如 http://172.40.1.201:44931

- 网页两个按钮，一个启动/暂停机械臂，一个return回原点/继续vla控制

## 6. GUI控制界面

***启动GUI控制界面时，请确保至少启动模型LLM,VLM,VLA服务***

- 返回按钮： 点击一次后，屏蔽vla模型action输出开始返回初始位置， 点击第二次后开启vla输出
- 停止按钮: 点击一次后，屏蔽所有的action, 点击第二次开启

- 注意若想单独测试vla, 请不要输入，llm指令和vllm指令， 因为llm指令会影响vllm指令， vllm指令会影响vla指令。若想测试vllm同理不要设置llm指令。
```bash
export CUDA_VISIBLE_DEVICES=2
conda activate deploy
source /home/pc3/deploy/Piper_ros/devel/setup.bash
cd /home/pc3/deploy/gui_4_2
python main.py
```