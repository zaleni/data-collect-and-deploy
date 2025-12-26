import time
from utils import parser_gripper_from_stream, parser_endpose_from_stream, enable_fun, ArmJoint
from piper_interface_v2 import C_PiperInterface_V2
from rich import print

piper = C_PiperInterface_V2()
piper.ConnectPort()
enable_fun(piper)

g_joint = parser_endpose_from_stream('data/03-04@11:07:27/follower_endpose_downsample')
g_joint = list(g_joint)

for index, joint in enumerate(g_joint):
    print(joint)
    print(f'execute joint')
    j1, j2, j3, j4, j5, j6 = [
        joint.joint_state.joint_1,
        joint.joint_state.joint_2,
        joint.joint_state.joint_3,
        joint.joint_state.joint_4,
        joint.joint_state.joint_5,
        joint.joint_state.joint_6 
    ]

    print(f'Index: {index} {[j1, j2, j3, j4, j5, j6]}')
    
    # piper.JointCtrl(
    #     j1, j2, j3, j4, j5, j6
    # )
    
    input('Enter to continue')
    