import os, sys, json, random, platform
from ua_headers import ua

red = '\033[31m'
yellow = '\033[93m'
lgreen = '\033[92m'
clear = '\033[0m'
bold = '\033[01m'
cyan = '\033[96m'
version = "1.0.9"
global log
log = False

class ip:
    def address(*ips:str):
        import requests
        headers = {
		'User-Agent' : ua.linux()
	}
        ipaddr = " ".join([str(m) for m in ips])
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        try:
            myip = requests.get("https://trackip.net/ip", headers=headers).text
        except:
            myip = requests.get("https://api64.ipify.org?format=text", headers=headers).text
        if ipaddr == myip:
            b = red+bold+"["+clear+"-"+red+bold+"]"+clear
            print(b, "error, you can't punch your IP, so there is a command: ip.my()")
            exit(4)
        try:
            ipdata_list = ['?api-key=6818a70bf0dcdbf1dd6bf89e62299740a49725ac65ff8e4056e3b343', '?api-key=7d9bf69a54c63b6f9274c6074b2f50aee46208d10a33533452add840', '?api-key=6453632fcabd2a4c2de4bb45ab35254594fd719e61d58bacde4429f0']
            ipdata = random.choice(ipdata_list)
            paste = "https://api.ipdata.co/"+ipaddr+ipdata
            data1 = requests.get(paste, headers=headers, timeout=10).json()
            data6 = requests.get("http://ip-api.com/json/"+ipaddr+"?fields=status,message,isp,org,as,reverse,mobile,proxy,hosting,query,district", headers=headers, timeout=10).json()
            data7 = requests.get("https://api.ipregistry.co/"+ipaddr+"?key=g54hjdzjnudhhsp4", headers=headers, timeout=10).json()
            a = lgreen+bold+"["+clear+"+"+lgreen+bold+"]"+clear
            r = lgreen+bold+"["+red+bold+"!"+lgreen+bold+"]"+clear
            data9 = data7['location']
            data5 = data9['country']
            data10 = data7['security']
            data11 = data9['language']
            print(a, "┌──────────[Geolocation]")
            print(a, "├ Status             :", data6['status'])
            print(a, "├ Victim             :", data1['ip'])
            print(a, "┼ Is eu              :", data1['is_eu'])
            print(a, "├ Type               :", data7['type'])
            print(a, "├ City               :", data1['city'])
            print(a, "├ Region             :", data1['region'])
            print(a, "├ Region code        :", data1['region_code'])
            print(a, "├ Region type        :", data1['region_type'])
            print(a, "├ Country name       :", data1['country_name'])
            print(a, "├ Country code       :", data1['country_code'])
            print(a, "├ Latitude           :", data1['latitude'])
            print(a, "├ Longitude          :", data1['longitude'])
            print(a, "├ Zip code           :", data1['postal'])
            print(a, "├ Calling code       :", data1['calling_code'])
            print(a, "├ Country area       :", data5['area'])
            print(a, "├ Country population :", data5['population'])
            print(a, "├ Country capital    :", data5['capital'])
            print(a, "├ Country tld        :", data5['tld'])
            print(a, "└ Language name      :", data11['name'])
            data2 = data1['asn']
            data8 = data7['connection']
            data3 = data1['time_zone']
            print(" ")
            print(a, "┌──────────[Router/Time zone]")
            print(a, "├ Asn name           :", data8['asn'])
            print(a, "├ Org name           :", data2['name'])
            print(a, "┼ Reverse            :", data6['reverse'])
            print(a, "├ District           :", data6['district'])
            print(a, "├ Hostname           :", data7['hostname'])
            print(a, "├ Domain             :", data8['domain'])
            print(a, "├ Route              :", data2['route'])
            print(a, "├ Wifi Type          :", data2['type'])
            print(a, "├ Time Zone          :", data3['name'])
            print(a, "├ Abbr               :", data3['abbr'])
            print(a, "├ Offset             :", data3['offset'])
            print(a, "└ Is dst             :", data3['is_dst'])
            print(" ")
            data4 = data1['threat']
            print(a, "┌──────────[Security]")
            print(a, "├ Using tor          :", data10['is_tor'])
            print(a, "├ Using vpn          :", data10['is_vpn'])
            print(a, "┼ Using proxy        :", data10['is_proxy'])
            print(a, "├ Is relay           :", data10['is_relay'])
            print(a, "├ Is hosting         :", data6['hosting'])
            print(a, "├ Is datacenter      :", data4['is_datacenter'])
            print(a, "├ Is anonymous       :", data10['is_anonymous'])
            print(a, "├ Cloud provider     :", data10['is_cloud_provider'])
            print(a, "├ Known attacker     :", data4['is_known_attacker'])
            print(a, "├ Known abuser       :", data4['is_known_abuser'])
            print(a, "├ Is threat          :", data4['is_threat'])
            print(a, "└ Is bogon           :", data4['is_bogon'])
        except KeyboardInterrupt:
            print('Quiting Utility! Bye Bye, Have a nice day!'+lgreen)
            sys.exit(0)
        except requests.exceptions.ConnectionError as e:
            print (red+"[-]"+" Please check your internet connection!"+clear)
            print (red+"[-]"+" Error code: 106 DNS server refused to connect!"+clear)
        except:
            b = red+bold+"["+clear+"-"+red+bold+"]"+clear
            print(b, "[Error]: Rate limited")
    def my():
        import requests
        headers = {
                'User-Agent' : ua.linux()
        }
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        a = lgreen+bold+"["+clear+"+"+lgreen+bold+"]"+clear
        try:
            get = requests.get("https://ipapi.co//json/", headers=headers).json()
            print(a, "┌──────────[My IP Address]")
            print(a, "├ Ip address : ", get['ip'])
            print(a, "├ Version    : ", get['version'])
            print(a, "├ Country    : ", get['country_name'])
            print(a, "├ Capital    : ", get['country_capital'])
            print(a, "├ Latitude   : ", get['latitude'])
            print(a, "├ Longitude  : ", get['longitude'])
            print(a, "├ Timezone   : ", get['timezone'])
            print(a, "├ Postal     : ", get['postal'])
            print(a, "├ Area       : ", get['country_area'])
            print(a, "├ City       : ", get['city'])
            print(a, "├ Asn name   : ", get['asn'])
            print(a, "└ Org name   : ", get['org'])
        except:
            get = requests.get("https://api64.ipify.org?format=text", headers=headers).text
            print(a, "┌──────────[My IP Address]")
            print(a, "└ Ip address : "+get)
        print(" ")
        print(a, "┌──────────[Sys Info]")
        print(a, "├ System     : ", platform.system())
        print(a, "├ Release    : ", platform.release())
        print(a, "├ Processor  : ", platform.processor())
        print(a, "├ Version    : ", platform.version())
        print(a, "└ Machine    : ", platform.machine())
    def domain(*link:str):
        import requests
        headers = {
                'User-Agent' : ua.linux()
        }
        ur = " ".join([str(m) for m in link])
        url = "http://" + ur
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        a = lgreen+bold+"["+clear+"+"+lgreen+bold+"]"+clear
        # http(s)
        r01 = url.replace("https://", "http://")
        url = r01.replace("http://http://", "http://")
        res=requests.get(url, stream=True, headers=headers)
        ip=res.raw._original_response.fp.raw._sock.getpeername()[0]
        res2=url + " : " + str(ip)
        print(a, "┌──────────[Domain Ip]")
        print(a, "└ "+url[7:] + " : " + str(ip))
    def proxy():
        from torpy import TorClient
        from torpy.http import requests as torreq
        from torpy.http.adapter import TorHttpAdapter
        tf = True
        with TorClient() as tor:
            with tor.get_guard() as guard:
                adapter = TorHttpAdapter(guard, 5)
                with torreq.Session() as sessp:
                    sessp.headers.update({'User-Agent': 'Mozilla/5.0'})
                    sessp.mount('http://', adapter)
                    sessp.mount('https://', adapter)
                    try:
                        while tf:
                            get = sessp.get("https://gimmeproxy.com/api/getProxy?anonymityLevel=1&supportsHttps=true&protocol=http&maxCheckPeriod=3600", timeout=15).json()
                            if get["websites"]["google"]:
                                print("Proxy ip   : "+get["ip"])
                                print("Proxy port : "+get["port"])
                                print("Google     : true")
                                print("Country    : "+get["country"])
                                print("Protocol   : "+get["protocol"])
                                print("Https      : true")
                                print("Http       : true")
                                tf = False
                    except:
                            tf = False
                            ft = True
                            import requests as untorreq
                            while ft:
                                get = untorreq.get("https://gimmeproxy.com/api/getProxy?anonymityLevel=1&supportsHttps=true&protocol=http&maxCheckPeriod=3600").json()
                                if get["websites"]["google"]:
                                    print("Proxy ip   : "+get["ip"])
                                    print("Proxy port : "+get["port"])
                                    print("Google     : true")
                                    print("Country    : "+get["country"])
                                    print("Protocol   : "+get["protocol"])
                                    print("Https      : true")
                                    print("Http       : true")
                                    ft = False
class inquiry:
    def get(*args, **kwargs):
        from torpy import TorClient
        from torpy.http import requests as torrequ
        from torpy.http.adapter import TorHttpAdapter
        if log:
            print("[10%] Importing tor client")
            print("[25%] Starting the tor client")
        with TorClient() as tor:
            if log:
                print("[35%] Getting the tor guard")
            with tor.get_guard() as guard:
                if log:
                    print("[45%] Tor Http Adapter, guard 3")
                adapter = TorHttpAdapter(guard, 3)
                with torrequ.Session() as sess:
                    if log:
                        print("[55%] Getting requests session")
                        print("[75%] Getting fake IP address")
                    sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                    sess.mount('http://', adapter)
                    sess.mount('https://', adapter)
                    #url = " ".join([str(m) for m in link])
                    if log:
                        print("[90%] Requests get URL")
                    try:
                        get = sess.get(*args, **kwargs, timeout=15)
                        if log:
                            print("[100%] Success")
                        return get
                    except:
                        return 'Website refused to connect '
    def post(*args, **kwargs):
        from torpy import TorClient
        from torpy.http import requests as torrequ
        from torpy.http.adapter import TorHttpAdapter
        if log:
            print("[10%] Importing tor client")
            print("[25%] Starting the tor client")
        with TorClient() as tor:
            if log:
                print("[35%] Getting the tor guard")
            with tor.get_guard() as guard:
                if log:
                    print("[45%] Tor Http Adapter, guard 3")
                adapter = TorHttpAdapter(guard, 3)
                with torrequ.Session() as sess:
                    if log:
                        print("[55%] Getting requests session")
                        print("[75%] Getting fake IP address")
                    sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                    sess.mount('http://', adapter)
                    sess.mount('https://', adapter)
                    #url = " ".join([str(m) for m in link])
                    if log:
                        print("[90%] Requests post URL")
                    try:
                        post = sess.post(*args, **kwargs, timeout=15)
                        if log:
                            print("[100%] Success")
                        return post
                    except:
                        return 'Website refused to connect '
    def put(*args, **kwargs):
        from torpy import TorClient
        from torpy.http import requests as torrequ
        from torpy.http.adapter import TorHttpAdapter
        if log:
            print("[10%] Importing tor client")
            print("[25%] Starting the tor client")
        with TorClient() as tor:
            if log:
                print("[35%] Getting the tor guard")
            with tor.get_guard() as guard:
                if log:
                    print("[45%] Tor Http Adapter, guard 3")
                adapter = TorHttpAdapter(guard, 3)
                with torrequ.Session() as sess:
                    if log:
                        print("[55%] Getting requests session")
                        print("[75%] Getting fake IP address")
                    sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                    sess.mount('http://', adapter)
                    sess.mount('https://', adapter)
                    #url = " ".join([str(m) for m in link])
                    if log:
                        print("[90%] Requests put URL")
                    try:
                        put = sess.put(*args, **kwargs, timeout=15)
                        if log:
                            print("[100%] Success")
                        return put
                    except:
                        return 'Website refused to connect '
    def delete(*args, **kwargs):
        from torpy import TorClient
        from torpy.http import requests as torrequ
        from torpy.http.adapter import TorHttpAdapter
        if log:
            print("[10%] Importing tor client")
            print("[25%] Starting the tor client")
        with TorClient() as tor:
            if log:
                print("[35%] Getting the tor guard")
            with tor.get_guard() as guard:
                if log:
                    print("[45%] Tor Http Adapter, guard 3")
                adapter = TorHttpAdapter(guard, 3)
                with torrequ.Session() as sess:
                    if log:
                        print("[55%] Getting requests session")
                        print("[75%] Getting requests session")
                    sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                    sess.mount('http://', adapter)
                    sess.mount('https://', adapter)
                    #url = " ".join([str(m) for m in link])
                    if log:
                        print("[90%] Requests delete URL")
                    try:
                        delete = sess.delete(*args, **kwargs, timeout=15)
                        if log:
                            print("[100%] Success")
                        return delete
                    except:
                        return 'Website refused to connect '
    def head(*args, **kwargs):
        from torpy import TorClient
        from torpy.http import requests as torrequ
        from torpy.http.adapter import TorHttpAdapter
        if log:
            print("[10%] Importing tor client")
            print("[25%] Starting the tor client")
        with TorClient() as tor:
            if log:
                print("[35%] Getting the tor guard")
            with tor.get_guard() as guard:
                if log:
                    print("[45%] Tor Http Adapter, guard 3")
                adapter = TorHttpAdapter(guard, 3)
                with torrequ.Session() as sess:
                    if log:
                        print("[55%] Getting requests session")
                        print("[75%] Getting fake IP address")
                    sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                    sess.mount('http://', adapter)
                    sess.mount('https://', adapter)
                    #url = " ".join([str(m) for m in link])
                    if log:
                        print("[90%] Requests head URL")
                    try:
                        head = sess.head(*args, **kwargs, timeout=15)
                        if log:
                            print("[100%] Success")
                        return head
                    except:
                        return 'Website refused to connect '
    def debug():
       global log
       if log:
           log = False
       else:
           log = True
