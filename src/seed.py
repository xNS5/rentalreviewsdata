import json
import pymongo
import firebase_admin
import pyinputplus as pyinput
from utilities import listFiles
from firebase_admin import credentials, firestore
from dotenv import dotenv_values


yelp_path = "yelp_input/output/"
google_path = "google_input/output/combined/"
combined_path = "summaries/"

config = {
    **dotenv_values("db.env")
}

paths = {
    yelp_path: "yelp_",
    google_path: "google_",
    combined_path: "combined_"
}

def populate(db, client, suffix):
   match client:
       case "MongoDB":
            for path, collection_prefix in paths.items():
                files = listFiles(path + suffix + "/")
                seed = []
                for file in files:
                    with open(file, "r") as inputFile:
                        seed.append(json.load(inputFile))
                collection_key = collection_prefix + suffix
                db[collection_key].insert_many(seed)
                db[collection_key].create_index("name")
       case "Firebase":
           doc_ref = db.collection("testcollection")
           docs = doc_ref.stream()
           for doc in docs:
               print(f"{doc.id} => {doc.to_dict()}")


def clear_db(db, client, suffix):
    for path, collection_prefix in paths.items():
        collection_key = collection_prefix + suffix
        db[collection_key].delete_many({})

def main():
    database_selection = pyinput.inputMenu(["MongoDB", "Firebase"], lettered=True, numbered=False)
    database_action = pyinput.inputMenu(["Seed", "Clear"], lettered=True, numbered=False)

    db = None

    match database_selection:
        case "MongoDB":
            client = pymongo.MongoClient("mongodb://%s:%s@%s" % (config["MONGODB_USER"], config["MONGODB_PASSWORD"], config["MONGODB_URL"]))
            db = client["rentalreviews"]
        case "Firebase":
          

           cred = credentials.Certificate("certificate.json")
           firebase_admin.initialize_app(cred)
           db = firestore.client()

    match database_action:
        case "Seed":
            populate(db, database_selection, "companies")
            populate(db, database_selection, "properties")
        case "Clear":
            clear_db(db, database_selection, "companies")
            clear_db(db, database_selection, "properties")
    

    
    # if arg == "seed":
    #     populate("companies")
    #     populate("properties")
    # elif arg == "clear":
    #     clear_db("companies")
    #     clear_db("properties")
    # print("Done")

if __name__ == "__main__":
    main()
