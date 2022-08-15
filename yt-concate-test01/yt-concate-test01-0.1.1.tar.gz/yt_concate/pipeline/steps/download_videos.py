import os
import time
from .step import Step
from threading import Thread
from multiprocessing import Process
import logging

from pytube import YouTube
from yt_concate.settings import VIDEOS_DIR


class DownloadVideos(Step):

    def process(self, data, inputs, utils):
        logger = logging.getLogger()
        yt_set = list(set([find.yt for find in data]))  # set方式去除重複(關鍵字多次出現於同一部影片)
        logger.info("search word and download counts of videos: " + str(len(yt_set)))

        start = time.time()
        multi_str = inputs['multi']


        # 此專案較適合multi-threading
        if inputs['multi'] == 'single-thread':
            self.multi_download_videos(yt_set, utils, multi_str, inputs['fast'])

        if inputs['multi'] == 'multi-threading':
            threads = []
            for i in range(os.cpu_count()):
                threads.append(Thread(target=self.multi_download_videos,
                                      args=(yt_set[i::os.cpu_count()], utils, multi_str + ' ' + str(i), inputs['fast'])))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

        if inputs['multi'] == 'multi-processing':
            processes = []
            for i in range(os.cpu_count()):
                processes.append(Process(target=self.multi_download_videos,
                                         args=(yt_set[i::os.cpu_count()], utils, multi_str + ' ' + str(i), inputs['fast'])))

            for process in processes:
                process.start()

            for process in processes:
                process.join()

        end = time.time()
        logger.info('>>download videos: took ' + str(end - start) + ' seconds')

        return data

    def multi_download_videos(self, yt_set, utils, multi_str, fast):
        logger = logging.getLogger()

        for yt in yt_set:  # yt = find.yt
            if fast:
                if utils.video_file_exists(yt):  # 已下載過的影片不需重新下載(雖然下列pytube亦會自動略過已下載的)
                    logger.info(f'find existing video file: {yt.url} , skipping')
                    continue

            logger.info(f'download videos({multi_str}): {yt.url}')
            YouTube(yt.url).streams.first().download(output_path=VIDEOS_DIR, filename=yt.id + '.mp4')

