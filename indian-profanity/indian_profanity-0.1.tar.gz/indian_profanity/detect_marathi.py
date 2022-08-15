
words=["madarchot", "madarchod", "aie ghalya", "aieghalya", "bhenchod", "bhenchot",\
       "tuzya aie chi gand", "gand", "chut", "chutya", "chut marichya", "chutmarichya",\
        "nalayak", "bhadkhau", "bhadvya"]


def detectSlangMarathi(string):
    for s in string.lower().split(" "):
        if s in words:
            return True
    return False

def detectSlangMarathiWord(string):
    word=[]
    for s in string.lower().split():
        if s in words:
            word.append(s)
    return word

def censoredSlangMarathiWord(string):
    word=[]
    for s in string.lower().split():
        if s in words:
            word.append(s)

    return ' '.join("***" if i in word else i for i in string.split())