from utils import parser_endpose_from_stream, ArmEndPose
from rich import print


leader = parser_endpose_from_stream('data/02-28@16:47:20/leader_endpose')
follower = parser_endpose_from_stream('data/02-28@16:47:20/follower_endpose')

convert_to_list = lambda eef: [
    eef.end_pose.X_axis,
    eef.end_pose.Y_axis,
    eef.end_pose.Z_axis,
    eef.end_pose.RX_axis,
    eef.end_pose.RY_axis,
    eef.end_pose.RZ_axis 
]

for i, (l, f) in enumerate(zip(leader, follower)):
    print(f'Index: {i}')
    print(f'Time: {l.time_stamp}')
    print(f'leader:')
    print(convert_to_list(l))
    print(f'follower:')
    print(convert_to_list(f))
    diff = [abs(a - b) for a, b in zip(convert_to_list(l), convert_to_list(f))]
    print(f'Total diff: {sum(diff)}')
    input('>')