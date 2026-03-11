source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
# conda activate deploy_act
python /home/go2/ARX_X5/inference/act_infer.py \
--config_path /home/pc3/deploy/RoboTwin/policy/ACT/act_config_umbrella.yaml \
--frame_rate 20 \
--momentum 0.2 \

