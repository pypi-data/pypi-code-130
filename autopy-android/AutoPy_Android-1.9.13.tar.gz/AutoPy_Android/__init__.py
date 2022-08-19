# -*- coding: utf-8 -*-

import sys
import time,json
import os,_thread

# import sys

# reload(sys)

# sys.setdefaultencoding('utf8')

if sys.version[0] == 2:
    from urllib2 import urlopen
    from urllib2 import quote
    from urllib.parse import urlencode

else:
    from urllib.request import urlopen
    from urllib.request import quote
    from urllib.parse import urlencode


server_url = 'http://127.0.0.1:33445/?code='


def dian(x,y):
    f=urlopen(server_url+'0,'+str(x)+','+str(y))
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]点击执行成功')
    time.sleep(0.1)

def tuo(x1,y1,x2,y2,t=1000):
    f=urlopen(server_url+'1,'+str(x1)+','+str(y1)+','+str(x2)+','+str(y2)+','+str(t))
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]滑动执行成功')
    time.sleep(0.0023*t)

def swipe(x1,y1,x2,y2,t=1000):
    f=urlopen(server_url+'1,'+str(x1)+','+str(y1)+','+str(x2)+','+str(y2)+','+str(t))
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]滑动执行成功')
    time.sleep(0.0023*t)

def tap(x,y):
    f=urlopen(server_url+'0,'+str(x)+','+str(y))
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]点击执行成功')
    time.sleep(0.1)

def click(x,y):
    f=urlopen(server_url+'0,'+str(x)+','+str(y))
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]点击执行成功')
    time.sleep(0.1)

def capturer():
    f=urlopen(server_url+'2,')
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]截屏执行成功')

def ListenServer(_Screenshots_='/sdcard/DCIM/Screenshots/',_newdir_='/sdcard/qpython/'):#暂时无用
    _Screenshots_=_Screenshots_
    _newdir_=_newdir_
    t=os.listdir(_Screenshots_)
    while (True):
      nt=os.listdir(_Screenshots_)
      li=list(set(nt)-set(t))
      if(len(li)!=0):
         t=os.listdir(_Screenshots_)
         print('监控到截图',li)#监控到截图
         os.system('mv '+_Screenshots_+li[0]+' '+_newdir_+'AutoPy_Screenshots.jpg')



def StartServer(_Screenshots_='/sdcard/DCIM/Screenshots/',_newdir_='/sdcard/qpython/'):
     _thread.start_new_thread(ListenServer, (_Screenshots_,_newdir_) )


def gesturer(li):
    li=li
    f=urlopen(server_url+'3,'+','.join(map(str,li)))
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]手势执行成功')

def HOME():
    f=urlopen(server_url+'HOME,')
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]主页键执行成功')

def BACK():
    f=urlopen(server_url+'BACK,')
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]返回键执行成功')

def RECENTS():
    f=urlopen(server_url+'RECENTS,')
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]菜单键执行成功')



def Locker():
    f=urlopen(server_url+'Lock,')
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]锁屏执行成功')

def floatWindowOpenApi():
    f=open('/sdcard/AutoFloatWindow.info','r+').read()
    if f=='1':
        return True
    #o=open('/sdcard/AutoFloatWindow.info',1w+').close()


def floatWindowCloseApi():
    f=open('/sdcard/AutoFloatWindow.info','r+').read()
    if f=='0':
        return True

def floatWindowClose():
    o=open('/sdcard/AutoFloatWindow.info','w+').close()
def systemCapturer():
    f=urlopen(server_url+'capturer,')
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]返回键执行成功')
def openapp(pkg,cls):
    f=urlopen(server_url+'openapk,'+pkg+','+cls+',')
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]打开应用执行成功')

def getID(ID):
    f=urlopen(server_url+'getID,'+ID)
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]ID点击成功')

def getText(Text):
    f=urlopen(server_url+'getText,'+quote(Text))
    f.close()
    print(time.ctime()[11:19]+' [AutoPy]Text点击成功')
def getView():
    f=urlopen(server_url+'getView,')
    data=f.read()
    f.close()
    return data




class FloatWindow:
    def __del__(self):
        print("程序结束，悬浮窗关闭")
        self.delete()
    def __init__(self,ID):
        self.server_url=server_url
        self.ID=str(ID)
        self.View={
            "id":self.ID,
            "type":"textview",
            "color":[255,255,0,0],
            "text":"测试文本",
            "Width":"500",
            "Height":"200",
            "size":"20",
            "X":"100",
            "Y":"100",
            "operation":"newly",
            "info":"备用"
        }
        # return data

    def show(self):
        #显示悬浮窗
        self.View["operation"]="newly"
        f=urlopen(self.server_url+quote(str(json.dumps(self.View))))
        data=f.read()
        f.close()
        return data   

    def delete(self):
        #删除悬浮窗
        self.View["operation"]="delete"
        f=urlopen(self.server_url+quote(str(json.dumps(self.View))))
        data=f.read()
        f.close()
        return data
    def modify(self):
        #修改悬浮窗
        self.View["operation"]="modify"
        f=urlopen(self.server_url+quote(str(json.dumps(self.View))))
        data=f.read()
        f.close()
        return data
    def makeToast(self,text="测试Toast"):
        self.View["type"]="Toast"
        self.View["text"]=text
        f=urlopen(self.server_url+quote(str(json.dumps(self.View))))
        data=f.read()
        f.close()
        self.View["type"]="textview"
        return data


class FloatButton(FloatWindow):
    def __init__(self,ID):
        super().__init__(ID)
        self.View["type"]="button"
    def getinfo(self):
        self.View["operation"]="getinfo"
        f=urlopen(self.server_url+quote(str(json.dumps(self.View))))
        data=f.read()
        f.close()
        return data

class FloatEditText(FloatWindow):
    def __init__(self,ID):
        super().__init__(ID)
        self.View["type"]="edittext"
        self.View["hint"]=""

    def getinfo(self):
        self.View["operation"]="getinfo"
        f=urlopen(self.server_url+quote(str(json.dumps(self.View))))
        data=f.read()
        f.close()
        return data

class FloatImgView(FloatWindow):


    def __init__(self,ID):
        super().__init__(ID)
        self.View["type"]="imgview"
        self.url=server_url.split("/?")[0]
        print(self.url)

    def setImg(self,Base64_data):
        self.View["Base64"]=Base64_data
        # print(self.View)
    
    def show(self):
        #显示悬浮窗
        self.View["operation"]="newly"
        data_xc={"code":str(json.dumps(self.View))}
        data_gg = urlencode(data_xc)
        data_x = data_gg.encode()
        # print(data_x)
        response = urlopen(url=self.url,data=data_x)
        ret = response.read()
        return ret   

    def delete(self):
        #删除悬浮窗
        self.View["operation"]="delete"
        data_xc={"code":str(json.dumps(self.View))}
        data_gg = urlencode(data_xc)
        data_x = data_gg.encode()
        response = urlopen(url=self.url,data=data_x)
        ret = response.read()
        return ret


    def modify(self):
        #修改悬浮窗
        self.View["operation"]="modify"
        data_xc={"code":str(json.dumps(self.View))}
        data_gg = urlencode(data_xc)
        data_x = data_gg.encode()
        response = urlopen(url=self.url,data=data_x)
        ret = response.read()
        return ret
    def getinfo(self):
        self.View["operation"]="getinfo"
        data_xc={"code":str(json.dumps(self.View))}
        data_gg = urlencode(data_xc)
        data_x = data_gg.encode()
        response = urlopen(url=self.url,data=data_x)
        ret = response.read()
        return ret

    def getinfo(self):
        self.View["operation"]="getinfo"
        f=urlopen(self.server_url+quote(str(json.dumps(self.View))))
        data=f.read()
        f.close()
        return data
    

def img_to_base64(path):
    image_path = path

    image= open(image_path, 'rb').read()
    image_base64 = str(base64.b64encode(image), encoding='utf-8')
    return image_base64



if __name__ == "__main__":
    import json,base64


    img_path=r'F:/AutoPy-Android/都市蓝领 .png'
    base64_data=img_to_base64(img_path)
    server_url='http://192.168.31.93:8020/?code='
    imgView=FloatImgView("x")
    imgView.setImg(base64_data)
    imgView.View["X"]="0"
    imgView.View["Y"]="100"
    imgView.View["Width"]="1000"
    imgView.View["Height"]="1000"

    ret=imgView.show()

    
    print(ret)
    Butt=FloatButton("b1")
    # Butt.delete()
    Butt.show()
    print(Butt.getinfo())
    edittext= FloatEditText("ED1")
    edittext.View["Y"]="1000"
    # edittext.delete()
    edittext.show()
    A=FloatWindow("a1")
    # A.delete()
    A.makeToast("开始运行AutoPy测试程序")
    time.sleep(1)
    A.show()
    for i in range(20):
        A.View["text"]=f"测试{i}"
        A.View["size"]=str(int(A.View["size"])+1)
        A.View["X"]=str(int(A.View["X"])+10)
        A.View["Y"]=str(int(A.View["Y"])+10)
        A.modify()
        # time.sleep(0.5)
    A.View["text"]=f"两秒关掉"
    A.modify()
    
    time.sleep(2)
    # A.delete()
    A.makeToast("已关掉，已结束")
    print(Butt.getinfo())
    # Butt.delete()
    # edittext.delete()
    # imgView.delete()

