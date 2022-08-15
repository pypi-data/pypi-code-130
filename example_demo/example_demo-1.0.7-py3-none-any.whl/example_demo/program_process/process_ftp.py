# -*- coding: utf-8 -*-
import traceback
import time
from example_demo.request_downloader.downloaders import ftp_connect
import example_demo.commons.common_fun as common
import datetime


class FtpProcess():
    def __init__(self, request_info, ftp_dir, download_file_name, local_file_path,  debug=False, **kwargs):
        self.request_info = request_info
        self.ftp_dir = ftp_dir
        self.download_file_name = download_file_name
        self.local_file_path = local_file_path
        self.debug = debug

    def cwd_load_file(self, ftp_con):
        load_res = False
        try:
            ftp_con.cwd(self.ftp_dir)
            buf_size = 1024  # 设置的缓冲区大小
            ftp_file_list = ftp_con.nlst()
            if self.download_file_name in ftp_file_list:
                file_obj = open(self.local_file_path, "wb")
                file_handle = file_obj.write  # 以写模式在本地打开文件
                ftp_con.retrbinary("RETR %s" % self.download_file_name, file_handle, buf_size)  # 接收服务器上文件并写入本地文件
                # ftp.set_debuglevel(0)  # 关闭调试模式
                # print(f'{download_file_name} download finished.')
                file_obj.close()
                ftp_con.quit()  # 退出ftp
                load_res = True
        except Exception as e:
            traceback.print_exc()
            time.sleep(2)
        return load_res
    def run(self):
        ftp_con = ftp_connect(**self.request_info)
        load_res = self.cwd_load_file(ftp_con)

        return load_res


class FTPBase():
    def __init__(self, request_info: dict, file_download_info: list, **kwargs):
        self.request_info = request_info
        self.file_download_info = file_download_info
        self.option_args = kwargs
        pass

    def get_all_source(self):
        """Returns source for the program."""
        all_source = []
        for source in self.file_download_info:
            source_info = {"request_info": self.request_info, "file_download_info": source}
            all_source.append({"info": source_info, "result": True})
        return all_source

    def download_source(self, source):
        """Returns source download result"""

        pass


class FtpParseBase():
    def __init__(self, source: dict, **kwargs):
        '''
        source need {"info":{},"result":True or False}
        "info" is your prepare source ==> {"request_info":{}, "file_download_info":{}}
        '''
        self.source = source

    def parse_source(self):
        """

        parse download result or file or you can customize yourself

        """
        pass
