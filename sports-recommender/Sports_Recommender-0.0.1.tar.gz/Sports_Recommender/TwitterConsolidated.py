#!/usr/bin/env python
# coding: utf-8

# In[20]:


from smack_gsheets import Google_Sheet as gs
import pandas as pd

sheets=gs.Open_Gsheets("Athletic_Tweets")
wrkslist=gs.Get_Worksheet_List(sheets)


tweet=[]
hashtag=[]
nlikes=[]
nreplies=[]
nretweets=[]
username=[]
link=[]
for i in range(len(wrkslist)):
    worksheet = sheets.get_worksheet(i)
    df=gs.Read_Gsheet(worksheet)
    t=df['tweet'].values
    h=df['hashtags'].values
    nl=df['nlikes'].values
    nrp=df['nreplies'].values
    nre=df['nretweets'].values
    u=df['username'].values
    l=df['link'].values
    for j in range(len(t)):
        tweet.append(t[j])
        hashtag.append(h[j])
        nlikes.append(nl[j])
        nreplies.append(nrp[j])
        nretweets.append(nre[j])
        username.append(u[j])
        link.append(l[j])


tweet_dict={"Tweets":tweet,"Hashtag":hashtag,"Likes":nlikes,"Replies":nreplies,"Retweets":nretweets,"Username":username,"Link":link}


# In[25]:
data=pd.DataFrame(tweet_dict)

data=data.dropna()

# In[31]:

data.to_csv("twitter.csv")

# In[19]:

# In[ ]:




