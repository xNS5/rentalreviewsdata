import pymongo
import os
import pprint
from dotenv import dotenv_values

config = {
    **dotenv_values("db.env")
}

def listFiles(path):
    ret = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            ret.append(file_path)
    return ret



yelp_path = "../yelp_input/output/"
google_path = "../google_input/output/combined/"
combined_path = "../combined/"
summary_path = "../summaries/"

# client = pymongo.MongoClient("mongodb://%s:%s@%s" % (config["MONGODB_USER"], config["MONGODB_PASSWORD"], config["MONGODB_URL"]))

# db = client["rentalreviews"]
categories = ["yelp_", "google_", "combined_", "summary_"]
paths = [yelp_path, google_path, combined_path, summary_path]



def populate(suffix):
    for path in paths:
        files = listFiles(path + suffix)
        dump = []
        for file in files:
            with open(file, "r") as inputFile:



populate("companies")