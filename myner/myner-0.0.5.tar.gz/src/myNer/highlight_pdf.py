# Import Libraries
import fitz
from ner import ner_spacy , find_imo,find_swift,ner_dicts
import base64
from text_preprocessing import spacy_preprocessing 
from ner import ner_spacy,find_imo,find_swift,ner_dicts
import os

#extract text from pdf
def extract_text(input_file):
    doc = fitz.open(input_file)
    text = []
    for page in doc:
        text.append(page.get_text("text"))
    return text

#find entities
def find_ent(input_file):
    text_ents  =[]
    for txt in  extract_text(input_file):
        page_ents = []
        page_ents.extend(ner_spacy(txt)[0]) #ner_spacy(txt)[0]:entities
        page_ents.extend(find_imo(txt))
        page_ents.extend(find_swift(txt))
        page_ents.extend(ner_dicts(txt,"postgresql://postgres:achraf@localhost:5432/ner_dicts","ports_banks_ships"))
        text_ents.append(page_ents)
    return text_ents

#highlight entities in pages
def highlight_ent(page ,page_no, matching_ents):
    positions_dict = {}
    for ent in matching_ents:
        matching_val_area = page.search_for(ent.text)
        positions_dict[ent] =(matching_val_area,page_no)
        highlight = page.addHighlightAnnot(matching_val_area)
        info = highlight.info
        info["title"] = ent.label_
        info["content"] = ent.label_ + ":" + ent.text
        
        highlight.set_info(info)
        highlight.update()
    return positions_dict
#pdf to base64
def pdf_to_base64(pdf):
    with open(pdf, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
    return encoded_string
#base64 to pdf
def base64_to_pdf(bbase64):
    with open('out.pdf', 'wb') as pdf:
        pdf.write(base64.b64decode(bbase64))
    return ".//out.pdf"
#final function
def output(input_file,output_path):
    """
    '/' in the path string should be replaced with '//' 
    """
    doc=fitz.open(input_file)
    text_ents = find_ent(input_file)
    i=0
    positions = {}
    for page in doc:
        for ent in text_ents[i]:
            if ent not in positions.keys():
                positions[ent] =[]
        part_pos=highlight_ent(page,i+1,text_ents[i])
        i+=1
        for entity,pos in part_pos.items():
            positions[entity].append(pos)
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    return output_path,positions

def charge_text(text_file):
    file = text_file
    f=open(file,'r',encoding='utf8')
    text= f.read()
    return text

def get_entites(text):
    """
    Text is the text from wich we extract the entities
    """ 
    preprocessed_text = spacy_preprocessing(text,lowercase=True,punctuation=True)
    ents = list(ner_spacy(preprocessed_text)[0])
    ents.extend(find_imo(text))
    ents.extend(find_swift(text))
    ents.extend(ner_dicts(text,"postgresql://postgres:achraf@localhost:5432/ner_dicts","ports_banks_ships"))
    return ents

def test(text_file,pdf):
    text = charge_text(text_file)
    text_ents = get_entites(text)
    output(pdf,".//output.pdf")
    return "pdf highlighté, entité dans le texte sont {}".format(text_ents)


def batch_ner(dir_path):
    for root , dirpath,filenames in os.walk(dir_path):
        files_to_ner =[os.path.join(root,file) for file in filenames] 
        for i,file in enumerate(files_to_ner):
            if ".pdf" in file:
                if not os.path.exists(root+"//DOSSIER_NER_RESULT"):
                    os.mkdir(root+"//DOSSIER_NER_RESULT")
                output(file,str(root+"//DOSSIER_NER_RESULT//"+str(i)+".pdf"))
        print(root+" est traité")