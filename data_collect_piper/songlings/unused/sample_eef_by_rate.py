from utils import parser_endpose_from_stream, endpose_to_bytes

# input_file = 'data/03-04@11:07:27/follower_endpose'
input_file = 'data/03-04@19:58:40/follower_endpose'
output_file = 'data/03-04@19:58:40/follower_endpose_downsample_10hz'
sample_rate = 1 / 10

eefs = parser_endpose_from_stream(input_file)
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
        f.write(endpose_to_bytes(eef))