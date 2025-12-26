import re
import rospy
from std_srvs.srv import SetBool, SetBoolRequest, SetBoolResponse, Trigger, TriggerRequest, TriggerResponse
import json

class ROSBackend:
    def __init__(self):
        rospy.init_node('ros_backend', anonymous=True)
        
        # rospy.Service('/piper_collect_data/query_switch', Trigger, query_switch_callback)
        # rospy.Service('/piper_collect_data/set_switch', SetBool, set_switch_callback)
        # rospy.Service('/piper_collect_data/query_status', Trigger, query_status_callback)
        # rospy.Service('/piper_collect_data/query_record_num', Trigger, query_recorded_callback)
        
        self.query_switch = rospy.ServiceProxy('/piper_collect_data/query_switch', Trigger)
        self.set_switch = rospy.ServiceProxy('/piper_collect_data/set_switch', SetBool)
        self.query_status = rospy.ServiceProxy('/piper_collect_data/query_status', Trigger)
        self.query_record_num = rospy.ServiceProxy('/piper_collect_data/query_record_num', Trigger)
    
    def query_switch_callback(self):
        """
        Callback function for the query switch service.
        :param req: Request object
        :return: Response object
        """
        try:
            response = self.query_switch()
            return {
                'success': response.success,
                'message': response.message
            }
        except rospy.ServiceException as e:
            return {
                'success': False,
                'message': str(e)
            }
        
    
    def set_switch_callback(self, switch_state):
        """
        Callback function for the set switch service.
        :param req: Request object
        :return: Response object
        """
        try:
            response = self.set_switch(SetBoolRequest(data=switch_state))
            return {
                'success': response.success,
                'message': response.message
            }
        except rospy.ServiceException as e:
            return {
                'success': False,
                'message': str(e)
            }
        
    def query_status_callback(self):
        """
        Callback function for the query status service.
        :param req: Request object
        :return: Response object
        """
        try:
            response = self.query_status()
            return {
                'success': response.success,
                'message': json.loads(response.message)
            }
        except rospy.ServiceException as e:
            return {
                'success': False,
                'message': str(e)
            }
        
    def query_record_num_callback(self):
        """
        Callback function for the query record number service.
        :param req: Request object
        :return: Response object
        """
        try:
            response = self.query_record_num()
            return {
                'success': response.success,
                'message': json.loads(response.message)
            }
        except rospy.ServiceException as e:
            return {
                'success': False,
                'message': str(e)
            }