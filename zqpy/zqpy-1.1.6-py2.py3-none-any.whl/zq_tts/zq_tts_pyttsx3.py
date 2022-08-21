import zq_log
zq_log.log_debug('好像没有维护了, 3.8上最新的pyttsx32.9用不了，这里需要指定安装 pip3 install pyttsx3==2.71')
import pyttsx3
def tts_pyttsx3_req(save, text):
    engine = pyttsx3.init() # object creation
    """ 把语音存储到文件 """
    engine.save_to_file(text,save)
    engine.runAndWait()
    engine.stop()

def tts_pyttsx3_speek(text):
    """更改速率"""
    engine = pyttsx3.init() # object creation
    rate = engine.getProperty('rate')   # getting details of current speaking rate
    engine.setProperty('rate', 125)     # setting up new voice rate


    """更改音量"""
    volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
    engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

    """更改声音"""
    voices = engine.getProperty('voices')       #getting details of current voice
    engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male  中文
    engine.say(text)
    engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female  英文
    engine.say(text)
    engine.runAndWait()
    engine.stop()
