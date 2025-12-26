from utils import parser_joint_ctrl_from_stream, endpose_to_bytes, ArmJointCtrl, ArmEndPose
from piper_sdk.kinematics.piper_fk import C_PiperForwardKinematics


calc = C_PiperForwardKinematics()

def conver_to_eef(joint: ArmJointCtrl):
    eff = ArmEndPose()
    eff.Hz = joint.Hz
    eff.time_stamp = joint.time_stamp
    x, y, z, rx, ry, rz = calc.arm_forward([
        joint.joint_ctrl.joint_1 / 1000,
        joint.joint_ctrl.joint_2 / 1000,
        joint.joint_ctrl.joint_3 / 1000,
        joint.joint_ctrl.joint_4 / 1000,
        joint.joint_ctrl.joint_5 / 1000,
        joint.joint_ctrl.joint_6 / 1000,
    ])
    eff.end_pose.X_axis = round(1000 * x)
    eff.end_pose.Y_axis = round(1000 * y)
    eff.end_pose.Z_axis = round(1000 * z)
    eff.end_pose.RX_axis = round(1000 * rx)
    eff.end_pose.RY_axis = round(1000 * ry)
    eff.end_pose.RZ_axis = round(1000 * rz)
    return eff

if __name__ == '__main__':
    file_path = 'data/orange_in_bowl/03-10@16:36:15_exceptioin/leader_joint'
    target_path = 'data/orange_in_bowl/03-10@16:36:15_exceptioin/leader_endpose'
    joints = parser_joint_ctrl_from_stream(file_path)
    with open(target_path, 'wb') as f:
        for eef in map(conver_to_eef, joints):
            # print(eef)
            f.write(endpose_to_bytes(eef))