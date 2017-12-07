import json

import configparser
import pymongo
import tweepy
from afinn import Afinn
from kafka import SimpleProducer, KafkaClient
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import keywords


class TweetListener(StreamListener):
    def __init__(self):
        client = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(client, async=True, batch_send_every_n=1000, batch_send_every_t=10)

    def on_data(self, data):
        try:
            json_data = json.loads(data)
            json_send_data = self.json_filter(json_data)

            json_send_data['senti_val'] = afinn.score(json_data['text'])
            json_send_data['sentiment'] = self.fun(afinn.score(json_data['text']))
            json_send_data['keywords'] = keywords.get_keywords(json_data['text']) + keywords.extract_hashtag(json_data['text'])
            print(json_send_data['text'], " >>>>>>>> ", json_send_data['keywords'], " >>>>>>>> ", json_send_data['sentiment'])

            self.producer.send_messages(b'twitter', json.dumps(json_send_data))

            client_mongo = pymongo.MongoClient('localhost', 27017)
            db = client_mongo['dicdatabase']
            db.test.insert_one(json_send_data)

            return True
        except KeyError:
            return True

    def on_error(self, status):
        print(status)
        return True

    @staticmethod
    def json_filter(data):
        essentials = {"id": None, "text": None, "created_at": None, "reply_count": None, "retweet_count": None, "favorite_count": None,
                      "user": {"id": None, "followers_count": None, "name": None, "screen_name": None}, "place": {"country": None, "name": None, "full_name": None}}

        for e in essentials.keys():
            if e in data:
                if isinstance(essentials[e], dict):
                    attrs = essentials[e].keys()
                    for i in attrs:
                        if data[e] and (i in data[e]):
                            essentials[e][i] = data[e][i]
                else:
                    essentials[e] = data[e]
        return essentials

    def fun(self, avg_senti_val):
        try:
            if avg_senti_val < 0:
                return 'NEGATIVE'
            elif avg_senti_val == 0:
                return 'NEUTRAL'
            else:
                return 'POSITIVE'
        except TypeError:
            return 'NEUTRAL'


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('twitter_config.txt')
    consumer_key = config['DEFAULT']['consumerKey']
    consumer_secret = config['DEFAULT']['consumerSecret']
    access_key = config['DEFAULT']['accessToken']
    access_secret = config['DEFAULT']['accessTokenSecret']

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # create AFINN object for sentiment analysis
    afinn = Afinn()

    twitter_stream = Stream(auth, TweetListener())
    twitter_stream.filter(languages=['en'], locations=[-180, -90, 180, 90])