#!/usr/bin/env python
# coding: utf-8

# In[1]:


from smack_gsheets import Google_Sheet as gs
#from base_smack_gsheets.smack_gsheets.Google_Sheet import Get_Worksheet_List, Open_Gsheets,Open_Worksheet,Read_Gsheet
import pandas as pd


# In[9]:

sheets=gs.Open_Gsheets("Reddit_Data")
wrkslist=gs.Get_Worksheet_List(sheets)

# In[11]:


name=[]
tag=[]
title=[]
upvotes=[]
url=[]
m_url=[]
comments=[]
for i in range(len(wrkslist)):
    worksheet = sheets.get_worksheet(i)
    df=gs.Read_Gsheet(worksheet)
    n=df['Name'].values
    content=df['Title']
    t=df['Tags'].values
    uv=df['Up_Votes'].values
    murl=df['Media_URL']
    c=df['comments'].values
    u=df['url'].values
    for j in range(len(t)):
        name.append(n[j])
        title.append(content[j])
        tag.append(t[j])
        upvotes.append(uv[j])
        comments.append(c[j])
        m_url.append(murl[j])
        url.append(u[j])
# In[12]:
reddit_dict={"Name":name,"Title":title,"Tags":tag,"Up_Votes":upvotes,"Comments":comments,"Media_Url":m_url,"URL":url}

# In[13]:
red_df=pd.DataFrame(reddit_dict)

# In[16]:
red_df=red_df.dropna()
# In[17]:
red_df.to_csv("reddit_consolidated.csv")
# In[ ]:




