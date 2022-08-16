from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips

from .step import Step


class EditVideo(Step):
    def process(self, data, inputs, utils):
        clips = []
        for find in data:
            # 取得整部影片總長度
            full_duration = VideoFileClip(find.yt.video_filepath).duration  # seconds

            # 取得關鍵字起始時間
            start, end = self.parse_caption_time(find.time)

            # 避免關鍵字字幕結束時間超過影片總長度
            if end[0]*60*60 + end[1]*60 + end[2] > full_duration:
                end = None

            # 剪輯影片
            video = VideoFileClip(find.yt.video_filepath).subclip(start, end)
            clips.append(video)

            # 避免記憶體不足, 所以有影片數限制
            if len(clips) >= inputs['limit']:
                break

        # 連接影片
        final_clip = concatenate_videoclips(clips)
        output_filepath = utils.get_output_filepath(inputs['channel_id'], inputs['search_word'])
        final_clip.write_videofile(output_filepath, temp_audiofile='temp-audio.m4a', remove_temp=True, codec="libx264", audio_codec="aac")

    def parse_caption_time(self, caption_time):
        start, end = caption_time.split(' --> ')
        return self.parse_time_str(start), self.parse_time_str(end)

    def parse_time_str(self, time_str):
        h, m, s = time_str.split(':')
        s, ms = s.split(',')
        return int(h), int(m), int(s) + int(ms) / 1000  # 自動回傳tuple
