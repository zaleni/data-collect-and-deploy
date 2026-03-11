#!/usr/bin/env python3
"""
处理HDF5文件中的夹爪数据抖动问题
使用滑动窗口平滑和阈值稳定化方法
处理 endpose/left_gripper, joint_action/left_gripper 和 joint_action/vector
"""

import os
import h5py
import argparse
import numpy as np
from pathlib import Path
import shutil


class GripperSmoother:
    """夹爪数据平滑处理器"""
    def __init__(self, 
                 window_size=5,
                 threshold_ratio=0.05,
                 min_stable_frames=5,
                 open_value=None,
                 closed_value=None):
        """
        Args:
            window_size: 滑动窗口大小
            threshold_ratio: 阈值比例(相对于开合范围)
            min_stable_frames: 最少稳定帧数
            open_value: 打开状态值(自动检测)
            closed_value: 闭合状态值(自动检测)
        """
        self.window_size = window_size
        self.threshold_ratio = threshold_ratio
        self.min_stable_frames = min_stable_frames
        self.open_value = open_value
        self.closed_value = closed_value
        self.threshold = None
    
    def auto_detect_values(self, data):
        """自动检测开合值"""
        self.closed_value = float(np.min(data))
        self.open_value = float(np.max(data))
        
        # 计算阈值
        gripper_range = abs(self.open_value - self.closed_value)
        self.threshold = gripper_range * self.threshold_ratio
        
        return self.closed_value, self.open_value, self.threshold
    
    def smooth_sliding_window(self, data):
        """滑动窗口平滑"""
        if len(data) < self.window_size:
            return data
        
        kernel = np.ones(self.window_size) / self.window_size
        smoothed = np.convolve(data, kernel, mode='same')
        
        # 处理边界
        edge = self.window_size // 2
        smoothed[:edge] = data[:edge]
        smoothed[-edge:] = data[-edge:]
        
        return smoothed
    
    def stabilize_threshold(self, data):
        """阈值稳定化 - 将接近闭合/打开值的数据统一设置"""
        stabilized = data.copy()
        
        # 检测闭合状态
        is_closed = np.abs(data - self.closed_value) < self.threshold
        stabilized[is_closed] = self.closed_value
        
        # 检测打开状态
        is_open = np.abs(data - self.open_value) < self.threshold
        stabilized[is_open] = self.open_value
        
        return stabilized
    
    def lock_stable_states(self, data):
        """状态锁定"""
        locked = data.copy()
        changes = np.abs(np.diff(data, prepend=data[0]))
        
        stable_value = data[0]
        stable_count = 0
        
        for i in range(len(data)):
            if changes[i] < self.threshold:
                stable_count += 1
                if stable_count >= self.min_stable_frames:
                    locked[i] = stable_value
            else:
                stable_value = data[i]
                stable_count = 0
        
        return locked
    
    def process(self, gripper_data):
        """完整处理流程"""
        # 如果没有预设值，自动检测
        if self.closed_value is None or self.open_value is None:
            self.auto_detect_values(gripper_data)
        
        processed = gripper_data.copy()
        
        # 步骤1: 滑动窗口平滑
        processed = self.smooth_sliding_window(processed)
        
        # 步骤2: 阈值稳定化
        processed = self.stabilize_threshold(processed)
        
        # 步骤3: 状态锁定
        processed = self.lock_stable_states(processed)
        
        return processed


def process_hdf5_file(input_path, output_path, processor, method='all', 
                     dry_run=False, visualize=False):
    """
    处理HDF5文件中的夹爪数据
    
    Args:
        input_path: 输入HDF5文件路径
        output_path: 输出HDF5文件路径
        processor: GripperSmoother实例
        method: 处理方法
        dry_run: 只分析不保存
        visualize: 是否可视化对比
    """
    print(f"\n{'='*60}")
    print(f"处理文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"处理方法: {method}")
    print(f"{'='*60}\n")
    
    with h5py.File(input_path, 'r') as f_in:
        # 打印文件结构
        print("HDF5文件结构:")
        print_structure(f_in)
        print()
        
        # 检查必要的数据集
        gripper_datasets = []
        
        # 检查 endpose/left_gripper
        if 'endpose' in f_in and 'left_gripper' in f_in['endpose']:
            gripper_datasets.append('endpose/left_gripper')
        
        # 检查 joint_action/left_gripper
        if 'joint_action' in f_in and 'left_gripper' in f_in['joint_action']:
            gripper_datasets.append('joint_action/left_gripper')
        
        # 检查 joint_action/vector
        if 'joint_action' in f_in and 'vector' in f_in['joint_action']:
            gripper_datasets.append('joint_action/vector')
        
        if not gripper_datasets:
            raise RuntimeError("未找到任何夹爪数据集")
        
        print(f"找到夹爪数据集: {gripper_datasets}\n")
        
        # 处理数据
        processed_data = {}
        
        # 1. 处理 endpose/left_gripper
        if 'endpose/left_gripper' in gripper_datasets:
            endpose_gripper = f_in['endpose/left_gripper'][:]
            
            print(f"endpose/left_gripper 原始数据:")
            print(f"  形状: {endpose_gripper.shape}")
            print(f"  范围: [{endpose_gripper.min():.6f}, {endpose_gripper.max():.6f}]")
            print(f"  均值: {endpose_gripper.mean():.6f}")
            print(f"  标准差: {endpose_gripper.std():.6f}")
            
            # 自动检测开合值
            closed_val, open_val, threshold = processor.auto_detect_values(endpose_gripper)
            
            print(f"\n自动检测夹爪参数:")
            print(f"  闭合值 (最小值): {closed_val:.6f}")
            print(f"  打开值 (最大值): {open_val:.6f}")
            print(f"  开合范围: {abs(open_val - closed_val):.6f}")
            print(f"  稳定化阈值: {threshold:.6f}")
            
            # 处理数据
            endpose_gripper_smoothed = processor.process(endpose_gripper)
            processed_data['endpose/left_gripper'] = endpose_gripper_smoothed
            
            print(f"\nendpose/left_gripper 平滑后:")
            print(f"  范围: [{endpose_gripper_smoothed.min():.6f}, {endpose_gripper_smoothed.max():.6f}]")
            print(f"  均值: {endpose_gripper_smoothed.mean():.6f}")
            print(f"  标准差: {endpose_gripper_smoothed.std():.6f}")
            print(f"  标准差降低: {(1 - endpose_gripper_smoothed.std()/endpose_gripper.std())*100:.1f}%")
            
            # 统计稳定帧数
            closed_frames = np.sum(np.abs(endpose_gripper_smoothed - closed_val) < 1e-6)
            open_frames = np.sum(np.abs(endpose_gripper_smoothed - open_val) < 1e-6)
            print(f"  闭合状态帧数: {closed_frames}/{len(endpose_gripper_smoothed)} ({closed_frames/len(endpose_gripper_smoothed)*100:.1f}%)")
            print(f"  打开状态帧数: {open_frames}/{len(endpose_gripper_smoothed)} ({open_frames/len(endpose_gripper_smoothed)*100:.1f}%)")
        
        # 2. 处理 joint_action/left_gripper
        if 'joint_action/left_gripper' in gripper_datasets:
            joint_gripper = f_in['joint_action/left_gripper'][:]
            
            print(f"\njoint_action/left_gripper 原始数据:")
            print(f"  形状: {joint_gripper.shape}")
            print(f"  范围: [{joint_gripper.min():.6f}, {joint_gripper.max():.6f}]")
            print(f"  标准差: {joint_gripper.std():.6f}")
            
            # 使用相同的处理器（已经检测过开合值）
            joint_gripper_smoothed = processor.process(joint_gripper)
            processed_data['joint_action/left_gripper'] = joint_gripper_smoothed
            
            print(f"\njoint_action/left_gripper 平滑后:")
            print(f"  范围: [{joint_gripper_smoothed.min():.6f}, {joint_gripper_smoothed.max():.6f}]")
            print(f"  标准差: {joint_gripper_smoothed.std():.6f}")
            print(f"  标准差降低: {(1 - joint_gripper_smoothed.std()/joint_gripper.std())*100:.1f}%")
        
        # 3. 处理 joint_action/vector 中的夹爪维度
        if 'joint_action/vector' in gripper_datasets:
            vector_data = f_in['joint_action/vector'][:]
            
            print(f"\njoint_action/vector 原始数据:")
            print(f"  形状: {vector_data.shape}")
            
            # vector 的结构: [left_arm(6), left_gripper(1), right_arm(6), right_gripper(1)] = 14
            # left_gripper 在索引 6
            vector_gripper = vector_data[:, 6]
            
            print(f"  vector[:, 6] (left_gripper):")
            print(f"    范围: [{vector_gripper.min():.6f}, {vector_gripper.max():.6f}]")
            print(f"    标准差: {vector_gripper.std():.6f}")
            
            # 处理夹爪数据
            vector_gripper_smoothed = processor.process(vector_gripper)
            
            # 创建新的vector数据（复制原始数据）
            vector_data_smoothed = vector_data.copy()
            # 替换夹爪维度
            vector_data_smoothed[:, 6] = vector_gripper_smoothed
            
            processed_data['joint_action/vector'] = vector_data_smoothed
            
            print(f"\njoint_action/vector 平滑后:")
            print(f"  vector[:, 6] (left_gripper):")
            print(f"    范围: [{vector_gripper_smoothed.min():.6f}, {vector_gripper_smoothed.max():.6f}]")
            print(f"    标准差: {vector_gripper_smoothed.std():.6f}")
            print(f"    标准差降低: {(1 - vector_gripper_smoothed.std()/vector_gripper.std())*100:.1f}%")
        
        # 可视化对比
        if visualize and 'endpose/left_gripper' in processed_data:
            visualize_comparison(
                endpose_gripper, 
                processed_data['endpose/left_gripper'],
                output_path.replace('.hdf5', '_gripper_comparison.png')
            )
        
        # 保存到新文件
        if not dry_run:
            print(f"\n保存到: {output_path}")
            with h5py.File(output_path, 'w') as f_out:
                # 复制所有其他数据
                exclude_paths = [
                    'endpose/left_gripper',
                    'joint_action/left_gripper', 
                    'joint_action/vector'
                ]
                copy_hdf5_structure(f_in, f_out, exclude_paths=exclude_paths)
                
                # 写入处理后的夹爪数据
                for path, data in processed_data.items():
                    group_name = '/'.join(path.split('/')[:-1])
                    dataset_name = path.split('/')[-1]
                    
                    if group_name not in f_out:
                        f_out.create_group(group_name)
                    
                    f_out[group_name].create_dataset(dataset_name, data=data, dtype=data.dtype)
                    print(f"  ✓ 保存 {path}: shape={data.shape}, dtype={data.dtype}")
                
                # 添加处理元数据
                f_out.attrs['gripper_processed'] = True
                f_out.attrs['processing_method'] = method
                f_out.attrs['window_size'] = processor.window_size
                f_out.attrs['threshold_ratio'] = processor.threshold_ratio
                f_out.attrs['closed_value'] = processor.closed_value
                f_out.attrs['open_value'] = processor.open_value
            
            print(f"✓ 保存成功!")
        else:
            print(f"\n[DRY RUN] 未保存文件")


def print_structure(h5_obj, prefix=""):
    """递归打印HDF5结构"""
    for key in h5_obj.keys():
        item = h5_obj[key]
        if isinstance(item, h5py.Group):
            print(f"{prefix}📁 {key}/")
            print_structure(item, prefix + "  ")
        elif isinstance(item, h5py.Dataset):
            print(f"{prefix}📄 {key}: shape={item.shape}, dtype={item.dtype}")


def copy_hdf5_structure(src, dst, exclude_paths=None):
    """复制HDF5结构,排除指定路径"""
    exclude_paths = exclude_paths or []
    
    def copy_node(src_node, dst_node, path=""):
        for key in src_node.keys():
            current_path = f"{path}/{key}" if path else key
            
            # 检查是否需要排除
            if current_path in exclude_paths:
                continue
            
            item = src_node[key]
            if isinstance(item, h5py.Group):
                dst_group = dst_node.create_group(key)
                # 复制属性
                for attr_key, attr_val in item.attrs.items():
                    dst_group.attrs[attr_key] = attr_val
                # 递归复制
                copy_node(item, dst_group, current_path)
            elif isinstance(item, h5py.Dataset):
                # 复制数据集
                dst_node.create_dataset(key, data=item[:], dtype=item.dtype)
                # 复制属性
                for attr_key, attr_val in item.attrs.items():
                    dst_node[key].attrs[attr_key] = attr_val
    
    copy_node(src, dst)
    
    # 复制根属性
    for attr_key, attr_val in src.attrs.items():
        dst.attrs[attr_key] = attr_val


def visualize_comparison(original, processed, save_path):
    """可视化原始数据和处理后数据的对比"""
    try:
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # 原始数据
        axes[0].plot(original, 'b-', linewidth=0.5, alpha=0.7, label='Original')
        axes[0].set_title('Original Gripper Data', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Position')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        
        # 处理后数据
        axes[1].plot(processed, 'r-', linewidth=0.5, alpha=0.7, label='Processed')
        axes[1].set_title('Processed Gripper Data', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Position')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        
        # 对比
        axes[2].plot(original, 'b-', linewidth=0.5, alpha=0.5, label='Original')
        axes[2].plot(processed, 'r-', linewidth=1, alpha=0.7, label='Processed')
        axes[2].set_title('Comparison', fontsize=12, fontweight='bold')
        axes[2].set_xlabel('Frame')
        axes[2].set_ylabel('Position')
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"\n✓ 可视化图表已保存到: {save_path}")
        plt.close()
        
    except ImportError:
        print("⚠️ matplotlib未安装,跳过可视化")


def batch_process(input_dir, output_dir, processor, method='all', pattern='*.hdf5'):
    """批量处理目录中的所有HDF5文件"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 查找所有HDF5文件
    hdf5_files = list(input_path.glob(pattern))
    
    if len(hdf5_files) == 0:
        print(f"❌ 未找到匹配的文件: {input_path / pattern}")
        return
    
    print(f"\n找到 {len(hdf5_files)} 个文件")
    
    # 处理每个文件
    for i, input_file in enumerate(hdf5_files, 1):
        output_file = output_path / f"processed_{input_file.name}"
        
        print(f"\n[{i}/{len(hdf5_files)}] 处理: {input_file.name}")
        
        try:
            process_hdf5_file(str(input_file), str(output_file), processor, method)
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*60}")
    print(f"批量处理完成! 输出目录: {output_path}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='处理HDF5文件中的夹爪数据抖动',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个文件
  python3 process_gripper.py episode_0.hdf5 -o processed_episode_0.hdf5
  
  # 自动检测开合值并平滑
  python3 process_gripper.py episode_0.hdf5 --method all
  
  # 批量处理
  python3 process_gripper.py /home/go2/ARX_X5/main/umbrella_1108 --batch -o /home/go2/ARX_X5/main/umbrella_1108/processed_datasets/
  
  # 只分析不保存 + 可视化
  python3 process_gripper.py episode_0.hdf5 --dry-run --visualize
  
说明:
  - 自动从数据中检测 left_gripper 的最大值和最小值
  - 同时处理 endpose/left_gripper, joint_action/left_gripper 和 joint_action/vector[:, 6]
  - right_gripper 保持不变
        """
    )
    
    parser.add_argument('input', help='输入HDF5文件或目录')
    parser.add_argument('-o', '--output', help='输出HDF5文件或目录')
    parser.add_argument('--method', 
                       choices=['smooth', 'threshold', 'lock', 'binary', 'all'],
                       default='all',
                       help='处理方法 (default: all)')
    parser.add_argument('--window-size', type=int, default=5,
                       help='滑动窗口大小 (default: 5)')
    parser.add_argument('--threshold-ratio', type=float, default=0.05,
                       help='阈值比例相对于夹爪范围 (default: 0.05 = 5%%)')
    parser.add_argument('--min-stable-frames', type=int, default=10,
                       help='状态锁定最少稳定帧数 (default: 10)')
    parser.add_argument('--batch', action='store_true',
                       help='批量处理目录')
    parser.add_argument('--pattern', default='*.hdf5',
                       help='批量处理时的文件匹配模式 (default: *.hdf5)')
    parser.add_argument('--dry-run', action='store_true',
                       help='只分析不保存')
    parser.add_argument('--visualize', action='store_true',
                       help='生成可视化对比图')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = GripperSmoother(
        window_size=args.window_size,
        threshold_ratio=args.threshold_ratio,
        min_stable_frames=args.min_stable_frames
    )
    
    # 检查输入
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 错误: 路径不存在 - {args.input}")
        return
    
    # 批量处理
    if args.batch:
        if not input_path.is_dir():
            print(f"❌ 错误: 批量处理需要目录路径")
            return
        
        output_dir = args.output or str(input_path / 'processed')
        batch_process(str(input_path), output_dir, processor, args.method, args.pattern)
    
    # 单文件处理
    else:
        if not input_path.is_file():
            print(f"❌ 错误: 不是有效的文件 - {args.input}")
            return
        
        # 确定输出路径
        if args.output:
            output_path = args.output
        else:
            output_path = str(input_path.parent / f"processed_{input_path.name}")
        
        process_hdf5_file(
            str(input_path), 
            output_path, 
            processor, 
            args.method,
            args.dry_run,
            args.visualize
        )


if __name__ == '__main__':
    main()