def import_necessary_packages():
    import pandas as pd
    import twint
    import nest_asyncio
    import time
    import os
    nest_asyncio.apply()

def get_tweets(twitter_handle_list, start_dates, end_dates, branch, sortation = 'party', limit = 1000):
    import_necessary_packages()
         # Iterate through politician list, runs 50 searches per value, keeping the largest set (due to the random collection of past tweets)
    c = twint.Config()
    for x in twitter_handle_list.iterrows():
        print(x[1]['twitter_handle'])
        c.Username = x[1]['twitter_handle']
        df = pd.DataFrame
        tweets_df = pd.DataFrame(columns = ['id', 'conversation_id', 'created_at', 'date', 'timezone', 'place',
                                        'tweet', 'language', 'hashtags', 'cashtags', 'user_id', 'user_id_str',
                                        'username', 'name', 'day', 'hour', 'link', 'urls', 'photos', 'video',
                                        'thumbnail', 'retweet', 'nlikes', 'nreplies', 'nretweets', 'quote_url',
                                        'search', 'near', 'geo', 'source', 'user_rt_id', 'user_rt',
                                        'retweet_id', 'reply_to', 'retweet_date', 'translate', 'trans_src',
                                        'trans_dest', 'party'])
        vals1 = start_dates
        vals2 = end_dates
        for i in range(4):
            counter = 0
            val1 = vals1[i]
            val2 = vals2[i]
            c.Limit = limit
            c.Since = val1
            c.Until = val2
            c.Pandas = True
            c.Hide_output = True
            for i in range(10):
                try:
                    twint.run.Search(c)
                    df1 = twint.storage.panda.Tweets_df
                    df1[sortation] = x[1][sortation]
                    if counter == 0:
                        df = twint.storage.panda.Tweets_df
                        print(df.shape)
                    else:
                        if df1.shape[0] > df.shape[0]:
                            df = twint.storage.panda.Tweets_df
                            print(df.shape)
                        else:
                            pass
                    counter += 1
                except:
                    time.sleep(100)
                    pass

            print(df.shape)
            tweets_df = pd.concat([tweets_df, df], axis = 0)
        tweets_df.to_csv(str(branch) + '_scraped_tweets_'+x[1]['twitter_handle']+val1+'_'+val2+'.csv')
        print(str(branch) + '_scraped_tweets_'+x[1]['twitter_handle']+val1+'_'+val2+'.csv')

def combine_tweets(folder):
    import_necessary_packages()
    df = pd.DataFrame(columns = ['Unnamed: 0', 'id', 'conversation_id', 'created_at', 'date', 'timezone',
           'place', 'tweet', 'language', 'hashtags', 'cashtags', 'user_id',
           'user_id_str', 'username', 'name', 'day', 'hour', 'link', 'urls',
           'photos', 'video', 'thumbnail', 'retweet', 'nlikes', 'nreplies',
           'nretweets', 'quote_url', 'search', 'near', 'geo', 'source',
           'user_rt_id', 'user_rt', 'retweet_id', 'reply_to', 'retweet_date',
           'translate', 'trans_src', 'trans_dest', 'party'])

    for x in os.listdir(folder + '/'):
            text = pd.read_csv(folder + '/' + x)
            df = pd.concat([df, text], axis = 0)
            #df = df.append(text)
            print(x + ' appended to dataframe')

    df.to_csv(folder + '/all_' + '_raw.csv')
    print(folder + '/all_' + '_raw.csv generated with all tweets')

def handle_import():
    gov = pd.read_csv('us-governors.csv')
    house = pd.read_csv('us-house.csv')
    senators = pd.read_csv('us-senate.csv')

    gov_party_handles = gov[['party','twitter_handle']]
    gov_party_handles_normalized = gov_party_handles.replace(['republican', 'democrat', 'independent'], [0, 1, 2])
    gov_gender_handles = gov[['gender', 'twitter_handle']]
    gov_gender_handles_normalized = gov_gender_handles.replace(['male', 'female'], [0, 1])

    house_party_handles = house[['party','twitter_handle']]
    house_party_handles_normalized = house_party_handles.replace(['republican', 'democrat', 'independent'], [0, 1, 2])
    house_gender_handles = house[['gender', 'twitter_handle']]
    house_gender_handles_normalized = house_gender_handles.replace(['male', 'female'], [0, 1])

    senate_party_handles = senators[['party','twitter_handle']]
    senate_party_handles_normalized = senate_party_handles.replace(['republican', 'democrat', 'independent'], [0, 1, 2])
    senate_gender_handles = senators[['gender', 'twitter_handle']]
    senate_gender_handles_normalized = senate_gender_handles.replace(['male', 'female'], [0, 1])
