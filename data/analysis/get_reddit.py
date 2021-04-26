import json
import praw
import requests
import pandas as pd
import re
# !pip install pymysql
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import time, datetime

from reddit_secret import CLIENT_ID, SECRET_KEY, username, password

SUB_CACHE = "submission_cache.json"
COMMENT_CACHE = "comment_cache.json"


def save_submission_database(table_name, submission_lyst):
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    print('Opened database successfully')
    for row in submission_lyst:
        sql = 'INSERT INTO %s(SUBID,URL,TITLE,SUBREDDIT,SCORE,SELFTEXT,NUMCOMMENTS, CREATE_TIME)\
            VALUES ("%s","%s","%s","%s",%d,"%s",%d,"%s")' % (table_name, row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
    db.close()


def select_submission_database(cache_lyst, limit):
    result = []
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    for i in range(len(cache_lyst)-1,len(cache_lyst)-1-limit, -1):
        sql = 'SELECT * FROM SUBMISSION WHERE SUBID="%s"' % (cache_lyst[i])
        cursor.execute(sql)
        result += cursor.fetchall()
    db.close()
    return result


def save_comment_database(table_name, comments):
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    print('Opened database successfully')
    for comment in comments:
        sql = 'INSERT INTO %s(SELFTEXT, SUBID)\
            VALUES ("%s","%s")' % (table_name, comment[0], comment[1])
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
    db.close()


def select_comment_database(subid, limit):
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    sql = 'SELECT * FROM COMMENT WHERE SUBID="%s" ORDER BY ID DESC LIMIT %d' % (subid, limit)
    cursor.execute(sql)
    result = list(cursor.fetchall())
    db.close()
    return result


def open_cache(file):
    try:
        cache_file = open(file, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, file):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(file, "w")
    fw.write(dumped_json_cache)
    fw.close()


def make_reddit_request():
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=SECRET_KEY, user_agent='MyAPI/0.0.1')
    return reddit


def get_subreddit_submissions(reddit, subreddit, limit):
    subreddit_record = open_cache("submission_cache.json")
    key = subreddit + "_" + str(datetime.date.today())
    if key in subreddit_record and limit <= len(subreddit_record[key]):
        print("using cache and select from database directly")
        return select_submission_database(subreddit_record[key], limit)
    else:
        print("not using cache")
        subreddit_object = reddit.subreddit(subreddit)
        submissions, temp_id_record = [], []
        for submit in subreddit_object.hot(limit=limit):
            subid = submit.id + "_" + str(datetime.date.today())
            # process submission time
            created_time = submit.created
            time_array = time.localtime(created_time)
            reddit_date_string = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            reddit_date = datetime.datetime.strptime(reddit_date_string, "%Y-%m-%d %H:%M:%S")

            submissions.append([subid, submit.url, submit.title, str(submit.subreddit), submit.score,
                                submit.selftext, submit.num_comments, reddit_date_string])
            temp_id_record.append(subid)

        # cache subreddit and its submissions in the cache file
        subreddit_record.update({key: temp_id_record})
        save_cache(subreddit_record, "submission_cache.json")
        # save into the database
        save_submission_database('SUBMISSION', submissions)
    return submissions


def get_submission_comment(reddit, subid, limit):
    comment_record = open_cache("comment_cache.json")

    if subid in comment_record and limit <= comment_record[subid][0] and \
            comment_record[subid][1] == str(datetime.date.today()):
        print("using cache and select from database directly")
        return select_comment_database(subid, limit)
    else:
        print("not using cache")
        comments = []
        for i, top_level_comment in enumerate(reddit.submission(id=subid[:6]).comments):
            if i == limit:
                break
            comments.append([top_level_comment.body, subid])

        # cache subreddit and its submissions in the cache file
        comment_record.update({subid: [limit, str(datetime.date.today())]})
        save_cache(comment_record, "comment_cache.json")
        # save into the database
        save_comment_database('COMMENT', comments)
    return comments


if __name__ == '__main__':
    reddit = make_reddit_request()
    submission_info = get_subreddit_submissions(reddit, "coronavirus", 500)
    comment = get_submission_comment(reddit, 'ms1u63_2021-04-18', 10)
    set_comment_database()
    set_submission_database()