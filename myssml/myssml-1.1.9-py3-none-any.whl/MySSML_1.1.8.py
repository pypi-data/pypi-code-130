#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    : MySSML.py
@Time    : 2022/08/21 15:14:11
@Author  : 呆哥
@Contact : rdaim@qq.com
@Version : 1.1.8
@Python Ver : 3.9.13 64-bit
@Desc    : 自由生成符合SSML格式规范的XML字符串或保存为XML文件
'''

""" MySSML is a helper to construct SSML
ABOUT SSML:
https://docs.microsoft.com/zh-cn/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=csharp
https://cloud.google.com/text-to-speech/docs/ssml?hl=zh-cn
https://www.w3.org/TR/speech-synthesis/

1. Create a MySSML object
    s = MySSML()

2. Add your speech text
    s.say('Hello')

3. Retrieve your SSML
    s.ssml()      # to retrieve ssml with <speak> wrapper

"""
from ntpath import join
import re
import urllib.parse
from xml.dom import minidom

class MySSML:
    INTERPRET_AS = ['characters', 'spell-out', 'cardinal', 'number',
                          'ordinal', 'digits', 'fraction', 'unit', 'date',
                          'time', 'telephone', 'address', 'interjection', 'expletive']

    DATE_FORMAT = ['mdy', 'dmy', 'ymd', 'md', 'dm', 'ym', 'my', 'd', 'm', 'y']

    ROLE = ['ivona:VB', 'ivona:VBD', 'ivona:NN', 'ivona:SENSE_1']

    IPA_CONSONANTS = ['b', 'd', 'd͡ʒ', 'ð', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'ŋ',
                      'p', 'ɹ', 's', 'ʃ', 't', 't͡ʃ', 'θ', 'v', 'w', 'z', 'ʒ']

    IPA_VOWELS = ['ə', 'ɚ', 'æ', 'aɪ', 'aʊ', 'ɑ', 'eɪ', 'ɝ', 'ɛ', 'i', 'ɪ', 'oʊ', 'ɔ', '',
                  'ɔɪ', 'u', 'ʊ', 'ʌ']

    X_SAMPA_CONSONANTS = ['b', 'd', 'dZ', 'D', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'N', 'p', 'r\\',
                          's', 'S', 't', 'tS', 'T', 'v', 'w', 'z', 'Z']

    X_SAMPA_VOWELS = ['@', '@`', '{', 'aI', 'aU', 'A', 'eI', '3`', 'E', 'i', 'I', 'oU', 'O', 'OI', 'U',
                      'U', 'V']

    IPA_SPECIAL = ['ˈ', 'ˌ', '.']

    X_SAMPA_SPECIAL = ['”', '%', '.']

    ALPHABETS = {
        'ipa': IPA_CONSONANTS + IPA_VOWELS + IPA_SPECIAL,
        'x-sampa': X_SAMPA_CONSONANTS + X_SAMPA_VOWELS + X_SAMPA_SPECIAL
    }

    PAUSE_STRENGTH = ['none', 'x-weak', 'weak', 'medium', 'strong', 'x-strong']

    EMPHASIS_LEVELS = ['strong', 'moderate', 'reduced']

    PROSODY_ATTRIBUTES = {
        'rate': ['x-slow', 'slow', 'medium', 'fast', 'x-fast'],
        'pitch': ['x-low', 'low', 'medium', 'high', 'x-high'],
        'volume': ['silent', 'x-soft', 'soft', 'medium', 'loud', 'x-loud']
    }

    VALID_SILENCE_NAMES = ('Leading','Tailing','Sentenceboundary')

    ROLE_NAMES = ("Girl","Boy","YoungAdultFemale","YoungAdultMale","OlderAdultFemale","OlderAdultMale","SeniorFemale","SeniorMale")

    TYPES = {
        "P":["<p*>","</p>",'<p(.*?)>(.*?)</p>'],
        "S":["<s*>","</s>",'<s(.*?)>(.*?)</s>'],
        "VOICE":["<voice*>","</voice>",'<voice(.*?)>(.*?)</voice>'],
        "EXPRESS_AS":["<mstts:express-as*>","</mstts:express-as>",'<mstts:express-as(.*?)>(.*?)</mstts:express-as>']
    }

    VALID_VOICE_NAMES = ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunyangNeural', 'zh-CN-XiaochenNeural', 'zh-CN-XiaohanNeural', 'zh-CN-XiaomoNeural', 'zh-CN-XiaoqiuNeural', 'zh-CN-XiaoruiNeural', 'zh-CN-XiaoshuangNeural', 'zh-CN-XiaoxuanNeural', 'zh-CN-XiaoyanNeural', 'zh-CN-XiaoyouNeural', 'zh-CN-YunxiNeural', 'zh-CN-YunyeNeural']

    VALID_VOICE_NAMES_CN = {'晓晓': 'zh-CN-XiaoxiaoNeural', '云扬': 'zh-CN-YunyangNeural', '晓辰': 'zh-CN-XiaochenNeural', '晓涵': 'zh-CN-XiaohanNeural', '晓墨': 'zh-CN-XiaomoNeural', '晓秋': 'zh-CN-XiaoqiuNeural', '晓睿': 'zh-CN-XiaoruiNeural', '晓双': 'zh-CN-XiaoshuangNeural', '晓萱': 'zh-CN-XiaoxuanNeural', '晓颜': 'zh-CN-XiaoyanNeural', '晓悠': 'zh-CN-XiaoyouNeural', '云希': 'zh-CN-YunxiNeural', '云野': 'zh-CN-YunyeNeural'}

    VALID_VOICE_NAMES_MAP = {'zh-CN-XiaoxiaoNeural': ['general', 'assistant', 'chat', 'customerservice', 'newscast', 'affectionate', 'angry', 'calm', 'cheerful', 'disgruntled', 'fearful', 'gentle', 'lyrical', 'sad', 'serious'], 'zh-CN-YunyangNeural': ['general', 'customerservice', 'narration-professional', 'newscast-casual'], 'zh-CN-XiaochenNeural': ['general'], 'zh-CN-XiaohanNeural': ['general', 'calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad', 'gentle', 'affectionate', 'embarrassed'], 'zh-CN-XiaomoNeural': ['general', 'embarrassed', 'calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad', 'depressed', 'affectionate', 'gentle', 'envious'], 'zh-CN-XiaoqiuNeural': ['general'], 'zh-CN-XiaoruiNeural': ['general', 'calm', 'fearful', 'angry', 'sad'], 'zh-CN-XiaoshuangNeural': ['general', 'chat'], 'zh-CN-XiaoxuanNeural': ['general', 'calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'gentle', 'depressed'], 'zh-CN-XiaoyanNeural': ['general'], 'zh-CN-XiaoyouNeural': ['general'], 'zh-CN-YunxiNeural': ['general', 'narration-relaxed', 'embarrassed', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad', 'depressed', 'chat', 'assistant', 'newscast'], 'zh-CN-YunyeNeural': ['general', 'embarrassed', 'calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad']}

    VALID_VOICE_STYLES = {
        'general':['通用'],
        'advertisement-upbeat':['广告','促销','推广'],
        'affectionate':['撒娇','卖萌'],
        'angry':['生气','气愤','厌恶','讨厌'],
        'assistant':['助理','助手'],
        'calm':['平静','淡定'],
        'chat':['聊天','随意','轻松'],
        'cheerful':['愉快','快乐','开心'],
        'customerservice':['客服','销售','热情'],
        'depressed':['沮丧','失落','忧郁'],
        'disgruntled':['不满','不开心','轻蔑','抱怨','不悦','蔑视'],
        'embarrassed':['尴尬','犹豫','不确定'],
        'empathetic':['同理心','同情','理解'],
        'envious':['钦佩','佩服','认可','崇拜'],
        'excited':['兴奋','乐观'],
        'fearful':['恐惧','紧张','不安'],
        'friendly':['友好','和善','真诚','关切'],
        'gentle':['温柔','温和','礼貌'],
        'hopeful':['期待','充满希望','渴望'],
        'lyrical':['抒情','深情','感伤','伤感'],
        'narration-professional':['专业旁白'],
        'narration-relaxed':['轻松旁白'],
        'newscast':['新闻'],
        'newscast-casual':['新闻-休闲'],
        'newscast-formal':['新闻-正式'],
        'poetry-reading':['诗歌朗诵','读诗'],
        'sad':['悲伤','伤心','痛苦'],
        'serious':['严肃','一本正经','命令'],
        'shouting':['大喊大叫','吵闹'],
        'sports-commentary':['轻松体育'],
        'sports-commentary-excited':['活力体育'],
        'whispering':['窃窃私语','柔和'],
        'terrified':['害怕','小心','颤抖'],
        'unfriendly':['冷漠','不友好','无情','冷淡','冷酷']
    }

    tmpstring = ['<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="zh-CN">']

    def __init__(self):
        # 用于存放SSML元素（对象）
        self.obj_list = []

        # 默认发音人
        self.defaut_speaker = "zh-CN-XiaoxiaoNeural"

        # 自动标记,如果设为True，则会自动添加书签标记，主要用于字幕合成
        self.automark = False 

    def clear(self):
        self.obj_list = []

    # 处理特殊字符，转义处理
    def _escape(self, text):
        # escaped_lines = html.escape(text)
        if text is None:
            return ""
        else:
            return re.sub('&', 'and', re.sub('[\<\>\"\']', '', str(text)))

    # 中英文分句函数
    def cut_sent(self, para):
        para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
        para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
        para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
        para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        para = para.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        return para.split("\n")

    # 保存XML文件
    def saveXML(self, xmlstr, filename, indent="\t", newl="\n", encoding="utf-8"):
        """Save SSML xml string to file"""
        dom = minidom.parseString(xmlstr)
        with open(filename, 'w') as f:
            dom.writexml(f, "", indent, newl, encoding)

    # 检验是否全是中文字符
    def is_all_chinese(self,strs):
        for _char in strs:
            if not '\u4e00' <= _char <= '\u9fa5':
                return False
        return True

    # 检查说话人中是否有相应的风格
    def check_speaker_style(self,speaker,style):
        res = False
        #判断一下发音人是否为中文
        if self.is_all_chinese(speaker):
            if speaker in self.VALID_VOICE_NAMES_CN:
                speaker = self.VALID_VOICE_NAMES_CN[speaker]
            else:
                return False

        if speaker not in self.VALID_VOICE_NAMES_MAP:
            return False
        else:
            speakerStyles = self.VALID_VOICE_NAMES_MAP[speaker]
        
        #判断一下风格是否为中文
        if self.is_all_chinese(style):
            found = False
            for key,value in self.VALID_VOICE_STYLES.items():
                if style in value:
                    style = key
                    found = True
                    break
            if not found:
                return False

        if style in speakerStyles:
            res = True
        return res

    # 检验时间值是否符合规范
    def _validate_duration(self, duration):
        try:
            matches = re.match('^(\d*\.?\d+)(s|ms)$', duration)
            value_part = int(matches.groups()[0])
            unit_part = matches.groups()[1]
            if (unit_part == 's' and value_part > 10) or value_part > 10000:
                raise ValueError('Duration %s is longer than 10 seconds' % duration)
        except Exception:
            raise ValueError('Duration %s is invalid' % duration)

    # 检验网址是否符合规范
    def _validate_url(self, url):
        try:
            parse_tokens = urllib.parse.urlparse(url)
            if parse_tokens[0] == '' or parse_tokens[1] == '':
                raise ValueError('URL %s invalid' % url)
        except Exception:
            raise ValueError('URL %s invalid' % url)

    # 打印SSML中的对象列表
    def dump(self):
        """Dump a list of all items added to obj_list object"""
        for item in self.obj_list:
            print(item)
    
    # 获取SSML中的对象列表
    def getObjList(self):
        """return a list of all items added to obj_list object"""
        return self.obj_list

    # 生成SSML的XML字符串
    def ssml(self):
        """Return the SSML, pass true to strip <speak> tag wrapper"""
        self.print_tree()
        self.tmpstring.append("</speak>")
        result = ''.join(self.tmpstring)
        return result

    # 获取SSML中的对象，构成树状结构
    def get_tree(self, pid = "ROOT"):
        """Return the SSML Tree from root"""
        result = []
        for item in self.obj_list:
            if pid == item["pid"]:
                temp = self.get_tree( item["id"])
                if (len(temp) > 0):
                    item["children"] = temp
                result.append(item)
        return  result

    # 获取SSML的XML字符对象列表
    def print_tree(self,objs=None):
        """Return the SSML Tree XML String"""
        TYPES = self.TYPES
        if objs is None:
            objs = self.get_tree()
        for obj in objs:
            if "children" in obj:              
                if obj["type"] in TYPES:                  
                    SZ = re.findall(TYPES[obj["type"]][2], obj["text"])
                    # print(SZ)
                    #print(TYPES[ obj["type"]][0].replace("*", SZ[0][0]))
                    self.tmpstring.append(TYPES[ obj["type"]][0].replace("*", SZ[0][0])) 
                    if SZ[0][1]!="":
                        #print(SZ[0][1])
                         self.tmpstring.append( SZ[0][1])
                self.print_tree(obj["children"])
                if obj["type"] in TYPES:
                    #print(TYPES[ obj["type"]][1])
                     self.tmpstring.append( TYPES[ obj["type"]][1])      
            else:           
                if obj["type"] in TYPES:
                    SZ = re.findall(TYPES[obj["type"]][2], obj["text"])
                    #print(TYPES[obj["type"]][0].replace("*", SZ[0][0]))
                    self.tmpstring.append(TYPES[ obj["type"]][0].replace("*", SZ[0][0]))
                    if SZ[0][1]!="":
                        #print(SZ[0][1])
                         self.tmpstring.append(SZ[0][1])
                    #print(TYPES[ obj["type"]][1])
                    self.tmpstring.append(TYPES[ obj["type"]][1])
                else:
                    #print(obj["text"])
                    self.tmpstring.append(obj["text"])           
            if self.automark and obj['type'] in ['P','S','PROSODY','TEXT']:
                mark = '<bookmark mark="{}" />'.format(obj["id"])
                self.tmpstring.append(mark)
 
    # 根据当前对象的类型，获取当前对象的ID以及父ID
    def get_objIdPid(self,objType):
        id = None
        pid = "ROOT"
        #print(self.obj_list)
        objTotal = len(self.obj_list)
        id = objType + "_" + str(objTotal)

        if objType in ["TEXT" ,"PROSODY" , "SUB" , "LANG" , "PAUSE" , "AUDIO" , "SAY_AS" , "W" , "PHONEME" , "EMPHASIS", "MARK"]:
            objPType = ["P","S","VOICE", "EXPRESS_AS"]

        elif objType == "S":
            objPType = ["P","VOICE", "EXPRESS_AS"]

        elif objType == "P":
            objPType = ["VOICE", "EXPRESS_AS"]

        elif objType in ["SILENCE" , "EXPRESS_AS"]:
            objPType = ["VOICE"] 

        elif objType in ["VOICE" , "BGM"]:
            objPType = ["ROOT"]
        
        else:
            pass
        
        #print(objTotal)
        if objTotal >0 and "ROOT" not in objPType:
            tmpObjList = reversed(self.obj_list)
            for obj in tmpObjList:
                if obj["type"] in objPType :
                    pid = obj["id"]
                    break

        #需要判断一下有没有建议VOICE对象，如果没有就需要新建一个
        if objType != "VOICE" and pid == "ROOT":
            print("---- no voice ---")
            self.voice()
            pid = self.obj_list[-1]["id"]

        return id,pid

    # 添加一个普通文本到SSML
    def say(self, text):
        """Add raw text to SSML"""
        if text is None:
            raise TypeError('Parameter text must not be None')

        TYPE = "TEXT"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '%s' % self._escape(text)
        })
        return self

    # 添加一个lang格式的文本到SSML
    def lang(self, text, lang="zh-CN"):
        """Wrap text with <lang> tag"""
        if text is None:
            raise TypeError('Parameter text must not be None')

        TYPE = "LANG"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '<lang xml:lang="{}">{}</lang>'.format(lang,  self._escape(text))
        })
        return self

    # 添加一个voice格式的文本到SSML
    
    def voice(self, text='', name=""):
        """Wrap text with <voice> tag"""
        # if text is None:
        #     raise TypeError('Parameter text must not be None')
        if name is None or name == "":
            name = self.defaut_speaker

        if self.is_all_chinese(name):
            if name in self.VALID_VOICE_NAMES_CN:
                name = self.VALID_VOICE_NAMES_CN[name]
            else:
                raise ValueError('The name provided to voice is not valid')

        if name not in self.VALID_VOICE_NAMES:
            raise ValueError('The name provided to voice is not valid')

        TYPE = "VOICE"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "params":   {"name":name,"text":text}, #这个参数非常重要，不要删除
            "text"  :   '<voice name="{}">{}</voice>'.format(name, self._escape(text))
        })
        return self

    # 添加一个静音设置到SSML，type 参数可选值还有： Leading(段落头部静音),Tailing(段落尾部静音)
    # 非通用元素，目前只微软TTS支持
    def silence(self, value="1000ms", type="Sentenceboundary"):
        """Wrap text with <silence> tag"""
        if value is None:
            raise TypeError('Parameter text must not be None')
        if type not in self.VALID_SILENCE_NAMES:
            raise TypeError('Parameter type must use on of' + ''.join(self.VALID_SILENCE_NAMES))
        TYPE = "SILENCE"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '<mstts:silence type="{}" value="{}" />'.format(type, value)
        })
        return self  
    # 增加一个别名
    sp = silence

    # 指定说话人的风格、角度以及风格强度
    def style(self, text="", style="general", styledegree=2, role = None):
        """Wrap text with <style> tag"""
        if self.is_all_chinese(style):
            found = False
            for key,value in self.VALID_VOICE_STYLES.items():
                if style in value:
                    style = key
                    found = True
                    break
            if not found:
                raise ValueError('The name provided to style is not valid')

            # 字典key和value互换
            # dict_new = {value:key for key,value in self.VALID_VOICE_STYLES.items()}
            # if style not in dict_new:
            #     raise ValueError('The name provided to style is not valid')
            # else:
            #     style = dict_new[style] #转为英文

        if style not in self.VALID_VOICE_STYLES:
            style = "general"
            #raise ValueError('The name provided to style is not valid')

        if role is not None: #还需要判断一下role规则
            if role in self.ROLE_NAMES:
                role = ' role="{}"'.format(role)
            else:
                role = ''
                #raise TypeError('role can not be found!')
        else:
            role = ''
        # if text is None:
        #     raise TypeError('Parameter text must not be None')
        TYPE = "EXPRESS_AS"
        id,pid = self.get_objIdPid(TYPE)

        # 判断一下是否发音人是否具备这种风格
        for obj in self.obj_list:
            if obj["id"] == pid and obj["type"] == "VOICE":
                speaker = obj["params"]["name"]
                res = self.check_speaker_style(speaker=speaker,style=style)
                print("speaker has style? ",res)
                if not res:
                    style = "general"
                break

        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '<mstts:express-as{} style="{}" styledegree="{}" >'.format(role,style, styledegree) + self._escape(text) + '</mstts:express-as>'
        })
        return self  

    # 添加一个背景音乐到SSML
    # 非通用元素，目前只微软TTS支持
    def backgroundaudio(self, url, volume="0.45", fadein="3000", fadeout="4000"):
        """Wrap text with <backgroundaudio> tag"""
        if url is None:
            raise TypeError('Parameter url must not be None')
        self._validate_url(url)
        TYPE = "BGM"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '<mstts:backgroundaudio src="{}" volume="{}" fadein="{}" fadeout="{}" />'.format(url, volume, fadein, fadeout)
        })
        return self
    # 增加一个别名  
    bgm = backgroundaudio            

    # 添加一个段落<p>到SSML
    def p(self, text=''):
        """paragraph Wrap text with <p> tag"""
        # if text is None:
        #     raise TypeError('Parameter text must not be None')
        TYPE = "P"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '<p>%s</p>' % self._escape(text)
        })
        return self 
    # 增加一个别名    
    paragraph = p

    # 添加一个句子<s>到SSML
    def s(self, text=''):
        """sentence Wrap text with <s> tag"""
        # if text is None:
        #     raise TypeError('Parameter text must not be None')
        # Get provius object type
        TYPE = "S"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '<s>%s</s>' % self._escape(text)
        })
        return self 
    # 增加一个别名    
    setence = s

    # 添加一个指定时间的停顿到SSML
    def pause(self, duration):
        """Add a pause to SSML, must be between 0 and 10 seconds"""
        if duration is None:
            raise TypeError('Parameter duration must not be None')
        self._validate_duration(duration)
        TYPE = "PAUSE"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   "<break time='%s'/>" % self._escape(duration)
        })
        return self 
    # 增加一个别名    
    td = pause

    # 添加一个指定名称的书签到SSML
    def mark(self, text):
        """Add a bookmark to SSML, must be string"""
        if text is None:
            raise TypeError('Parameter duration must not be None')
        TYPE = "MARK"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   '<bookmark mark="{}" />'.format(self._escape(text))
        })
        return self 

    # 添加一个指定强度的停顿到SSML
    def pause_by_strength(self, strength):
        """Add a pause to SSML, with a preset strength value like strong"""
        if strength is None:
            raise TypeError('Parameter strength must not be None')
        try:
            strength = strength.lower().strip()
        except AttributeError:
            raise AttributeError('Parameter strength must be a string')
        if strength in MySSML.PAUSE_STRENGTH:
            TYPE = "PAUSE"
            id,pid = self.get_objIdPid(TYPE)
            self.obj_list.append({
                "id"    :   id,
                "pid"   :   pid,
                "type"  :   TYPE,
                "text"  :   "<break strength='%s'/>" % strength
            })
            return self
        else:
            raise ValueError('Value %s is not a valid strength' % strength)

    # 添加一个声音元素到SSML
    def audio(self, url):
        """Add audio to SSML, must pass a valid url"""
        if url is None:
            raise TypeError('Parameter url must not be None')
        self._validate_url(url)
        TYPE = "AUDIO"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   "<audio src='%s'/>" % self._escape(url)
        })
        return self 

    # 逐字读出单词中每一个字母或字
    def spell(self, text):
        """Read out each character in text"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        TYPE = "SAY_AS"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   "<say-as interpret-as='spell-out'>%s</say-as>" % self._escape(text)
        })
        return self 

    # 以非常慢的速度逐字读出单词中每一个字母或字
    def spell_slowly(self, text, duration):
        """Read out each character in text slowly placing a pause between characters, pause between 0 and 10 seconds"""
        if text is None:
            raise TypeError('Parameter text must not be None')
        if duration is None:
            raise TypeError('Parameter duration must not be None')
        self._validate_duration(duration)
        ssml = ''
        for c in self._escape(text):
            ssml += "<say-as interpret-as='spell-out'>%s</say-as> <break time='%s'/> " % (c, self._escape(duration))
        TYPE = "SAY_AS"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   ssml.strip()
        })
        return self 

    # 以指定格定读出相关词语，如“1：3” 可以读成 “1比3”
    def say_as(self, word, interpret, interpret_format=None):
        """Special considerations when speaking word include date, numbers, etc."""
        if word is None:
            raise TypeError('Parameter word must not be None')
        if interpret is None:
            raise TypeError('Parameter interpret must not be None')
        if interpret not in MySSML.INTERPRET_AS:
            raise ValueError('Unknown interpret as %s' % str(interpret))
        if interpret_format is not None and interpret_format not in MySSML.DATE_FORMAT:
            raise ValueError('Unknown date format %s' % str(interpret_format))
        if interpret_format is not None and interpret != 'date':
            raise ValueError('Date format %s not valid for interpret as %s' % (str(interpret_format), str(interpret)))
        format_ssml = '' if interpret_format is None else " format='%s'" % interpret_format
        TYPE = "SAY_AS"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   "<say-as interpret-as='%s'%s>%s</say-as>" % (interpret, format_ssml, str(word))
        })
        return self

    def parts_of_speech(self, word, role):
        """Special considerations when speaking word include usage or role of word"""
        if word is None:
            raise TypeError('Parameter word must not be None')
        if role is None:
            raise TypeError('Parameter role must not be None')
        if role not in MySSML.ROLE:
            raise ValueError('Unknown role %s' % str(role))
        TYPE = "W"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   "<w role='%s'>%s</w>" % (self._escape(role), self._escape(word))
        })
        return self
    # 增加一个别名    
    w = parts_of_speech

    # 使用音素改善发音
    def phoneme(self, word, alphabet, ph):
        """Specify specific phonetics used when speaking word"""
        if word is None:
            raise TypeError('Parameter word must not be None')
        if alphabet is None:
            raise TypeError('Parameter alphabet must not be None')
        if ph is None:
            raise TypeError('Parameter ph must not be None')
        if alphabet not in MySSML.ALPHABETS:
            raise ValueError('Unknown alphabet %s' % str(alphabet))
        TYPE = "PHONEME"
        id,pid = self.get_objIdPid(TYPE)
        self.obj_list.append({
            "id"    :   id,
            "pid"   :   pid,
            "type"  :   TYPE,
            "text"  :   "<phoneme alphabet='%s' ph='%s'>%s</phoneme>" % (self._escape(alphabet), self._escape(ph), self._escape(word))
        })
        return self

    # 用于添加或删除文本的单词级强调
    def emphasis(self, level, word):
        """Specify specific emphasis used when speaking word"""
        if level is None:
            raise TypeError('Parameter level must not be None')
        if word is None:
            raise TypeError('Parameter word must not be None')
        try:
            if len(word.strip()) == 0:
                raise ValueError('Parameter word must not be empty')
            level = level.lower().strip()
            if level in MySSML.EMPHASIS_LEVELS:
                self.obj_type = "EMPHASIS"
                TYPE = "PHONEME"
                id,pid = self.get_objIdPid(TYPE)
                self.obj_list.append({
                    "id"    :   id,
                    "pid"   :   pid,
                    "type"  :   TYPE,
                    "text"  :   "<emphasis level='%s'>%s</emphasis>" % (level, self._escape(word))
                })
                return self
            else:
                raise ValueError('Unknown emphasis level %s' % level)
        except AttributeError:
            raise AttributeError('Parameters must be strings')

    # 指定文本转语音输出的音节、调型、范围、速率和音量的变化
    def prosody(self, attributes, word):
        """Specify set some words's rate|vol|pitch params when say sentence"""
        tag_attributes = ''
        if attributes is None:
            raise TypeError('Parameter attributes must not be None')
        if word is None:
            raise TypeError('Parameter word must not be None')
        try:
            for k, v in attributes.items():
                v = v.lower().strip()
                if v in MySSML.PROSODY_ATTRIBUTES[k]:
                    tag_attributes += " %s='%s'" % (k, v)
                elif k == 'rate':
                    rate_value = int(''.join([c for c in v if c in '0123456789']))
                    if 0 <= rate_value <= 50:
                        tag_attributes += " %s='%d%%'" % (k, rate_value)
                    else:
                        raise ValueError('Attribute %s value %s is invalid' % (v, k))
                else:
                    raise ValueError('Attribute %s value %s is invalid' % (v, k))
            TYPE = "PROSODY"
            id,pid = self.get_objIdPid(TYPE)
            self.obj_list.append({
                "id"    :   id,
                "pid"   :   pid,
                "type"  :   TYPE,
                "text"  :   "<prosody%s>%s</prosody>" % (tag_attributes, self._escape(word))
            })
            return self
        except AttributeError:
            raise AttributeError('Parameters must be strings')
        except KeyError:
            raise KeyError('Attribute is unknown')
        except ValueError:
            raise ValueError('Attribute value is invalid')
    # 增加一个别名    
    ps = prosody

    # 以别名读出指定的词语
    def sub(self, alias, word):
        """Wrap text with <sub> tag with alias"""
        if alias is None:
            raise TypeError('Parameter alias must not be None')
        if word is None:
            raise TypeError('Parameter word must not be None')
        try:
            alias = alias.strip()
            if len(alias) == 0:
                raise ValueError('Alias must not be empty')
            word = word.strip()
            if len(word) == 0:
                raise ValueError('Word must not be empty')
            TYPE = "SUB"
            id,pid = self.get_objIdPid(TYPE)
            self.obj_list.append({
                "id"    :   id,
                "pid"   :   pid,
                "type"  :   TYPE,
                "text"  :   "<sub alias='%s'>%s</sub>" % (alias, self._escape(word))
            })
            return self
        except AttributeError:
            raise AttributeError('Parameters alias and word must be strings')