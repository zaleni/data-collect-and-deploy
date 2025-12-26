from utils import parser_gripper_from_stream, gripper_to_bytes


# input_file = 'data/03-04@11:07:27/follower_gripper'
# output_file = 'data/03-04@11:07:27/follower_gripper_downsample_10hz'
input_file = 'data/03-05@11:02:44/follower_gripper'
output_file = 'data/03-05@11:02:44/follower_gripper_downsample_10hz'
sample_rate = 1 / 10

grippers = parser_gripper_from_stream(input_file)
grippers = list(grippers)
last_time = grippers[0].time_stamp

grippers = grippers[1:]

out_gippers = []

for gipper in grippers:
    if gipper.time_stamp - last_time > sample_rate:
        out_gippers.append(gipper)
        last_time = gipper.time_stamp

with open(output_file, 'wb') as f:
    for gipper in out_gippers:
        f.write(gripper_to_bytes(gipper))