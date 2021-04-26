from datetime import datetime

import matplotlib

import get_reddit
import get_twitter
from wordcloud import WordCloud
from spacy.lang.en.stop_words import STOP_WORDS
import re
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import spacy
# nltk.download('vader_lexicon')
nlp = spacy.load('en_core_web_sm')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from spacy.tokens import Doc
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import base64
from io import BytesIO



def remove_punctuations(sent, df, col):
    temp = ""
    for i in range(len(df)):
        temp += df.loc[i,col].lower()
        temp = re.sub("(’m)"," am", temp)
        temp = re.sub("(won’t)","well not", temp)
        temp = re.sub("(n’t)"," not", temp)
        temp = re.sub("(’s)"," is", temp)
        temp = re.sub(r'[^\w\s]', ' ', temp)
    return sent + temp


def remove_stop_words(string):
    lyst = string.split()
    for i in range(len(lyst)-1,-1,-1):
        if lyst[i] in STOP_WORDS or lyst[i]=="https" or len(lyst[i])==1 or lyst[i] in "news":
            lyst.pop(i)
    return lyst


def word_cloud(df, column, title):
    cloud = remove_stop_words(remove_punctuations("", df, column))
    f, ax1 = plt.subplots(1, 1, figsize=(12, 10))
    ax1.set_title("word cloud", fontdict={'weight': 'normal', 'size': 15})
    wordCloud = WordCloud(max_words=1000, margin=10, random_state=1).generate(" ".join(cloud))
    ax1.imshow(wordCloud)
    ax1.axis("off")
    # plt.show()
    plt.title(title)
    sio = BytesIO()
    plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    plt.close()
    return src


def sentiment_scores(docx):
    sent_analyzer = SentimentIntensityAnalyzer()
    return sent_analyzer.polarity_scores(docx.text)


def get_score(df):
    today = str(datetime.date.today())
    subreddit_name = df.loc[0,'SUBREDDIT']
    key = today+"_"+subreddit_name
    score_record = get_reddit.open_cache("score_record.json")
    if key in score_record:
        print("using cache")
        query = 'SELECT SCORE FROM SCORE WHERE SUBREDDIT = "%s" AND CREATE_TIME = "%s" ORDER BY ID DESC LIMIT 1 ' % \
                (subreddit_name, today)
        db = MySQLdb.connect(host="localhost", user="root", passwd="shepherd", db="SI507Final")
        cursor = db.cursor()
        cursor.execute(query)
        result = list(cursor.fetchall())
        db.close()
        return result
    else:
        Doc.set_extension("sentimenter", getter=sentiment_scores, force=True)
        score = df['TITLE'].apply(lambda x: nlp(x)._.sentimenter['compound']).mean()
        save_score(subreddit_name, score, today)
        score_record.update({key: score})
        get_reddit.save_cache(score_record, "score_record.json")
        return score


def save_score(subreddit, score, score_time):
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    print('Opened database successfully')
    sql = 'INSERT INTO %s (SUBREDDIT,SCORE,CREATE_TIME)\
            VALUES ("%s",%f,"%s")' % ('SCORE', subreddit, score, score_time)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()


def select_submission(subreddit, submission_time, order, number_of_submissions):
    query = "SELECT * FROM SUBMISSION "
    where = 'WHERE SUBREDDIT = "%s" ' % (subreddit)
    if submission_time != "none":
        lyst = submission_time.split(",")
        if len(lyst) == 1:
            where += 'AND CREATE_TIME = "%s" ' % (lyst[0])
        else:
            where += 'AND CREATE_TIME BETWEEN "%s" AND "%s" ' % (lyst[0],lyst[1])
    order_by = 'ORDER BY %s DESC ' % (order)
    limit = 'LIMIT %d ' % (int(number_of_submissions))
    query += where+order_by+limit
    print(query)
    result = []
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    cursor.execute(query)
    result += cursor.fetchall()
    db.close()
    return result


def auto():
    lyst = ['wallstreetbets', 'coronavirus', 'news']
    reddit = get_reddit.make_reddit_request()
    results = []
    db = MySQLdb.connect(host="localhost", user="root", passwd="shepherd", db="SI507Final")
    for subreddit in lyst:
        print("----------")
        print(subreddit)
        submission = get_reddit.get_subreddit_submissions(reddit, subreddit, 100)
        submission_df = pd.DataFrame(submission, columns=['SUBID', 'URL', 'TITLE', 'SUBREDDIT', 'SCORE', \
                                                         'SELFTEXT', 'NUMCOUNTS', 'CREATE_TIME'])
        score = get_score(submission_df)
        query = 'SELECT CREATE_TIME, SCORE  FROM SCORE WHERE SUBREDDIT = "%s" ORDER BY CREATE_TIME' % \
                (subreddit)
        cursor = db.cursor()
        cursor.execute(query)
        result = list(cursor.fetchall())
        print(result)
        results.append(result)

    db.close()
    matplotlib.use('Agg')
    name = ['wallstreetbets', 'coronavirus', 'news']
    for i in range(len(results)):
        data = pd.DataFrame(results[i], columns=['date', 'score'])
        sns.lineplot(data=data, x='date', y='score', label=name[i])
    plt.xticks(rotation=30)
    plt.legend(loc='best')
    # plt.show()
    sio = BytesIO()
    plt.savefig(sio, format='png', bbox_inches='tight', pad_inches=0.0)
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    plt.close()
    return src


def plot(lyst):
    name = ['wallstreetbets', 'coronavirus', 'news']
    for i in range(len(lyst)):
        data = pd.DataFrame(lyst[i], columns=['date','score'])
        sns.lineplot(data=data, x='date', y='score', label=name[i])
    plt.xticks(rotation=30)
    plt.show()


if __name__ == "__main__":
    auto()
    choose = input("Enter 0 for get, 1 for select: ")
    if choose == "0":
        print("Get submissions ")
        while True:
            subreddit = input("input the subreddit name or exit: ")
            if subreddit == "exit":
                break
            limit = int(input("input the number of submissions: "))
            reddit = get_reddit.make_reddit_request()
            submission = get_reddit.get_subreddit_submissions(reddit, subreddit, limit)
            submission_df = pd.DataFrame(submission, columns=['SUBID', 'URL', 'TITLE', 'SUBREDDIT', 'SCORE', 'SELFTEXT', 'NUMCOUNTS', 'CREATE_TIME'])
            word_cloud(submission_df)
            print(get_score(submission_df))

    print("Select submissions ")
    while True:
        subreddit = input("Enter the subreddit name or exit: ")
        if subreddit == "exit":
            break
        submission_time = input("Enter the time range, which can be a certain day, a certain period of time or none, e.g. 2021-4-22 or 2021-4-22,2021-4-23 or none: ")
        order_by = input("Enter order, score, comment or none: ")
        order_by = "NUMCOMMENTS" if order_by == "comment" else order_by
        limit = input("Enter the number of submissions you want to return: ")
        # fields = input("Enter the field you want to select: ")
        select_reddit = select_submission(subreddit, submission_time, order_by, limit)
        print("Sentimental score for the title of submissions: ")
        submission_df = pd.DataFrame(select_reddit, columns=['SUBID', 'URL', 'TITLE', 'SUBREDDIT', 'SCORE', 'SELFTEXT', 'NUMCOUNTS', 'CREATE_TIME'])
        print(submission_df)
        print(get_score(submission_df))

