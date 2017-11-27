from elasticsearch import Elasticsearch
es1 = Elasticsearch([])
print(es1.info())
#delete = es1.indices.delete(index = 'dicdatabase')