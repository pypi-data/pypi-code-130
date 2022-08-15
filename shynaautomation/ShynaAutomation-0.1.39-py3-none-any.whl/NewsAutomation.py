from Shynatime import ShTime
from ShynaProcess import ShynaNews, ShynaWordnet
from ShynaDatabase import Shdatabase
import mysql.connector
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer


class ShynaNewsAutomation:
    s_time = ShTime.ClassTime()
    s_news = ShynaNews.ShynaNews()
    s_data = Shdatabase.ShynaDatabase()
    s_word = ShynaWordnet.ShynaWordnet()
    database_user = os.environ.get('user')
    host = os.environ.get('host')
    passwd = os.environ.get('passwd')
    stop_words = set(stopwords.words('english'))
    custom_ignore_keyword_list = ['the', 'how', 'call', 'high', 'says', 'why', 'study', 'full', 'team', 'check',
                                  'women', 'players', 'top', 'may', 'key', 'govt', 'new', 'year', 'list', 'man',
                                  'live', 'yrs', 'that', 'hrs', 'could', 'weeks', 'th']

    def get_news(self):
        try:
            self.s_data.default_database = os.environ.get('status_db')
            self.s_data.query = "Select task_date,task_time from last_run_check where process_name='news_details'"
            last_run_datetime = self.s_data.select_from_table()
            self.s_data.default_database = os.environ.get('news_db')
            self.s_data.query = "SELECT news_urls, host_name, category from news_url"
            result = self.s_data.select_from_table()
            for item in result:
                self.s_news.url = item[0]
                if str(item[1]).lower().__eq__('indiatimes'):
                    print("Getting News from India Times Server from ", item[2], " category")
                    for key, value in self.s_news.get_news_toi().items():
                        if self.s_time.string_to_date(last_run_datetime[0][0]) <= self.s_time.string_to_date(
                                str(value[2])):
                            if self.s_time.string_to_time(last_run_datetime[0][1]) <= self.s_time.string_to_time(
                                    str(value[3])):
                                print(self.s_time.string_to_time(last_run_datetime[0][1]),
                                      self.s_time.string_to_time(str(value[3])))
                                self.insert_news_in_database(news_title=str(key), news_summary=str(value[0]),
                                                             news_link=str(value[1]), news_date=value[2],
                                                             news_time=value[3],
                                                             publish_date_time=str(value[2]) + " " + str(value[3]),
                                                             categories=str(item[2]))
                else:
                    print("Getting News from Zee News Server from ", item[2], " category")
                    for key, value in self.s_news.get_news_zee().items():
                        if self.s_time.string_to_date(last_run_datetime[0][0]) <= self.s_time.string_to_date(
                                str(value[2])) and self.s_time.string_to_time(last_run_datetime[0][1]) <= \
                                self.s_time.string_to_time(str(value[3])):
                            # print(self.s_time.string_to_time(last_run_datetime[0][1]),self.s_time.string_to_time(str(value[3])))
                            self.insert_news_in_database(news_title=str(key), news_summary=str(value[0]),
                                                         news_link=str(value[1]), news_date=value[2],
                                                         news_time=value[3],
                                                         publish_date_time=str(value[2]) + " " + str(value[3]),
                                                         categories=str(item[2]))
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name='get_news')

    def insert_news_in_database(self, news_title, news_summary, news_link, news_date, news_time, publish_date_time,
                                categories):
        mydb = mysql.connector.connect(
            host=self.host,
            user=self.database_user,
            passwd=self.passwd,
            database=str(os.environ.get('news_db'))
        )
        try:
            print("Entering insert_news_in_database")
            my_cursor = mydb.cursor()
            my_cursor.execute("INSERT INTO news_alert (news_title, news_description, news_time, news_date, news_link, "
                              "task_date, task_time, publish_date_time, categories) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s )", (str(news_title), str(news_summary),
                                                                               str(news_time), str(news_date),
                                                                               str(news_link),
                                                                               str(self.s_time.now_date),
                                                                               str(self.s_time.now_time),
                                                                               str(publish_date_time),
                                                                               str(categories)))
            mydb.commit()
        except Exception as e:
            print(e)
        finally:
            mydb.close()
            self.s_data.set_date_system(process_name="news_details")

    def update_news_keyword(self):
        print("checking keyword")
        title_word = []
        count_tokens = {}
        count_token = []
        keyword_count = {}
        count_tok = []
        count_list = []
        tokenizer = RegexpTokenizer(r'\w+')
        try:
            self.s_data.default_database = os.environ.get('news_db')
            self.s_data.query = "Select count, news_title from news_alert where keyword_process <> 'True'"
            title_count = self.s_data.select_from_table()
            if str(title_count[0]).lower().__eq__('empty'):
                pass
            else:
                for item in title_count:
                    count_list.append(item[0])
                    word_tokens = tokenizer.tokenize(str(item[1]).lower())
                    title_word.extend([w for w in word_tokens if not w in self.stop_words and w.isalpha()])
                for item in title_word:
                    count_tokens.update({item: title_word.count(item)})
                self.s_data.query = "Select news_keyword, repeat_count from news_keyword"
                result = self.s_data.select_from_table()
                for item in result:
                    keyword_count.update({item[0]: item[1]})
                for key, val in count_tokens.items():
                    if val > 2 and key in keyword_count.keys():
                        count_tokens.update({key: val + keyword_count.get(key)})
                for key, val in list(count_tokens.items()):
                    if val < 3 or len(str(key)) < 2:
                        del count_tokens[key]
                for key, val in count_tokens.items():
                    for item in title_count:
                        if key in str(item[1]).lower():
                            count_token.append(item[0])
                        count_tok.append((key, count_token))
                    count_token = []
                title_count = []
                for item in count_tok:
                    if item not in title_count:
                        title_count.append(item)
                        # title_count.append((item[0], str(item[1]).replace('[', '').replace(']', ''), len(list(item[1]))))
                for item in title_count:
                    if item[0] not in self.custom_ignore_keyword_list:
                        print(item[0], str(item[1]).replace('[', '').replace(']', ''), len(list(item[1])))
                        self.s_data.query = "INSERT INTO news_keyword (news_keyword,repeat_count,task_date, task_time," \
                                            " news_key) VALUES('" + str(item[0]) + "','" + str(len(list(item[1]))) + "','" \
                                            + str(self.s_time.now_date) + "','" + str(self.s_time.now_time) + \
                                            "','" + str(item[1]).replace('[', '').replace(']', '') +\
                                            "') ON DUPLICATE KEY UPDATE repeat_count='" + str(len(list(item[1]))) + \
                                            "', task_date='" + str(self.s_time.now_date) + "', task_time='" \
                                            + str(self.s_time.now_time) + "', news_key='" \
                                            + str(item[1]).replace('[', '').replace(']', '') + "'"
                        print(self.s_data.query)
                        self.s_data.create_insert_update_or_delete()
                else:
                    pass
                counts = str(count_list).replace('[', '(').replace(']', ')')
                self.s_data.query = "Update news_alert set keyword_process = 'True' where count in " + str(counts)
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)
        finally:
            print("done")
            self.s_data.set_date_system(process_name="news_keyword_details")


if __name__ == "__main__":
    ShynaNewsAutomation().get_news()
    ShynaNewsAutomation().update_news_keyword()
