import json, tweepy, configparser, pymongo, yaml, praw
from kafka import SimpleProducer, KafkaClient

def get_reddit():
    def reddit_filter(data):
        reddit_dict = {
            "score": data.score,
            "text": data.body,
            "sentiment": data.controversiality,
            "created_at": format_time(created_utc),
            "keywords": []
        }
        return json.dumps(reddit_dict)

    reddit = praw.Reddit(client_id='yi_ETjv7GOXrag',
                         client_secret='0dRBM-34_PRv5qPCfB_TVmqIk5g',
                         user_agent='android:com.example.myredditapp:v1.2.3')

    subreddit = reddit.subreddit('blackfriday')

    for comment in subreddit.comments(limit=999999999999999):
        reddit_json = reddit_filter(comment)

class TweeterStreamListener(tweepy.StreamListener):
    """ A class to read the twitter stream and push it to Kafka"""

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        
    def on_data(self, status):
        twitter_json = self.twitter_filter(status)
        common_json = self.common_filter(status1)
        twitter_msg = twitter_json.encode('utf-8')
        common_msg = common_json.encode('utf-8')
        
        try:
            self.producer.send_messages(b'twitterstream', msg)
            self.producer.send_messages(b'commonstream', msg)
        except Exception as e:
            print(e)
            return False
        return True

    def on_error(self, status_code):
        print("Error received in kafka producer")
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream

    def twitter_filter(self, data):
        essentials = {"id": None, "text": None, "timestamp_ms": None, "reply_count": None, "retweet_count": None, "favorite_count": None,
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

        return json.dumps(essentials)

    def common_filter(self, data):
        twitter_dict = {
            "text": data[text], 
            "created_at": format_time(data[timestamp_ms]), 
            "score": score,
            "sentiment": data[retweet_count]*0.5 + data[favorite_count]*0.5,
            "keywords": []
        }
        return json.dumps(twitter_dict)
        

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
    stream.filter(locations=[-180, -90, 180, 90], languages=['en'])
