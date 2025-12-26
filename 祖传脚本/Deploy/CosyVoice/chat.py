import sys
import numpy as np
import pyaudio
import torchaudio
from cosyvoice.cli.cosyvoice import CosyVoice, CosyVoice2
from cosyvoice.utils.file_utils import load_wav
import rospy
from std_msgs.msg import String
import rosnode
import time
sys.path.append('third_party/Matcha-TTS')
class ChatInference:
    def __init__(self):
        self.check_ros_master()
        # 1. 初始化TTS模型
        self.cosyvoice = CosyVoice2('pretrained_models/CosyVoice2-0.5B', 
                            load_jit=False, 
                            load_trt=False, 
                            fp16=True)

        # 2. 加载提示语音
        self.prompt_speech_16k = load_wav('./asset/zero_shot_prompt.wav', 16000)

        # 3. 初始化PyAudio
        self.p = pyaudio.PyAudio()

        # 音频流参数配置
        SAMPLE_RATE = self.cosyvoice.sample_rate  # 从模型获取采样率
        CHANNELS = 1                        # 单声道
        FORMAT = pyaudio.paFloat32          # 32位浮点格式
        CHUNK_SIZE = 1024                   # 每次处理的音频块大小

        # 4. 创建音频输出流
        self.stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        output=True,
                        frames_per_buffer=CHUNK_SIZE)

        rospy.init_node('chat_subscriber', anonymous=True) 
        rospy.Subscriber('/chat/', String, self.chat_callback, queue_size=10, tcp_nodelay=False)
        print("init ok")

    # 5. 定义音频播放函数
    def play_audio(self,audio_data: np.ndarray):
        """
        播放音频数据
        
        参数:
            audio_data: numpy数组形式的音频数据(单声道, 32位浮点)
        """
        # 确保音频数据是连续的(避免出现strided array错误)
        audio_data = np.ascontiguousarray(audio_data)
        
        # 转换为bytes并播放
        self.stream.write(audio_data.tobytes())


    def chat_callback(self,msg):
        print("recieve data:",msg.data)

        for i, chunk in enumerate(self.cosyvoice.inference_zero_shot(
            msg.data,'希望你以后能够做的比我还好呦。',
            self.prompt_speech_16k,
            stream=False
        )):
            # 获取当前音频块
            audio_tensor = chunk['tts_speech']  # PyTorch tensor
            
            # 转换为numpy数组并确保是单声道
            audio_np = audio_tensor.numpy().squeeze()  # 去除多余的维度
            
            # 确保数据类型是32位浮点
            audio_np = audio_np.astype(np.float32)
            
            # 实时播放当前音频块
            self.play_audio(audio_np)


    def check_ros_master(self):
        try:
            rosnode.rosnode_ping("rosout", max_count=1, verbose=False)
            rospy.loginfo("ROS Master is running.")
        except rosnode.ROSNodeIOException:
            rospy.logerr("ROS Master is not running.")
            raise RuntimeError("ROS Master is not running.")


if __name__ == "__main__":

    # 加载 ChatTTS
    ChatInference()

    while True and not rospy.is_shutdown():
        time.sleep(1)