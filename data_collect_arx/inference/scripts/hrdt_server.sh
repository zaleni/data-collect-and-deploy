source /home/go2/ARX_X5/ROS2/X5_ws/install/setup.bash
cd /home/pc3/deploy/inference/lib
python server.py \
    --lang_embeddings_path /home/go2/ARX_X5/checkpoint/arrange_the_umbrellas.pt \
    --config_path /home/go2/ARX_X5/checkpoint/finetune_real_robot_14d.yaml   \
    --pretrained_model_path /home/go2/ARX_X5/checkpoint/arrange_the_umbrellas/hrdt_14d_norm_cos/checkpoint-10000 \
    --stat_file_path /home/go2/ARX_X5/checkpoint/arrange_the_umbrellas_14d.json \
    --model_dimension 14 \
    --normalize_actions \
    --host 127.0.0.1 \
    --port 9998