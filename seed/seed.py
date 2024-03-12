import pymongo
import os
import pprint
import json
import sys
from dotenv import dotenv_values

yelp_path = "../yelp_input/output/"
google_path = "../google_input/output/combined/"
combined_path = "../summaries/"

config = {
    **dotenv_values("db.env")
}

client = pymongo.MongoClient("mongodb://%s:%s@%s" % (config["MONGODB_USER"], config["MONGODB_PASSWORD"], config["MONGODB_URL"]))

db = client["rentalreviews"]

paths = {
    yelp_path: "yelp_",
    google_path: "google_",
    combined_path: "combined_"
}


def listFiles(path):
    ret = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            ret.append(file_path)
    return ret

def populate(suffix):
    for path, collection_prefix in paths.items():
        files = listFiles(path + suffix)
        seed = []
        for file in files:
            with open(file, "r") as inputFile:
                seed.append(json.load(inputFile))
        collection_key = collection_prefix + suffix
        db[collection_key].insert_many(seed)
        db[collection_key].create_index("name")

def clear_db(suffix):
    for path, collection_prefix in paths.items():
        collection_key = collection_prefix + suffix
        db[collection_key].delete_many({})

def main():
    arg = sys.argv[1].lower()
    if arg == "seed":
        populate("companies")
        populate("properties")
    elif arg == "clear":
        clear_db("companies")
        clear_db("properties")
    print("Done")

if __name__ == "__main__":
    main()
