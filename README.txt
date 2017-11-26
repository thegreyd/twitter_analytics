Installing Required Python Libraries
We have provided a text file containing the required python packages: requirements.txt. 
To install all of these at once, simply run (only missing packages will be installed):
$ sudo pip2 install -r requirements.txt

Start zookeeper service:
$ $KAFKA_HOME/bin/zookeeper-server-start.sh config/zookeeper.properties 

Start kafka service:
$ $KAFKA_HOME/bin/kafka-server-start.sh config/server.properties 

Create a topic named twitterstream in kafka:
$ $KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic twitterstream 
Check what topics you have with:
$ $KAFKA_HOME/bin/kafka-topics.sh --list --zookeeper localhost:2181


In order to download the tweets from twitter streaming API and push them to kafka queue, run the python script  twitter_to_kafka.py. The script will need your twitter authentication tokens (keys). Once you have your authentication tokens, create or update the  twitter.txt file with these credentials.

After updating the text file with your twitter keys, you can start downloading tweets from the twitter stream API and push them to the twitterstream topic in Kafka. Do this by running our program as follows:
$ python twitter_to_kafka.py

To check if the data is landing in Kafka:
$ $KAFKA_HOME/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic twitterstream --from-beginning
Running the Stream Analysis Program
$ $SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.10:1.5.1 twitterStream.py

/Users/sachin/spark-1.6.2-bin-hadoop2.6/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.10:1.5.1 twitterStream.py

bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic twitterstream

bin/kafka-topics.sh --list --zookeeper localhost:2181

bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic twitterstream --from-beginning