from airflow import DAG
import dataops
from jindefund.pipeline.decorators import win_virtualenv

from {airflow_owner}.{project_name}.env_dag_cfg import DAG_CFGS, CONN_ID, REQUIREMENTS, PIP_INSTALL_OPTIONS, PY_VERSION, \
    PROGRAM_DAG_FOLDER
import os

dataops.turnoff_all_warnings()


# 1. 数据准备及检查 入口
@win_virtualenv(python_version=PY_VERSION, requirements=REQUIREMENTS, psrp_conn_id=CONN_ID, task_id="get_source_info",
                do_xcom_push=True, pip_install_options=PIP_INSTALL_OPTIONS)
def get_source_info(run_path):
    import sys
    sys.path.insert(0, run_path)
    from example_demo.program_process.process_request import HTTPBase

    class HTTPProcess(HTTPBase):
        def __init__(self):
            # 1. ftp 请求信息
            self.request_info = {
                "url": [''],
                "url_params": {},
                "request_type": "",  # GET && POST
            #   'request_auth_name': '',
            #   'request_auth_password':'',

            }

            # 2. 下载的文件信息
            # 2. 文件信息
            self.file_download_info = [{
                "file": '',  # 下载文件名
                "file_download_path_dir": r'',  # 下载至路径
            }]

            super().__init__(self.request_info, self.file_download_info)
        # 整理 返回抓取list
        # def get_all_source(self):
        #     pass

    return HTTPProcess().get_all_source()





# 3. 数据解析
@win_virtualenv(python_version=PY_VERSION, requirements=REQUIREMENTS, psrp_conn_id=CONN_ID,
                task_id="download_parser_info", do_xcom_push=True, pip_install_options=PIP_INSTALL_OPTIONS)
def download_parser_info(sour, run_path):
    import sys
    sys.path.insert(0, run_path)
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

    return DownloadParseSource(sour).downloader()


with DAG(
        **DAG_CFGS
) as dag:
    # task prepare_source
    all_resource = get_source_info(PROGRAM_DAG_FOLDER)
    for source in all_resource:
        info = source.get("info")
        if info:
            # task download_file
            download_res = download_parser_info(info)
            source["result"] = download_res

            # task parse download source
            download_parser_info(source)
