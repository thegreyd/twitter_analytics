# ============================================================================================
# @author: Sachin Saligram, Akanksha Singh, Siddharth Sharma
# @description: This code is a sample processing task to check if we are receiving data from
#              Apache Kafka in a appropriate manner. Once evaluation is done, data processing
#              tasks will be updated to match the current use case.
# ============================================================================================

from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


def main():
    conf = SparkConf().setMaster("local[2]").setAppName("Streamer")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 10)  # Create a streaming context with batch interval of 10 sec
    ssc.checkpoint("checkpoint")
    sc.setLogLevel("ERROR")

    stream(ssc)


def stream(ssc):
    kstream = KafkaUtils.createDirectStream(ssc, topics=['twitterstream'], kafkaParams={"metadata.broker.list": 'localhost:9092'})
    tweets = kstream.map(lambda x: x[1].encode("ascii", "ignore"))

    # Each element of tweets will be the text of a tweet.
    # You need to find the count of all the positive and negative words in these tweets.
    # Keep track of a running total counts and print this at every time step (use the pprint function).

    # Obtain list of words from tweets
    #tweet_words = tweets.flatMap(lambda line: line.split(" "))

    tweets.pprint()


if __name__ == "__main__":
    main()
