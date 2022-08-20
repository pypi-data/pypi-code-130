from execjs import RuntimeUnavailableError
from bilix.log import logger
# base
from .base_downloader_m3u8 import BaseDownLoaderM3u8
from .base_downloader_part import BaseDownloaderPart
# site
from .downloader_bilibili import DownloaderBilibili
from .downloader_jable import DownloaderJable
from .downloader_douyin import DownLoaderDouyin
from .downloader_yinghuacd import DownloaderYinghuacd

# js runtime require
try:
    from .downloader_yhdmp import DownloaderYhdmp
except RuntimeUnavailableError as e:
    logger.warning(f"Due to {e} Yhdmp is not available, to avoid this warning plz install node.js in your os")
