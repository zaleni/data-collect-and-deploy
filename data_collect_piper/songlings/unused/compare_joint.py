from utils import parser_endpose_from_stream, ArmJoint
from rich import print


leader = parser_endpose_from_stream('data/02-28@16:47:20/follower_joint')
follower = parser_endpose_from_stream('data/02-28@16:47:20/leader_joint')

convert_to_list = lambda joint: [
    joint.joint_state.joint_1,
    joint.joint_state.joint_2,
    joint.joint_state.joint_3,
    joint.joint_state.joint_4,
    joint.joint_state.joint_5,
    joint.joint_state.joint_6,
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