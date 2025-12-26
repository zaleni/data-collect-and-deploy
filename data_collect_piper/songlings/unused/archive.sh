#!/bin/bash

# 检查参数是否正确
if [ $# -ne 1 ]; then
    echo "用法: $0 <目标路径>"
    exit 1
fi

target_path="$1"

# 验证目标路径是否存在
if [ ! -d "$target_path" ]; then
    echo "错误: 路径 $target_path 不存在或不是目录"
    exit 1
fi

# 查找目标路径下所有直接子目录
find "$target_path" -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
    # 获取目录名和父路径
    dir_name=$(basename "$dir")
    parent_dir=$(dirname "$dir")
    
    # 压缩文件名
    tar_file="${dir}.tar.gz"
    
    echo "正在压缩目录: $dir"
    
    # 执行压缩（保留目录结构）
    if tar czf "$tar_file" -C "$parent_dir" "$dir_name"; then
        echo "成功创建压缩包: $tar_file"
        # 删除原目录
        rm -rf "$dir"
        echo "已删除目录: $dir"
    else
        echo "错误: $dir 压缩失败，跳过删除操作" >&2
    fi
done

echo "操作完成"