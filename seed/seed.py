import pymongo
import os
import pprint
from dotenv import dotenv_values

config = {
    **dotenv_values("db.env")
}

def listFiles(path):
    return os.listdir(path)


client = pymongo.MongoClient("mongodb://%s:%s@%s" % (config["MONGODB_USER"], config["MONGODB_PASSWORD"], config["MONGODB_URL"]))

db = client["rentalreviews"]
yelp_property_collection = db[""]

