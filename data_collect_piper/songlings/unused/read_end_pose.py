#!/usr/bin/env python3
# -*-coding:utf8-*-
# 注意demo无法直接运行，需要pip安装sdk后才能运行

from typing import (
    Optional,
)
import time
from piper_sdk import *

import os
from rich import print
from piper_sdk.kinematics.piper_fk import C_PiperForwardKinematics
# 测试代码
if __name__ == "__main__":
    piper = C_PiperInterface_V2()
    piper.ConnectPort()
    # os.system('clear')
    x_range = [float('inf'), float('-inf')]
    y_range = [float('inf'), float('-inf')]
    z_range = [float('inf'), float('-inf')]
    rx_range = [float('inf'), float('-inf')]
    ry_range = [float('inf'), float('-inf')]
    rz_range = [float('inf'), float('-inf')]
    while True:
        os.system('clear')
        print(f'Endpose')
        pose = piper.GetArmEndPoseMsgs()
        joint = piper.GetArmJointMsgs()
        
        print(joint)
        print(pose)
        x = pose.end_pose.X_axis
        y = pose.end_pose.Y_axis
        z = pose.end_pose.Z_axis
        rx = pose.end_pose.RX_axis
        ry = pose.end_pose.RY_axis
        rz = pose.end_pose.RZ_axis
        
        x_range[0] = min(x_range[0], x)
        x_range[1] = max(x_range[1], x)
        y_range[0] = min(y_range[0], y)
        y_range[1] = max(y_range[1], y)
        z_range[0] = min(z_range[0], z)
        z_range[1] = max(z_range[1], z)
        rx_range[0] = min(rx_range[0], rx)
        rx_range[1] = max(rx_range[1], rx)
        ry_range[0] = min(ry_range[0], ry)
        ry_range[1] = max(ry_range[1], ry)
        rz_range[0] = min(rz_range[0], rz)
        rz_range[1] = max(rz_range[1], rz)
        
        print(f'x_range: {x_range}')
        print(f'y_range: {y_range}')
        print(f'z_range: {z_range}')
        print(f'rx_range: {rx_range}')
        print(f'ry_range: {ry_range}')
        print(f'rz_range: {rz_range}')
        
        # x_s = -430
        # y_s = -63759
        # z_s = 392301
        
        # x_dist = abs(x - x_s)
        # y_dist = abs(y - y_s)
        # z_dist = abs(z - z_s)
        
        # def get_color(dist):
        #     if dist > 10000:
        #         return '[red]{0}[/red]'
        #     else:
        #         return '[green]{0}[/green]'
        
        x_s = [-16000, 0]
        y_s = [-83000, -72000]
        z_s = [330000, 380000]
        
        def get_color(b, bs):
            if bs[0] <= b <= bs[1]:
                return '[green]{0}[/green]'
            else:
                return '[red]{0}[/red]'
        
        print(get_color(x, x_s).format(f'{x} ----> {x_s}'))
        print(get_color(y, y_s).format(f'{y} ----> {y_s}'))
        print(get_color(z, z_s).format(f'{z} ----> {z_s}'))

        # print()
        # print(f'FK')
        # print()
        # print(piper.GetAllMotorMaxAccLimit())
        time.sleep(0.5)