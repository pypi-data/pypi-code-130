
from .step import Step


class ReadCaption(Step):
    def process(self, data, inputs, utils):
        for yt in data:
            if not utils.caption_file_exists(yt):
                continue

            captions = {}
            with open(yt.caption_filepath, 'r') as f:
                is_time_line = False
                time_str = None
                caption_str = None
                for line in f:
                    if '-->' in line:
                        is_time_line = True
                        time_str = line.strip()
                        continue
                    if is_time_line:
                        caption_str = line.strip()
                        captions[caption_str] = time_str
                        is_time_line = False
            yt.captions = captions  # dictionary

        return data



