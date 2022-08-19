import spacy 
import pandas as pd
sp = spacy.load('en_core_web_sm')
df=pd.read_csv("CombinedContentTrial.csv")
content=df['Content'].values.tolist()
#content=content[0:10]
#print(content[1])
sen=sp(content[2])
ents=sen.ents
tags=[]
labels=['PERSON','FAC','ORG']

for data in content:
    sen=sp(data)
    #print(sen)
    st=""
    ents=sen.ents
    for entity in ents:
        print(entity)
        if (entity.label_ in labels):
            print(entity.label_+" "+str(spacy.explain(entity.label_)))
            st=st+str(entity)
            st=st+","
    tags.append(st)
tags_dictionary={"Tags":tags}
dataf=pd.DataFrame(tags_dictionary)
dataf.to_csv('TagsSpacy.csv')
    #print(entity.label_+" "+str(spacy.explain(entity.label_)))
print(tags)