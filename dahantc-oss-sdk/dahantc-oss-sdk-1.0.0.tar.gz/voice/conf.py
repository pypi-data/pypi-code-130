"""
  模块描述：服务配置
  @author 8526
  @date 2022-05-12 14:15:33
  版权所有 Copyright www.dahantc.com
"""
# 基本接口调用地址
BASE_URL = 'http://voice.3tong.net'

# 语言外呼提交
VOC_SUBMIT = "/json/voiceSms/SubmitVoc"

# 语言文件上传
VOC_MEDIA_UPLOAD = "/json/voiceSms/MediaFileUpload"

# 隐号呼叫AXB
VOC_AXB = "/json/voiceSms/AXB/getPhone"

# 隐号呼叫AXN
VOC_AXN = "/json/voiceSms/AXN/getPhone"

# 隐号呼叫AXYB
VOC_AXYB = "/json/voiceSms/AXYB/getPhone"

# 隐号呼叫AXxYB
VOC_AXxYB = "/json/voiceSms/AXxYB/getPhone"

# 隐号状态报告获取
VOC_H_REPORT = "/json/voiceSms/GetReport"

# 隐号释放
VOC_H_DELETE = "/json/voiceSms/delete"
