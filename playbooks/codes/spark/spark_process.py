from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from afinn import Afinn
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json, datetime, twitter_keywords, boto3

action = {
    "index": {
        "_index": "twitter_new",
        "_type": 'twitter',
    }
}

request_body = {
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

def main():
    conf = SparkConf().setAppName("Streamer")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 3)  # Create a streaming context with batch interval of 5 sec
    ssc.checkpoint("checkpoint")
    sc.setLogLevel("ERROR")
    print("======Created Spark Streaming Context")
    stream(ssc)

def format_time(utc_timestamp):
    return datetime.datetime.fromtimestamp(
        int(utc_timestamp)
    ).strftime('%Y-%m-%dT%H:%M:%S')


def stream(ssc):
    kstream = KafkaUtils.createDirectStream(ssc, topics=['twitterstream'], kafkaParams={"metadata.broker.list": '10.0.0.226:9092'})
    tweet_DStream = kstream.map(lambda v: json_filter(json.loads(v[1])))
    tweet_DStream.foreachRDD(lambda rdd: rdd.foreachPartition(sendPartition))
    print("====Received from Kafka====", kstream)
    ssc.start()
    ssc.awaitTermination()

def sendPartition(iter):
    mgclient = MongoClient('10.0.0.253')
    db = mgclient['dicdatabase']
    es = Elasticsearch(['10.0.0.105'])
    actions = []
    for tweet in iter:
        db.twitter_new.insert_one(tweet)
        print("twitter_new", db.twitter_new.count())
        actions.append(action)
        tweet.pop("_id")
        actions.append(tweet)
    if actions:
        es.bulk(index = "twitter_new", body = actions, refresh = True)
    mgclient.close()

def json_filter(data):
    essentials = {
        "id": None, 
        "text": None, 
        "reply_count": None, 
        "retweet_count": None, 
        "favorite_count": None,
        "user": {
            "id": None, 
            "followers_count": None, 
            "name": None, 
            "screen_name": None
        }, 
        "place": {
            "country": None, 
            "name": None, 
            "full_name": None,
            "bounding_box": {
                "coordinates": None
            },
            "country_code": None
        }
    }

    def parser(node, data):
        for e in node.keys():
            if data and (e in data):
                if isinstance(node[e], dict):
                    parser(node[e], data[e])
                else:
                    node[e] = data[e]
        return node

    essentials = parser(essentials, data)    

    if ('timestamp_ms' in data) and data['timestamp_ms']:
        essentials["created_at"] = format_time(int(data["timestamp_ms"])/1000)
    if ('text' in data) and data['text']:
        essentials['senti_val'] = afinn.score(data['text'])
        essentials['sentiment'] = fun(afinn.score(data['text']))
        essentials["keywords"] = twitter_keywords.get_keywords(essentials['text']) + twitter_keywords.extract_hashtag(essentials['text'])
    else:
        essentials['senti_val'] = None
        essentials['sentiment'] = None
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


if __name__ == "__main__":
    # create AFINN object for sentiment analysis
    afinn = Afinn()
    global_list_rdd = []
    main()
