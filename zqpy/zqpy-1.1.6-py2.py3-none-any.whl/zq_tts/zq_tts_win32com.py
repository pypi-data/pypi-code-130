import win32com.client

def tts_win32com_speek(text):
    '''
    微软声音
    '''
    speak = win32com.client.Dispatch('SAPI.SpVoice')  #连接到SAPI.SpVoice COM服务
    speak.Speak(text)

def tts_win32com_req(save, text):
    '''
    微软声音保存
    '''
    fileStream = win32com.client.Dispatch("SAPI.SpFileStream")
    fileStream.Open(save, 3, False)
    speak = win32com.client.Dispatch("SAPI.SpVoice")
    speak.AudioOutputStream = fileStream
    speak.Volume = 80     # 设置音量 ，值范围是0到100，分别代表最小和最大音量级别
    speak.Rate = 2        # 设置速度 ，值介于-10到10之间，分别代表最慢的说话速度和最快的说话速度
    print(speak.Voice.GetDescription())      # 看这个语音的具体描述
    speak.Speak(text)
    fileStream.Close()
    return True


