from .step import Step
from yt_concate.model.find import Find


class SearchCaption(Step):
    def process(self, data, inputs, utils):
        search_word = inputs['search_word']

        find = []
        for yt in data:
            captions = yt.captions  # dictionary

            if not captions:
                continue
            # key: caption, value: time, 但不需取出全部key與value:
            # for caption, time in captions.items():
            for caption in captions:
                if search_word in caption:
                    time = captions[caption]
                    f = Find(yt, caption, time)
                    find.append(f)
        #print(len(find))
        #print(find)
        return find
