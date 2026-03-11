export CUDA_VISIBLE_DEVICES=0
source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
python /home/go2/ARX_X5/inference/pi0_infer.py \
--frame_rate 25 \
--momentum 0 \
--chunk_size 50 \
--normalize_actions