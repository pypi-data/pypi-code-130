# Author: Keston Smith
# Library: Caribe 
# Contact: keston.smith@my.uwi.edu
#Copyright: Apache-2.0 2021
import re

guyanesedict={
"bai":"boy",
"budday":"friend",
"whaam":"what happened",
"how nah":"how are you",
"waam star": "what going on brother",
"whey":"where",
"wey":"where",
"gu goo":"will go",
"ga fu":"have to",
"gadu":"have to",   
"kom":"come",
"somi":"sometimes",
"vamit":"vomit",
"yu":"you",
"fuud":"food",
"hapn":"happen",
"wid":"with",
"bredda":"brother",
"breda":"brother",
"wit":"with",
"le":"let",
"tel":"tell",
"wo":"what",
"stomik":"stomach",
"ga":"got",
"du":"do",
"yor":"your",
"dis":"this",
"kain":"kind",
"di":"the",
"swet":"sweat",
"badi":"body",
"somtaim":"sometimes",
"lef":"left",
"dem":"them",
"fut":"foot",
"wok":"work",
"waan":"want",
"markit":"market",
"muuv":"move",
"mi":"me",
"Ah":"I",
"tek":"take",
"wuk":"work",
"dong":"down",
"fu":"for",
"gu":"go",
"maan":"man",
"batam":"bottom",
"den":"then",
"aal":"all",
"awii":"all of us",
"taim":"time",
"le":"let",
"tuu":"two",
"shi":"she",
"kaal":"call",
"kozn":"cousin",
"ii":"it",
"kyaa":"cannot",
"swel":"swell",
"tugeda":"together",
"pul":"pull",
"peen":"pain",
"bos":"bust",
"das":"that is",
"tuh":"to",
"wuda":"would of",
"cuda":"could of",
"bika":"because",
"rong":"around",
"bwoy":"boy",
"notn":"nothing",
"els":"else",
"piipl":"people",
"kot":"cut",
"aks":"ask",
"bacoos":"ghosts",
"balanjay":"eggplant",
"bhaigan":"eggplant",
"luk":"look",
"da":"that",
"lef lef":"leftovers",
"pickney":"children",
"manin":"morning",
"gad":"god",
"mih":"my",
"dutty":"dirty",
"duttyness":"dirtyness",



    
    
}

class guyanese_file_encode:
    _data = []
    _out = []
    def __init__(self, filename:str, encode_filetype:str):
        self.filename = filename
        self.filetype = encode_filetype
        __mode = "r+"
        self.file = open(self.filename, __mode, encoding='utf-8') 

        for _ in self.file:
            self._data.append(_)
        for __ in self._data:
            encode = guyanese_encode(__)
            self._out.append(encode)
        self.file.close()
    
        if (self.filetype == "text" or self.filetype == "txt"):
            if (self.filename.endswith(".txt")):
                self.output = open("Translated.txt", "w")
                for x in self._out:
                    self.output.write(x)
                self.output.close()
            else:
                raise TypeError("filename type  and encode filetype mismatch")

        elif (self.filetype == "json"):
            if (self.filename.endswith(".json")):
                self.output = open("Translated.json", "w")
                for x in self._out:
                    self.output.write(x)
                self.output.close()
            else:
                raise TypeError("filename type  and encode filetype mismatch")

        elif(self.filetype == "csv"): 
            if (self.filename.endswith(".csv")):
                self.output = open("Translated.csv", "w")
                for x in self._out:
                    self.output.write(x)
                self.output.close()
            else:
                raise TypeError("filename type  and encode filetype mismatch")   

        else: 
            raise TypeError("filetype options only include 'text', 'json', 'xlsx' or 'csv'")


def guyanese_encode(sentence:str):
    sentence=sentence.lower()
    for words in guyanesedict:
        if guyanesedict[words].lower() in sentence:
            sentence = re.sub(r'\b%s\b' %guyanesedict[words].lower(), words.lower(), sentence)
    return sentence

def guyanese_decode(sentence:str):
    sentence=sentence.lower()
    sentence = " " + sentence 
    for x in guyanesedict:
        if sentence.find(x):
            sentence = re.sub(r'\b%s\b' %x, guyanesedict[x], sentence)
    return sentence.strip()

