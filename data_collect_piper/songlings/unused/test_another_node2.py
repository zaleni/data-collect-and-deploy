import rospy
from rich import print
import os
from sensor_msgs.msg import JointState

if __name__ == "__main__":
    rospy.init_node("mzk_test", anonymous=True)

    def cb(joint_state: JointState):
        os.system('clear')
        print(f'Gripper Infos')
        print(f"TimeStamp: {joint_state.header.stamp}")
        print(f"Pos: {joint_state.position}")
        print(f"Vel: {joint_state.velocity}")
        print(f"Eff: {joint_state.effort}")

    rospy.Subscriber("imitator_gripper", JointState, cb)

    rospy.spin()
