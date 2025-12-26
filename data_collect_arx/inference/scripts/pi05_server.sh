source /home/pc3/deploy/pi05/.venv/bin/activate
# source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
CUDA_VISIBLE_DEVICES=0 XLA_PYTHON_CLIENT_PREALLOCATE=false python /home/pc3/deploy/openpi/scripts_/deploy_server.py \
--checkpoint_bucket /home/go2/ARX_X5/inference/ckpt/all/29999 \
--config_name pi05_base_real_lora