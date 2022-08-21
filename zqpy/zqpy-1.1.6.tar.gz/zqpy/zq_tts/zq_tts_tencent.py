# -*- coding:utf-8 -*-
import urllib
import base64
import hmac
import hashlib
import requests
import wave
import json
import time

class tts_tencent_data_authorization_class:
    '''
    腾讯语音合成鉴权数据
    '''
    def __init__(self):
        #用户鉴权参数
        self.AppId = 1252113161
        self.SecretId = 'AKIDTp12qQmwufBSWN2SfgU3OYUDhvxkIaeE'
        self.SecretKey = 'NSHtIVYTHm48yZ7RWN3UiiRyFKBpFRO8'
        self.Expired = 3600

    def verify_param(self):
        if len(str(self.AppId)) == 0:
             print('AppId can not empty')
        if len(str(self.SecretId)) == 0:
             print('SecretId can not empty')
        if len(str(self.SecretKey)) == 0:
             print('SecretKey can not empty')

    def init_auth(self, appid, secret_id, secret_key):
        self.AppId = appid
        self.SecretId = secret_id
        self.SecretKey = secret_key

    def generate_sign(self, request_data):
        url = "tts.cloud.tencent.com/stream"
        sign_str = "POST" + url + "?"
        sort_dict = sorted(request_data.keys())
        for key in sort_dict:
            sign_str = sign_str + key + "=" + urllib.parse.unquote(str(request_data[key])) + '&'
        sign_str = sign_str[:-1]
        sign_bytes = sign_str.encode('utf-8')
        key_bytes = self.SecretKey.encode('utf-8')
        print(sign_bytes)
        tts_tencent_data_authorization_class = base64.b64encode(hmac.new(key_bytes, sign_bytes, hashlib.sha1).digest())
        return tts_tencent_data_authorization_class.decode('utf-8')

class tts_tencent_data_request_class:
    '''
    腾讯语音合成请求数据
    '''
    def __init__(self, save=None, text=None, sessionId=None):
        self.Text = text if text else '要被转化成语音的文字，最大支持500字符。'
        self.Action = 'TextToStreamAudio' # 请求参数固定值，不能改
        self.Codec = 'pcm'          #返回音频格式：Python SDK只支持pcm格式  #pcm：返回二进制 pcm 音频，使用简单，但数据量大。
        self.Expired = 3600         #鉴权有效时间 单位 s,不设置默认为一小时
        self.ModelType = 1          #模型类型，1：默认模型
        self.PrimaryLanguage = 1    #主语言类型 1：中文（默认）2：英文
        self.ProjectId = 0          #项目 ID，用户自定义，默认为0。
        self.SampleRate = 16000     #音频采样率：16000：16k（默认） 8000：8k
        self.SessionId = str(sessionId if sessionId else int(time.time()))          #一次请求对应一个 SessionId，会原样返回，建议传入类似于 uuid 的字符串防止重复。
        self.Speed = 1              #语速，范围：[-2，2]，分别对应不同语速：［0.6倍,0.8倍,1.0倍（默认）,1.2倍,1.5倍]
        self.Volume = 5             #音量大小，范围：[0，10]，分别对应11个等级的音量，默认值为0，代表正常音量。没有静音选项。
        self.VoiceType = 0          #音色： #0：亲和女声（默认） #1：亲和男声 #2：成熟男声 #3：活力男声 #4：温暖女声 #5：情感女声 #6：情感男声 #标准音色 #10510000-智逍遥，阅读男声 #1001-智瑜，情感女声 #1002-智聆，通用女声 #1003-智美，客服女声 #1004-智云，通用男声 #1005-智莉，通用女声 #1007-智娜，客服女声 #1008-智琪，客服女声 #1009-智芸，知性女声 #1010-智华，通用男声 #1017-智蓉，情感女声 #1018-智靖，情感男声 #1050-WeJack，英文男声 #1051-WeRose，英文女声 #精品音色 #精品音色拟真度更高，价格不同于标准音色，查看购买指南 #100510000-智逍遥，阅读男声 #101001-智瑜，情感女声 #101002-智聆，通用女声 #101003-智美，客服女声 #101004-智云，通用男声 #101005-智莉，通用女声 #101006-智言，助手女声 #101007-智娜，客服女声 #101008-智琪，客服女声 #101009-智芸，知性女声 #101010-智华，通用男声 #101011-智燕，新闻女声 #101012-智丹，新闻女声 #101013-智辉，新闻男声 #101014-智宁，新闻男声 #101015-智萌，男童声 #101016-智甜，女童声 #101017-智蓉，情感女声 #101018-智靖，情感男声 #101019-智彤，粤语女声 #101020-智刚，新闻男声 #101021-智瑞，新闻男声 #101022-智虹，新闻女声 #101023-智萱，聊天女声 #101024-智皓，聊天男声 #101025-智薇，聊天女声 #101026-智希，通用女声 #101027-智梅，通用女声 #101028-智洁，通用女声 #101029-智凯，通用男声 #101030-智柯，通用男声 #101031-智奎，通用男声 #101032-智芳，通用女声 #101033-智蓓，客服女声 #101034-智莲，通用女声 #101035-智依，通用女声 #101040-智川，四川女声 #101050-WeJack，英文男声 #101051-WeRose，英文女声
        self.SavePath = save if save else 'tts_tencent.wav'        #文件存放位置

    def verify_param(self):
        if len(str(self.Action)) == 0:
             print('Action can not empty')
        if len(str(self.SampleRate)) == 0:
             print('SampleRate is not set, assignment default value 16000')
             self.SampleRate = 16000

    def init_param(self, save, text, action=None, codec=None, expired=None, model_type=None, prim_lan=None, project_id=None, sample_rate=None, session_id=None, speed=None, voice_type=None, volume=None):
        self.Action = action if action else self.Action
        self.Text = text
        self.Codec = codec if codec else self.Codec
        self.Expired = expired if expired else self.Expired
        self.ModelType = model_type if model_type else self.ModelType
        self.PrimaryLanguage = prim_lan if prim_lan else self.PrimaryLanguage
        self.ProjectId = project_id if project_id else self.ProjectId
        self.SampleRate = sample_rate if sample_rate else self.SampleRate
        self.SessionId = session_id if session_id else self.SessionId
        self.Speed = speed if speed else self.Speed
        self.VoiceType = voice_type if voice_type else self.VoiceType
        self.Volume = volume if volume else self.Volume
        self.SavePath = save

class tts_tencent_class():
    def __init__(self, auth:tts_tencent_data_authorization_class=None):
        self.auth = auth if auth else tts_tencent_data_authorization_class()

    def tts_tencent_req_by_text(self, save, text):
        req = tts_tencent_data_request_class()
        req.init_param(save, text)
        self.tts_tencent_req(req)

    def tts_tencent_req(self, req:tts_tencent_data_request_class=None):
        request_data = dict()
        request_data['Action'] = 'TextToStreamAudio'
        request_data['AppId'] = self.auth.AppId
        request_data['Codec'] = req.Codec
        request_data['Expired'] = int(time.time()) + self.auth.Expired
        request_data['ModelType'] = req.ModelType
        request_data['PrimaryLanguage'] = req.PrimaryLanguage
        request_data['ProjectId'] = req.ProjectId
        request_data['SampleRate'] = req.SampleRate
        request_data['SecretId'] = self.auth.SecretId
        request_data['SessionId'] = req.SessionId
        request_data['Speed'] = req.Speed
        request_data['Text'] = req.Text
        request_data['Timestamp'] = int(time.time())
        request_data['VoiceType'] = req.VoiceType
        request_data['Volume'] = req.Volume

        signature = self.auth.generate_sign(request_data = request_data)
        header = {
            "Content-Type": "application/json",
            "Authorization": signature
        }
        url = "https://tts.cloud.tencent.com/stream"

        r = requests.post(url, headers=header, data=json.dumps(request_data), stream = True)
        '''
        if str(r.content).find("Error") != -1 :
            print(r.content)
            return
        '''
        i = 1
        wavfile = wave.open(req.SavePath, 'wb')
        wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        for chunk in r.iter_content(1000):
            if (i == 1) & (str(chunk).find("Error") != -1) :
                print(chunk)
                return False
            i = i + 1
            wavfile.writeframes(chunk)
        wavfile.close()
        return req