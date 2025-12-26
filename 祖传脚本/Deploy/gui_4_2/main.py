import sys
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
# 在文件顶部的导入部分添加
from PyQt5.QtCore import QThreadPool
from functools import partial

from lib.actor import setup_actor
from lib.vla_inference import VLAMInference
from lib.vllm_inference import VLLMInference
from lib.ros_operator import RosOperator
from lib.audio_recorder import MicroPhoneRecorder
from lib.whisper_inference import WhisperInference
from lib.llm_inference import LlmInference
from lib.task_buffer import TaskBuffer
import argparse
import torch
import numpy as np
import rospy
import os
from std_msgs.msg import Bool,String
from lib.task_buffer import TaskBuffer
import logging
from lib.image_source import LiveCameraMixIn
import threading
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)


class Backend(QObject):
    vlmChanged = pyqtSignal(str)
    vlaChanged = pyqtSignal(str)
    armRunningChanged = pyqtSignal(bool)
    isRecordingChanged = pyqtSignal(bool)  # 统一信号定义
    # 新增信号
    llmChanged = pyqtSignal(str)
    frankaChanged = pyqtSignal(str)
    modeChanged = pyqtSignal(str)  # 新增模式信号
    imageUpdated = pyqtSignal()
    armStatusUpdated = pyqtSignal()

    def __init__(self, args, config):
        super().__init__()
        self._vlm_instruction = "VLM指令显示区域"
        self._vla_instruction = "VLA指令显示区域"
        # 新增属性初始化
        self._llm_instruction = "LLM指令显示区域"
        self._franka_instruction = "franka指令显示区域"
        self._which_mode = "vla"
        self._audio_data = None
        # self.rack = Rack(config["goods_dict"])
        LiveCameraMixIn.__init__(self, self.imageUpdated)
        self.task_buffer = TaskBuffer()
        self.ros_operator = RosOperator(args, config)
        self.vla_inference = VLAMInference(args, config, self.ros_operator)
        self.vllm_inference = VLLMInference(args, config, self.ros_operator)
        self.LlmInference = LlmInference(config)
        self.micro_phone_recorder = MicroPhoneRecorder()
        
        # 人类指令-》给llm产生json, 我们需要解码出对应的action, （比较能不竜完成嘛， 不能完成就提醒）放进buffer中，并输出语音提醒
        # franka查询buffer, buffer中有动作就执行, ·
        # 如果增加物品， franka执行完了一个buffer中的action, 执行下一个
        # 
        self.whisper = WhisperInference()
        # joint_left_r1 = [-91224,   34755,    -51317,   -5722,    63601,    -5152, 3000] 
        joint_left_r1 = [-91224,  43116, -52626, 0, 62386, 432, -4830]
        # XRange = [73886, 110733]
        # YRange = [-15133, 4886]
        # ZRange = [365219, 381277]
        # self.ros_operator.update_observation_window()
        # print(self.ros_operator.observation_window[-1]['qpos'])
        self.ros_operator.puppet_arm_publish_continuous(joint_left_r1)
        self.vllm_inference.onVlaPromptChanged.connect(self.set_vla)
        self.task_buffer.vllmActionChanged.connect(self._update_vlm_instruction)
        self.LlmInference.put_task_to_buffer.connect(self.task_buffer.add_task)
        self.LlmInference.onVLMClean.connect(self._update_vlm_instruction_clean)
        self.vllm_inference.onVla_for_table_clean.connect(self.vla_inference.set_vla_for_table_clean)
        self.task_buffer.rack_dic_Changed.connect(self.set_rack_dic)
        self.vla_inference_thread = setup_actor(self.vla_inference)
        self.vllm_inference_thread = setup_actor(self.vllm_inference)
        self.task_buffer_thread = setup_actor(self.task_buffer)
        self._is_recording = False  # 私有变量统一命名
        rospy.Subscriber('/voice/recording', Bool,self.call_back_for_sub_record_button, queue_size=10,)
        rospy.Subscriber('/is_stop/', Bool, self.setArmRunning_by_web, queue_size=10,) #是否暂停
        rospy.Subscriber('/change_mode_vla_or_return/', String, self.set_mode_by_botton_call_back, queue_size=20, tcp_nodelay=True)#是否切换vla
        rospy.Subscriber('/arm_control/table_sweep', Bool, self.set_vllm_sweep, queue_size=10,) #是否暂停
        rospy.Subscriber('/arm_control/table_clean', Bool, self.set_vllm_table_clean, queue_size=10,) #是否暂停
        rospy.Subscriber('/arm_control/vllm_mode', Bool, self.set_vllm_mode, queue_size=10,) #vllm
        rospy.Subscriber('/arm_control/move_left', Bool, self.set_move_left, queue_size=10,) #vllm
        rospy.Subscriber('/arm_control/move_right', Bool, self.set_move_right, queue_size=10,) #vllm
        rospy.Subscriber('/arm_control/dump', Bool, self.set_dump, queue_size=10,) #vllm
        rospy.Subscriber('/arm_control/put_plate', Bool, self.set_put_plate, queue_size=10,) #vllm
        rospy.Subscriber('/arm_control/sweep_all', Bool, self.set_sweep_all, queue_size=10,) #vllm
       
        # rospy.Subscriber("/arm_control/return_pos",Bool,self.set_mode_by_botton_call_back,queue_size=10, tcp_nodelay=True)
        try:
            # self.whisper.transcription_complete.connect(self._update_vlm_instruction)
            self.whisper.transcription_failed.connect(self._handle_transcription_error)
            self.micro_phone_recorder.recording_state_changed.connect(
                lambda state: setattr(self, "isRecording", state))   
        except Exception as e:
            logging.error(f"信号连接失败: {str(e)}")
            raise
        
    def call_back_for_sub_record_button(self,msg):
        is_record  = msg.data
        if is_record and self._is_recording == False:
            self.startRecording()
        elif is_record == False and self._is_recording == True:
            self.stopRecording()
            
    def _update_vlm_instruction(self, text):
        """安全更新指令"""
        try:
            self.vlmInstruction = text
        except Exception as e:
            logging.error(f"更新指令失败: {str(e)}")

    def _update_vlm_instruction_clean(self, text):
        """安全更新指令"""
        try:
            self.vlmInstruction = text
            self.task_buffer.set_table_clean_state()
        except Exception as e:
            logging.error(f"更新指令失败: {str(e)}")

    def _handle_transcription_error(self, error_msg):
        """处理识别错误"""
        logging.error(error_msg)
        # 可以在这里添加错误提示到UI的逻辑

    def _handle_recording_state(self, is_recording):
        """处理录音状态变化"""
        try:
            self.isRecording = is_recording
        except Exception as e:
            logging.error(f"状态更新失败: {str(e)}")
        
    @pyqtProperty(str, notify=vlmChanged)
    def vlmInstruction(self):
        return self._vlm_instruction

    @vlmInstruction.setter
    def vlmInstruction(self, value):
        if self._vlm_instruction != value:
            self._vlm_instruction = value
            self.vllm_inference.instruction = value
            self.vlmChanged.emit(value)

    @pyqtProperty(str, notify=vlaChanged)
    def vlaInstruction(self):
        return self._vla_instruction

    @vlaInstruction.setter
    def vlaInstruction(self, value):
        if self._vla_instruction != value:
            self._vla_instruction = value
            # print("there in ")
            self.vla_inference.vla_prompt = value
            self.vlaChanged.emit(value)

    @pyqtSlot(str)
    def set_vlm(self, text):
        self.vlmInstruction = text
    

    @pyqtSlot(str)
    def set_vla(self, text):
        self.vlaInstruction = text

    # 新增属性和槽函数
    @pyqtProperty(str, notify=llmChanged)
    def llmInstruction(self):
        return self._llm_instruction

    # 开启推理
    @llmInstruction.setter
    def llmInstruction(self, value):
        if self._llm_instruction != value:
            self._llm_instruction = value
            self.LlmInference.thread_run(value)
            self.llmChanged.emit(value)

    @pyqtSlot(str)
    def set_llm(self, text):
        self.llmInstruction = text

    @pyqtProperty(str, notify=frankaChanged)
    def frankaInstruction(self):
        return self._franka_instruction

    @frankaInstruction.setter
    def frankaInstruction(self, value):
        if self._franka_instruction != value:
            self._franka_instruction = value
            self.frankaChanged.emit(value)

    @pyqtSlot(str)
    def set_franka(self, text):
        self.frankaInstruction = text


    # =========== Arm Start/Stop Control ===========
    # 修改 Backend 类中的 armRunning 属性定义
    @pyqtProperty(bool, notify=armRunningChanged)  # 添加 notify 参数
    def armRunning(self):
        return self.vla_inference.is_running

    @pyqtSlot(bool)
    def setArmRunning(self, value):
        self.vla_inference.is_running = value
        self.armRunningChanged.emit(value)
    
    def setArmRunning_by_web(self, msg):
        if self.vla_inference.is_running == True:
            value = False
        else:
            value = True
        self.vla_inference.is_running = value
        self.armRunningChanged.emit(value)
    
    # =========== Microphone Control ===========
    # =========== 修正后的录音属性 ===========
    @pyqtProperty(bool, notify=isRecordingChanged)
    def isRecording(self):
        return self._is_recording

    @isRecording.setter
    def isRecording(self, value):
        if self._is_recording != value:
            self._is_recording = value
            self.isRecordingChanged.emit(value)

    # =========== 修正后的录音控制方法 ===========
    @pyqtSlot()
    def startRecording(self):
        self.isRecording = True
        self.micro_phone_recorder.start()
        self._audio_data = None  # 清空旧数据

    @pyqtSlot()
    def stopRecording(self):
        if self.isRecording:
            self.isRecording = False
            self.micro_phone_recorder.stop()
            
            try:
                # 获取音频数据并创建本地副本
                audio_data = self.micro_phone_recorder.get_audio_data()
                if audio_data.size > 0:
                    # 使用functools.partial避免闭包变量引用问题
                    from functools import partial
                    QThreadPool.globalInstance().start(
                        partial(self._process_audio, audio_data.copy())  # 显式传递数据副本
                    )
            except Exception as e:
                print(f"获取音频数据失败: {str(e)}")
            finally:
                try:
                    self.micro_phone_recorder.clear_buffer()
                except AttributeError:
                    pass

    def _process_audio(self, audio_data):
        """线程安全的音频处理"""
        try:
            # Chinese
            text, language = self.whisper.transcribe_audio(audio_data)
            self.llmInstruction = text  # 通过信号更新UI
            # print(language)
            if language == "zh":
                self.LlmInference.response_language = "Chinese"
                self.task_buffer.response_language = "Chinese"
            else:
                self.LlmInference.response_language = "English"
                self.task_buffer.response_language = "English"
        except Exception as e:
            print(f"Transcription failed: {str(e)}")
    
    # =========== 新增模式控制 ===========
    @pyqtProperty(str, notify=modeChanged)
    def currentMode(self):
        return self._which_mode

    @currentMode.setter
    def currentMode(self, value):
        if self._which_mode != value:
            self._which_mode = value
            tmp = True
            if self._which_mode == "vla":
                tmp = False
            print("self.vla_inference.ctrl_mode_for_vla(tmp) tmp = ", tmp)
            # 创建一个线程对象
            thread = threading.Thread(target=self.vla_inference.ctrl_mode_for_vla, args=(tmp,))

            # 启动线程
            thread.start()
            # self.vla_inference.ctrl_mode_for_vla(tmp)
            self.modeChanged.emit(value)

    @pyqtSlot()
    def set_mode(self):
        self.currentMode = "vla" if self._which_mode == "return" else "return"
        logging.info(f"切换模式到：{self.currentMode}")
    
    def set_mode_by_botton_call_back(self, msg):
        self.currentMode = "vla" if self._which_mode == "return" else "return"
        logging.info(f"切换模式到：{self.currentMode}")

    def set_vllm_sweep(self, msg):
        self.vlmInstruction = "[sweep the table]"
        
    def set_vllm_table_clean(self, msg):
        self.vlmInstruction = "[table clean]"

    def set_vllm_mode(self,msg):
        self.vla_inference.vllm_mode=True
        self.vla_inference.sys_vlm_prompt=None

    def set_move_left(self,msg):
        self.vla_inference.vllm_mode=False
        self.vla_inference.sys_vlm_prompt="move the arm to the left"
    
    def set_move_right(self,msg):
        self.vla_inference.vllm_mode=False
        self.vla_inference.sys_vlm_prompt="move the arm to the right"

    
    def set_dump(self,msg):
        self.vla_inference.vllm_mode=False
        self.vla_inference.sys_vlm_prompt="dump sth into the trash can"

    def set_put_plate(self,msg):
        self.vla_inference.vllm_mode=False
        self.vla_inference.sys_vlm_prompt="put the plate into the tray"

        
    def set_rack_dic(self, ss):
        # ss to dict
        tmp_list = ss.split()
        dict_ = {}
        for x in tmp_list:
            if x not in dict_:
                dict_[x] = 1
            else:
                dict_[x] += 1
        # dict_ = tmp
        self.LlmInference.rack_dic = dict_
        print(self.LlmInference.rack_dic)

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_publish_step', action='store', type=int, 
                        help='Maximum number of action publishing steps', default=10000, required=False)
    parser.add_argument('--seed', action='store', type=int, 
                        help='Random seed', default=None, required=False)

    parser.add_argument('--img_front_topic', action='store', type=str, help='img_front_topic',
                        default='/camera_f/color/image_raw', required=False)
    parser.add_argument('--img_left_topic', action='store', type=str, help='img_left_topic',
                        default='/camera_l/color/image_raw', required=False)
    parser.add_argument('--img_front_depth_topic', action='store', type=str, help='img_front_depth_topic',
                        default='/camera_f/depth/image_raw', required=False)
    parser.add_argument('--img_left_depth_topic', action='store', type=str, help='img_left_depth_topic',
                        default='/camera_l/depth/image_raw', required=False)
    parser.add_argument('--puppet_arm_left_js_topic', action='store', type=str, help='puppet_arm_left_js_topic',
                        default='joint_states_single', required=False)
    parser.add_argument('--puppet_arm_left_eef_topic', action='store', type=str, help='puppet_arm_left_eef_topic',
                        default='eef_states_single', required=False)
    
    parser.add_argument('--publish_rate', action='store', type=int, 
                        help='The rate at which to publish the actions',
                        default=20, required=False)
    parser.add_argument('--ctrl_freq', action='store', type=int, 
                        help='The control frequency of the robot',
                        default=25, required=False)
    parser.add_argument('--chunk_size', action='store', type=int, 
                        help='Action chunk size',
                        default=20, required=False)
    parser.add_argument('--arm_steps_length_eef', action='store', type=float, 
                        help='The maximum change allowed for each joint per timestep',
                        default=[1000, 1000, 1000, 1000, 1000, 1000, 30], required=False)
    parser.add_argument('--arm_steps_length_js', action='store', type=float, 
                        help='The maximum change allowed for each joint per timestep',
                        default=[200, 200, 200, 200, 200, 200, 30], required=False)

    parser.add_argument('--use_actions_interpolation', action='store_true',
                        help='Whether to interpolate the actions if the difference is too large',
                        default=False, required=False)
    parser.add_argument('--use_depth_image', action='store_true', 
                        help='Whether to use depth images',
                        default=True, required=False)
    
    parser.add_argument('--disable_puppet_arm', action='store_true',
                        help='Whether to disable the puppet arm. This is useful for safely debugging',default=False)
    
    parser.add_argument('--config_path', type=str, default="configs/base.yaml", 
                        help='Path to the config file')
    parser.add_argument('--use_eef', action='store_true', 
                        help='Whether to use eef',
                        default=False, required=False)
    # parser.add_argument('--cfg_scale', type=float, default=2.0,
    #                     help='the scaling factor used to modify the magnitude of the control features during denoising')
    # parser.add_argument('--pretrained_model_name_or_path', type=str, required=True, help='Name or path to the pretrained model')
    
    # parser.add_argument('--lang_embeddings_path', type=str, required=True, 
    #                     help='Path to the pre-encoded language instruction embeddings')
    
    args = parser.parse_args()
    return args
CAMERA_NAMES = ['cam_wrist', 'cam_thirdPerson','cam_wrist_depth', 'cam_thirdPerson_depth']
def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
def get_config(args):
    config = {
        'episode_len': args.max_publish_step,
        'state_dim': 7,
        'chunk_size': args.chunk_size,
        'camera_names': CAMERA_NAMES,
        'rack_dic': {
                        'coffee': 1,     # 咖啡
                        'cookie': 1,     # 饼干
                        'tea': 1,        # 茶
                        'milk': 1,       # 牛奶
                        'water': 1,      # 水
                        # 'popcorn':1,      # 爆米花
                        'gum': 1,        # 口香糖
                        'chocolate': 1,   # 巧克力
                        # 'cola':1,     #可乐
                        'plate':1,    #木盘子
                        'oreo': 1, 
                        'biscuits':1
                    }#coffee, cookie, tea, milk, water, gum, chocolate, cola, oreo, biscuits
    }
    return config

if __name__ == "__main__":
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/home/pc3/.conda/envs/deploy/lib/python3.10/site-packages/PyQt5/Qt5/plugins'
    args = get_arguments()
    if args.seed is not None:
        set_seed(args.seed)
    config = get_config(args)
    
    app = QGuiApplication(sys.argv)
    print("get app")
    
    backend = Backend(args, config)
    print("get backend") 
    
    engine = QQmlApplicationEngine()
    # 注册图像提供器
    engine.addImageProvider("liveimage", backend.image_provider)
    engine.rootContext().setContextProperty("backend", backend)
    engine.load("main.qml")
    print("load qml")

    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec_())