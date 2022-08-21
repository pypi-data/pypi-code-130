import os
import requests
import chardet
from contextlib import closing
import zq_log, zq_file

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.9',
    # 'accept-encoding': 'gzip, deflate, br', #加密
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    # 'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
    'user-agent': 'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; MI 4S Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.146 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.1.3',
}

def http_get_requests_url_result(url, headers = None, params = None, data = None, stream = False, verify=False, timeout=60, proxies=False, isAutoEncoding=False):
    '''
    requests get 网络数据
    :param proxies: {"https":"127.0.0.1:12639"}
    '''
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False
    res = None
    
    try:
        if headers:
            for headerItem in headers:
                headers[headerItem] = headers[headerItem]
        requests.packages.urllib3.disable_warnings()
        res = s.get(url, headers = headers, params = params, data = data, verify=verify, stream=stream, timeout=timeout, proxies=proxies)
        if isAutoEncoding:
            res.encoding = chardet.detect(res.content).get('encoding')
        res.close()            
        return res
    except BaseException as e:            
        zq_log.log_debug("http_get_requests_url_result BaseException error ==>> URL: {}  Error: {}".format(url, str(e)))        
    return res

def http_post_requests_url_result(url, headers = None, params = None, data = None, stream = False, files= False, verify=False, cookies=False, timeout=60, proxies=None, isAutoEncoding=False):
    '''
    requests post 网络数据
    :param proxies: {"https":"127.0.0.1:12639"}
    '''
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False
    res = None
    
    try:
        if headers:
            for headerItem in headers:
                headers[headerItem] = headers[headerItem]
        requests.packages.urllib3.disable_warnings()
        res = s.post(url, headers = headers, params = params, data = data, verify=verify, stream=stream, files= files, cookies=cookies, timeout=timeout, proxies=proxies)
        if isAutoEncoding:
            res.encoding = chardet.detect(res.content).get('encoding')
        res.close()            
        return res
    except BaseException as e:            
        zq_log.log_debug("http_post_requests_url_result BaseException error ==>> URL: {}  Error: {}".format(url, str(e)))        
    return res

def http_download(urlPath, saveFilePath, exists_jump=True, desc='文件下载中: '):
    '''
    http下载  适用于大文件
    :param urlPath: 下载地址
    :param saveFilePath: 保存路径，带后缀
    :param exists_jump: 已存在是否跳过
    :return bool: 是否成功
    '''
    try:
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False
        with closing(requests.get(urlPath, headers = headers, stream=True)) as response:
            if not response.ok:
                zq_log.log_debug('错误页面：==>>>  ' + response.text)
                return False
            chunk_size = 1024
            content_size = -1
            if 'content-length' in response.headers:
                content_size = int(response.headers['content-length'])
            if(os.path.exists(saveFilePath) and os.path.getsize(saveFilePath)==content_size) and exists_jump:
                zq_log.log_debug('跳过'+saveFilePath)
                return True
            else:
                videoDirPath = os.path.dirname(saveFilePath)
                zq_file.dir_auto_create_dir_by_file(saveFilePath)
                with open(saveFilePath, "wb") as fs:
                    curr_size = 0
                    for data in response.iter_content(chunk_size=chunk_size):
                        fs.write(data)
                        curr_size += len(data)
                        zq_log.log_progress_bar(curr_size, content_size, desc)
        return True
    except BaseException as e:
        zq_log.log_debug("http_download error ==>>  " + str(e))
        return False

def http_download_img(urlPath, saveFilePath):
    '''
    http下载  适用于小文件，图片那种，很快的
    '''
    from urllib.request import urlretrieve
    return urlretrieve(urlPath, filename=saveFilePath)