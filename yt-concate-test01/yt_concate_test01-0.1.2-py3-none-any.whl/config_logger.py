import logging
import os

from yt_concate.settings import OUTPUTS_DIR

def config_logger(level):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 所有軌道的base level, 如果權限高於其他軌道, 則以base level為主

    # 軌道: 檔案輸出
    logger_filepath = os.path.join(OUTPUTS_DIR, 'yt_concate_logging.log')
    file_handler = logging.FileHandler(logger_filepath)
    file_handler.setLevel(logging.WARNING)  # level 固定
    file_formatter = logging.Formatter('%(module)s:%(levelname)s:%(asctime)s:%(message)s')
    file_handler.setFormatter(file_formatter)

    # 軌道: 螢幕輸出
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)  # from inputs["level"]
    stream_formatter = logging.Formatter('%(levelname)s:%(message)s')
    stream_handler.setFormatter(stream_formatter)

    # 加入軌道handler至logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

