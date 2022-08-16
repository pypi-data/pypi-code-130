from typing import List
import fasttext


def validate_language(srcs: List[str]):
    fasttext_model = fasttext.load_model("lid.176.bin")
    label, score = fasttext_model.predict(' '.join(srcs))
    label = label[0].split('__')[-1]
    score = round(score[0],4)
    return label,score
 
