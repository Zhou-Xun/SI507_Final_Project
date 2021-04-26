import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb


def set_twitter_database():
    db = MySQLdb.connect(host="localhost", user="root", passwd="shepherd", db="SI507Final")
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE TWITTER
           (
            ID INT NOT NULL auto_increment,
            VALUE     TEXT    NOT NULL,
            TAG       TEXT    NOT NULL,
            TWITTERTEXT      TEXT    NOT NULL,
            PRIMARY KEY(ID)
            );''')
    db.close()


def set_submission_database():
    db = MySQLdb.connect(host="localhost", user="root", passwd="shepherd", db="SI507Final")
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE SUBMISSION
           (
            SUBID         VARCHAR(30)    NOT NULL,
            URL           TEXT    NOT NULL,
            TITLE         TEXT    NOT NULL,
            SUBREDDIT     TEXT    NOT NULL,
            SCORE         INT             ,    
            SELFTEXT      TEXT            ,
            NUMCOMMENTS   INT     NOT NULL,
            CREATE_TIME   DATETIME,
            PRIMARY KEY(SUBID)
            );''')
    db.close()


def set_comment_database():
    db = MySQLdb.connect(host="localhost", user="root", passwd="shepherd", db="SI507Final")
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE COMMENT
           (
            ID INT NOT NULL auto_increment,
            SELFTEXT      TEXT    NOT NULL,
            SUBID         TEXT REFERENCES SUBMISSION(SUBID),
            PRIMARY KEY(ID)
            );''')
    db.close()


def set_score():
    db = MySQLdb.connect(host="localhost", user="root", passwd="shepherd", db="SI507Final")
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE SCORE
           (
            ID INT NOT NULL auto_increment,
            SUBREDDIT     TEXT    NOT NULL,
            SCORE         FLOAT   NOT NULL,    
            CREATE_TIME   DATETIME,
            PRIMARY KEY(ID)
            );''')
    db.close()


if __name__ == '__main__':
    set_twitter_database()
    set_submission_database()
    set_comment_database()
    set_score()


