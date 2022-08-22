
from flask import Flask, request
from pywebcopy import save_webpage
import requests
import requests.packages.urllib3, requests, json, time, datetime, re, os, csv
from bs4 import BeautifulSoup as bs
from os import listdir, system
from os.path import isfile, join
import re
import hashlib
from apscheduler.schedulers.background import BlockingScheduler
import threading
import datetime

def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")
        
botEmail = "bob8gook_kisa@webex.bot"
accessToken = "YzE4Y2ZhYjAtMDk5Yy00NTZlLWIwYjAtODYwNzQwNDExOWRmMDFjZmI1ODYtM2Rm_PF84_22cb7792-d880-4ec5-b6a6-649d9411bb5e"
headers = {"Authorization": "Bearer %s" % accessToken, "Content-Type": "application/json", 'Accept' : 'application/json'}
roomId_kisa_private = 'Y2lzY29zcGFyazovL3VzL1JPT00vNDkwNzIwMjAtMTBhNy0xMWVkLTk4ZDktNzU3YWU5MmY2MDFh' #kisa 개인방
roomId_soc = 'Y2lzY29zcGFyazovL3VzL1JPT00vZmIwY2M1YTAtMDYzZS0xMWVjLWExNzgtZDEzYjhjMjEwNzVk'
roomId_availability = 'Y2lzY29zcGFyazovL3VzL1JPT00vZTVmMmJiYTAtMTE2Ni0xMWVkLThmMjctZmQ4YjY5ODZmODc3'
roomId_use = roomId_kisa_private

now = datetime.datetime.now()
now = now + datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=9, weeks=0)

try:
    with open('num_last.txt', 'r') as f:
        num_last = int(f.read())
except:
        num_last = 9999
print('num_last : ' + str(num_last))
now = datetime.datetime.now()
now = now + datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=9, weeks=0)
url = 'https://krcert.or.kr'
fPath_working = os.getcwd()
fPath_kisa =fPath_working + '/kisa'
createDirectory(fPath_kisa)
print('[*] path : ' + os.getcwd() + '/kisa')
enc = hashlib.md5()

def DownloadFullPage(url, fPath):  
    kwargs = {'bypass_robots': True, 'project_name': 'recognisable-name'}
    save_webpage(url, fPath, **kwargs)

def SendMessage(payload, msg):
    payload["text"] = str(msg)
    response = requests.request("POST", "https://webexapis.com/v1/messages", data=json.dumps(payload),
                                    headers=headers)
    response = json.loads(response.text)
    return {'messageId' : response['id']}

def ModifyMessage(payload, msg, messageId):
    payload["text"] = str(msg)
    requests.request("PUT", "https://webexapis.com/v1/messages/{}".format(messageId),
                                                data=json.dumps(payload), headers=headers)
    
def SendFile(fullPath, roomId, text=""):
    print('send the file')
    with open(fullPath, 'rb') as f:
        cmd = f"""curl --request POST\
         --header "Authorization: Bearer {accessToken}"\
         --form "files=@{fullPath};type=image/png"\
         --form "roomId={roomId}"\
         --form "text={text}"\
         https://webexapis.com/v1/messages"""
        os.system(cmd)

def CheckNotice():
    print("???")
    global num_last, roomId_kisa_private, roomId_use, fPath_kisa, fPath_working
    list_files = []
    for page in range(5,0,-1):
        #print("url : " + f"{url}/data/secNoticeList.do?page={page}")
        response = requests.get(f"{url}/data/secNoticeList.do?page={page}")
        soup = bs(response.text, "html.parser")
        elements = soup.select('#contentDiv > table > tbody > tr')
        for element in elements[::-1]:
            tds = element.select("td")
            num = tds[0].get_text().strip()
            title = tds[1].get_text().strip()
            link = url + tds[1].find('a')['href']
            fullDate = tds[4].get_text().strip()
            try:
                num = int(num)
            except ValueError:
                print(f'[*] 보안공지 다운로드 실패 - 아마 공지사항.. : {fullDate}_{title}_{num}')
                continue
                #if num == '1780':
            try:
                if num > int(num_last):
                    date = ''.join(fullDate.split('.')[1:])
                    title = '_'.join(title.split(' '))
                    htmlPath = f'{fPath_kisa}/{date}_{title}_{num}'
                    DownloadFullPage(link, htmlPath)
                    sourcePath = htmlPath + '/recognisable-name/krcert.or.kr/data'
                    htmlName = listdir(sourcePath)[0]
                    source = ''
                    with open(f'{sourcePath}/{htmlName}', 'r') as f:
                        source = f.read()
                    soup = bs(source, "html.parser")
                    imagePath = htmlPath + '/recognisable-name/krcert.or.kr/img'
                    for idx, img in enumerate(soup.findAll('img'), start=1):
                        src = img['src']
                        ext = re.search('\.(png|gif|tif|jpg|bmp)', src).group(1)
                        enc.update(src.encode())
                        encText = enc.hexdigest()
                        new_src = f'{encText}.{ext}'
                        source = source.replace(src, '../img/' + new_src )
                        system(f'wget {url}{src} -O {imagePath}/{new_src}')

                    with open(f'{sourcePath}/{htmlName}', 'w') as f:
                        f.write(source)
                    os.chdir(fPath_kisa + f'/{date}_{title}_{num}/recognisable-name/')
                    time.sleep(2)
                    system(f'zip -r {date}_{title}_{num}.zip *')
                    system(f'mv {date}_{title}_{num}.zip {fPath_kisa}')
                    list_files.append([f'{fPath_kisa}/{date}_{title}_{num}.zip', f'[*] 새로운 보안공지 확인\n[{num}] {title} ({fullDate})'])
                    time.sleep(2)
                    os.chdir(fPath_kisa)
                    system(f'rm -rf {date}_{title}_{num}')
                    num_last = int(num)
            except Exception as e:
                payload = {"roomId": roomId_use}
                #SendMessage(payload, f'[*] 보안공지 다운로드 실패 - 수동 확인 필요 : {fullDate}_{title}_{num}')
                num_last = int(num)
                print('### ' + str(e))
                os.chdir(fPath_working)
                with open('error.log', 'a') as f:
                    now = datetime.datetime.now()
                    now = now + datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=9, weeks=0)
                    f.write(f'[{now}] ' + str(e) + f'({num_last})\n')
                    print('@@@ num : ' + str(num_last))
    return list_files

                
app = Flask(__name__)
@app.route('/', methods=['POST'])
def receive():
    data = request.json.get('data')
    email, messageId = data['personEmail'], data['id']
    print('message : ' + str(data))
    if email == botEmail:
        return ("")
    response = json.loads(requests.request("GET", "https://api.ciscospark.com/v1/messages/{}".format(messageId), headers=headers).text)
    #print(str(response))
    #msgs = response['text'].strip().split('\n')
    SendMessage(payload, "test")
    return {'status' : 'success', 'num_last': num_last}

@app.route('/', methods=['GET'])
def BotComu():
    global roomId_use, num_last
    temp = num_last
    print('num_last : ' + str(num_last) )
    GS25()
    try:
        num = request.args.to_dict()['num']
        print('@num : ' + str(num))
        num = int(num)
        num_last = num
    except:
        print('@num_last : ' + str(num_last))
    return {'status' : 'success', 'num_last': num_last}

def GS25():
    global roomId_kisa_private, roomId_soc, num_last, roomId_use, fPath_working
    print('Im GS25  - num last : ' + str(num_last))
    for fPath, title in CheckNotice():
    	#SendFile(fPath, roomId_use, title)
    	SendFile(fPath, roomId_use, title)
    	system(f"rm {fPath}")
    os.chdir(fPath_working)
    with open('num_last.txt', 'w') as f:
        print('what is wrong? : '+ str(num_last))
        f.write(str(num_last))
    print('Bye Bye - num last : ' + str(num_last))
    
def CallerCheck():
    sched = BlockingScheduler(timezone='Asia/Seoul')
    #sched.add_job(GS25,'interval', minutes=30, id='kisa')
    sched.add_job(GS25,'interval', minutes=1, id='kisa')
    sched.start()
def CallerCheck2():
    sched = BlockingScheduler(timezone='Asia/Seoul')
    #sched.add_job(CheckAvailability,'interval', minutes=60*24, id='availability')
    sched.add_job(CheckAvailability,'interval', minutes=1, id='availability')
    sched.start()
    
def CheckAvailability():
    global roomId_availability, now, roomId_use
    payload = {"roomId": roomId_use}
    now = datetime.datetime.now()
    now = now + datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=9, weeks=0)
    SendMessage(payload, "[{}] 상태 체크".format(now.strftime('%Y-%m-%d %H:%M:%S')))
    
def run():
    GS25()
    payload = {"roomId": roomId_use}
    SendMessage(payload, "[{}] 상태 체크".format(now.strftime('%Y-%m-%d %H:%M:%S')))
    t = threading.Thread(target=CallerCheck)
    t.start()
    t2 = threading.Thread(target=CallerCheck2)
    t2.start()
    app.run(host="0.0.0.0", port=8777)