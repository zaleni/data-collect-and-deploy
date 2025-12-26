import plotly.graph_objects as go
import numpy as np

from utils import parser_endpose_from_stream, ArmEndPose
from typing import List
from rich import print


eefs : List[ArmEndPose] = list(parser_endpose_from_stream('data/ano/re_clean_dump/04-10AAA00:47:18/follower_endpose'))

times = [item.time_stamp for item in eefs]
xs = [item.end_pose.X_axis / 1000 for item in eefs]
ys = [item.end_pose.Y_axis / 1000 for item in eefs]
zs = [item.end_pose.Z_axis / 1000 for item in eefs]

time0 = times[0]
times = [t - time0 for t in times]

xs = np.array(xs)[::10]
ys = np.array(ys)[::10]
zs = np.array(zs)[::10]
times = np.array(times)

def mean_pooling_with_padding(arr, pool_size):
    if pool_size <= 0:
        raise ValueError("pool_size must be greater than 0")
    
    n = len(arr)
    pad_size = (pool_size - 1) // 2  # 计算两侧需要填充的数量
    padded_arr = np.pad(arr, (pad_size, pad_size), mode='edge')  # 以边界元素填充
    
    pooled_arr = np.convolve(padded_arr, np.ones(pool_size) / pool_size, mode='valid')  # 计算滑动均值
    
    return pooled_arr

pooling_size = 5
fig = go.Figure(go.Scatter3d(
    x=mean_pooling_with_padding(xs, pooling_size),
    y=mean_pooling_with_padding(ys, pooling_size),
    z=mean_pooling_with_padding(zs, pooling_size),
    mode='lines',
    line=dict(width=4, color='green'),
    name="平滑数据"
))

fig.add_trace(go.Scatter3d(
    x=xs, y=ys, z=zs,
    mode='lines+markers',
    line=dict(width=4, color='blue'),
    marker=dict(size=1, color='red'),  # 让点更显眼
    text=[f"Time: {t}, Index: {i}, ({x}, {y}, {z})" for i, (t, x, y, z) in enumerate(zip(times, xs, ys, zs))],  # 作为 hover 标签
    hoverinfo='text',  # 仅显示 text 信息
    name="原始数据"
))


x_min, x_max = -91, 108
y_min, y_max = -230, 0
z_min, z_max = 152, 544
EnableBoundaryCheck = False
if EnableBoundaryCheck:
    # 生成网格点
    x_range = np.linspace(x_min, x_max, 10)
    y_range = np.linspace(y_min, y_max, 10)
    z_range = np.linspace(z_min, z_max, 10)

    # 1️⃣ x = x_min 平面
    Y, Z = np.meshgrid(y_range, z_range)
    X = np.full_like(Y, x_min)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.5, showscale=False, hoverinfo="skip"))

    # 2️⃣ x = x_max 平面
    X = np.full_like(Y, x_max)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.5, showscale=False, hoverinfo="skip"))

    # 3️⃣ y = y_min 平面
    X, Z = np.meshgrid(x_range, z_range)
    Y = np.full_like(X, y_min)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.5, showscale=False, hoverinfo="skip"))

    # 4️⃣ y = y_max 平面
    Y = np.full_like(X, y_max)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.5, showscale=False, hoverinfo="skip"))

    # 5️⃣ z = z_min 平面
    X, Y = np.meshgrid(x_range, y_range)
    Z = np.full_like(X, z_min)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.5, showscale=False, hoverinfo="skip"))

    # 6️⃣ z = z_max 平面
    Z = np.full_like(X, z_max)
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Reds', opacity=0.5, showscale=False, hoverinfo="skip"))

fig.update_layout(scene=dict(
    xaxis=dict(title="X (Left)", range=[max(xs), min(xs)]),  # 反转 X 轴
    yaxis=dict(title="Y (Backward)", range=[max(ys), min(ys)]),  # 反转 Y 轴
    zaxis=dict(title="Z (Up)"),
    aspectmode='cube'  # 保持立方体比例，避免变形
))
fig.show()
# fig.write_html('tmp/index.html')