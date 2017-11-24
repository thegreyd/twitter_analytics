from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, parallel_bulk
from collections import deque
from tqdm import tqdm
import time, json

def main():

    mgclient = MongoClient('localhost', 27017)
    db = mgclient['dicdatabase']
    col = db['twitterTweets']

    print(col.count())

    es1 = Elasticsearch()
    ESinfo=(es1.info())

    #delete = es1.indices.delete(index = 'dicdatabase')
    def upload():
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
            actions.append(filter(data))
        
        request_body = {
            "settings" : {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        es1.indices.create(index='dicdatabase', body = request_body, ignore=400)
        res = es1.bulk(index = 'dicdatabase', body = actions, refresh = True)

    upload()

def filter(data):
    essentials = {
        "id" : None, 
        "text" : None, 
        "created_at" : None, 
        "reply_count" : None, 
        "retweet_count" : None, 
        "favorite_count" : None, 
        "user" : {
            "id": None, 
            "followers_count": None, 
            "name": None, 
            "screen_name": None
        },
        "place" : {
            "country": None, 
            "name": None, 
            "full_name": None
        }
    }
    
    for e in essentials.keys():
        if e in data:
            if isinstance(essentials[e], dict):
                attrs = essentials[e].keys()
                for i in attrs:
                    if i in data[e]:
                        essentials[e][i] = data[e][i]
            else:
                essentials[e] = data[e]
        
    return json.dumps(essentials)
    
if __name__ == "__main__":
    main()

#_id, text
