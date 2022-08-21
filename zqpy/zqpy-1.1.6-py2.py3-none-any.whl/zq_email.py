#region 邮件
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import zq_log

def dosc():
    zq_log.log_debug('email 邮件收发系统')

class email_class():
    def __init__(self, host='smtp.qq.com', user='1620829248@qq.com', pw='rdtbkktznzpkddec'): #vsjgukkyzjjcfacd
        self.mail_host= host    #设置服务器
        self.mail_user= user    #用户名
        self.mail_pass= pw      #口令 密码
        self.sender = user
    
    def SendMail(self, userName, title, content, *receivers):
        '''
        发送邮件
        :param username: 用户名
        :param title: 标题
        :param content: 内容
        :param receivers: 接受方邮箱地址
        '''
        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = Header(userName, 'utf-8')
        msgRoot['To'] =  Header('用户', 'utf-8')
        subject = title #'Python SMTP 邮件测试'
        msgRoot['Subject'] = Header(subject, 'utf-8')
        
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        
        
        mail_msg = '''
        <p>Python 邮件发送测试...</p>
        <p><a href='http://vip.mayishidai.cn'>菜鸟教程链接</a></p>
        <p>图片演示：</p>
        <p><img src='cid:image1'></p>
        '''
        # msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
        msgAlternative.attach(MIMEText(content, 'html', 'utf-8'))
        
        '''
        fp = open('./image/test.jpg', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        
        # 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)
        '''

        reTitle = title
        if len(title + content) < 256 :
        	reTitle = title + content
        try:
            smtpObj = smtplib.SMTP() 
            smtpObj.connect(self.mail_host, 25)    # 25 为 SMTP 端口号
            smtpObj.login(self.mail_user,self.mail_pass)
            smtpObj.sendmail(self.sender, receivers, msgRoot.as_string())
            zq_log.log_debug('邮件【success】：%s \n %s'%(reTitle, content))
            return True
        except smtplib.SMTPException as e:
            zq_log.log_debug('邮件【faile】：%s \n %s \n %s'%(reTitle, content, str(e)))
            return False

if __name__ == '__main__':
    email = email_class()
    content = '''
        <p>Python 邮件发送测试...</p>
        <p><a href='http://vip.mayishidai.cn'>菜鸟教程链接</a></p>
        <p>图片演示：</p>
        <p><img src='cid:image1'></p>
        '''
    email.SendMail('用户','嘿嘿嘿',content,'877665041@qq.com')

#endregion