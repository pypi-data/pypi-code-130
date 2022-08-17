from beanie import Document, Link, Indexed, Insert, after_event
from typing import List, Optional
from datetime import datetime
import pymongo

'''
{'InfoHash': '9YEG9gJ9sNAre93F1cRXgsnXGjI=', 
'Name': 'Shin Chan - Serie Animada [HDTVrip MP4][Cap.201_225][AAC 2.0 Castellano]', 
'TotalSize': 1398604714, 
'DiscoveredOn': 1658008591, 
'Files': [{'size': 196, 'path': 'www.newpct1.com.url'}]}
'''


async def file_endswith(file: str, endings: List[str]) -> bool:
    ret = False
    for end in endings:
        if file.endswith(end):
            ret = True
            break
    return ret


class TorrentFile(Document):
    size: int
    path: Indexed(str, pymongo.TEXT)

    async def is_video(self) -> bool:
        return await file_endswith(
            self.path, [".mp4", ".avi", ".mov", ".wmv", ".flv", ".f4v", ".swf", ".webm", ".pcm", ".mpeg"]
        )

    async def is_audio(self) -> bool:
        return await file_endswith(
            self.path, [".mp3", ".aac", ".ogg", ".flac", ".alac", ".wav", ".aiff", ".dsd", ".midi", ".m4a", ".amr"]
        )

    async def is_document(self) -> bool:
        return await file_endswith(
            self.path, [".txt", ".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".ods", ".odp"]
        )

    async def is_archive(self) -> bool:
        return await file_endswith(
            self.path, [".epub", ".zip", ".tar", ".gz", ".bz2", ".rar", ".7z", ".cab", ".xz", ".deb", ".ar", ".z",
                        ".lzo", ".lz", ".lz4", ".rpm", ".zst"]
        )

    async def is_executable(self) -> bool:
        return await file_endswith(
            self.path, [".wasm", ".exe", ".elf", ]
        )

    async def is_font(self) -> bool:
        return await file_endswith(
            self.path, [".woff", ".woff2", ".ttf", ".otf"]
        )

    async def is_image(self) -> bool:
        return await file_endswith(
            self.path, [".jpg", ".jpx", ".apng", ".png", ".gif", ".webp", ".cr2", ".tiff", ".bmp", ".jxr", ".psd",
                        ".ico", ".heic", ".dcm", ".dwg", ".xcf"]
        )


class TorrentTag(Document):
    Name: Indexed(str, pymongo.TEXT)
    Seen: int

    @staticmethod
    def get_tags():
        return ["Video", "Audio", "Document", "Archive", "Executable", "Font", "Image"]

    @staticmethod
    async def create_all():
        for tag in TorrentTag.get_tags():
            if (await TorrentTag.find_one(TorrentTag.Name == tag)) is None:
                tt = TorrentTag(Name=tag, Seen=0)
                await tt.save()


class Torrent(Document):
    InfoHash: str
    Name: Indexed(str, pymongo.TEXT)
    Tags: Optional[List[str]]
    TotalSize: int
    DiscoveredOn: datetime
    Files: List[Link[TorrentFile]]
    SeenCounter: int

    @after_event(Insert)
    async def tag(self):
        # by file ending
        tags = []
        for file in self.Files:
            if "Video" not in self.Tags and await file.is_video():
                tags.append("Video")
            elif "Audio" not in self.Tags and await file.is_audio():
                tags.append("Audio")
            elif "Document" not in self.Tags and await file.is_document():
                tags.append("Document")
            elif "Archive" not in self.Tags and await file.is_archive():
                tags.append("Archive")
            elif "Executable" not in self.Tags and await file.is_executable():
                tags.append("Executable")
            elif "Font" not in self.Tags and await file.is_font():
                tags.append("Font")
            elif "Image" not in self.Tags and await file.is_image():
                tags.append("Image")

        for tag in tags:
            tt = await TorrentTag.find_one(TorrentTag.Name == tag)
            tt.Seen += 1
            await tt.save()

        await self.save()
