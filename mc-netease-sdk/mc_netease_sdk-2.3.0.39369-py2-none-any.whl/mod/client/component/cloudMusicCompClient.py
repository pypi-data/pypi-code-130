# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent

class CloudMusicCompClient(BaseComponent):
    def GetSongDetail(self, songId, cb):
        # type: (str, function) -> None
        """
        获取该歌曲的详细信息
        """
        pass

    def PlayCloudSong(self, songId):
        # type: (str) -> None
        """
        播放网易云音乐
        """
        pass

    def StopCloudMusic(self):
        # type: () -> None
        """
        停止播放网易云音乐
        """
        pass

    def PauseCloudMusic(self):
        # type: () -> None
        """
        暂停播放网易云音乐
        """
        pass

    def ResumeCloudMusic(self):
        # type: () -> None
        """
        恢复播放网易云音乐
        """
        pass

