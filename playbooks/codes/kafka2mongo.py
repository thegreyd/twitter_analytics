import json, tweepy, configparser, pymongo

class TweeterStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

    def on_data(self, status):
        try:
            client_mongo = pymongo.MongoClient('localhost')
            db = client_mongo['dicdatabase']
            coll = db['twitterTweets']
            tweet = json.loads(status) # load it as Python dict
            result = db.twitterTweets.insert_one(tweet)
            print(db.twitterTweets.count())
        except Exception as e:
            print(e)
            return False
        return True

    def on_error(self, status_code):
        print("Error received in kafka producer")
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream


if __name__ == '__main__':
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
    stream.filter(locations=[-180, -90, 180, 90], languages=['en'])
