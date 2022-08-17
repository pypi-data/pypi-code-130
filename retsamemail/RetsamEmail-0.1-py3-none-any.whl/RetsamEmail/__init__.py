


import retsam_modules.RetsamWL
import threading
from datetime import datetime
import os
import traceback



import base64
import imaplib
import json
import smtplib
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import lxml.html

class RetsamEmail:

    def __init__(self, 
                 str_log_path,
                 ui_log_func = False, ui_log_params = []):
        self.MUTEX_DUMP_EMAIL = threading.Lock()
        self.log = RetsamWL.Log(str_path = str_log_path, ui_log_func = ui_log_func, ui_log_params = ui_log_params)
        self.GOOGLE_CLIENT_ID = '662369546516-p7j8u5jmk24vkckgj6b9dfpuvq6os7fk.apps.googleusercontent.com'
        self.GOOGLE_CLIENT_SECRET = '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'
        self.GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
        self.REDIRECT_URI = 'http://localhost:1'
        #self.GOOGLE_REFRESH_TOKEN = None
        #self.str_email_password = str_email_password
        #self.str_email_login = str_email_login
        self.str_data_path = str_path = os.getenv("USERPROFILE") + '//retsam software//email.json'
        self.get_dict_data()

        

    
    # habr start =================================================================


    def command_to_url(self, command):
        return '%s/%s' % (self.GOOGLE_ACCOUNTS_BASE_URL, command)

    def url_escape(self, text):
        return urllib.parse.quote(text, safe='~-._')


    def url_unescape(self, text):
        return urllib.parse.unquote(text)

    def url_format_params(self, params):
        param_fragments = []
        for param in sorted(params.items(), key=lambda x: x[0]):
            param_fragments.append('%s=%s' % (param[0], self.url_escape(param[1])))
        return '&'.join(param_fragments)

    def generate_permission_url(self, client_id, scope='https://mail.google.com/'):
        params = {}
        params['client_id'] = client_id
        params['redirect_uri'] = self.REDIRECT_URI
        params['scope'] = scope
        params['response_type'] = 'code'
        return '%s?%s' % (self.command_to_url('o/oauth2/auth'), self.url_format_params(params))

    def call_authorize_tokens(self, client_id, client_secret, authorization_code):
        params = {}
        params['client_id'] = client_id
        params['client_secret'] = client_secret
        params['code'] = authorization_code
        params['redirect_uri'] = self.REDIRECT_URI
        params['grant_type'] = 'authorization_code'
        request_url = self.command_to_url('o/oauth2/token')
        response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode('UTF-8')).read().decode('UTF-8')
        return json.loads(response)


    def call_refresh_token(self, client_id, client_secret, refresh_token):
        params = {}
        params['client_id'] = client_id
        params['client_secret'] = client_secret
        params['refresh_token'] = refresh_token
        params['grant_type'] = 'refresh_token'
        request_url = self.command_to_url('o/oauth2/token')
        response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode('UTF-8')).read().decode('UTF-8')
        return json.loads(response)

    def generate_oauth2_string(self, username, access_token, as_base64=False):
        auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
        if as_base64:
            auth_string = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        return auth_string

    def refresh_authorization(self, google_client_id, google_client_secret, refresh_token):
        response = self.call_refresh_token(google_client_id, google_client_secret, refresh_token)
        return response['access_token'], response['expires_in']

    def get_code_with_selenium(self, 
                               str_url, 
                               str_email, 
                               str_pass):
        my_driver = Selen_driver_4()
        if not my_driver.create_chromedriver(bool_headless = True):
            self.log.write_log("get_code_with_selenium: не удалось создать браузер")
            return False
        if not my_driver.go_to_url(str_url):
            self.log.write_log("get_code_with_selenium: ERROR #8UwNdtgqch0TOG8")
            return False
        if not my_driver.by_XPATH().send("//*[@type = 'email']",
                                         str_email):
            self.log.write_log("get_code_with_selenium: ERROR #8UwNdtgqch0TOG8")
            return False
        if not my_driver.by_XPATH().click("Далее",
                                         bool_text = True):
            self.log.write_log("get_code_with_selenium: ERROR #dwOXZQKWVrmi8Oa")
            return False
        
    def get_authorization(self, 
                          google_client_id, 
                          google_client_secret, 
                          str_email, 
                          str_pass):
        scope = "https://mail.google.com/"
        #print('Navigate to the following URL to auth:', self.generate_permission_url(google_client_id, scope))
        #authorization_code = input('Enter verification code: ')
        str_url = self.generate_permission_url(google_client_id, scope)
        print(str_url)
        str_authorization_code = get_code_with_selenium(str_url)
        if not str_authorization_code:
            return False, False, False
        # тут прописать авто получение кода
        response = self.call_authorize_tokens(google_client_id, google_client_secret, str_authorization_code)
        return response['refresh_token'], response['access_token'], response['expires_in']
    # habr end =====================================================================


    def get_dict_data(self):
        with self.MUTEX_DUMP_EMAIL:
            try:
                with open(self.str_data_path, "r", encoding="utf-8") as fr:
                    dict_data = json.load(fr)
                self.dict_tokens_data = dict_data
                return True
            except:
                return False
    # вернет token или false
    def get_token(self, 
                  str_email, 
                  ):


        try:
            return self.dict_tokens_data[str_email]['token']
        except:
            pass
        self.log.write_log("ОШИБКА, НЕВОЗМОЖНО ОТПРАВИТЬ ПИСЬМО, НУЖНО ПЕРЕСОЗДАТЬ ТОКЕН ДОСТУПА К ПОЧТЕ!")
        return False


    def test_imap(self, user, auth_string):
        try:
            imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
            imap_conn.debug = 4
            imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
            imap_conn.select('INBOX')
        except:
            return False
        return True


    def test_smpt(self, user, base64_auth_string):
        try:
            smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_conn.set_debuglevel(True)
            smtp_conn.ehlo('test')
            smtp_conn.starttls()
            smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64_auth_string)
        except:
            return False
        return True
    def init_token(self, str_email):
        str_refresh_token = self.get_token(str_email)
        if not str_refresh_token:
            return False
        access_token, expires_in = self.refresh_authorization(self.GOOGLE_CLIENT_ID, self.GOOGLE_CLIENT_SECRET, str_refresh_token)
        auth_string = self.generate_oauth2_string(str_email, access_token, as_base64=True)
        if not self.test_smpt(str_email, auth_string):
            return False
        else:
            return True
    def send_email(self, addr_from, password, addr_to_many, sub, text,
                   bool_add_in_data_b = True, bool_token = True):





        list_logins = addr_from.split(' ')
        list_passwords = password.split(' ')
        if len(list_logins) != len(list_passwords):
            pass
            self.log.write_log("Не совпадает количество логинов почт и паролей для оптпрвления письма!")
        if len(list_logins) == 0 or len(list_passwords) == 0:
            self.log.write_log("Нет логина либо пароля для почты отправителя")
            return False



        for addr_to in addr_to_many.split(" "):
            bool_was_error = True
            for i, addr_from in enumerate(list_logins):
                if len(list_passwords) <= i:
                    self.log.write_log("Нет пароля для почты: " + addr_from)
                    continue
                else:
                    password = list_passwords[i]
       
                    error = 0
                    try:
                        if bool_token:
                            str_refresh_token = self.get_token(addr_from)
                            if not str_refresh_token:
                                self.log.write_log(f"Не удалось получить refresh token для почты: {addr_from}")
                                continue
                            access_token, expires_in = self.refresh_authorization(self.GOOGLE_CLIENT_ID, self.GOOGLE_CLIENT_SECRET, str_refresh_token)
                            auth_string = self.generate_oauth2_string(addr_from, access_token, as_base64=True)


                        #print(addr_from, password)
                        msg = MIMEMultipart()                               # Создаем сообщение
                        msg['From']    = addr_from                          # Адресат
                        msg['To']      = addr_to                            # Получатель
                        msg['Subject'] = sub                                # Тема сообщения
    
                        body = text.replace("\n", '<br>')
                        msg.attach(MIMEText(body, 'html'))                 # Добавляем в сообщение текст
    
    
                        #server = smtplib.SMTP_SSL('smtp.rambler.ru', 465) 
                        server = smtplib.SMTP('smtp.gmail.com', 587)           # Создаем объект SMTP
                        server.set_debuglevel(True)                         # Включаем режим отладки - если отчет не нужен, строку можно закомментировать
                        server.ehlo(self.GOOGLE_CLIENT_ID)
                        server.starttls()# для рамблера раскомментировать   # Начинаем шифрованный обмен по TLS
                        if bool_token:
                            server.docmd('AUTH', 'XOAUTH2 ' + auth_string)
                                         # Получаем доступ
                        else:
                            server.login(addr_from, password)      
                        server.sendmail(addr_from, addr_to, msg.as_string())
                        #server.send_message(msg)                            # Отправляем сообщение
                        server.quit()                                       # Выходим
                        #self.log.write_log("Письмо с почты {} отправил".format(addr_from))
                    except:
                        self.log.write_log("Не удалось отправить письмо с почты:{} на почту:{}".format(addr_from, addr_to))
                        self.log.write_log(traceback.format_exc())
                        error = 1
                    if error == 0:
                        #self.log.write_log("УДАЛОСЬ отправить письмо с почты:{} на почту:{}".format(addr_from, addr_to))
                        self.log.write_log("Письмо с почты {} отправил".format(addr_from))
                        bool_was_error = False
                        break
            # если произошла ошибка и если нужна добавлять в бд неоптрпавленные письма:
            if bool_was_error and bool_add_in_data_b:
                self.dump_bad_email(addr_to, sub, text)
                self.log.write_log("Не удалось отправить письмо, записываю его в БД")
            # с таким параметром вызывается для отправки одного сообщения, которое не логируется при неудаче
            elif bool_add_in_data_b == False and bool_was_error:
                self.log.write_log("Не удалось отправить письмо, снова")
                return False
        return True
    


    # в файле хранится время в секундах и addr_to, sub, text
    # времени в секундах достаточно, т.к. будем считать разницу между показателями времени
    def dump_bad_email(self, addr_to, sub, text):
        with self.MUTEX_DUMP_EMAIL:
            try:
                # считываем список
                with open("email.bd", 'r') as fr:
                    list_data = json.load(fr)
                # если там не список, затираем все то что считали
                if not isinstance(list_data, list):
                    list_data = []

            except:
                self.log.write_log("Не удалось считать файл с неотправленными письмами")
                list_data = []
            list_data.append([int((datetime.now() - datetime(2020, 1, 1, 1, 1)).total_seconds()), addr_to, sub, text])

            try:
                # считываем список
                with open("email.bd", 'w') as fw:
                    json.dump(list_data, fw)
            except:
                self.log.write_log("Не удалось записать неотпрапвленное письмо в файл")
                return
            self.log.write_log("Неотпрпавленное письмо в файл записал")

    def try_send_from_dump(self, 
                           addr_from, 
                           password, 
                           bool_token = True,
                           int_resend_time = 60*60*4 # задержка перед повтороной отправкой
                           ):
        with self.MUTEX_DUMP_EMAIL:
            try:
                # считываем список
                with open("email.bd", 'r') as fr:
                    list_data = json.load(fr)
                # если там не список, затираем все то что считали
                if not isinstance(list_data, list):
                    self.log.write_log("Файл с неоптравленными письмами повреждем")
                    return

            except:
                self.log.write_log("Файла с неоптравленными письмами нету")
                return
            if len(list_data) == 0:
                self.log.write_log("Неотправленных писем нету")
                return
            

            #int_resend_time = 10
            while (len(list_data) != 0 and
                   int((datetime.now() - datetime(2020, 1, 1, 1, 1)).total_seconds()) - list_data[0][0] > int_resend_time):
                self.log.write_log("Извлекли неотправленное письмо, пытаемся послать")
                list_elem = list_data.pop(0)
                status = self.send_email(addr_from, password, list_elem[1], list_elem[2], list_elem[3],
                   bool_add_in_data_b = False,
                   bool_token = bool_token)
                if status == False:
                    list_data.append([int((datetime.now() - datetime(2020, 1, 1, 1, 1)).total_seconds()),
                                     list_elem[1], list_elem[2], list_elem[3]])
                    self.log.write_log("Неотпрпавленное письмо в файл записал, НЕ СМОГ ПОВТОРНО ЕГО ОТПРАВИТЬ")
                else:
                    self.log.write_log("Неотпрпавленное письмо ОТПРАВИЛ, удаляю его из файла")
                try:
                    # перезаписываем файл
                    with open("email.bd", 'w') as fw:
                        json.dump(list_data, fw)
                except:
                    self.log.write_log("Не удалось записать неотпрапвленное письмо в файл")
                    return


"""
OLD HELP:

Adapted from:
https://github.com/google/gmail-oauth2-tools/blob/master/python/oauth2.py
https://developers.google.com/identity/protocols/OAuth2

1. Generate and authorize an OAuth2 (generate_oauth2_token)
2. Generate a new access tokens using a refresh token(refresh_token)
3. Generate an OAuth2 string to use for login (access_token)
"""









if __name__ == '__main__':
    email = RetsamEmail("data\\log")
    str_login = "ruslan69623@gmail.com"
    bool_stat = email.init_token(str_login)
    #email.send_email(str_login, "123", "ruslan_piter@mail.ru", "SUB", "TEXT", "1")
    #send_email(self, addr_from, password, addr_to_many, sub, text,
                   #bool_add_in_data_b = True):
    email.try_send_from_dump(str_login, "123")
    pass