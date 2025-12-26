from typing import Union, Literal, Final
import os
import sys
from pathlib import Path
import datetime
import json

import cv2
import rospy
import numpy as np
from ros_numpy import numpify
from sensor_msgs.msg import Image as Image_msg
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QColor
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickImageProvider

from utils import joint_ctrl_to_bytes, joint_to_bytes, gripper_ctrl_to_bytes, gripper_to_bytes, endpose_to_bytes
from piper_interface_v2 import MessageSaver, C_PiperInterface_V2
from remote_service import register_service, Trigger, TriggerResponse, SetBool, SetBoolResponse


ImageFolderName : Final[str] = 'img'
ImagePosFront   : Final[str] = 'front'
ImagePosWrist   : Final[str] = 'wrist'
ImageTypeRGB    : Final[str] = 'color'
ImageTypeDepth  : Final[str] = 'depth'

# ImagePos = Literal[ImagePosFront, ImagePosWrist]
ImagePos = Literal['front', 'wrist']
# ImageType = Literal[ImageTypeRGB, ImageTypeDepth]
ImageType = Literal['color', 'depth']

# XRange = [-10375, 6943] # 8659
# YRange = [113748, 126212] # 6232
# ZRange = [381192, 392772] # 5790
# XRange = [-7280, 10038] #1379
# YRange = [-141915, -129451] #-135683
# ZRange = [390063, 401643] #395853


XRange = [-4991,-1991] #-3491
YRange = [-50607, -30607] #-40607
ZRange = [418925, 428925] #423925




class ImageSource:
    @property
    def wrist(self) -> QImage:
        pass
    
    @property
    def front(self) -> QImage:
        pass
    
    @property
    def interval(self) -> int:
        pass
    
    def _make(self, img):
        h, w, c = img.shape
        return QImage(img.data, w, h, QImage.Format_RGB888)

class LiveCameraSource(ImageSource):
    def __init__(self):
        self._image_front = (np.random.rand(640, 360, 3) * 255).astype(np.uint8)
        self._image_wrist = (np.random.rand(640, 360, 3) * 255).astype(np.uint8)

    def get_subscriber(self, pos: ImagePos):
        def func(msg):
            # img = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            # print(f'update camera image')
            img = numpify(msg)
            if pos == ImagePosFront:
                self._image_front = img
            elif pos == ImagePosWrist:
                self._image_wrist = img
        return func

    @property
    def interval(self):
        return 33

    @property
    def front(self):
        return self._make(self._image_front)

    @property
    def wrist(self):
        return self._make(self._image_wrist)
    
class DiskImageSource(ImageSource):
    def __init__(self, image_dir):
        self._image_front = (np.random.rand(640, 360, 3) * 255).astype(np.uint8)
        self._image_wrist = (np.random.rand(640, 360, 3) * 255).astype(np.uint8)
        
        self._create_images(image_dir)
        
    def _create_images(self, image_dir):
        self.front_images = []
        self.wrist_images = []
        image_dir = Path(str(image_dir)) / ImageFolderName
        
        self.front_images = [
            str(image_dir / f'{ImagePosFront}_{ImageTypeRGB}' / item)
            for item in os.listdir(str(image_dir / f'{ImagePosFront}_{ImageTypeRGB}'))
        ]
        self.wrist_images = [
            str(image_dir / f'{ImagePosWrist}_{ImageTypeRGB}' / item)
            for item in os.listdir(str(image_dir / f'{ImagePosWrist}_{ImageTypeRGB}'))
        ]
        
        self.front_images.sort()
        self.wrist_images.sort()
        self.image_count = min(len(self.front_images), len(self.wrist_images))
        self.front_images = self.front_images[:self.image_count]
        self.wrist_images = self.wrist_images[:self.image_count]
        self.front_index = -1
        self.wrist_index = -1
        
    @property
    def interval(self):
        to_timestamp = lambda x: float(x.split('/')[-1].split('.')[-2].replace('_', '.'))
        start_timestamp = [
            to_timestamp(self.front_images[0]),
            to_timestamp(self.wrist_images[0])
        ]
        end_timestamp = [
            to_timestamp(self.front_images[-1]),
            to_timestamp(self.wrist_images[-1])
        ]
        start_timestamp = max(start_timestamp)
        end_timestamp = min(end_timestamp)
        time_span = end_timestamp - start_timestamp
        return int(time_span / self.image_count * 1000)
        
    @property
    def front(self):
        if hasattr(self, "front_images"):
            self.front_index += 1
            img = self.front_images[self.front_index % self.image_count]
            img = QImage(img)
            return img
        return self._make(self._image_front)
    
    @property
    def wrist(self):
        if hasattr(self, "wrist_images"):
            
            self.wrist_index += 1
            img = self.wrist_images[self.wrist_index % self.image_count]
            img = QImage(img)
            return img
        return self._make(self._image_wrist)


class ImageProvider(QQuickImageProvider):
    def __init__(self, image_source: ImageSource):
        super().__init__(QQuickImageProvider.Image) 
        self.image_source = image_source

    def requestImage(self, id, requestedSize):
        """ 必须实现的接口方法 """
        id = id.split('?')[0]
        if id == ImagePosFront:
            return self.image_source.front, self.image_source.front.size()
        elif id == ImagePosWrist:
            return self.image_source.wrist, self.image_source.wrist.size()
        else:
            raise ValueError("Unknown image id")
        
    def set_image_source(self, image_source):
        self.image_source = image_source
        
    def get_interval(self):
        return self.image_source.interval


class SimpleSaver(MessageSaver):
    def __init__(self, base_dir):
        assert base_dir is not None, '提供一个文件夹来保存此次采集的数据先'
        self.base_dir = Path(base_dir)
        self.running = False
        self.run_name = None
        # self.bridge = CvBridge()
        
        rospy.Subscriber('/ob_camera_02/color/image_raw', Image_msg, self.save_image_to(ImagePosFront, ImageTypeRGB, 'img_2_color_count'))
        rospy.Subscriber('/ob_camera_01/color/image_raw', Image_msg, self.save_image_to(ImagePosWrist, ImageTypeRGB, 'img_1_color_count'))
        rospy.Subscriber('/ob_camera_02/depth/image_raw', Image_msg, self.save_image_to(ImagePosFront, ImageTypeDepth, 'img_2_depth_count'))
        rospy.Subscriber('/ob_camera_01/depth/image_raw', Image_msg, self.save_image_to(ImagePosWrist, ImageTypeDepth, 'img_1_depth_count'))
        
    def set_run_name(self, run_name):
        if self.run_name is None:
            self.run_name = run_name
            self.base_dir = self.base_dir / run_name
            if not os.path.exists(self.base_dir):
                os.makedirs(self.base_dir, exist_ok=True)
        else:
            raise ValueError('Run name already set')
        
    def start_saver(self):
        task_name = str(datetime.datetime.now().strftime("%m-%dAAA%H:%M:%S"))
        self.working_dir = self.base_dir / task_name
        os.makedirs(self.working_dir, exist_ok=True)
        
        self.leader_joint_f     = open(self.working_dir / 'leader_joint',     'wb')
        self.leader_gripper_f   = open(self.working_dir / 'leader_gripper',   'wb')
        self.follower_joint_f   = open(self.working_dir / 'follower_joint',   'wb')
        self.follower_gripper_f = open(self.working_dir / 'follower_gripper', 'wb')
        self.follower_ep_f      = open(self.working_dir / 'follower_endpose', 'wb')
        
        for folder in [
            self.working_dir / ImageFolderName / f'{ImagePosFront}_{ImageTypeRGB}',
            self.working_dir / ImageFolderName / f'{ImagePosFront}_{ImageTypeDepth}',
            self.working_dir / ImageFolderName / f'{ImagePosWrist}_{ImageTypeRGB}',
            self.working_dir / ImageFolderName / f'{ImagePosWrist}_{ImageTypeDepth}'
        ]:
            os.makedirs(folder, exist_ok=True)
        
        self.leader_joint_count = 0
        self.leader_gripper_count = 0
        self.follower_joint_count = 0
        self.follower_gripper_count = 0
        self.follower_eef_count = 0
        
        self.img_1_color_count = 0
        self.img_2_color_count = 0
        self.img_1_depth_count = 0
        self.img_2_depth_count = 0
        
        self.running = True
        
    @property
    def last_saving_dir(self):
        if hasattr(self, 'working_dir'):
            return self.working_dir
        else:
            return None
        
    @property
    def runs_folder(self):
        if self.run_name is not None:
            return self.base_dir
        else:
            return None

    def save_leader_joint(self, joint):
        if self.running:
            self.leader_joint_f.write(joint_ctrl_to_bytes(joint))
            self.leader_joint_f.flush()
            self.leader_joint_count += 1

    def save_leader_gripper(self, gripper):
        if self.running:
            self.leader_gripper_f.write(gripper_ctrl_to_bytes(gripper))
            self.leader_gripper_f.flush()
            self.leader_gripper_count += 1

    def save_follower_joint(self, joint):
        if self.running:
            self.follower_joint_f.write(joint_to_bytes(joint))
            self.follower_joint_f.flush()
            self.follower_joint_count += 1

    def save_follower_gripper(self, gripper):
        if self.running:
            self.follower_gripper_f.write(gripper_to_bytes(gripper))
            self.follower_gripper_f.flush()
            self.follower_gripper_count += 1

    def save_follower_endpose(self, ep):
        if self.running:
            self.follower_ep_f.write(endpose_to_bytes(ep))
            self.follower_ep_f.flush()
            self.follower_eef_count += 1

    def save_image_to(self, pos: Union[Literal['front'], Literal['wrist']], cat: Union[Literal['color'], Literal['depth']], counter_name):
        def save_image(msg: Image_msg):
            if self.running:
                # decoding_type = 'bgr8' if cat == 'color' else 'passthrough'
                # cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding=decoding_type)
                cv_image = numpify(msg)
                if cat == ImageTypeRGB:
                    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
                
                timestamp = msg.header.stamp
                timestamp_str = f'{timestamp.to_sec()}'.ljust(20, '0').replace('.', '_')
                image_filename = self.working_dir / ImageFolderName / f'{pos}_{cat}' / f"{timestamp_str}.png" 
                cv2.imwrite(image_filename, cv_image)
                
                if counter_name is not None:
                    setattr(self, counter_name, getattr(self, counter_name) + 1)
        return save_image

    def stop(self):
        self.running = False
        self.follower_joint_f.close()
        self.follower_gripper_f.close()
        self.follower_ep_f.close()
        self.leader_gripper_f.close()
        self.leader_joint_f.close()


class RealTimeDataProvider(QObject):
    # 修改3：信号定义使用 pyqtSignal
    state_updated = pyqtSignal(int, int, int, int, int, int, int)
    
    def __init__(self, piper : C_PiperInterface_V2):
        super().__init__()
        self.piper = piper
        self.timer = QTimer()
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.update)
        self.timer.start()
        
    def update(self):
        eef = self.piper.GetArmEndPoseMsgs()
        joint = self.piper.GetArmJointMsgs().joint_state
        gripper = self.piper.GetArmGripperMsgs()
        
        x, y, z, rx, ry, rz, gripper = [
            eef.end_pose.X_axis,
            eef.end_pose.Y_axis,
            eef.end_pose.Z_axis,
            eef.end_pose.RX_axis,
            eef.end_pose.RY_axis,
            eef.end_pose.RZ_axis,
            gripper.gripper_state.grippers_angle
        ]

        #show joint
        # x, y, z, rx, ry, rz, gripper = [
        #     joint.joint_1,
        #     joint.joint_2,
        #     joint.joint_3,
        #     joint.joint_4,
        #     joint.joint_5,
        #     joint.joint_6,
        #     gripper.gripper_state.grippers_angle
        # ]

        
        self.state_updated.emit(x, y, z, rx, ry, rz, gripper)
        


class ViewModel(QObject):
    # 准备阶段的信号
    inputValidChanged = pyqtSignal()
    confirmedChanged = pyqtSignal()
    
    # 运行阶段的信号
    statusChanged = pyqtSignal()
    
    # 重播阶段的信号
    savedTasksChanged = pyqtSignal()
    selectedTaskChanged = pyqtSignal()
    imageModeChanged = pyqtSignal()
    imageUpdated = pyqtSignal()
    
    # 数据更新的信号
    data_changed = pyqtSignal()
    
    def __init__(self, 
            parent=None, 
            saver: SimpleSaver = None, 
            camera_source: LiveCameraSource = None,
            data_provider: RealTimeDataProvider = None
        ):
        super().__init__(parent)
        self._input_text = ""
        self._input_valid = False
        self._confirmed = False
        
        self._status = "停止"
        self._status_color = QColor("red")
        self._is_saving = False
        
        self._arm_state = [0, 0, 0, 0, 0, 0, 0] # x, y, z, rx, ry, rz, gripper
        
        self.camera_source = camera_source
        self.image_provider = ImageProvider(self.camera_source)
        self.image_play_timer = QTimer()
        self.image_play_timer.setInterval(self.image_provider.get_interval())
        self.image_play_timer.timeout.connect(self.imageUpdated)
        self.image_play_timer.start()
        
        self.data_generator = data_provider
        self.data_generator.state_updated.connect(self.update_data)
        
        self.saver = saver
        self.tasks = []
        self.selected_tasks_index = -1
        self.is_living = True
        
        
        
    # =============准备阶段的交互================= BEGIN
    @pyqtProperty(bool, notify=inputValidChanged)
    def inputValid(self):
        return self._input_valid
        
    @pyqtProperty(bool, notify=confirmedChanged)
    def confirmed(self):
        return self._confirmed
    
    @pyqtSlot(str)
    def validateInput(self, text : str):
        print(f'input updated: {text}')
        self._input_text = text.strip()
        if len(text) > 0:
            self._input_valid = True
            self.inputValidChanged.emit()
            
    @pyqtSlot()
    def confirm(self):
        print(f'confirmed pressed')
        self._confirmed = True
        self.saver.set_run_name(self._input_text)
        self.confirmedChanged.emit()
        self.reload_tasks()
    # =============准备阶段的交互================= End
        
    
    # =============收集阶段的交互================= BEGIN
    @pyqtProperty(str, notify=statusChanged)
    def status(self):
        return self._status
        
    @pyqtProperty(QColor, notify=statusChanged)
    def statusColor(self):
        return self._status_color
    
    @pyqtProperty(bool, notify=statusChanged)
    def isSaving(self):
        return self._is_saving
    
    @pyqtProperty(str, notify=statusChanged)
    def lastSavedTask(self):
        return self.saver.last_saving_dir
    
    @pyqtSlot()
    def start(self):
        self._status = "运行中"
        self._status_color = QColor("green")
        self._is_saving = True
        self.statusChanged.emit()
        
        self.saver.start_saver()
        
    @pyqtSlot()
    def stop(self):
        self._status = "停止"
        self._status_color = QColor("red")
        self._is_saving = False
        self.statusChanged.emit()
        
        self.saver.stop()
        self.reload_tasks()
    # =============收集阶段的交互================= End
    
    
    # =============历史数据的交互================= BEGIN
    @pyqtProperty(list, notify=savedTasksChanged)
    def savedTasks(self):
        return self.tasks
    
    @pyqtProperty(str, notify=selectedTaskChanged)
    def selectedTask(self):
        if self.selected_tasks_index == -1:
            return ""
        return self.tasks[self.selected_tasks_index]
        
    @pyqtProperty(int, notify=selectedTaskChanged)
    def selectedTaskIndex(self):
        return self.selected_tasks_index
    
    @pyqtProperty(bool, notify=imageModeChanged)
    def isLiving(self):
        return self.is_living

    @pyqtSlot(int)
    def handleSelection(self, index):
        self.selected_tasks_index = index
        self.selectedTaskChanged.emit()

    @pyqtSlot()
    def replay(self):
        if self.selected_tasks_index == -1:
            return
        self.is_living = False
        self.imageModeChanged.emit()
        self.image_provider.set_image_source(DiskImageSource(str(self.saver.runs_folder / self.selectedTask)))
        print(f'set interval {self.image_provider.get_interval()}')
        self.image_play_timer.setInterval(self.image_provider.get_interval())
        
    @pyqtSlot()
    def live(self):
        self.is_living = True
        self.imageModeChanged.emit()
        self.image_provider.set_image_source(self.camera_source)
        self.image_play_timer.setInterval(self.image_provider.get_interval())

    def reload_tasks(self):
        tasks = os.listdir(str(self.saver.runs_folder))
        tasks.sort()
        self.tasks = tasks
        self.savedTasksChanged.emit()
    # =============历史数据的交互================= End
        
    
    # =============数据更新的展示================= BEGIN
    @pyqtProperty(str, notify=data_changed)
    def x(self):
        val = str(self._arm_state[0])
        attn = None
        if self._arm_state[0] < XRange[0]:
            attn = '左' # 左
        elif self._arm_state[0] > XRange[1]:
            attn = '右' # 右
        if attn is not None:
            val = f'{val} {attn}'
        return val
    
    @pyqtProperty(str, notify=data_changed)
    def xColor(self):
        x = self._arm_state[0]
        if XRange[0] <= x <= XRange[1]:
            return "#90EE90"
        else:
            return "#FFA07A"
        
    @pyqtProperty(str, notify=data_changed)
    def y(self):
        val = str(self._arm_state[1])
        attn = None
        if self._arm_state[1] < YRange[0]:
            attn = '后' # 前
        elif self._arm_state[1] > YRange[1]:
            attn = '前' # 后
        if attn is not None:
            val = f'{val} {attn}'
        return val
    
    @pyqtProperty(str, notify=data_changed)
    def yColor(self):
        y = self._arm_state[1]
        if YRange[0] <= y <= YRange[1]:
            return "#90EE90"
        else:
            return "#FFA07A"
        
    @pyqtProperty(str, notify=data_changed)
    def z(self):
        val = str(self._arm_state[2])
        attn = None
        if self._arm_state[2] < ZRange[0]:
            attn = '上'
        elif self._arm_state[2] > ZRange[1]:
            attn = '下'
        if attn is not None:
            val = f'{val} {attn}'
        return val
    
    @pyqtProperty(str, notify=data_changed)
    def zColor(self):
        z = self._arm_state[2]
        if ZRange[0] <= z <= ZRange[1]:
            return "#90EE90"
        else:
            return "#FFA07A"
    
    @pyqtProperty(str, notify=data_changed)
    def rx(self):
        return str(self._arm_state[3])
    
    @pyqtProperty(str, notify=data_changed)
    def ry(self):
        return str(self._arm_state[4])
    
    @pyqtProperty(str, notify=data_changed)
    def rz(self):
        return str(self._arm_state[5])
    
    @pyqtProperty(str, notify=data_changed)
    def gripper(self):
        return str(self._arm_state[6])
    
    def update_data(self, x, y, z, rx, ry, rz, gripper):
        self._arm_state = [x, y, z, rx, ry, rz, gripper]
        # print(f'self._arm_state: {self._arm_state}')
        self.data_changed.emit()
    # =============数据更新的展示================= End    
    
    # =============remote service ==============
    def query_switch(self, req):
        return TriggerResponse(success=self._is_saving, message=self.status)
    
    def change_switch(self, req: SetBool):
        if not self.confirmed:
            return SetBoolResponse(success=False, message='请先确认输入')
        if req.data:
            if self._is_saving:
                return SetBoolResponse(success=False, message='已经在运行了')
            else :
                self.start()
        else:
            if not self._is_saving:
                return SetBoolResponse(success=False, message='已经停止了')
            else:
                self.stop()
        return SetBoolResponse(success=True, message=self.status)
    
    def query_status(self, req: Trigger):
        return TriggerResponse(success=True, message=json.dumps({
            'x': self.x,
            'xColor': self.xColor,
            'y': self.y,
            'yColor': self.yColor,
            'z': self.z,
            'zColor': self.zColor,
            'rx': self.rx,
            'ry': self.ry,
            'rz': self.rz,
            'gripper': self.gripper
        }))
    
    def query_record_num(self, req: Trigger):
        return TriggerResponse(success=True, message=json.dumps({
            'saved_tasks_count': len(self.savedTasks),
        }))

if __name__ == "__main__":
    camera_pipe = LiveCameraSource()
    rospy.init_node('display_image', anonymous=True)
    
    # check if camera inited
    rospy.sleep(1)
    published_topics = rospy.get_published_topics()
    published_topics = [item[0] for item in published_topics]
    if False or \
        '/ob_camera_01/color/image_raw' not in published_topics or \
        '/ob_camera_02/color/image_raw' not in published_topics or \
        '/ob_camera_01/depth/image_raw' not in published_topics or \
        '/ob_camera_02/depth/image_raw' not in published_topics:
        print(f'摄像头尚未初始化，请初始化先')
        raise Exception('初始化去吧你')
    
    rospy.Subscriber('/ob_camera_01/color/image_raw', Image_msg, camera_pipe.get_subscriber('wrist'))
    rospy.Subscriber('/ob_camera_02/color/image_raw', Image_msg, camera_pipe.get_subscriber('front'))
    
    saver = SimpleSaver('data/tmp')
    try:
        piper = C_PiperInterface_V2(saver=saver)
        piper.ConnectPort()
    except ValueError as e:
        print(f'Can口没有初始化，请先初始化can口')
        raise e
    
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    view_model = ViewModel(
        saver=saver,
        camera_source=camera_pipe,
        data_provider=RealTimeDataProvider(piper)
    )
    
    register_service(
        set_switch_callback=view_model.change_switch,
        query_switch_callback=view_model.query_switch,
        query_status_callback=view_model.query_status,
        query_recorded_callback=view_model.query_record_num
    )
    
    engine.rootContext().setContextProperty("viewModel", view_model)
    engine.addImageProvider("liveimage", view_model.image_provider)
    
    # engine.load(QUrl.fromLocalFile("main.qml"))
    engine.load('main.qml')
    
    # if not engine.rootObjects():
    #     sys.exit(-1)
    
    # sys.exit(app.exec_())
    app.exec_()
