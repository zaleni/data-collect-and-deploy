import pickle
import numpy as np
doc = pickle. load(open('/home/robot/mzk_workspace/data_collect/tmp/verify_data/vd.pickle', 'rb'))

# print(len(doc))
# print(doc[0])
# print(len(doc[30][1]))
# print(doc[30][1])

all_state = []
all_action = []
diff = []

for data_sample in doc:
    for sample in data_sample:
        # print(sample["state"][:3])
        # print(sample["state"][6:])
        # state = np.concatenate([sample["state"][:3], sample["state"][6:]])
        # action = np.concatenate([sample["action"][:3], sample["action"][6:]])
        state = sample["state"]
        action = sample["action"]
        all_state.append(state)
        # print(np.concatenate([sample["state"][:3], sample["state"][6:]]))
        all_action.append(action)
        different = action-state
        different[different>60000] = -1000
        different[different<-60000] = 1000
        diff.append(different)
        
        
all_state = np.stack(all_state)
all_action = np.stack(all_action)
diff = np.stack(diff)

state_mean = np.mean(all_state, axis = 0)
action_mean = np.mean(all_action, axis = 0)
diff_mean = np.mean(diff, axis = 0)
# print(state_mean)

# print(action_mean)
# print(diff_mean)
# print(np.min(np.abs(diff)))
diff_sum = np.sum(np.abs(diff), axis = 1)
print(diff_sum.shape)
diff_sum[diff_sum>10000]=10000
print(np.sum(diff_sum<500))
# print(diff_sum.shape)
import matplotlib.pyplot as plt

# # 生成示例数据（正态分布）
# data = np.random.randn(100000)

# 计算直方图，分为256个区间
counts, bins = np.histogram(diff_sum, bins=256)

# print(counts)
# print(bins)

# 绘制条形图
plt.figure(figsize=(10, 6))
plt.bar(bins[:-1], counts, width=np.diff(bins), align='edge', alpha=0.7, edgecolor='none')

# 添加标签和标题
plt.xlabel('Value Bins')
plt.ylabel('Frequency')
plt.title('Distribution of Values Discretized into 256 Bins')

# 显示图形
plt.savefig("./fig/hh.jpg")

# diff_mean = np.mean(diff_sum, axis = 0)
# print(diff_mean)



# print(all_state.shape)
# print(len(all_state))


