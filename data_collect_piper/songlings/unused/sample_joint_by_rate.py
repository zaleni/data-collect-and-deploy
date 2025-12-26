from utils import parser_joint_from_stream, joint_to_bytes


# input_file = 'data/03-04@11:07:27/follower_joint'
# output_file = 'data/03-04@11:07:27/follower_joint_downsample_10hz'
input_file = 'data/03-05@11:02:44/follower_joint'
output_file = 'data/03-05@11:02:44/follower_joint_downsample_10hz'
sample_rate = 1 / 10

eefs = parser_joint_from_stream(input_file)
eefs = list(eefs)
last_time = eefs[0].time_stamp

eefs = eefs[1:]

out_eefs = []

for eef in eefs:
    if eef.time_stamp - last_time > sample_rate:
        out_eefs.append(eef)
        last_time = eef.time_stamp

with open(output_file, 'wb') as f:
    for eef in out_eefs:
        f.write(joint_to_bytes(eef))