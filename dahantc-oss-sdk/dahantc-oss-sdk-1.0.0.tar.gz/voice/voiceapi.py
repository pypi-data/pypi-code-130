"""
  模块描述：语音api 模块
  @author 8526
  @date 2022-05-12 13:53:05
  版权所有 Copyright www.dahantc.com
"""

import json

import requests

import common.util as util
import voice.conf as conf
import voice.param as param
import voice.response as res


# 语音短信客户端
class VoiceSmsClient:
    def __init__(self, base_url):
        if base_url is None:
            base_url = conf.BASE_URL
        self.base_url = base_url

    # 验证码提交
    def captchaSubmit(self, params):
        if type(params) != param.CaptchaVoiceParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数CaptchaVoiceParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_SUBMIT, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.voiceSubmitResponseDecoder(json.loads(result.content))

    # 文本外呼
    def textSubmit(self, params):
        if type(params) != param.TextVoiceParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数TextVoiceParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_SUBMIT, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.voiceSubmitResponseDecoder(json.loads(result.content))

    # 混合呼叫
    def mixSubmit(self, params):
        if type(params) != param.MixVoiceParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数MixVoiceParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_SUBMIT, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.voiceSubmitResponseDecoder(json.loads(result.content))

    # 语音文件验证码
    def mediaCaptchaSubmit(self, params):
        if type(params) != param.MediaCaptchaParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数MediaCaptchaParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_SUBMIT, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.voiceSubmitResponseDecoder(json.loads(result.content))

    # 语音文件外呼
    def mediaSubmit(self, params):
        if type(params) != param.MediaVoiceParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数MediaVoiceParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_SUBMIT, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.voiceSubmitResponseDecoder(json.loads(result.content))

    # 语音文件上传
    def vocMediaUpload(self, params):
        if type(params) != param.VocMediaUploadParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数MediaParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.VOC_MEDIA_UPLOAD, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.vocUploadResponseDecoder(json.loads(result.content))


if __name__ == '__main__':
    pwdMd5 = util.md5Encode("456.com")
    account = "dhst8526"
    smsClient = VoiceSmsClient('http://180.168.192.126:16766')
    mediaParam = param.CaptchaVoiceParam(account, pwdMd5, 'true', [param.CaptchaVoiceData('msgid', 'callee', 'text', 'playmode', 'calltype', 'params')])
    print(smsClient.captchaSubmit(mediaParam))
