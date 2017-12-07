import json, tweepy, configparser, pymongo, keywords
from afinn import Afinn

def filter(data):
    data = json.loads(data)
    essentials = {
        "text" : None, 
        "created_at" : None, 
        "reply_count" : None, 
        "retweet_count" : None, 
        "favorite_count" : None, 
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
    
    return json.dumps(essentials)

class TweeterStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

    def on_data(self, status):
        try:
            twitter_json = filter(status)
            twitter.insert_one(twitter_json)
            print(db.twitter.count())
        except Exception as e:
            print(e)
            return False
        return False

    def on_error(self, status_code):
        print("Error")
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream


if __name__ == '__main__':
    client_mongo = pymongo.MongoClient('localhost')
    db = client_mongo['dicdatabase']
    twitter = db['twitter']
    
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
    stream.filter(track=['#BlackFriday', '#CyberMonday', '#deals'])
