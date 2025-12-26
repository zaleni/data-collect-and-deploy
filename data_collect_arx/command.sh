source ./install/setup.bash
ros2 topic echo /arm_status  arx5_arm_msg/msg/RobotStatus
ros2 topic echo /end_pose
ros2 topic list
ros2 node list



/home/go2/ARX_X5/ROS2/X5_ws/install/arx_x5_controller/share/arx_x5_controller

source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash

-2.11,-0.00,0.52,-1.29,-1.14,-1.57,0.00
2.38,2.60,2.23,0.25,1.47,1.69,5.31


workspace=$(pwd)
source ~/.bashrc

# CAN
gnome-terminal -t "can" -x sudo bash -c "cd ${workspace};cd ../.. ; cd ARX_CAN/arx_can; ./arx_can1.sh; exec bash;"
sleep 1
#x7s
gnome-terminal -t "L" -x  bash -c "cd ${workspace}; cd ../..; cd ROS2/X5_ws; source install/setup.bash && ros2 launch arx_x5_controller open_single_arm.launch.py; exec bash;"
sleep 0.1

1.16,2.5,3.0,0,1,1.72,5.3
-1.58,0.36,1.15,-1.3,-1,-1.72,0.1




#1225


#部署
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
python /home/go2/ARX_X5/inference/inference.py




#ARX keyboard
conda activate ARX
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
source /home/go2/ARX_X5/py/arx_x5_python/setup.sh
source ~/unitree_ros2/setup.sh
export PYTHONPATH=$PYTHONPATH:/home/go2/miniconda3/envs/ARX/lib/python3.8/site-packages
python /home/go2/ARX_X5/py/arx_x5_python/test_keyboard.py



##从臂
conda activate ARX
cd /home/go2/ARX_X5/ARX_CAN/arx_can
./arx_can1.sh
#主臂
conda activate ARX
cd /home/go2/ARX_X5/ARX_CAN/arx_can
./arx_can0.sh

#主从臂采集
conda activate ARX
cd /home/go2/ARX_X5/ROS2/X5_ws
source install/setup.bash
ros2 launch arx_x5_controller open_remote_master.launch.py

conda activate ARX
cd /home/go2/ARX_X5/ROS2/X5_ws
source install/setup.bash
ros2 launch arx_x5_controller open_remote_slave.launch.py



#collect

conda activate ARX
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
python /home/go2/ARX_X5/main/collect_noop.py
python3 process_gripper.py /home/go2/ARX_X5/main/duikang_1226 --batch -o /home/go2/ARX_X5/main/duikang_1226/processed
python3 process_gripper.py /home/go2/ARX_X5/main/Fuji_1225 --batch -o /home/go2/ARX_X5/main/Fuji_1225/processed
python3 process_gripper.py /home/go2/ARX_X5/main/Mc_1225 --batch -o /home/go2/ARX_X5/main/Mc_1225/processed
python3 process_gripper.py /home/go2/ARX_X5/main/tissue_1225 --batch -o /home/go2/ARX_X5/main/tissue_1225/processed
python3 process_gripper.py /home/go2/ARX_X5/main/Vida_1225 --batch -o /home/go2/ARX_X5/main/Vida_1225/processed

#主从臂重播
conda activate ARX
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
cd /home/go2/ARX_X5/main
python replay.py /home/go2/ARX_X5/main/umbrella_1107/episode_0.hdf5


python replay.py /home/go2/ARX_X5/main/duikang_1226/episode_0.hdf5 --init-interpolation --rate 30



#ARX
conda activate ARX
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
cd  /home/go2/ARX_X5/00-sh/ROS2
dog@123
./04single_arm.sh

conda activate ARX
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
python /home/go2/ARX_X5/main/set_init.py



#piper
conda activate ARX
source /home/go2/piper_ros/install/setup.bash
export PYTHONPATH=$PYTHONPATH:/home/go2/miniconda3/envs/ARX/lib/python3.8/site-packages
bash /home/go2/piper_ros/can_activate.sh can0 1000000

ros2 launch piper start_single_piper.launch.py can_port:=can0 auto_enable:=true


source /home/go2/piper_ros/install/setup.bash
export PYTHONPATH=$PYTHONPATH:/home/go2/miniconda3/envs/ARX/lib/python3.8/site-packages
ros2 topic echo /arm_status

#collect
conda activate ARX
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
source /home/go2/piper_ros/install/setup.bash
python /home/go2/ARX_X5/run/BridgeControl.py




#6 7 9 11 13 17 19

#camera
conda activate ARX
. /home/go2/ARX_X5/ros2_ws/install/setup.bash
ros2 launch orbbec_camera dabai_dcw.launch.py


cd /home/go2/ARX_X5/ros2_ws
colcon build --event-handlers  console_direct+  --cmake-args  -DCMAKE_BUILD_TYPE=Release
ros2 run orbbec_camera list_devices_node


！#multi-camera
echo 256 | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb

conda activate ARX
. /home/go2/ARX_X5/ros2_ws/install/setup.bash
ros2 launch orbbec_camera multi_camera.launch.py



conda activate ARX
. /home/go2/ARX_X5/ros2_ws/install/setup.bash
cd /home/go2/ARX_X5/ros2_ws
rviz2


#record
conda activate ARX
. /home/go2/ARX_X5/ros2_ws/install/setup.bash
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
python /home/go2/ARX_X5/run/record.py


#replay
conda activate ARX
. /home/go2/ARX_X5/ros2_ws/install/setup.bash
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
python /home/go2/ARX_X5/run/replay_joints.py /home/go2/ARX_X5/run/save/record_20250905_154437/joints.csv


conda activate ARX
. /home/go2/ARX_X5/ros2_ws/install/setup.bash
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
ros2 topic echo /arm_cmd





ros2 topic echo /arm_status
ros2 topic echo /camera/color/image_raw
ros2 topic list
ros2 service list
ros2 param list



cd /home/go2/ARX_X5/main
python collect.py --datasets datasets --episode_idx -1 --max_timesteps 800