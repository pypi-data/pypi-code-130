import os
from typing import Dict

import fasttext

path_to_pretrained_model = os.path.join(os.path.dirname(__file__), '../', 'models/lid.176.ftz')
fmodel = fasttext.load_model(path_to_pretrained_model)


def detect_language(text: str, threshold: float = 0.85) -> Dict[str, float]:
    prediction = fmodel.predict([text.replace('\n', ' ')], threshold=threshold)
    if prediction[0][0]:
        return prediction[0][0][0][-2:]
