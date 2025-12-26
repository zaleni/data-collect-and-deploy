source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
cd /home/go2/ARX_X5/inference
python hrdt_infer.py \
    --model_host 127.0.0.1 \
    --model_port 9998 \
    --chunk_size 16 \
    --frame_rate 15 \
    --momentum 0.5