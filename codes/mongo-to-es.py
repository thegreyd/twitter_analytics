from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
from collections import deque
from tqdm import tqdm
import time

def main():

    mgclient = MongoClient('localhost', 27017)
    db = mgclient['dicdatabase']
    col = db['twitterTweets']

    print(col.count())

    es1 = Elasticsearch()
    ESinfo=(es1.info())

    while True:
        # Pull from mongo and dump into ES using bulk API
        actions = []
        for data in tqdm(col.find(), total=col.count()):
            data.pop('_id')
            action = {
                    "index": {
                            "_index": 'dicdatabase',
                            "_type": 'twitterTweets',
                            }
            }
            actions.append(action)
            actions.append(data)

        delete = es1.indices.delete(index = 'dicdatabase')
        request_body = {
            "settings" : {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        es1.indices.create(index='dicdatabase', body = request_body, ignore=400)
        res = es1.bulk(index = 'dicdatabase', body = actions, refresh = True)
        time.sleep(20)

    
    
if __name__ == "__main__":
    main()

    