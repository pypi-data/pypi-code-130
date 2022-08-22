from WallStreetSocial import database
from pmaw import PushshiftAPI
import datetime as dt
import pandas as pd
import os


class TickerBits(object):
    def __int__(self, symbol='', start_date='', end_date='',
                positive_vectors=None, negative_vectors=None, cc_vectors=None,
                daily_bars=None, weekly_bars=None, total_bars=None):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

        self.positive_vectors = positive_vectors
        self.negative_vectors = negative_vectors
        self.cc_vectors = cc_vectors

        self.daily_bars = daily_bars
        self.weekly_bars = weekly_bars
        self.total_bars = total_bars


class SummariseBase(TickerBits):
    def __str__(self):
        to_join = list()
        to_join.append('Symbol: {}'.format(self.symbol))
        to_join.append('Start Date: {}'.format(self.start_date))
        to_join.append('End Date: {}'.format(self.end_date))

        to_join.append('--------------------------------')

        to_join.append('Positive Related Vectors: {}'.format(self.positive_vectors))
        to_join.append('Negative Related Vectors: {}'.format(self.negative_vectors))
        to_join.append('Cross Contaminated Vectors: {}'.format(self.cc_vectors))

        to_join.append('--------------------------------')

        to_join.append('Total  : {}'.format(self.daily_bars))
        to_join.append('Daily : {}'.format(self.daily_bars))
        to_join.append('Weekly : {}'.format(self.weekly_bars))

        return '\n'.join(to_join)


def validate_model(path):
    if database.model_loc == '':
        exit("model has no location")
    elif not os.path.isdir(path):
        exit("could not find path")
    else:
        database.model_loc = path
    print("Model Found!")
    return database.model_loc


def summarise_symbol(symbol, period):
    db = database.DatabasePipe()
    base = SummariseBase()

    tc_query = f"""
                    SELECT count(*) FROM Comment c, Ticker t 
                    WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id 
                    GROUP BY strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch'))
                """
    total_count = [x for sublist in db.cursor.execute(tc_query).fetchall() for x in sublist]

    pc_query = f"""
                    SELECT count(*) FROM Comment c, Ticker t 
                    WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id AND t.TickerSentiment BETWEEN 0.0001 AND 1 
                    GROUP BY strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch'))
                """
    pos_count = [x for sublist in db.cursor.execute(pc_query).fetchall() for x in sublist]

    nc_query = f"""
                    SELECT count(*) FROM Comment c, Ticker t 
                    WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id AND t.TickerSentiment BETWEEN -1 AND -0.0001 
                    GROUP BY strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch'))
                """
    neg_count = [x for sublist in db.cursor.execute(nc_query).fetchall() for x in sublist]

    ps_query = f"""
                        SELECT AVG(TickerSentiment)  FROM Comment c, Ticker t 
                        WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id AND t.TickerSentiment BETWEEN 0.0001 AND 1 
                        GROUP BY strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch'))
                    """
    pos_sent_count = [x for sublist in db.cursor.execute(ps_query).fetchall() for x in sublist]

    ns_query = f"""
                        SELECT AVG(TickerSentiment)  FROM Comment c, Ticker t 
                        WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id AND t.TickerSentiment BETWEEN -1 AND -0.0001 
                        GROUP BY strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch'))
                    """
    neg_sent_count = [x for sublist in db.cursor.execute(ns_query).fetchall() for x in sublist]

    sentiment_query = f"""
                            SELECT AVG(TickerSentiment)  FROM Comment c, Ticker t 
                            WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id 
                            GROUP BY strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch'))
                        """
    sentiment = [x for sublist in db.cursor.execute(sentiment_query).fetchall() for x in sublist]

    neut_count = f"""
                SELECT count(*) FROM Comment c, Ticker t 
                WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id AND t.TickerSentiment = 0
                GROUP BY strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch'))
            """
    natural_count = [x for sublist in db.cursor.execute(neut_count).fetchall() for x in sublist]

    all_counts = list(zip(total_count, pos_count, neg_count, natural_count, pos_sent_count, neg_sent_count, sentiment))
    print(all_counts)

    return base


def has_symbol(symbol):
    db = database.DatabasePipe()
    symbol_query = f"""SELECT DISTINCT(TickerSymbol) FROM ticker WHERE TickerSymbol = "{symbol}" """
    symbols = db.cursor.execute(symbol_query).fetchall()

    if symbols is None or len(symbols) == 0:
        return False

    else:
        return True


def unique_symbols():
    db = database.DatabasePipe()
    symbol_query = """SELECT DISTINCT(TickerSymbol) FROM ticker"""
    symbols = db.cursor.execute(symbol_query).fetchall()
    return [x for sublist in symbols for x in sublist]


def convert_date(date):
    """
    Description:
        converts a date/datetime to a unix timestamp so that Pushshift can understand it
    Parameters:
        date (str): takes a date-time, example 'YEAR-MONTH-DAY HOUR:MINUTE:SECOND'
    Returns:
        Returns a unix timestamp
    """

    datetime = str(date).split(" ")
    if len(datetime) == 1:
        datetime = datetime[0] + " 00:00:00"
    else:
        datetime = date

    return int(dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M:%S').timestamp())


def log_submissions(df):
    """
    Description:
        Converts a dataframe to CSV which is saved for logging/debugging purposes.
            Which can be found in /dependencies/logs
    Parameters:
        df (dataframe): takes a date-time, example 'YEAR-MONTH-DAY HOUR:MINUTE:SECOND'
    Returns:
        Returns a unix timestamp
    """
    dir_name = os.path.dirname(os.getcwd())
    folder = 'temp'
    file_name = 'wsb_comments_' + dt.datetime.now().strftime("%Y_%m_%d_%I_%M")
    path = f"{dir_name}\{folder}\{file_name}.csv"
    df.to_csv(path, encoding='utf-8-sig', index=False)
    return path


def run(subreddits, start, end):
    start = convert_date(start)
    end = convert_date(end)
    api = PushshiftAPI(shards_down_behavior="None")
    db = database.DatabasePipe()
    db.create_database()
    db.ticker_generation()
    print("fetching posts in the data range")
    posts = api.search_submissions(subreddit=subreddits, before=end, after=start)
    posts_df = pd.DataFrame(posts.responses)
    posts_df = posts_df.filter(["author", "subreddit", "url", "title", "created_utc", "score"])
    db.insert_into_row("post", posts_df)

    print("fetching comments in the data range")
    comments = api.search_comments(subreddit=subreddits, before=end, after=start)
    comment_df = pd.DataFrame(comments.responses)
    comment_df = comment_df.filter(["permalink", "subreddit", "author", "body", "score", "created_utc"])
    db.insert_into_row("comment", comment_df)
