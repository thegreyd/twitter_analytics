import json, random, datetime
import tweepy, pymongo
import config, twitter_keywords
from afinn import Afinn
#import mongo2es
import subprocess

def format_time(utc_timestamp):
    return datetime.datetime.fromtimestamp(
        int(utc_timestamp)
    ).strftime('%Y-%m-%dT%H:%M:%S')

def twitter_filter(data):
    data = json.loads(data)
    essentials = {
        "text": data["text"], 
        "user" : {
            "followers_count": None,
            "name": None,
            "screen_name": None
        },
        "place" : {
            "country": None,
            "name": None,
            "full_name": None
        }
    }

    for e in essentials.keys():
        if e in data:
            if isinstance(essentials[e], dict):
                attrs = essentials[e].keys()
                for i in attrs:
                    if data[e] and (i in data[e]):
                        essentials[e][i] = data[e][i]
            else:
                essentials[e] = data[e]

    
    essentials["keywords"] = twitter_keywords.get_keywords(essentials['text']) + twitter_keywords.extract_hashtag(essentials['text'])
    essentials["created_at"] = format_time(int(data["timestamp_ms"])/1000), 
    essentials["score"] = int(essentials["user"]["followers_count"])*0.5,
    essentials["senti_val"] = afinn.score(essentials['text']),
    essentials["sentiment"] = fun(afinn.score(essentials['text'])),
    return essentials

def fun(avg_senti_val):
    try:
        if avg_senti_val < 0:
            return 'NEGATIVE'
        elif avg_senti_val == 0:
            return 'NEUTRAL'
        else:
            return 'POSITIVE'
    except TypeError:
        return 'NEUTRAL'

class TweeterStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

    def on_data(self, status):
        try:
            twitter_json = twitter_filter(status)
            db.twitter_all.insert_one(twitter_json)
            db.twitter_latest.insert_one(twitter_json)
            latest_count = db.twitter_latest.count()
            if latest_count == 1000:
                python2_command = "python3 mongo2es.py"
                process = subprocess.Popen(python2_command.split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
                print(output)
                
                db.twitter_latest.drop()
                print("twitter_latest erased")

            print("twitter_all", db.twitter_all.count())
            print("twitter_latest", latest_count)
        except Exception as e:
           print("Error:", e)
           return True
        return True

    def on_error(self, status_code):
        print("Error", status_code)
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream

if __name__ == '__main__':
    client_mongo = pymongo.MongoClient()
    db = client_mongo['dicdatabase']
    
    consumer_key = config.consumerKey
    consumer_secret = config.consumerSecret
    access_key = config.accessToken
    access_secret = config.accessTokenSecret

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    afinn = Afinn()
    stream = tweepy.Stream(auth, listener=TweeterStreamListener(api))
    stream.filter(languages=['en'], locations=[-180, -90, 180, 90])
