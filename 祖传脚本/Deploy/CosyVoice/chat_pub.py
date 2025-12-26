#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import String
import time

def chinese_test_publisher():
    # 初始化节点
    rospy.init_node('chinese_test_publisher', anonymous=True)
    
    # 创建发布者
    pub = rospy.Publisher('/chat/', String, queue_size=10)
    
    # 等待订阅者连接
    rospy.loginfo("等待TTS订阅者连接...")
    time.sleep(2)
    
    # 中文测试内容
    test_messages = [
        "你好，这是一条测试语音",
        "今天的天气真不错，你觉得呢？",
        "我正在测试中文语音合成系统",
        "恭喜你，所有测试已完成！"
    ]
    
    try:
        rospy.loginfo("开始发送中文测试内容...")
        for idx, msg in enumerate(test_messages, 1):
            rospy.loginfo(f"发送测试 {idx}/{len(test_messages)}: {msg}")
            pub.publish(msg)
            time.sleep(2)  
            
        rospy.loginfo("所有测试内容发送完毕！")
        
    except rospy.ROSInterruptException:
        rospy.logwarn("测试被中断")

if __name__ == '__main__':
    try:
        chinese_test_publisher()
    except rospy.ROSInterruptException:
        pass