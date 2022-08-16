from airflow import DAG
import dataops
from jindefund.pipeline.decorators import win_virtualenv

from {airflow_owner}.{project_name}.env_dag_cfg import DAG_CFGS, CONN_ID, REQUIREMENTS, PIP_INSTALL_OPTIONS, PY_VERSION, \
    PROGRAM_DAG_FOLDER
import os

dataops.turnoff_all_warnings()

# 项目名称
DAG_CFGS["dag_id"] = ''
# 项目计划执行时间 支持crontab '8 9 * * *'
DAG_CFGS["schedule_interval"] = ''

# 1. 数据准备及检查 入口
@win_virtualenv(python_version=PY_VERSION, requirements=REQUIREMENTS, psrp_conn_id=CONN_ID, task_id="get_source_info",
                do_xcom_push=True, pip_install_options=PIP_INSTALL_OPTIONS)
def get_source_info(run_path):
    import sys
    sys.path.insert(0, run_path)
    from example_demo.program_process.process_request import HTTPBase

    class HTTPProcess(HTTPBase):
        """
            http 请求模板流程
            1. 请求url-->直接下载为文件-->(解析文件内容存取数据库)
            2. 请求url-->解析请求内容---> 存取文件
            3. 请求url-->解析请求内容---> 存取数据库
        """
        def __init__(self):
            # 1. ftp 请求信息
            self.request_info = {
                "url": [''],
                "url_params": {},
                "request_type": "",  # GET && POST
            #   'request_auth_name': '',
            #   'request_auth_password':'',

            }

            # 2. 文件信息 (按需配置：流程1,2）
            self.file_download_info = [{
                "file": '',  # 下载文件名
                "file_download_path_dir": r'',  # 下载至路径
            }]

            # 3. 数据库信息(按需配置：流程1（存取数据库的情况），流程3）
            self.out_db_info = {
                "connect_url": "",  # sqlalchemy connect_url if has no need next db host.etc info
                "db_type": '',
                "host": '',
                "port": '',
                "user": '',
                "password": '',
                "table": '',
                "check_data_sql": "",
                # "get_sql": [''],
                # "to_sql": ''
                "to_sql_params": {"if_exists": 'append', "index": False}

            }

            # 其他配置 （非必要）
            # email_info = {
            #     "email_host": "",
            #     "email_from": "",
            #     "email_to_list": "",
            # }

            super().__init__(self.request_info, self.file_download_info, out_db_info=self.out_db_info)
        # 整理 返回抓取list
        # def get_all_source(self):
        #     pass

    return HTTPProcess().get_all_source()





# 2. 数据解析
@win_virtualenv(python_version=PY_VERSION, requirements=REQUIREMENTS, psrp_conn_id=CONN_ID,
                task_id="download_parser_info", do_xcom_push=True, pip_install_options=PIP_INSTALL_OPTIONS)
def download_parse_info(sour, run_path):
    import pandas
    from example_demo.program_process.process_request import HttpDownloadParseBase
    # 目前的http模板：
    # 配置了prepare_source 的 file_download_info，则标识为下载文件，模板downloader方法会直接进行下载文件,如果需要对下载文件进行自定义处理，在downloader_parse_customize，先调用download_parse_source，进行下载
    # 直接下载的方法为 HTTPDownloader


    class DownloadParseSource(HttpDownloadParseBase):
        def __init__(self, source):
            self.source = source
            super().__init__(self.source)

        # def downloader(self):
        #     from example_demo.request_downloader.http_downloader import HTTPDownloader
        #     request_info = self.source.get("request_info")
        #     download_res, res_content = HTTPDownloader(request_info).downloader()

        # 可自定义如何解析
        # def downloader_parse_customize(self):
        #     self.download_parse_source()
        #     pass

        # 检查数据是否已输出
        # def parse_check_out_data(self, data: pandas.DataFrame):
        #     '''
        #     检查数据是否已下载，最终输出为数据库时，data为db_info check_data_sql 获取到的数据
        #     '''
            # 数据是否已存在；数据是否正常
            # need_get_data = False
            # data_success = False
            # if data.shape[0] == 0:
            #     need_get_data = True
            # elif data.shape[0] == 5:
            #     data_success = True
            # return [need_get_data, data_success]

        def parse_fileinfo(self,file_download_path):
            '''
            解析http请求下载的文件，返回内容，若配置了数据库等参数，会默认将数据插入数据库
            file_download_path 为下载文件的目录
            '''


            pass


    for source in sour:
        info = source.get("info")
        if info:
            # task download_file
            DownloadParseSource(sour).download_parse_source()



with DAG(
        **DAG_CFGS
) as dag:
    # task prepare_source
    download_parse_info(get_source_info(PROGRAM_DAG_FOLDER), run_path=PROGRAM_DAG_FOLDER)
