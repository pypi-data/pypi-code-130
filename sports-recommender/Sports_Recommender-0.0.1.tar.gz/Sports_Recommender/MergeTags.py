import pandas as pd

df=pd.read_csv("CombinedContentTrial.csv")

df_tags=pd.read_csv("TagsSpacy.csv")
df_tags=df_tags.rename(columns={'Unnamed: 0':'id'})
tags=df_tags['Tags'].values.tolist()
print(df_tags.columns)

df['id']=df.index.values.tolist()
print(df['id'])
df_outer=df.merge(df_tags, on='id',how="outer")
df_outer["Tags"] = (df_outer["Author"] +","+df_outer["Tags"]).astype("str")
tg=df_outer['Tags'].values.tolist()
for i in range(len(tg)):
    if(tg[i]=="nan"):
        if(df_outer['Author'].values.tolist()[i]=="Gunners"):
            tg[i]="Arsenal"
        else:
            tg[i]=df_outer['Author'].values.tolist()[i]
df_outer['Tags']=tg
df_outer.to_csv("MergedDf.csv")