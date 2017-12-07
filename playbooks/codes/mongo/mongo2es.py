from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm
import time, config

def main():
    print("mongo2es running..")
    mgclient = MongoClient()
    db = mgclient["dicdatabase"]
    twitter_new_col = db["twitter_new"]

    es = Elasticsearch(['10.0.0.105'])
    actions = []
    
    action = {
        "index": {
            "_index": "twitter_new",
            "_type": 'twitter',
        }
    }

    for data in tqdm(twitter_new_col.find(), total=twitter_new_col.count()):
        actions.append(action)
        data.pop("_id")
        actions.append(data)
        
    request_body = {
        "settings" : {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    es.bulk(index = "twitter_new", body = actions, refresh = True)
    

if __name__ == "__main__":
    main()