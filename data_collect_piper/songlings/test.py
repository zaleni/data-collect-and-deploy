# 伪代码示例
import pvporcupine  # 唤醒词检测
import sounddevice as sd  # 音频采集

# 初始化唤醒引擎
porcupine = pvporcupine.create(keywords=["你好小智"])

# 音频流回调函数
def audio_callback(indata, frames, time, status):
    pcm = indata[:,0].tobytes()
    keyword_index = porcupine.process(pcm)
    
    if keyword_index >= 0:
        # 唤醒后处理
        asr_result = cloud_asr.recognize(record_until_silence())
        task = nlu_processor.parse(asr_result)
        execute_task(task)

# 启动音频流
with sd.InputStream(callback=audio_callback):
    while True: pass  # 保持常驻