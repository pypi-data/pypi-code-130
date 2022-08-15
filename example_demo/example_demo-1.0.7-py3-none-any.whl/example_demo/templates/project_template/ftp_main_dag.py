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
    from example_demo.program_process.process_ftp import FTPBase

    class FTPProcess(FTPBase):
        def __init__(self):
            # 1. ftp 请求信息
            self.ftp_info = {
                "ftp_host": '',
                "ftp_port": '',
                "ftp_user": '',
                "ftp_password": ''
            }

            # 2. 下载的文件信息
            # 2. 文件信息
            # file_download_path = r'D:\Schedule\YieldCurve\csv_tmp'
            self.file_download_info = [{
                "file": '',  # 下载文件名
                "file_download_path_dir": r'',  # 下载至路径
                "file_download_from_dir": "",  # 下载源路径
            }]

            super().__init__(self.ftp_info, self.file_download_info)
        # 整理 返回抓取list
        # def get_all_source(self):
        #     pass

    return FTPProcess().get_all_source()


# . 数据下载解析
@win_virtualenv(python_version=PY_VERSION, requirements=REQUIREMENTS, psrp_conn_id=CONN_ID,
                task_id="download_parser_info", do_xcom_push=True, pip_install_options=PIP_INSTALL_OPTIONS)
def download_parse_info(sour, run_path=''):
    import sys
    if run_path:
        sys.path.insert(0, run_path)
    from example_demo.request_downloader.ftp_downloader import FTPDownloader
    from example_demo.program_process.process_ftp import FtpParseBase
    class ParseSource(FtpParseBase):
        def __init__(self, source):
            self.source = source
            super().__init__(self.source)

        def parse_source_customize(self):
            pass
    for source in sour:
        info = source.get("info")
        if info:
            download_res = FTPDownloader(info).download()
            source["result"] = download_res
            ParseSource(source).parse_source_customize()



with DAG(
        **DAG_CFGS
) as dag:

    download_parse_info(get_source_info(PROGRAM_DAG_FOLDER), run_path=PROGRAM_DAG_FOLDER)


