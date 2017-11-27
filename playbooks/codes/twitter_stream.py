import json, random, datetime
import tweepy, configparser, pymongo

def format_time(utc_timestamp):
    return datetime.datetime.fromtimestamp(
        int(utc_timestamp)
    ).strftime('%Y-%m-%dT%H:%M:%S')

def twitter_filter(data):
    data = json.loads(data)
    essentials = {
        "text": data["text"], 
        "created_at": format_time(int(data["timestamp_ms"])/1000), 
        "score": int(data["user"]["followers_count"])*0.5,
        "sentiment": random.choice([0,1]),
        "keywords": []
    }
    return essentials

class TweeterStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

    def on_data(self, status):
        try:
            twitter_json = twitter_filter(status)
            db.common_all.insert_one(twitter_json)
            #db.common_latest.insert_one(twitter_json)
            print("all", db.common_all.count())
            #print("latest", db.common_latest.count())
        except Exception as e:
           print("Error:", e)
           return False
        return True

    def on_error(self, status_code):
        print("Error")
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream

if __name__ == '__main__':
    client_mongo = pymongo.MongoClient('localhost')
    db = client_mongo['dicdatabase']
    
    config = configparser.ConfigParser()
    config.read('twitter.txt')
    consumer_key = config['DEFAULT']['consumerKey']
    consumer_secret = config['DEFAULT']['consumerSecret']
    access_key = config['DEFAULT']['accessToken']
    access_secret = config['DEFAULT']['accessTokenSecret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    stream = tweepy.Stream(auth, listener=TweeterStreamListener(api))
    stream.filter(languages=["en"], track=['#BlackFriday', '#CyberMonday', '#deals'])
