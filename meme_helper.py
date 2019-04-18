import random
import praw
import os

reddit = praw.Reddit(client_id=os.environ['ID'],
                     client_secret=os.environ['SECRET'],
                     user_agent='Henry by Greatle')
checkWords = ['jpg', 'png', 'jpeg']

def get_memes(sub):
    return [(submission.title, submission.url, submission.author.name) for submission in reddit.subreddit(sub).top(limit=25) if any(string in submission.url for string in checkWords)]

def get_meme(sub='HistoryMemes'):
    memes = get_memes(sub)
    return memes[random.randint(0, len(memes) - 1)] if len(memes) > 0 else None

# print(get_meme())
