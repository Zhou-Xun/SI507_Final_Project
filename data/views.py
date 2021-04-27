from django.views import View
from django.shortcuts import render, redirect
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = BASE_DIR
sys.path.append(os.path.join(ROOT_DIR, 'analysis'))
import get_reddit
import get_twitter
import process_reddit
import pandas as pd


class HomeView(View):
    def get(self, request):
        reddit = get_reddit.make_reddit_request()
        submission = get_reddit.get_subreddit_submissions(reddit, "news", 100)
        submission_df = pd.DataFrame(submission,
                                     columns=['SUBID', 'URL', 'TITLE', 'SUBREDDIT', 'SCORE', 'SELFTEXT', 'NUMCOUNTS',
                                              'CREATE_TIME'])
        src_reddit = process_reddit.word_cloud(submission_df, 'TITLE', "reddit word cloud: news")
        twitter = get_twitter.get_twitter("news lang:en - is: retweet", "#world news", 100)
        twitter_df = pd.DataFrame(twitter, columns=["content"])
        src_twitter = process_reddit.word_cloud(twitter_df, 'content', "twitter word cloud: world news")
        return render(request, 'data/main.html', {"src_reddit": src_reddit, "src_twitter": src_twitter})


class RedditListView(View):
    def get(self, request):
        reddit = get_reddit.make_reddit_request()
        submission = get_reddit.get_subreddit_submissions(reddit, "coronavirus", 100)
        submission_df = pd.DataFrame(submission,
                                     columns=['SUBID', 'URL', 'TITLE', 'SUBREDDIT', 'SCORE', 'SELFTEXT', 'NUMCOUNTS',
                                              'CREATE_TIME'])
        src = process_reddit.auto()
        cntx = {
            'src': src,
        }
        print(src)
        return render(request, 'data/reddit.html', cntx)

    def post(self,request):
        subreddit = request.POST.get("subreddit")
        date1 = request.POST.get("datepicker")
        date2 = request.POST.get("datepicker2")
        order = request.POST.get("order")
        limit = request.POST.get("limit")
        submission_time = date1+","+date2
        reddit_list = process_reddit.select_submission(subreddit, submission_time, order, limit)
        reddit_list = [(x[0],x[2]) for x in reddit_list]
        cntx = {
            "reddit_list": reddit_list,
        }
        return render(request, 'data/reddit.html', cntx)


class RedditCommentView(View):
    def get(self, request, subid):
        return render(request, 'data/reddit_comment.html', {"subid": subid})

    def post(self, request, subid):
        reddit = get_reddit.make_reddit_request()
        limit = int(request.POST.get("limit"))
        comments = get_reddit.get_submission_comment(reddit, subid, limit)
        comments_list = [x[1] for x in comments]
        cntx = {
            'comments_list': comments_list,
            'subid': subid,
        }
        return render(request, 'data/reddit_comment.html', cntx)


class TwitterListView(View):
    def get(self, request):
        return render(request, 'data/twitter.html')

    def post(self,request):
        value = request.POST.get("value")
        tag = request.POST.get("tag")
        limit = int(request.POST.get("limit"))
        print((value,tag,limit))
        twitter_list = get_twitter.get_twitter(value, tag, limit)
        print(twitter_list)
        return render(request, 'data/twitter.html', {'twitter_list': twitter_list})
