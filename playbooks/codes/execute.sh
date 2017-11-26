#!/bin/sh

# Start zookeeper service:
cd $KAFKA_HOME
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start kafka service:
cd $KAFKA_HOME; bin/kafka-server-start.sh config/server.properties &

# Create a topic named twitterstream in kafka:
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic twitterstream

# Check what topics you have with:
$KAFKA_HOME/bin/kafka-topics.sh --list --zookeeper localhost:2181

# Start MongoDB
Mongod &

# Dump data into Kafka and MongoDB
python kafka_mongo.py

# To check if the data is landing in Kafka:
$KAFKA_HOME/bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic twitterstream --from-beginning
