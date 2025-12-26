import time
import sys
import os



from piper_interface_v2 import C_PiperInterface_V2
from utils import enable_fun
from get_eef_data import RobotController

# ================= 主程序 =================

robot = None
try:
    # 1. 初始化并使能机器人
    robot = RobotController(can_name="can0")
    robot.enable_robot()

    # 2. 检查初始状态
    status = robot.piper.GetArmStatus().arm_status
    print(f"当前机械臂状态: ctrl_mode={status.ctrl_mode}, arm_status={status.arm_status}, err_code={status.err_code}")
    if status.err_code != 0:
        print(f"[错误] 机械臂启动后即处于错误状态 {status.err_code}，无法继续。")
        exit()
    
    # 3. 设置控制模式和运动模式
    print("\n正在设置控制模式为 [CAN指令控制] 和 [MOVE P 模式]...")
    # ctrl_mode=0x01, move_mode=0x00, speed=100%
    robot.piper.MotionCtrl_2(0x01, 0x00, 60) 
    
    # **关键：** 等待模式切换生效
    time.sleep(0.5) 
    print("模式设置指令已发送。")



    # print(f"\n当前姿态 (raw): rx={current_rx_raw}, ry={current_ry_raw}, rz={current_rz_raw}")
    # print(f"目标位置 (mm): x={target_x_mm}, y={target_y_mm}, z={target_z_mm}")
    
    # 5. 发送末端坐标控制指令
    print("正在发送末端坐标指令...")
    robot.piper.EndPoseCtrl(
        # int(target_x_mm * 1000), 
        # int(target_y_mm * 1000), 
        # int(target_z_mm * 1000),
        # current_rx_raw, 
        # current_ry_raw, 
        # current_rz_raw
        162447, 5869, 492958, 145119, 72198, 147610
    )
    
    print("\n移动指令已发送。")
    print("等待机械臂运动...")


    status_aft = robot.piper.GetArmStatus().arm_status
    print(f"hou机械臂状态: ctrl_mode={status_aft.ctrl_mode}, arm_status={status_aft.arm_status}, err_code={status_aft.err_code}")
    
    # 6. 等待并监控位置变化
    # start_time = time.time()
    # timeout = 10 # 等待10秒
    # while time.time() - start_time < timeout:
    #     current_pose = robot.get_eef_pose_raw()
    #     print(f"当前位置 (mm): x={current_pose[0]/1000:.1f}, y={current_pose[1]/1000:.1f}, z={current_pose[2]/1000:.1f}", end='\r')
    #     time.sleep(0.2)
        
    #     # 简单的完成判断（实际应用中需要更复杂的逻辑）
    #     dist_to_target = ( (current_pose[0]/1000 - target_x_mm)**2 + 
    #                        (current_pose[1]/1000 - target_y_mm)**2 + 
    #                        (current_pose[2]/1000 - target_z_mm)**2 )**0.5
    #     if dist_to_target < 5: # 如果距离目标小于5mm，认为到达
    #         print("\n[成功] 机械臂已移动到目标位置附近。")
    #         break
    # else: # 如果循环正常结束（超时）
    #     print("\n[警告] 机械臂在10秒内未到达目标位置。")


except Exception as e:
    print(f"\n[主程序发生错误]: {e}")
finally:
    if robot:
        # 7. 退出前恢复待机模式（好习惯）
        print("\n正在设置机械臂为待机模式...")
        robot.piper.MotionCtrl_2(0x00, 0x00, 100) # ctrl_mode=0x00 待机
        robot.stop()