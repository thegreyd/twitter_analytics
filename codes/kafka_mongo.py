# =========================================================================================
# @author: Sachin Saligram, Akanksha Singh, Siddharth Sharma
# @description: This code listens to streams from a streaming API. Data is simultaneously
#              sent to Apache Kafka and MongoDB for persistent storage.
# =========================================================================================

import json, tweepy, configparser, pymongo, yaml
from kafka import SimpleProducer, KafkaClient


# Note: Some of the imports are external python libraries. They are installed on the current machine.
# If you are running multi-node cluster, you have to make sure that these libraries
# and current version of Python is installed on all the worker nodes.

class TweeterStreamListener(tweepy.StreamListener):
    """ A class to read the twitter stream and push it to Kafka"""

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        client = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(client, async=True, batch_send_every_n=1000, batch_send_every_t=10)
        # self.producer = kafka.KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('ascii'))

    def on_data(self, status):
        """ This method is called whenever new data arrives from live stream.
        We asynchronously push this data to kafka queue"""
        # msg = status.text.encode('utf-8')
        # print(json.loads(status))
        try:
            status1 = json.dumps(status.replace("\\'", "'"))
            d = yaml.safe_load(status1)
            print d
            # jd = json.dumps(d)
            self.producer.send_messages(b'twitterstream', d)
            # self.producer.send('twitterstream', status)
        except Exception as e:
            print(e)
            return False
        return True

        # client_mongo = pymongo.MongoClient('localhost', 27017)
        # db = client_mongo['dicdatabase']
        # coll = db['diccoll']
        #
        # result = db.diccoll.insert_one(json.loads(status))
        # print(result.inserted_id)

    def on_error(self, status_code):
        print("Error received in kafka producer")
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream


if __name__ == '__main__':
    # Read the credentials from 'twitter.txt' file
    config = configparser.ConfigParser()
    config.read('twitter.txt')
    consumer_key = config['DEFAULT']['consumerKey']
    consumer_secret = config['DEFAULT']['consumerSecret']
    access_key = config['DEFAULT']['accessToken']
    access_secret = config['DEFAULT']['accessTokenSecret']

    # Create Auth object
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # Create stream and bind the listener to it
    stream = tweepy.Stream(auth, listener=TweeterStreamListener(api))

    # Custom Filter rules pull all traffic for those filters in real time.
    # stream.filter(track = ['love', 'hate'], languages = ['en'])
    stream.filter(locations=[-180, -90, 180, 90], languages=['en'])
