import time
import sys
import getopt
import logging

from yt_concate.pipeline.steps.preflight import Preflight
from yt_concate.pipeline.steps.get_video_list import GetVideoList
from yt_concate.pipeline.steps.initialize_yt import InitializeYT
from yt_concate.pipeline.steps.download_captions import DownloadCaptions
from yt_concate.pipeline.steps.read_caption import ReadCaption
from yt_concate.pipeline.steps.search_caption import SearchCaption
from yt_concate.pipeline.steps.download_videos import DownloadVideos
from yt_concate.pipeline.steps.edit_video import EditVideo
from yt_concate.pipeline.steps.postflight import Postflight
from yt_concate.pipeline.steps.step import StepException
from yt_concate.pipeline.pipeline import Pipeline
from yt_concate.utils import Utils
from yt_concate.config_logger import config_logger

CHANNEL_ID = 'UCKSVUHI9rbbkXhvAXK-2uxA'

def print_usage():
    print('python yt-concate OPTIONS')
    print('OPTIONS:')
    print('{:>6} {:<14} {}'.format('-h', '--help', 'help'))
    print('{:>6} {:<14} {}'.format('-c', '--channel_id', 'Input channel id'))
    print('{:>6} {:<14} {}'.format('-s', '--search_word', 'Input keyword'))
    print('{:>6} {:<14} {}'.format('-l', '--limit', 'Input maximum number of videos to concatenate video '))
    print('{:>6} {:<14} {}'.format('', '--cleanup', 'Whether to clean up download files, default is False. If want to be True, just input "cleanup"'))
    print('{:>6} {:<14} {}'.format('-f', '--fast', 'Whether to skip download action when find existing file, default is True.'))
    print('{:>6} {:<14} {}'.format('', '--level', 'Input log level of message displayed on the screen, default is WARNING. Example: DEBUG, INFO, WARNING, ERROR, CRITICAL'))


def get_args(inputs):
    short_opts = 'hc:s:l:f:'  # ':'代表該參數後面必須有內容
    long_opts = 'help channel_id= search_word= cleanup limit= fast= level='.split()  # 需為list  # '='代表該參數後面必須有內容

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif opt in ("-c", "--channel_id"):
            inputs['channel_id'] = arg
        elif opt in ("-s", "--search_word"):
            inputs['search_word'] = arg
        elif opt in ("-l", "--limit"):
            inputs['limit'] = int(arg)
        elif opt in ("-f", "--fast"):
            inputs['fast'] = str(arg).lower()
        elif opt == '--cleanup':  # cleanup沒縮寫, 不允許接arg
            inputs['clean_up_download'] = True
        elif opt == '--level':  # level沒縮寫
            inputs['level'] = str(arg).upper()

    # channel_id, search_word, limit 防呆是否為empty
    if not inputs['channel_id'] or not inputs['search_word'] or not inputs['limit']:
        print_usage()
        sys.exit(2)

    # fast 防呆與assign bool True/False
    if inputs['fast'] in ["true", "false"]:
        inputs['fast'] = inputs['fast'] == "true"
    else:
        print_usage()
        sys.exit(2)

    # level 防呆
    if not inputs['level'] in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        print_usage()
        sys.exit(2)

    return inputs

def main():

    # default args
    inputs = {
        'channel_id': CHANNEL_ID,
        'search_word': 'incredible',
        'limit': 5,
        'clean_up_download': False,
        'fast': True,
        'level': 'INFO',
        # 'multi': 'single-thread',
        'multi': 'multi-threading',
        # 'multi': 'multi-processing',
    }
    inputs = get_args(inputs)

    config_logger(inputs['level'])

    steps = [
        Preflight(),
        GetVideoList(),
        InitializeYT(),
        DownloadCaptions(),
        ReadCaption(),
        SearchCaption(),
        DownloadVideos(),
        EditVideo(),
        Postflight(),
    ]

    utils = Utils()
    p = Pipeline(steps)
    p.run(inputs, utils)


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    logger = logging.getLogger()
    logger.info('>>total: took ' + str(end - start) + ' seconds')
