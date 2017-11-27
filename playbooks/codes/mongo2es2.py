from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm

def main():

    mgclient = MongoClient()
    db = mgclient['dicdatabase']
    col = db['common_latest']

    print(col.count())

    es1 = Elasticsearch(['10.0.0.49'])
    
    def upload():
        actions = []
        for data in tqdm(col.find(), total=col.count()):
            action = {
                    "index": {
                            "_index": 'common_latest',
                            "_type": 'twitterreddit',
                            }
            }
            data.pop("_id")
            actions.append(action)
            actions.append(data)
        #print(actions)
        
        request_body = {
            "settings" : {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        es1.indices.create(index='common_latest', body = request_body, ignore=400)
        res = es1.bulk(index = 'common_latest', body = actions, refresh = True)

    upload()

if __name__ == "__main__":
    main()
