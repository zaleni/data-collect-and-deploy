import rospy
from std_srvs.srv import Trigger, TriggerResponse, SetBool, SetBoolResponse

from pydantic import BaseModel

def register_service(
    set_switch_callback,
    query_switch_callback,
    query_status_callback,
    query_recorded_callback
):
    rospy.Service('/piper_collect_data/query_switch', Trigger, query_switch_callback)
    rospy.Service('/piper_collect_data/set_switch', SetBool, set_switch_callback)
    rospy.Service('/piper_collect_data/query_status', Trigger, query_status_callback)
    rospy.Service('/piper_collect_data/query_record_num', Trigger, query_recorded_callback)