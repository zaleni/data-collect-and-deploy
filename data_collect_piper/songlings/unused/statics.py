from utils import (
    parser_endpose_from_stream,
    parser_gripper_from_stream,
    parser_endpose_from_stream,
    parser_joint_ctrl_from_stream,
    parser_gripper_ctrl_from_stream,
)

follower_joint = list(parser_endpose_from_stream('data/ano/clean_10/04-03AAA11:36/follower_joint'))
follower_gripper = list(parser_gripper_from_stream('data/ano/clean_10/04-03AAA11:36/follower_gripper'))
follower_eef = list(parser_endpose_from_stream('data/ano/clean_10/04-03AAA11:36/follower_endpose'))

leader_joint = list(parser_joint_ctrl_from_stream('data/ano/clean_10/04-03AAA11:36/leader_joint'))
leader_gripper = list(parser_gripper_ctrl_from_stream('data/ano/clean_10/04-03AAA11:36/leader_gripper'))
# leader_eef = list(parser_endpose_from_stream('data/02-28@16:47:20/leader_endpose'))

def make_correct_timestamp(l):
    for item in l:
        item.time_stamp /= 1e9
    return l
        
follower_gripper = make_correct_timestamp(follower_gripper)
leader_gripper = make_correct_timestamp(leader_gripper)

time_span = lambda l : l[-1].time_stamp - l[0].time_stamp
item_per_sencond = lambda l : len(l) / time_span(l)

print(f'time_span: {time_span(follower_joint)}')

print(f'len(follower_joint): {len(follower_joint)}')
print(f'len(follower_gripper): {len(follower_gripper)}')
print(f'len(follower_eef): {len(follower_eef)}')
print(f'len(leader_joint): {len(leader_joint)}')
print(f'len(leader_gripper): {len(leader_gripper)}')
# print(f'len(leader_eef): {len(leader_eef)}')

print(f'follower joint frequency: {item_per_sencond(follower_joint)}')
print(f'follower gripper frequency: {item_per_sencond(follower_gripper)}')
print(f'follower eef frequency: {item_per_sencond(follower_eef)}')
print(f'leader joint frequency: {item_per_sencond(leader_joint)}')
print(f'leader gripper frequency: {item_per_sencond(leader_gripper)}')
# print(f'leader eef frequency: {item_per_sencond(leader_eef)}')