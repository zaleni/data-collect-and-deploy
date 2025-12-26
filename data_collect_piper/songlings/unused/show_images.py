import tkinter as tk
from PIL import Image, ImageTk
import json
import os

# # 在此处替换为实际的图片路径列表
# image_paths = [
#     "path/to/image1.jpg",
#     "path/to/image2.png",
#     # 添加更多图片路径.
# ]

# doc = json.load(open('files.json', 'r'))
# doc = doc[4]
# left_image_paths = [item['wrist_rgb'] for item in doc]
# right_image_paths = [item['front_rgb'] for item in doc]

img_folder = 'ddata/ano/clean_remake/04-07AAA16:28_夹牛奶盒时移动方向错了一次/follower_endpose'
path1 = f'{img_folder}/front_color'
path2 = f'{img_folder}/wrist_color'

left_image_paths = [
    f'{path1}/{file}' for file in os.listdir(path1)
]
right_image_paths = [
    f'{path2}/{file}' for file in os.listdir(path2)
]

left_image_paths = left_image_paths[:len(right_image_paths)]
right_image_paths = right_image_paths[:len(left_image_paths)]

key = lambda x: float(x.split('/')[-1][:-4].replace('_', '.'))
left_image_paths.sort(key=key)
right_image_paths.sort(key=key)

left_image_paths = left_image_paths[::3]
right_image_paths = right_image_paths[::3]

class DualImagePlayer:
    def __init__(self, master : tk.Tk, left_paths, right_paths):
        self.master = master
        self.left_paths = left_paths
        self.right_paths = right_paths
        self.timer = None
        
        # 图片缓存
        self.left_photos = []
        self.right_photos = []
        self.current_index = 0
        
        # 初始化处理
        self.load_images()
        self.validate_images()
        self.setup_ui()
        self.update_image()

    def load_images(self):
        """加载双路图片到内存"""
        def _load(path_list, target_list):
            for path in path_list:
                try:
                    img = Image.open(path)
                    img = img.resize((400, 300), Image.Resampling.LANCZOS)  # 统一尺寸
                    target_list.append(ImageTk.PhotoImage(img))
                except Exception as e:
                    print(f"图片加载失败：{path}\n错误信息：{str(e)}")
        
        _load(self.left_paths, self.left_photos)
        _load(self.right_paths, self.right_photos)

    def validate_images(self):
        """验证图片有效性"""
        error_msg = ""
        if not self.left_photos:
            error_msg += "左侧图片列表无有效图片\n"
        if not self.right_photos:
            error_msg += "右侧图片列表无有效图片\n"
        if len(self.left_photos) != len(self.right_photos):
            error_msg += "左右图片数量不一致\n"
        
        if error_msg:
            tk.messagebox.showerror("初始化错误", error_msg)
            self.master.destroy()

    def setup_ui(self):
        """构建用户界面"""
        self.master.title("双画面播放器")
        
        # 主显示区域
        main_frame = tk.Frame(self.master)
        main_frame.pack(pady=20)
        
        # 左侧画面
        self.left_label = tk.Label(main_frame)
        self.left_label.pack(side=tk.LEFT, padx=10)
        
        # 右侧画面
        self.right_label = tk.Label(main_frame)
        self.right_label.pack(side=tk.RIGHT, padx=10)
        
        # 控制面板
        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=15)
        
        # 速度控制条
        self.speed_scale = tk.Scale(
            control_frame,
            from_=33,
            to=3000,
            orient=tk.HORIZONTAL,
            label="播放间隔（毫秒）",
            length=350
        )
        self.speed_scale.set(100)
        self.speed_scale.pack(side=tk.LEFT, padx=20)
        
        # 重置按钮
        self.reset_btn = tk.Button(
            control_frame,
            text="重新开始",
            command=self.reset_playback,
            width=12,
            height=2
        )
        self.reset_btn.pack(side=tk.RIGHT, padx=20)

    def update_image(self):
        """更新双画面显示"""
        if self.left_photos and self.right_photos:
            idx = self.current_index % len(self.left_photos)
            
            self.left_label.config(image=self.left_photos[idx])
            self.right_label.config(image=self.right_photos[idx])
            
            self.current_index += 1
            self.timer = self.master.after(self.speed_scale.get(), self.update_image)
            

    def reset_playback(self):
        """重置播放进度"""
        self.current_index = 0
        self.update_image()  # 立即更新显示
        if self.timer is not None:
            self.master.after_cancel(self.timer)
        
        
def main():
    root = tk.Tk()
    DualImagePlayer(root, left_image_paths, right_image_paths)
    root.mainloop()


if __name__ == "__main__":
    main()