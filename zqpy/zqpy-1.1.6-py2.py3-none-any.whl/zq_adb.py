import time, os, subprocess, re
import zq_log

def adb_execute(adbCommand, device = None, shell = True, stdout = subprocess.PIPE):
    ''' adb 方法执行 '''
    if device:
        device = device.replace('_a_','')
        device = device.replace('_b_','-')
        device = device.replace('_c_','.')
        device = device.replace('_d_',':')
        adbCommand = adbCommand.replace('adb ', 'adb -s %s '%(device))
    zq_log.log_debug(adbCommand)
    popen = subprocess.Popen(adbCommand,shell=shell,stdout=stdout)
    popen.wait()
    if stdout == subprocess.PIPE:
        readLine = popen.stdout.readlines()
        return readLine
    else:
        return True

def adb_get_copy_value(device = None):
    ''' 获取复制的值 '''
    adb_execute('adb shell am startservice ca.zgrs.clipper/.ClipboardService', device=device)
    readLine = adb_execute('adb shell am broadcast -a clipper.get', device=device)
    if len(readLine) < 2:
        return ''
    resultData = str(readLine[1], 'utf8')
    return resultData

def adb_kill_app(packageName, device = None):
    ''' 杀掉某APP '''
    return adb_execute('adb shell "am force-stop %s"'%(packageName), device=device)     #退出后台但是不会清理数据
    # zq_log.log_debug('adb shell pm clear %s'%(packageName.split('/')[0]))
    # return adb_execute('adb shell pm clear %s'%(packageName.split('/')[0]), device=device)

def adb_show_app(appPackage, appLayer, device = None):
    ''' 显示某个应用的 某层 '''
    return adb_execute('adb shell am start -n %s/%s'%(appPackage,appLayer), device=device)

def adb_get_app_curr(device = None):
    ''' 查看当前所在的页面 属于的package 和 活动层，方便打开用 '''
    readLine = adb_execute('adb shell dumpsys window windows | findstr "Current"', device=device,shell=True,stdout=subprocess.PIPE)
    return readLine

def adb_click(x, y, device = None):
    ''' ADB点击 '''
    return adb_execute('adb shell input tap %s %s'%(x,y), device=device)

def adb_drag_and_drop(x1, y1, x2, y2, device = None):
    ''' ADB按住滑动 '''
    return adb_execute('adb shell input draganddrop %s %s %s %s'%(x1, y1, x2, y2), device=device)

def adb_swipe(x1, y1, x2, y2, device = None):
    ''' ADB滑动 '''
    return adb_execute('adb shell input swipe %s %s %s %s'%(x1, y1, x2, y2), device=device)

def adb_input_key_event(content = '', device = None):
    ''' 输入键 '''
    return adb_execute('adb shell input keyevent "%s"'%(content), device=device)

def adb_input_text(content = '', device = None):
    ''' 输入内容，不支持中文  模拟器以 /mnt开头 + /sdcard手机最高目录名字 '''
    return adb_execute('adb shell input text "%s"'%(content), device=device)
    # return adb_execute('adb shell am broadcast -a ADB_INPUT_TEXT --es msg "%s"'%(content))

def adb_input_text_by_app(content = '', device = None):
    ''' 输入内容，支持中文  必须满足 1.安装了ADBKeyboard.apk  2.adb 1.0.32以上 '''
    return adb_execute('adb shell am broadcast -a ADB_INPUT_TEXT --es msg "%s"'%(content), device=device)

def adb_push_file(pcPath, androidPath, device = None):
    ''' 输电脑文件复制到手机上，手机测不支持中文 '''
    return adb_execute('adb push %s %s'%(pcPath, androidPath), device=device,stdout = subprocess.DEVNULL) # 小文件可以用subprocess.PIPE，大文件用它要崩，一直卡

def adb_pull_file(androidPath, pcPath, device = None):
    ''' 手机文件复制到电脑上，手机测不支持中文 '''
    return adb_execute('adb pull %s %s'%(androidPath, pcPath), device=device)

def adb_screenshot(targetPath='', device = None):
    '''
    手机截图
    :param targetPath: 目标路径
    :return:
    '''
    format_time = int(time.time())
    adb_execute('adb shell screencap -p /sdcard/%s.png'%format_time, device=device)
    time.sleep(1)
    outPath = targetPath
    if targetPath == '':
        outPath = os.path.dirname(__file__)
    adb_pull_file('/sdcard/%s.png' % (format_time,), outPath)
    adb_remove_file('/sdcard/%s.png' % (format_time,))
    time.sleep(1)
    return outPath if ('.jpg' in outPath or '.png' in outPath) else ('%s%s.png' % (outPath, format_time,))

def adb_remove_file(path):
    '''
    从手机端删除文件
    :return:
    '''
    adb_execute('adb shell rm %s'%path)

def adb_remove_dir(path):
    '''
    从手机端删除目录
    :return:
    '''
    adb_execute('adb shell rm -r %s'%path)

def adb_get_devices(device = None):
    ''' 获取设备信息列表 '''
    devices = []
    readLine = adb_execute('adb devices', device=device) 
    for item in readLine:
        item = item.decode('utf-8')
        items = item.split('\t')
        if len(items) == 2:
            newItems = []
            for itemTemp in items:
                itemTemp = itemTemp.strip().replace('-','_b_')
                itemTemp = itemTemp.replace('.','_c_')
                itemTemp = itemTemp.replace(':','_d_')
                if itemTemp.split('_')[0].isdigit():
                    itemTemp = '_a_' + itemTemp
                newItems.append(itemTemp)
            devices.append(newItems)
    return devices

def adb_open_uri(uri, device=None):
    ''' 打开Uri '''
    return adb_execute('adb shell am start -a android.intent.action.VIEW -d '%uri, device=device)

def adb_create_mkdir(path, device=None):
    '''
    创建目录
    :param path: 路径
    :return:
    '''
    return adb_execute('adb shell mkdir -p %s'%path)


def adb_dump_apk(path):
    '''
    dump apk文件
    :param path: apk路径
    :return:
    '''
    # 检查build-tools是否添加到环境变量中
    # 需要用到里面的aapt命令
    l = os.environ['PATH'].split(';')
    build_tools = False
    for i in l:
        if 'build-tools' in i:
            build_tools = True
    if not build_tools:
        raise EnvironmentError('ANDROID_ADB BUILD-TOOLS COMMAND NOT FOUND.\nPlease set the environment variable.')
    return os.popen('aapt dump badging %s' % (path,))

def adb_dump_xml(path, filename):
    '''
    dump apk xml文件
    :return:
    '''
    return os.popen('aapt dump xmlstrings %s %s' % (path, filename))

def adb_uiautomator_dump():
    '''
    获取屏幕uiautomator xml文件
    :return:
    '''
    return adb_execute('adb shell uiautomator dump').read().split()[-1]

def adb_clear_app_data(package):
    '''
    清理应用数据
    :return:
    '''
    return adb_execute('adb shell pm clear %s' % (package,))
 
def adb_install(path, device = None):
    '''
    安装apk文件
    :return:
    '''
    # adb install 安装错误常见列表
    errors = {'INSTALL_FAILED_ALREADY_EXISTS': '程序已经存在',
                'INSTALL_DEVICES_NOT_FOUND': '找不到设备',
                'INSTALL_FAILED_DEVICE_OFFLINE': '设备离线',
                'INSTALL_FAILED_INVALID_APK': '无效的APK',
                'INSTALL_FAILED_INVALID_URI': '无效的链接',
                'INSTALL_FAILED_INSUFFICIENT_STORAGE': '没有足够的存储空间',
                'INSTALL_FAILED_DUPLICATE_PACKAGE': '已存在同名程序',
                'INSTALL_FAILED_NO_SHARED_USER': '要求的共享用户不存在',
                'INSTALL_FAILED_UPDATE_INCOMPATIBLE': '版本不能共存',
                'INSTALL_FAILED_SHARED_USER_INCOMPATIBLE': '需求的共享用户签名错误',
                'INSTALL_FAILED_MISSING_SHARED_LIBRARY': '需求的共享库已丢失',
                'INSTALL_FAILED_REPLACE_COULDNT_DELETE': '需求的共享库无效',
                'INSTALL_FAILED_DEXOPT': 'dex优化验证失败',
                'INSTALL_FAILED_DEVICE_NOSPACE': '手机存储空间不足导致apk拷贝失败',
                'INSTALL_FAILED_DEVICE_COPY_FAILED': '文件拷贝失败',
                'INSTALL_FAILED_OLDER_SDK': '系统版本过旧',
                'INSTALL_FAILED_CONFLICTING_PROVIDER': '存在同名的内容提供者',
                'INSTALL_FAILED_NEWER_SDK': '系统版本过新',
                'INSTALL_FAILED_TEST_ONLY': '调用者不被允许测试的测试程序',
                'INSTALL_FAILED_CPU_ABI_INCOMPATIBLE': '包含的本机代码不兼容',
                'CPU_ABIINSTALL_FAILED_MISSING_FEATURE': '使用了一个无效的特性',
                'INSTALL_FAILED_CONTAINER_ERROR': 'SD卡访问失败',
                'INSTALL_FAILED_INVALID_INSTALL_LOCATION': '无效的安装路径',
                'INSTALL_FAILED_MEDIA_UNAVAILABLE': 'SD卡不存在',
                'INSTALL_FAILED_INTERNAL_ERROR': '系统问题导致安装失败',
                'INSTALL_PARSE_FAILED_NO_CERTIFICATES': '文件未通过认证 >> 设置开启未知来源',
                'INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES': '文件认证不一致 >> 先卸载原来的再安装',
                'INSTALL_FAILED_INVALID_ZIP_FILE': '非法的zip文件 >> 先卸载原来的再安装',
                'INSTALL_CANCELED_BY_USER': '需要用户确认才可进行安装',
                'INSTALL_FAILED_VERIFICATION_FAILURE': '验证失败 >> 尝试重启手机',
                'DEFAULT': '未知错误'
                }
    zq_log.log_debug('Installing...')
    l = adb_execute('adb install -r %s' % (path,), device).read()
    if 'Success' in l:
        zq_log.log_debug('adb_install Success')
    if 'Failure' in l:
        reg = re.compile('\\[(.+?)\\]')
        key = re.findall(reg, l)[0]
        try:
            zq_log.log_debug('install Failure >> %s' % errors[key])
        except KeyError:
            zq_log.log_debug('install Failure >> %s' % key)
    return l

def adb_uninstall(package, device):
    '''
    卸载apk
    :param package: 包名
    :return:
    '''
    zq_log.log_debug('Uninstalling...')
    l = adb_execute('adb uninstall %s' % (package,), device).read()
    zq_log.log_debug(l)
 
def adb_get_cache_logcat():
    '''
    导出缓存日志
    :return:
    '''
    return adb_execute('adb logcat -v time -d')
 
def adb_get_crash_logcat():
    '''
    导出崩溃日志
    :return:
    '''
    return adb_execute('adb logcat -v time -d | %s AndroidRuntime' % ('findstr',))

def adb_clear_cache_logcat():
    '''
    清理缓存区日志
    :return:
    '''
    return adb_execute('adb logcat -c')

def adb_get_device_time():
    '''
    获取设备时间
    :return:
    '''
    return adb_execute('adb shell date').read().strip()
 
def adb_ls(command):
    '''
    shell ls命令
    :return:
    '''
    return adb_execute('adb shell ls %s' % (command,)).readlines()
 
def adb_file_exists(target):
    '''
    判断文件在目标路径是否存在
    :return:
    '''
    l = adb_ls(target)
    for i in l:
        if i.strip() == target:
            return True
    return False
 
def adb_is_install(target_app):
    '''
    判断目标app在设备上是否已安装
    :param target_app: 目标app包名
    :return: bool
    '''
    return target_app in adb_execute('adb shell pm list packages %s' % (target_app,)).read()
 
def adb_get_device_model():
    '''
    获取设备型号
    :return:
    '''
    return adb_execute('adb shell getprop ro.product.model').read().strip()
 
def adb_get_device_id():
    '''
    获取设备id
    :return:
    '''
    return adb_execute('adb get-serialno').read().strip()
 
def adb_get_device_android_version():
    '''
    获取设备Android版本
    :return:
    '''
    return adb_execute('adb shell getprop ro.build.version.release').read().strip()

def adb_get_device_sdk_version():
    '''
    获取设备SDK版本
    :return:
    '''
    return adb_execute('adb shell getprop ro.build.version.sdk').read().strip()

def adb_get_device_mac_address():
    '''
    获取设备MAC地址
    :return:
    '''
    return adb_execute('adb shell cat /sys/class/net/wlan0/address').read().strip()

def adb_get_device_ip_address():
    '''
    获取设备IP地址
    pass: 适用WIFI 蜂窝数据
    :return:
    '''
    if not adb_get_wifi_state() and not adb_get_data_state():
        return
    l = adb_execute('adb shell ip addr | %s global' % 'findstr').read()
    reg = re.compile('\d+\.\d+\.\d+\.\d+')
    return re.findall(reg, l)[0]

def adb_root():
    '''
    获取root状态
    :return:
    '''
    return 'not found' not in adb_execute('adb shell su -c ls -l /data/').read().strip()

def adb_get_device_imei():
    '''
    获取设备IMEI
    :return:
    '''
    sdk = adb_get_device_sdk_version()
    # Android 5.0以下方法
    if int(sdk) < 21:
        l = adb_execute('adb shell dumpsys iphonesubinfo').read()
        reg = re.compile('[0-9]{15}')
        return re.findall(reg, l)[0]
    elif adb_root():
        l = adb_execute('adb shell service call iphonesubinfo 1').read()
        zq_log.log_debug(l)
        zq_log.log_debug(re.findall(re.compile("'.+?'"), l))
        imei = ''
        for i in re.findall(re.compile("'.+?'"), l):
            imei += i.replace('.', '').replace("'", '').replace(' ', '')
        return imei
    else:
        zq_log.log_debug('The device not root.')
        return ''

def adb_check_sim_card():
    '''
    检查设备SIM卡
    :return:
    '''
    return len(adb_execute('adb shell getprop | %s gsm.operator.alpha]' % 'findstr').read().strip().split()[-1]) > 2

def adb_get_device_operators():
    '''
    获取运营商
    :return:
    '''
    return adb_execute('adb shell getprop | %s gsm.operator.alpha]' % 'findstr').read().strip().split()[-1]

def adb_get_device_state():
    '''
    获取设备状态
    :return:
    '''
    return adb_execute('adb get-state').read().strip()

def adb_get_display_state():
    '''
    获取屏幕状态
    :return: 亮屏/灭屏
    '''
    l = adb_execute('adb shell dumpsys power').readlines()
    for i in l:
        if 'mScreenOn=' in i:
            return i.split()[-1] == 'mScreenOn=true'
        if 'Display Power' in i:
            return 'ON' in i.split('=')[-1].upper()

def adb_get_screen_normal_size():
    '''
    获取设备屏幕分辨率 >> 标配
    :return:
    '''
    return adb_execute('adb shell wm size').read().strip().split()[-1].split('x')

def adb_get_screen_reality_size():
    '''
    获取设备屏幕分辨率 >> 实际分辨率
    :return:
    '''
    x = 0
    y = 0
    l = adb_execute('adb shell getevent -p | %s -e "0"' % 'findstr').readlines()
    for n in l:
        if len(n.split()) > 0:
            if n.split()[0] == '0035':
                x = int(n.split()[7].split(',')[0])
            elif n.split()[0] == '0036':
                y = int(n.split()[7].split(',')[0])
    return x, y

def adb_get_device_interior_sdcard():
    '''
    获取内部SD卡空间
    :return: (path,total,used,free,block)
    '''
    return adb_execute('adb shell df | %s \/mnt\/shell\/emulated' % 'findstr').read().strip().split()

def adb_get_device_external_sdcard():
    '''
    获取外部SD卡空间
    :return: (path,total,used,free,block)
    '''
    return adb_execute('adb shell df | %s \/storage' % 'findstr').read().strip().split()

def __fill_rom(path, stream, count):
    '''
    填充数据
    :param path: 填充地址
    :param stream: 填充流大小
    :param count: 填充次数
    :return:
    '''
    adb_execute('adb shell dd if=/dev/zero of=%s bs=%s count=%s' % (path, stream, count)).read().strip()

def adb_fill_interior_sdcard(filename, size):
    '''
    填充内置SD卡
    :param filename: 文件名
    :param size: 填充大小，单位byte
    :return:
    '''
    if size > 10485760:  # 10m
        __fill_rom('sdcard/%s' % filename, 10485760, size / 10485760)
    else:
        __fill_rom('sdcard/%s' % filename, size, 1)

def adb_fill_external_sdcard(filename, size):
    '''
    填充外置SD卡
    :param filename: 文件名
    :param size: 填充大小，单位byte
    :return:
    '''
    path = adb_get_device_external_sdcard()[0]
    if size > 10485760:  # 10m
        __fill_rom('%s/%s' % (path, filename), 10485760, size / 10485760)
    else:
        __fill_rom('%s/%s' % (path, filename), size, 1)

def adb_kill_process(pid):
    '''
    杀死进程
    pass: 一般需要权限不推荐使用
    :return:
    '''
    return adb_execute('adb shell kill %s' % pid).read().strip()

def adb_quit_app(package):
    '''
    退出应用
    :return:
    '''
    return adb_execute('adb shell am force-stop %s' % package).read().strip()

def adb_reboot():
    '''
    重启设备
    :return:
    '''
    adb_execute('adb reboot')

def adb_recovery():
    '''
    重启设备并进入recovery模式
    :return:
    '''
    adb_execute('adb reboot recovery')

def adb_fastboot():
    '''
    重启设备并进入fastboot模式
    :return:
    '''
    adb_execute('adb reboot bootloader')

def adb_wifi(power):
    '''
    开启/关闭wifi
    pass: 需要root权限
    :return:
    '''
    if not adb_root():
        zq_log.log_debug('The device not root.')
        return
    if power:
        adb_execute('adb shell su -c svc wifi enable').read().strip()
    else:
        adb_execute('adb shell su -c svc wifi disable').read().strip()

def adb_data(power):
    '''
    开启/关闭蜂窝数据
    pass: 需要root权限
    :return:
    '''
    if not adb_root():
        zq_log.log_debug('The device not root.')
        return
    if power:
        adb_execute('adb shell su -c svc data enable').read().strip()
    else:
        adb_execute('adb shell su -c svc data disable').read().strip()

def adb_get_wifi_state():
    '''
    获取WiFi连接状态
    :return:
    '''
    return 'enabled' in adb_execute('adb shell dumpsys wifi | %s ^Wi-Fi' % 'findstr').read().strip()

def adb_get_data_state():
    '''
    获取移动网络连接状态
    :return:
    '''
    return '2' in adb_execute('adb shell dumpsys telephony.registry | %s mDataConnectionState' % 'findstr').read().strip()

def adb_get_network_state():
    '''
    设备是否连上互联网
    :return:
    '''
    return 'unknown host' not in adb_execute('adb shell ping -w 1 www.baidu.com').read().strip()

def adb_get_wifi_password_list():
    '''
    获取WIFI密码列表
    :return:
    '''
    if not adb_root():
        zq_log.log_debug('The device not root.')
        return []
    l = re.findall(re.compile('ssid=".+?"\s{3}psk=".+?"'), adb_execute('adb shell su -c cat /data/misc/wifi/*.conf').read())
    return [re.findall(re.compile('".+?"'), i) for i in l]

def adb_call(number):
    '''
    拨打电话
    :param number:
    :return:
    '''
    adb_execute('adb shell am start -a android.intent.action.CALL -d tel:%s' % number)

def adb_open_url(url):
    '''
    打开网页
    :return:
    '''
    adb_execute('adb shell am start -a android.intent.action.VIEW -d %s' % url)

def adb_start_application(component):
    '''
    启动一个应用
    e.g: com.android.settings/com.android.settings.Settings
    '''
    adb_execute('adb shell am start -n %s' % component)

def adb_send_keyevent(keycode):
    '''
    发送一个按键事件
    https://developer.android.com/reference/android/view/KeyEvent.html
    :return:
    '''
    adb_execute('adb shell input keyevent %s' % keycode)

def adb_rotation_screen(param):
    '''
    旋转屏幕
    :param param: 0 >> 纵向，禁止自动旋转; 1 >> 自动旋转
    :return:
    '''
    adb_execute('adb shell /system/bin/content insert --uri content://settings/system --bind '
                'name:s:accelerometer_rotation --bind value:i:%s' % param)

def adb_instrument(command):
    '''
    启动instrument app
    :param command: 命令
    :return:
    '''
    return adb_execute('adb shell am instrument %s' % command).read()

def adb_export_apk(package, target_path='', timeout=5000):
    '''
    从设备导出应用
    :param timeout: 超时时间
    :param target_path: 导出后apk存储路径
    :param package: 包名
    :return:
    '''
    num = 0
    if target_path == '':
        adb_execute('adb pull /data/app/%s-1/base.apk %s' % (package, os.path.expanduser('~')))
        while 1:
            num += 1
            if num <= timeout:
                if os.path.exists(os.path.join(os.path.expanduser('~'), 'base.apk')):
                    os.rename(os.path.join(os.path.expanduser('~'), 'base.apk'),
                                os.path.join(os.path.expanduser('~'), '%s.apk' % package))

    else:
        adb_execute('adb pull /data/app/%s-1/base.apk %s' % (package, target_path))
        while 1:
            num += 1
            if num <= timeout:
                if os.path.exists(os.path.join(os.path.expanduser('~'), 'base.apk')):
                    os.rename(os.path.join(os.path.expanduser('~'), 'base.apk'),
                                os.path.join(os.path.expanduser('~'), '%s.apk' % package))


class ABD_KEY:
    KEYCODE_UNKNOWN = 0,
    KEYCODE_MENU = 1, 
    KEYCODE_SOFT_RIGHT = 2, 
    KEYCODE_HOME = 3  # Home键
    KEYCODE_BACK = 4  # 返回键
    KEYCODE_CALL = 5  # 拨号键
    KEYCODE_ENDCALL = 6  # 挂机键
    KEYCODE_0 = 7, 
    KEYCODE_1 = 8, 
    KEYCODE_2 = 9, 
    KEYCODE_3 = 10,
    KEYCODE_4 = 11,
    KEYCODE_5 = 12,
    KEYCODE_6 = 13,
    KEYCODE_7 = 14,
    KEYCODE_8 = 15,
    KEYCODE_9 = 16,
    KEYCODE_STAR = 17  # *
    KEYCODE_POUND = 18  # #
    KEYCODE_DPAD_UP = 19  # 导航键 >> 向上
    KEYCODE_DPAD_DOWN = 20  # 导航键 >> 向下
    KEYCODE_DPAD_LEFT = 21  # 导航键 >> 向左
    KEYCODE_DPAD_RIGHT = 22  # 导航键 >> 向右
    KEYCODE_DPAD_CENTER = 23  # 导航键 >> 确定键
    KEYCODE_VOLUME_UP = 24  # 音量+键
    KEYCODE_VOLUME_DOWN = 25  # 音量-键
    KEYCODE_POWER = 26  # 电源键
    KEYCODE_CAMERA = 27  # 拍照键
    KEYCODE_CLEAR = 28,
    KEYCODE_A = 29,
    KEYCODE_B = 30,
    KEYCODE_C = 31,
    KEYCODE_D = 32,
    KEYCODE_E = 33,
    KEYCODE_F = 34,
    KEYCODE_G = 35,
    KEYCODE_H = 36,
    KEYCODE_I = 37,
    KEYCODE_J = 38,
    KEYCODE_K = 39,
    KEYCODE_L = 40,
    KEYCODE_M = 41,
    KEYCODE_N = 42,
    KEYCODE_O = 43,
    KEYCODE_P = 44,
    KEYCODE_Q = 45,
    KEYCODE_R = 46,
    KEYCODE_S = 47,
    KEYCODE_T = 48,
    KEYCODE_U = 49,
    KEYCODE_V = 50,
    KEYCODE_W = 51,
    KEYCODE_X = 52,
    KEYCODE_Y = 53,
    KEYCODE_Z = 54,
    KEYCODE_COMMA = 55  # ,
    KEYCODE_PERIOD = 56  # .
    KEYCODE_ALT_LEFT = 57,
    KEYCODE_ALT_RIGHT = 58,
    KEYCODE_SHIFT_LEFT = 59,
    KEYCODE_SHIFT_RIGHT = 60,
    KEYCODE_TAB = 61  # Tab键
    KEYCODE_SPACE = 62  # 空格键
    KEYCODE_SYM = 63,
    KEYCODE_EXPLORER = 64,
    KEYCODE_ENVELOPE = 65,
    KEYCODE_ENTER = 66  # 回车键
    KEYCODE_DEL = 67  # 退格键
    KEYCODE_GRAVE = 68  # `
    KEYCODE_MINUS = 69  # -
    KEYCODE_EQUALS = 70  # =
    KEYCODE_LEFT_BRACKET = 71  # [
    KEYCODE_RIGHT_BRACKET = 72  # ]
    KEYCODE_BACKSLASH = 73  # \
    KEYCODE_SEMICOLON = 74  # ;
    KEYCODE_APOSTROPHE = 75  # '
    KEYCODE_SLASH = 76  # /
    KEYCODE_AT = 77  # @
    KEYCODE_NUM = 78,
    KEYCODE_HEADSETHOOK = 79,
    KEYCODE_FOCUS = 80  # 对焦键
    KEYCODE_PLUS = 81  # +
    KEYCODE_MENU = 82  # 菜单键
    KEYCODE_NOTIFICATION = 83  # 通知键
    KEYCODE_SEARCH = 84  # 搜索键
    KEYCODE_TAG_LAST = 85,
    KEYCODE_MEDIA_PLAY_PAUSE = 85  # 多媒体键 >> 播放 / 暂停
    KEYCODE_MEDIA_STOP = 86  # 多媒体键 >> 停止
    KEYCODE_MEDIA_NEXT = 87  # 多媒体键 >> 下一首
    KEYCODE_MEDIA_PREVIOUS = 88  # 多媒体键 >> 上一首
    KEYCODE_MEDIA_REWIND = 89  # 多媒体键 >> 快退
    KEYCODE_MEDIA_FAST_FORWARD = 90  # 多媒体键 >> 快进
    KEYCODE_MUTE = 91  # 话筒静音键
    KEYCODE_PAGE_UP = 92  # 向上翻页键
    KEYCODE_PAGE_DOWN = 93  # 向下翻页键
    KEYCODE_ESCAPE = 111  # ESC键
    KEYCODE_FORWARD_DEL = 112  # 删除键
    KEYCODE_CAPS_LOCK = 115  # 大写锁定键
    KEYCODE_SCROLL_LOCK = 116  # 滚动锁定键
    KEYCODE_BREAK = 121  # Break / Pause键
    KEYCODE_MOVE_HOME = 122  # 光标移动到开始键
    KEYCODE_MOVE_END = 123  # 光标移动到末尾键
    KEYCODE_INSERT = 124  # 插入键
    KEYCODE_MEDIA_PLAY = 126,    # 多媒体键 >> 播放
    KEYCODE_MEDIA_PAUSE = 127  # 多媒体键 >> 暂停
    KEYCODE_MEDIA_CLOSE = 128  # 多媒体键 >> 关闭
    KEYCODE_MEDIA_EJECT = 129  # 多媒体键 >> 弹出
    KEYCODE_MEDIA_RECORD = 130  # 多媒体键 >> 录音
    KEYCODE_NUM_LOCK = 143  # 小键盘锁
    KEYCODE_VOLUME_MUTE = 164  # 扬声器静音键
    KEYCODE_ZOOM_IN = 168  # 放大键
    KEYCODE_ZOOM_OUT = 169  # 缩小键
