import random
import praw
import os

reddit = praw.Reddit(client_id=os.environ['ID'],
                     client_secret=os.environ['SECRET'],
                     user_agent='Henry by Greatle')
checkWords = ['i.imgur.com', 'jpg', 'png', 'jpeg']

def get_memes(sub):
    return [(submission.title, submission.url) for submission in reddit.subreddit(sub).hot(limit=25) if any(string in submission.url for string in checkWords)]

def get_meme(sub='HistoryMemes'):
    memes = get_memes(sub)
    return memes[random.randint(0, len(memes) - 1)]

print(get_meme())