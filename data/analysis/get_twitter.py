import json
import praw
import requests
import pandas as pd
import datetime
import re
import requests
from time import sleep
import os
import twitter_secret as secrets # file that contains my OAuth credentials
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET
CACHE_FILE = "twitter_cache.json"

stream_url = "https://api.twitter.com/2/tweets/search/stream"
rules_url = "https://api.twitter.com/2/tweets/search/stream/rules"


def get_bearer_token():
    response = requests.post("https://api.twitter.com/oauth2/token",
                             auth=(client_key, client_secret),
                             data={"grant_type": "client_credentials"})

    body = response.json()
    return body['access_token']


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def save_twitter_database(table_name, twitter_lyst, value, tag):
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    print('Opened database successfully')
    for row in twitter_lyst:
        sql = 'INSERT INTO %s(VALUE, TAG, TWITTERTEXT)\
            VALUES ("%s","%s","%s")' % (table_name, value, tag, row)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
    db.close()


def select_twitter_database(value, tag, limit):
    result = []
    db = MySQLdb.connect(host="localhost",user="root",passwd="shepherd",db="SI507Final" )
    cursor = db.cursor()
    sql = 'SELECT * FROM TWITTER WHERE VALUE="%s" AND TAG="%s" ORDER BY id DESC LIMIT %d' % (value, tag, limit)
    cursor.execute(sql)
    result += cursor.fetchall()
    db.close()
    return [res[3] for res in result]


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


def get_rules(headers, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(headers, delete, bearer_token, value, tag):
    rules = [{ 'value': value, 'tag': tag}]
    payload = {"add": rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(headers, twitter_set, bearer_token, limit, value, tag):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    count, res = 0, []
    for response_line in response.iter_lines():
        count += 1
        if count > limit:
            break
        if response_line:
            json_response = json.loads(response_line)
#             print(json.dumps(json_response, indent=4, sort_keys=True))
            res.append(json_response['data']['text'])
    # save into the database
    save_twitter_database('TWITTER', res, value, tag)
    return res


def get_twitter(value, tag, limit):
    twitter_cache = open_cache(CACHE_FILE)
    print("-----------")
    print((value,tag))
    key = value + "_" + tag
    print(key)
    if key in twitter_cache:
        cache_limit = twitter_cache[key][0]
        cache_date = twitter_cache[key][1]
        cache_date = datetime.datetime.strptime(cache_date, '%Y-%m-%d').date()
        if cache_limit >= limit and cache_date == datetime.date.today():
            print("using cache and select from database directly")
            return select_twitter_database(value, tag, limit)

    print("not using cache")
    bearer_token = get_bearer_token()
    headers = create_headers(bearer_token)
    rules = get_rules(headers, bearer_token)
    delete = delete_all_rules(headers, bearer_token, rules)
    twitter_set = set_rules(headers, delete, bearer_token, value, tag)
    # save into twitter cache
    twitter_cache.update({key: [limit, str(datetime.date.today())]})
    save_cache(twitter_cache, CACHE_FILE)
    # save into the database
    print("yes")
    return get_stream(headers, twitter_set, bearer_token, limit, value, tag)


if __name__ == '__main__':
    limit, value, tag = 50, 'context:123.1220701888179359745  lang:en -is', 'covid-19'
    res = get_twitter(value, tag, limit)
    print(res)
