import re

from sympy import true
import rospy
# from std_srvs.srv import SetBool, SetBoolRequest, SetBoolResponse, Trigger, TriggerRequest, TriggerResponse
import json
from std_msgs.msg import Bool, String

class ROSBackend:
    def __init__(self):
        rospy.init_node('ros_backend', anonymous=True)
        
        
        self.pub_vla = rospy.Publisher('/change_mode_vla_or_return/', String, queue_size=10)
        self.pub_pos = rospy.Publisher('/is_stop/', Bool, queue_size=10)
        self.pub_franka = rospy.Publisher('/arm_control/franka_msg', String, queue_size=10)
        # ~/data_collect/arm_sys_control_web
        self.pub_sweep = rospy.Publisher('/arm_control/table_sweep', Bool, queue_size=10)

        self.pub_pick_up = rospy.Publisher('/arm_control/bottle_pick_up', Bool, queue_size=10)


        self.pub_clean = rospy.Publisher('/arm_control/table_clean', Bool, queue_size=10)
        self.pub_vllm = rospy.Publisher('/arm_control/vllm_mode', Bool, queue_size=10)
        self.pub_move_left = rospy.Publisher('/arm_control/move_left', Bool, queue_size=10)
        self.pub_move_right = rospy.Publisher('/arm_control/move_right', Bool, queue_size=10)
        self.pub_dump = rospy.Publisher('/arm_control/dump', Bool, queue_size=10)
        self.pub_put_plate = rospy.Publisher('/arm_control/put_plate', Bool, queue_size=10)
        self.pub_sweep_all = rospy.Publisher('/arm_control/sweep_all', Bool, queue_size=10)
        self.pub_return_initial_position = rospy.Publisher('/arm_control/return_initial_position', Bool, queue_size=10)



        self.pub_put_bottle_on_table= rospy.Publisher('/arm_control/put_bottle_on_table', Bool, queue_size=10)


    
    def use_vla(self):
        # self.pub_vla.publish(True)
        s = String()
        s.data = 'use_vla'
        self.pub_vla.publish(s)
    
    def return_to_init_pos(self):
        self.pub_pos.publish(True)
        
    def notify_franka_control(self, ss):
        s = String()
        s.data = ss
        # print(ss)
        self.pub_franka.publish(s)
        
    def sweep(self):
        self.pub_sweep.publish(True)

    def pick_up(self):
        self.pub_pick_up.publish(True)
        
    def clean(self):
        self.pub_clean.publish(True)

    def vllm(self):
        self.pub_vllm.publish(True)
    
    def move_left(self):
        self.pub_move_left.publish(True)
    
    def move_right(self):
        self.pub_move_right.publish(True)
    def dump(self):
        self.pub_dump.publish(True)
    def put_plate(self):
        self.pub_put_plate.publish(True)
    def sweep_all(self):
        self.pub_sweep_all.publish(True)
    def return_initial_position(self):
        self.pub_return_initial_position.publish(True)


        
    def put_bottle_on_table(self):
        self.pub_put_bottle_on_table.publish(True)
        
