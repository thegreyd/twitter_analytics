from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm
import time, config

def main():
    print("mongo2es running..")
    mgclient = MongoClient()
    db = mgclient[config.mongo_db_name]
    twitter_latest_col = db[config.twitter_latest_collection]

    es_all = Elasticsearch(['10.0.0.105'])
    es_latest = Elasticsearch(['10.0.0.49'])
    
    actions_all,actions_latest = [],[]
    
    action_all = {
        "index": {
            "_index": config.twitter_all_collection,
            "_type": 'twitter',
        }
    }

    action_latest = {
        "index": {
            "_index": config.twitter_latest_collection,
            "_type": 'twitter',
        }
    }

    for data in tqdm(twitter_latest_col.find(), total=twitter_latest_col.count()):
        actions_all.append(action_all)
        actions_latest.append(action_latest)
        data.pop("_id")
        actions_all.append(data)
        actions_latest.append(data)
        
    request_body = {
        "settings" : {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    # overwrite es_latest
    es_latest.indices.delete(index=config.twitter_latest_collection, ignore=[400, 404])
    es_latest.indices.create(index=config.twitter_latest_collection, body = request_body, ignore=400)
    es_latest.bulk(index = config.twitter_latest_collection, body = actions_latest, refresh = True)
    

    # append to es_all
    es_all.bulk(index = config.twitter_all_collection, body = actions_all, refresh = True)
    

if __name__ == "__main__":
    main()
