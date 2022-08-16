import os
import time
from pytube import YouTube
from threading import Thread
from multiprocessing import Process
import logging

from .step import Step
from .step import StepException


class DownloadCaptions(Step):

    def process(self, data, inputs, utils):
        start = time.time()
        multi_str = inputs['multi']
        logger = logging.getLogger()

        # 此專案較適合multi-threading
        if inputs['multi'] == 'single-thread':
            self.multi_download_captions(data, utils, multi_str, inputs['fast'])

        if inputs['multi'] == 'multi-threading':
            threads = []
            for i in range(os.cpu_count()):
                # i = 0-> 0,8,16,24... -> data[0], data[8]...
                # i = 1-> 1,9,17,25... -> data[1], data[9]...
                threads.append(Thread(target=self.multi_download_captions,
                                      args=(data[i::os.cpu_count()], utils, multi_str + ' ' + str(i), inputs['fast'])))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

        if inputs['multi'] == 'multi-processing':
            processes = []
            for i in range(os.cpu_count()):
                processes.append(Process(target=self.multi_download_captions,
                                         args=(data[i::os.cpu_count()], utils, multi_str + ' ' + str(i), inputs['fast'])))

            for process in processes:
                process.start()

            for process in processes:
                process.join()

        end = time.time()
        logger.info('>>download captions: took ' + str(end - start) + ' seconds')
        return data

    def multi_download_captions(self, data, utils, multi_str, fast):
        logger = logging.getLogger()

        for yt in data:
            if fast:
                if utils.caption_file_exists(yt):
                    logger.info(f'find existing caption file: {yt.id}, skipping')
                    continue
            try:
                logger.info(f'download caption({multi_str}): {yt.id}')
                source = YouTube(yt.url)
                en_caption = source.captions.get_by_language_code('a.en')
                en_caption_convert_to_srt = (en_caption.generate_srt_captions())
            except (KeyError, AttributeError):
                logger.warning('Error when download caption for ' + yt.url)
                continue

            text_file = open(yt.caption_filepath, "w", encoding='utf-8')
            text_file.write(en_caption_convert_to_srt)
            text_file.close()

