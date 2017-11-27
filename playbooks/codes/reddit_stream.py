import datetime
import pymongo, praw

def format_time(utc_timestamp):
    return datetime.datetime.fromtimestamp(
        int(utc_timestamp)
    ).strftime('%Y-%m-%dT%H:%M:%S')

def reddit_filter(data):
    essentials = {
        "text": data.body,
        "created_at": format_time(data.created_utc),
        "score": data.score,
        "sentiment": data.controversiality,
        "keywords": []
    }
    return essentials

def reddit_stream():
    reddit = praw.Reddit(client_id='yi_ETjv7GOXrag',
                         client_secret='0dRBM-34_PRv5qPCfB_TVmqIk5g',
                         user_agent='android:com.example.myredditapp:v1.2.3')

    subreddits = ['blackfriday', 'cybermonday', 'deals', 'dealsreddit']

    for sub in subreddits:
        for comment in reddit.subreddit(sub).comments(limit=999999999999999):
            reddit_json = reddit_filter(comment)
            db.common_all.insert_one(reddit_json)
            #db.common_latest.insert_one(reddit_json)
            print("all",db.common_all.count())
            #print("latest",db.common_latest.count())

if __name__ == '__main__':
    client_mongo = pymongo.MongoClient('localhost')
    db = client_mongo['dicdatabase']
    reddit_stream()
