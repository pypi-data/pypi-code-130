from tracemalloc import stop
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


df=pd.read_csv("MergedDf.csv")

low=df["Tags"].values.tolist()
low=[l.lower() for l in low]
df["Tags"]=low

check=True

input_tags=[]
count=0
while(check==True):
    input_tags.append(input("Enter Interested Clubs "))
    input_tags[count]=input_tags[count].lower()
    count+=1
    chk=input("Press 1 to stop ")
    if(chk=="1"):
        check=False
ind=[]
content=df['Content'].values.tolist()
author=df['Author'].values.tolist()
likes=df['Likes'].values.tolist()
comments=df['Comments'].values.tolist()

recc_author=[]
recc_likes=[]
recc_comments=[]
recc_content=[]
tg=df['Tags'].values.tolist()
count=0
for i in tg:
    for inp in input_tags:
        if inp in i:
            print(i)
            recc_content.append(content[count])
            recc_author.append(author[count])
            recc_likes.append(likes[count])
            recc_comments.append(comments[count])
    count+=1
score=[]

for i in range(len(recc_comments)):
    sm=recc_comments[i]+recc_likes[i]
    div=max(recc_comments)+max(recc_likes)    
    score.append(sm/div)
  
recc_dict={"Content":recc_content,"Author":recc_author,"Score":score}
recc_df=pd.DataFrame(recc_dict)
print(recc_df)
recc_df.sort_values(by='Score',inplace=True,ascending=False)
recc_df.to_csv("newrecc.csv")
"""""
vect=CountVectorizer(stop_words='english')
vect_matrix=vect.fit_transform(df['Tags'])
cos_sim=cosine_similarity(vect_matrix,vect_matrix)

rc=recommendations("LiverpoolFC", df, cos_sim, 10)
print(rc)
"""""
#filter_df=df.loc[df['Tags'].isin(input_tags)] 

#comments=filter_df['Comments'].values.tolist()
#Likes=filter_df['Likes'].values.tolist()
#downvotes=filter_df['Down_Votes'].values.tolist()
"""""

"""""

"""""
filter_df['Content_Score']=score    
filter_df.sort_values(by='Content_Score',inplace=True,ascending=False)
filter_df.to_csv("FilterTrial.csv")
"""""