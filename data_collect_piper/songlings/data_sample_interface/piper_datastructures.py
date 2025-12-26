from typing import Literal

class ArmMsgEndPoseFeedBack():
    '''
    机械臂末端姿态反馈,单位0.001mm
    
    CAN ID: 
        0x152、0x153、0x154
    
    Args:
        X_axis: X坐标
        Y_axis: Y坐标
        Z_axis: Z坐标
        RX_axis: RX角度
        RY_axis: RY角度
        RZ_axis: RZ角度
    '''
    '''
    End-Effector Pose Feedback for the Robotic Arm, unit: 0.001 mm.
    
    CAN ID: 
        0x152、0x153、0x154
    
    Args:
        X_axis: X-coordinate.
        Y_axis: Y-coordinate.
        Z_axis: Z-coordinate.
        RX_axis: Rotation angle around the X-axis (RX).
        RY_axis: Rotation angle around the Y-axis (RY).
        RZ_axis: Rotation angle around the Z-axis (RZ).
    '''
    def __init__(self, X_axis: int=0, Y_axis: int=0, 
                 Z_axis: int=0, RX_axis: int=0, 
                 RY_axis: int=0, RZ_axis: int=0):
        self.X_axis = X_axis
        self.Y_axis = Y_axis
        self.Z_axis = Z_axis
        self.RX_axis = RX_axis
        self.RY_axis = RY_axis
        self.RZ_axis = RZ_axis

    def __str__(self):
        # 将角度乘以0.001，并保留三位小数
        end_pose = [
            (" X_axis ", self.X_axis, self.X_axis * 0.001),
            (" Y_axis ", self.Y_axis, self.Y_axis * 0.001),
            (" Z_axis ", self.Z_axis, self.Z_axis * 0.001),
            (" RX_axis ", self.RX_axis, self.RX_axis * 0.001),
            (" RY_axis ", self.RY_axis, self.RY_axis * 0.001),
            (" RZ_axis ", self.RZ_axis, self.RZ_axis * 0.001)
        ]

        # 生成格式化字符串，保留三位小数
        formatted_ = "\n".join([f"{name}: {pose}, {pose_f:.3f}" for name, pose, pose_f in end_pose])
        
        return f"ArmMsgEndPoseFeedBack:\n{formatted_}"
    
    def __repr__(self):
        return self.__str__()
    
class ArmMsgJointFeedBack():
    '''
    机械臂关节角度反馈,单位0.001度
    
    CAN ID: 
        0x2A5、0x2A6、0x2A7
    
    Args:
        joint_1: 关节1反馈角度
        joint_2: 关节2反馈角度
        joint_3: 关节3反馈角度
        joint_4: 关节4反馈角度
        joint_5: 关节5反馈角度
        joint_6: 关节6反馈角度
    '''
    '''
    Joint Angle Feedback for Robotic Arm, in 0.001 Degrees
    
    CAN ID: 
        0x2A5、0x2A6、0x2A7
    
    Args:
        joint_1: Feedback angle of joint 1, in 0.001 degrees.
        joint_2: Feedback angle of joint 2, in 0.001 degrees.
        joint_3: Feedback angle of joint 3, in 0.001 degrees.
        joint_4: Feedback angle of joint 4, in 0.001 degrees.
        joint_5: Feedback angle of joint 5, in 0.001 degrees.
        joint_6: Feedback angle of joint 6, in 0.001 degrees.
    '''
    def __init__(self, joint_1: int=0, joint_2: int=0, 
                 joint_3: int=0, joint_4: int=0, 
                 joint_5: int=0, joint_6: int=0):
        self.joint_1 = joint_1
        self.joint_2 = joint_2
        self.joint_3 = joint_3
        self.joint_4 = joint_4
        self.joint_5 = joint_5
        self.joint_6 = joint_6

    def __str__(self):
        # 将角度乘以0.001，并保留三位小数
        joint_angles = [
            ("Joint 1", self.joint_1, self.joint_1 * 0.001),
            ("Joint 2", self.joint_2, self.joint_2 * 0.001),
            ("Joint 3", self.joint_3, self.joint_3 * 0.001),
            ("Joint 4", self.joint_4, self.joint_4 * 0.001),
            ("Joint 5", self.joint_5, self.joint_5 * 0.001),
            ("Joint 6", self.joint_6, self.joint_6 * 0.001)
        ]

        # 生成格式化字符串，保留三位小数
        formatted_angles = "\n".join([f"{name}:{angle}, {angle_f:.3f}" for name, angle, angle_f in joint_angles])
        
        return f"ArmMsgJointFeedBack:\n{formatted_angles}"
    
    def __repr__(self):
        return self.__str__()

class ArmMsgGripperFeedBack:
    '''
    夹爪反馈消息
    
    CAN ID:
        0x2A8
    
    Args:
        grippers_angle: 夹爪角度，以整数表示。
        grippers_effort: 夹爪扭矩，以整数表示。
        status_code: 夹爪状态码，以整数表示。
    
    位描述:

        Byte 0: 夹爪行程最高位, int32, 单位 0.001mm
        Byte 1: 
        Byte 2: 
        Byte 3: 
        Byte 4: 夹爪扭矩 H, int16, 单位 0.001N/m
        Byte 5: 夹爪扭矩 L
        Byte 6: 状态码, uint8
            bit[0]      电源电压是否过低(0:正常 1:过低)
            bit[1]      电机是否过温(0:正常 1:过温)
            bit[2]      驱动器是否过流(0:正常 1:过流)
            bit[3]      驱动器是否过温(0:正常 1:过温)
            bit[4]      传感器状态(0:正常 1:异常)
            bit[5]      驱动器错误状态(0:正常 1:错误)
            bit[6]      驱动器使能状态(1:使能 0:失能)
            bit[7]      回零状态(0:没有回零 1:已经回零,或已经回过零)
        Byte 7: 保留
    '''
    '''
    Gripper Feedback Message

    CAN ID:
        0x2A8
    
    Args:
        grippers_angle: The angle of the gripper, represented as an integer.
        grippers_effort: The torque of the gripper, represented as an integer.
        status_code: The status code of the gripper, represented as an integer.
    
    Bit Definitions:

        Byte Definitions:
        Byte 0: Gripper Stroke (Most Significant Byte), int32, unit: 0.001 mm
        Byte 1: Gripper Stroke (Second Most Significant Byte)
        Byte 2: Gripper Stroke (Second Least Significant Byte)
        Byte 3: Gripper Stroke (Least Significant Byte)
        Byte 4: Gripper Torque (High Byte), int16, unit: 0.001 N·m
        Byte 5: Gripper Torque (Low Byte)
        Byte 6: Status Code, uint8:
            bit[0]: Power voltage low (0: Normal, 1: Low)
            bit[1]: Motor over-temperature (0: Normal, 1: Over-temperature)
            bit[2]: Driver over-current (0: Normal, 1: Over-current)
            bit[3]: Driver over-temperature (0: Normal, 1: Over-temperature)
            bit[4]: Sensor status (0: Normal, 1: Abnormal)
            bit[5]: Driver error status (0: Normal, 1: Error)
            bit[6]: Driver enable status (1: Enabled, 0: Disabled)
            bit[7]: Zeroing status (0: Not zeroed, 1: Zeroed or previously zeroed)
        Byte 7: Reserved
    '''
    def __init__(self, grippers_angle: int=0, grippers_effort: int=0, status_code: int=0):
        self.grippers_angle = grippers_angle
        self.grippers_effort = grippers_effort
        self._status_code = status_code
        self.foc_status = self.FOC_Status()
    
    class FOC_Status:
        def __init__(self):
            self.voltage_too_low  = False
            self.motor_overheating = False
            self.driver_overcurrent = False
            self.driver_overheating = False
            self.sensor_status = False
            self.driver_error_status = False
            self.driver_enable_status = False
            self.homing_status  = False
        def __str__(self): 
            return (f"    voltage_too_low : {self.voltage_too_low}\n"
                    f"    motor_overheating: {self.motor_overheating}\n"
                    f"    driver_overcurrent: {self.driver_overcurrent}\n"
                    f"    driver_overheating: {self.driver_overheating}\n"
                    f"    sensor_status: {self.sensor_status}\n"
                    f"    driver_error_status: {self.driver_error_status}\n"
                    f"    driver_enable_status: {self.driver_enable_status}\n"
                    f"    homing_status: {self.homing_status}\n"
                    )
    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value: int):
        if not (0 <= value < 2**8):
            raise ValueError("status_code must be an 8-bit integer between 0 and 255.")
        self._status_code = value
        # Update foc_status based on the status_code bits
        self.foc_status.voltage_too_low = bool(value & (1 << 0))
        self.foc_status.motor_overheating = bool(value & (1 << 1))
        self.foc_status.driver_overcurrent = bool(value & (1 << 2))
        self.foc_status.driver_overheating = bool(value & (1 << 3))
        self.foc_status.sensor_status = bool(value & (1 << 4))
        self.foc_status.driver_error_status = bool(value & (1 << 5))
        self.foc_status.driver_enable_status = bool(value & (1 << 6))
        self.foc_status.homing_status = bool(value & (1 << 7))
    
    def __str__(self):
        return (f"ArmMsgGripperFeedBack(\n"
                f"  grippers_angle: {self.grippers_angle}, {self.grippers_angle * 0.001:.3f},\n"
                f"  grippers_effort: {self.grippers_effort} \t {self.grippers_effort * 0.001:.2f},\n"
                f"  status_code: \n{self.foc_status}\n"
                f")")

    def __repr__(self):
        return self.__str__()

class ArmMsgGripperCtrl:
    '''
    夹爪控制指令
    
    CAN ID:
        0x159
    
    Args:
        grippers_angle: 夹爪行程
        grippers_effort: 夹爪扭矩
        status_code: 夹爪使能/失能/清除错误
        set_zero: 夹爪零点设置
    
    位描述:
    
        Byte 0 grippers_angle: int32, 单位 0.001°, 夹爪角度,以整数表示。
        Byte 1
        Byte 2
        Byte 3
        Byte 4 grippers_effort: uint16, 单位 0.001N/m, 夹爪扭矩,以整数表示。
        Byte 5
        Byte 6 status_code: uint8, 夹爪状态码，使能/失能/清除错误
                0x00失能,0x01使能
                0x03/0x02,使能清除错误,失能清除错误
        Byte 7 set_zero: uint8, 设定当前位置为0点
                0x00无效值
                0xAE设置零点
    '''
    '''
    Gripper Control Command

    CAN ID:
        0x159

    Args:
        grippers_angle: Gripper stroke, represented as an integer, unit: 0.001°.
        grippers_effort: Gripper torque, represented as an integer, unit: 0.001N·m.
        status_code: Gripper state for enable/disable/clear error.
            0x00: Disable.
            0x01: Enable.
            0x03/0x02: Enable with clear error / Disable with clear error.
        set_zero: Set the current position as the zero point.

    Bit Description:

        Byte 0-3 grippers_angle: int32, unit: 0.001°, represents the gripper angle.
        Byte 4-5 grippers_effort: uint16, unit: 0.001N·m, represents the gripper torque.
        Byte 6 status_code: uint8, gripper status code for enable/disable/clear error.
        Byte 7 set_zero: uint8, flag to set the current position as the zero point.
    '''
    def __init__(self, 
                 grippers_angle: int=0, 
                 grippers_effort: int=0, 
                 status_code: Literal[0x00,0x01,0x02,0x03]=0,
                 set_zero: Literal[0x00,0xAE]=0):
        if status_code not in [0x00, 0x01, 0x02, 0x03]:
            raise ValueError(f"status_code 值 {status_code} 超出范围 [0x00, 0x01, 0x02, 0x03]")
        self.grippers_angle = grippers_angle
        self.grippers_effort = grippers_effort
        self.status_code = status_code
        self.set_zero = set_zero

    def __str__(self):
        return (f"ArmMsgGripperCtrl(\n"
                f"  grippers_angle: {self.grippers_angle * 0.001:.3f},\n"
                f"  grippers_effort: {self.grippers_effort * 0.01:.2f},\n"
                f"  status_code: {self.status_code},\n"
                f"  set_zero: {self.set_zero}\n"
                f")")

    def __repr__(self):
        return self.__str__()


class ArmJoint:
    """
    机械臂关节角度和夹爪二次封装类,将夹爪和关节角度信息放在一起,增加时间戳
    """

    """
    Secondary Encapsulation Class for Robotic Arm Joint Angles and Gripper, 
    Combine Gripper and Joint Angle Information Together, Add Timestamp
    """

    def __init__(self):
        self.time_stamp: float = 0
        self.Hz: float = 0
        self.joint_state = ArmMsgJointFeedBack()

    def __str__(self):
        return (
            f"time stamp:{self.time_stamp}\n"
            f"Hz:{self.Hz}\n"
            f"{self.joint_state}\n"
        )   

class ArmEndPose:
    """
    机械臂末端姿态二次封装类,增加时间戳
    """

    """
    Secondary Encapsulation Class for Robotic Arm End-Effector Pose, Add Timestamp
    """

    def __init__(self):
        self.time_stamp: float = 0
        self.Hz: float = 0
        self.end_pose = ArmMsgEndPoseFeedBack()

    def __str__(self):
        return (
            f"time stamp:{self.time_stamp}\n" f"Hz:{self.Hz}\n" f"{self.end_pose}\n"
        )
        
class ArmGripper:
    """
    机械臂关节角度和夹爪二次封装类,将夹爪和关节角度信息放在一起,增加时间戳
    """

    """
    Secondary Encapsulation Class for Robotic Arm Joint Angles and Gripper, 
    Combining Gripper and Joint Angle Information Together, with Timestamp
    """

    def __init__(self):
        self.time_stamp: float = 0
        self.Hz: float = 0
        self.gripper_state = ArmMsgGripperFeedBack()

    def __str__(self):
        return (
            f"time stamp:{self.time_stamp}\n"
            f"Hz:{self.Hz}\n"
            f"{self.gripper_state}\n"
        )

class ArmJointCtrl:
    """
    机械臂关节角度和夹爪二次封装类,将夹爪和关节角度信息放在一起,增加时间戳
    这个是主臂发送的消息，用来读取发送给从臂的目标值
    """

    """
    Secondary Encapsulation Class for Robotic Arm Joint Angles and Gripper, Combining Gripper and Joint Angle Information, Adding Timestamp
    This is the message sent by the main arm to read the target values sent to the slave arm.
    """

    def __init__(self):
        self.time_stamp: float = 0
        self.Hz: float = 0
        self.joint_ctrl = ArmMsgJointCtrl()

    def __str__(self):
        return f"time stamp:{self.time_stamp}\n" f"{self.joint_ctrl}\n"

class ArmGripperCtrl:
    """
    机械臂关节角度和夹爪二次封装类,将夹爪和关节角度信息放在一起,增加时间戳
    这个是主臂发送的消息，用来读取发送给从臂的目标值
    """

    """
    Secondary Encapsulation Class for Robotic Arm Joint Angles and Gripper, Combining Gripper and Joint Angle Information, Adding Timestamp
    This is a message sent by the main arm to read the target values sent to the slave arm.
    """

    def __init__(self):
        self.time_stamp: float = 0
        self.Hz: float = 0
        self.gripper_ctrl = ArmMsgGripperCtrl()

    def __str__(self):
        return f"time stamp:{self.time_stamp}\n" f"{self.gripper_ctrl}\n"

class ArmMsgJointCtrl():
    '''
    机械臂关节控制,单位0.001度
    
    CAN ID:
        0x155,0x156,0x157
    
    Args:
        joint_1: joint_1角度
        joint_2: joint_2角度
        joint_3: joint_3角度
        joint_4: joint_4角度
        joint_5: joint_5角度
        joint_6: joint_6角度
    '''
    '''
    Robotic Arm Joint Control (Unit: 0.001°)

    CAN IDs:
        0x155, 0x156, 0x157
    
    Args:
        joint_1: The target angle of joint 1 in 0.001°.
        joint_2: The target angle of joint 2 in 0.001°.
        joint_3: The target angle of joint 3 in 0.001°.
        joint_4: The target angle of joint 4 in 0.001°.
        joint_5: The target angle of joint 5 in 0.001°.
        joint_6: The target angle of joint 6 in 0.001°.
    '''
    def __init__(self, joint_1: int=0, joint_2: int=0, 
                 joint_3: int=0, joint_4: int=0, 
                 joint_5: int=0, joint_6: int=0):
        self.joint_1 = joint_1
        self.joint_2 = joint_2
        self.joint_3 = joint_3
        self.joint_4 = joint_4
        self.joint_5 = joint_5
        self.joint_6 = joint_6

    def __str__(self):
        # 将角度乘以0.001，并保留三位小数
        joint_angles = [
            ("Joint_1", self.joint_1 * 0.001),
            ("Joint_2", self.joint_2 * 0.001),
            ("Joint_3", self.joint_3 * 0.001),
            ("Joint_4", self.joint_4 * 0.001),
            ("Joint_5", self.joint_5 * 0.001),
            ("Joint_6", self.joint_6 * 0.001)
        ]

        # 生成格式化字符串，保留三位小数
        formatted_angles = "\n".join([f"{name}: {angle:.3f}" for name, angle in joint_angles])
        
        return f"ArmMsgJointCtrl:\n{formatted_angles}"
    
    def __repr__(self):
        return self.__str__()