import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from queue import Queue, Empty
from sensor_msgs.msg import Image as ImageMSG
from cv_bridge import CvBridge
from ros_numpy import numpify
import rospy

# 使用线程安全队列，最大长度为1以保存最新图像
image1_queue = Queue(maxsize=1)
image2_queue = Queue(maxsize=1)

class ImageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Image Update")
        # 初始化为随机图像
        self.last_image1 = (np.random.rand(480, 640, 3) * 255).astype(np.uint8)
        self.last_image2 = (np.random.rand(480, 640, 3) * 255).astype(np.uint8)

        # 图像显示标签
        self.label1 = tk.Label(root)
        self.label1.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.label2 = tk.Label(root)
        self.label2.pack(side=tk.BOTTOM, padx=10, pady=10)

        # 初始占位图像
        self.photo1 = ImageTk.PhotoImage(Image.new("RGB", (640, 480), "black"))
        self.label1.config(image=self.photo1)
        self.photo2 = ImageTk.PhotoImage(Image.new("RGB", (640, 480), "black"))
        self.label2.config(image=self.photo2)

        # 控制更新任务的状态
        self.running = True
        self.scheduled_update = False  # 标记是否有待处理的更新任务
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

    def update_image(self, image_array1, image_array2):
        """更新图像，允许其中一个为None"""
        if image_array1 is not None:
            # 转换并更新图像1
            img = Image.fromarray(image_array1)
            self.photo1 = ImageTk.PhotoImage(img)
            self.label1.config(image=self.photo1)
        if image_array2 is not None:
            # 转换并更新图像2
            img = Image.fromarray(image_array2)
            self.photo2 = ImageTk.PhotoImage(img)
            self.label2.config(image=self.photo2)

    def update_loop(self):
        """从队列获取最新图像并调度更新"""
        while self.running:
            time.sleep(1 / 30)  # 控制循环频率
            # 非阻塞获取队列中的最新图像
            new_image1, new_image2 = None, None
            try:
                new_image1 = image1_queue.get_nowait()
            except Empty:
                pass
            try:
                new_image2 = image2_queue.get_nowait()
            except Empty:
                pass
            # 如果有新数据且无待处理任务，则调度更新
            if (new_image1 is not None or new_image2 is not None) and not self.scheduled_update:
                self.scheduled_update = True
                self.root.after(0, self.process_update, new_image1, new_image2)

    def process_update(self, img1, img2):
        """执行图像更新并重置标记"""
        self.update_image(img1, img2)
        self.scheduled_update = False

    def close(self):
        """关闭时停止线程"""
        self.running = False
        self.root.quit()

# ROS回调函数
def cb1(msg):
    try:
        cv_image = numpify(msg)
        # 非阻塞放入队列，若满则替换旧数据
        if image1_queue.full():
            image1_queue.get_nowait()
        image1_queue.put_nowait(cv_image)
    except Exception as e:
        rospy.logerr(f"Error processing image1: {e}")

def cb2(msg):
    try:
        cv_image = numpify(msg)
        if image2_queue.full():
            image2_queue.get_nowait()
        image2_queue.put_nowait(cv_image)
    except Exception as e:
        rospy.logerr(f"Error processing image2: {e}")

# 初始化ROS和GUI
rospy.init_node('display_image', anonymous=True)
rospy.Subscriber('/ob_camera_01/color/image_raw', ImageMSG, cb1)
rospy.Subscriber('/ob_camera_02/color/image_raw', ImageMSG, cb2)

root = tk.Tk()
gui = ImageGUI(root)
root.protocol("WM_DELETE_WINDOW", gui.close)
root.mainloop()