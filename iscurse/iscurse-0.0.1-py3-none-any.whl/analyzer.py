import json

afinn = json.load(open('../AFINN-pt.json'))

class Analyzer:
    def __init__(self, text):
        self.text = text
        self.score = self._sentiment(text)

    def get_score(self):
        return self.score

    def get_text(self):
        return self.text
    
    
    def _sentiment(self,text):
        score = []
        point  = 0
        final_score = 0
        for sent in afinn.keys():
            if sent in text:
                point += 1
                score.append(afinn[sent])
        
    
        score = sum(score)
        final_score = score/point if point > 0 else 0

        return final_score
    