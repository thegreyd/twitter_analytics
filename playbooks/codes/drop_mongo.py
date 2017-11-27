from pymongo import MongoClient
mgclient = MongoClient('10.0.0.253')
db = mgclient['dicdatabase']
db.common_all.drop()