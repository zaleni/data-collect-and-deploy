source /home/pc3/deploy/pi05/.venv/bin/activate
# source /home/pc3/deploy/Piper_ros/devel/setup.bash
CUDA_VISIBLE_DEVICES=0 XLA_PYTHON_CLIENT_PREALLOCATE=false python /home/pc3/deploy/openpi/scripts_/deploy_server.py \
--checkpoint_bucket /mnt/pi05/checkpoint_pi05/pi0_real_arrange_the_umbrellas_5_3499 \
--config_name pi0_base_real_full