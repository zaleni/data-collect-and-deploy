### ROS

ROS主要通过**节点**(node)间**发布/订阅**(pub/sub)**话题**(topic)的方式实现通信

---

| 核心节点  | 说明 |
| ------------- | ------------- |
| [piper_ctrl_single_node](piper_ctrl_single_node.py)  | 机械臂执行动作节点  |
| [joint_state_publisher](gui_4_2\lib\ros_operator.py) | 系统控制节点 |
| chat_subscriber | 语音输出节点  |

---

| 主要话题 | 说明 |
| ------- | -------- |
| /ob_camera_01/color/image_raw | 机械臂摄像头图像话题 | 
| /ob_camera_02/color/image_raw | 第三视角摄像头图像话题 | 
| joint_states_single | 当前机械joint state状态话题 |
| js_cmd | 系统控制机械臂joint state话题 |
| /arm_control/franka_msg/ | franka完成当前[order food]消息话题 |
| /chat/| 语音文本消息话题 |

---

#### ros发布和订阅示例：

*注意：发布和订阅之间需要保持话题名称和话题消息类型相同*

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
