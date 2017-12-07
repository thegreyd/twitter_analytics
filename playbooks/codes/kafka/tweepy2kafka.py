import passwords
import tweepy, json
from kafka import SimpleProducer, KafkaClient
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

class TweetListener(StreamListener):
    def __init__(self):
        super(TweetListener, self).__init__()
        client = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(client, async=True, batch_send_every_n=1000, batch_send_every_t=10)
        print("========= Connected to Kafka Client===========")

    def on_data(self, data):
        try:
            print("*Collecting Tweet*")
            json_data = json.loads(data)
            self.producer.send_messages(b'twitterstream', json.dumps(json_data))

            return True
        except KeyError:
            return True

    def on_error(self, status):
        print(status)
        return True

if __name__ == "__main__":

    consumer_key = passwords.consumerKey
    consumer_secret = passwords.consumerSecret
    access_key = passwords.accessToken
    access_secret = passwords.accessTokenSecret

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    twitter_stream = Stream(auth, TweetListener())
    twitter_stream.filter(languages=['en'], locations=[-180, -90, 180, 90])