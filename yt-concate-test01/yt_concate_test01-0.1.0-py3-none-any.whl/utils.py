import os
import shutil

from yt_concate.settings import DOWNLOADS_DIR
from yt_concate.settings import VIDEOS_DIR
from yt_concate.settings import CAPTIONS_DIR
from yt_concate.settings import OUTPUTS_DIR

class Utils:
    def __int__(self):
        pass

    def creat_dirs(self):  # for Preflight()
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        os.makedirs(CAPTIONS_DIR, exist_ok=True)
        os.makedirs(OUTPUTS_DIR, exist_ok=True)

    def delete_dirs(self):  # for Postflight()
        shutil.rmtree(CAPTIONS_DIR)
        shutil.rmtree(VIDEOS_DIR)

    def get_video_list_filepath(self, channel_id):  # for GetVideoList(), self
        return os.path.join(DOWNLOADS_DIR, channel_id + '.txt')

    def video_list_file_exists(self, channel_id):  # for GetVideoList()
        path = self.get_video_list_filepath(channel_id)
        return os.path.exists(path) and os.path.getsize(path) > 0

    def caption_file_exists(self, yt):  # for DownloadCaptions()、ReadCaption()
        filepath = yt.caption_filepath
        return os.path.exists(filepath) and os.path.getsize(filepath) > 0

    def video_file_exists(self, yt):  # for DownloadVideos()
        filepath = yt.video_filepath
        return os.path.exists(filepath) and os.path.getsize(filepath) > 0

    def get_output_filepath(self, channel_id, search_word):  # for EditVideo()
        return os.path.join(OUTPUTS_DIR, channel_id + '_' + search_word + '.mp4')


