import pandas as pd


def seperate_list(Tags):
    Tg=[]
    
    for i in range(len(Tags)):
        st=""
        T=Tags[i]
        #print(T)
        for j in range(len(T)) :
            st=st+T[j]
            print(T[j])
        Tg.append(st)
    return Tg
#df_red=pd.read_csv("FilterTrial.csv")
df_red=pd.read_csv("reddit_consolidated.csv")
df_twit=pd.read_csv("twitter.csv")
print(df_red.columns)
print(df_twit.columns)

#df_red=df_red.drop('Unnamed: 0',axis=1)
df_twit=df_twit.drop('Unnamed: 0',axis=1)

Name=df_red['Name'].values.tolist()
Likes=df_red['Up_Votes'].values.tolist()
Comments=df_red['Comments'].values.tolist()
content=df_red['Title'].values.tolist()

user=df_twit['Username'].values.tolist()
twitter_likes=df_twit['Likes'].values.tolist()
replies=df_twit['Replies'].values.tolist()

#content.append(df_twit['Tweets'].values.tolist())
tweets=df_twit['Tweets'].values.tolist()
for i in range(len(tweets)):
    content.append(tweets[i])
    Likes.append(twitter_likes[i])
    Name.append(user[i])
    Comments.append(replies[i])


d={"Content":content,"Author":Name,"Likes":Likes,"Comments":Comments}
df=pd.DataFrame(d)
df.to_csv("CombinedContentTrial.csv")
