import json
import pyinputplus as pyinput
from utilities import listFiles
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
    seed = []
    for path, collection_prefix in paths.items():
        files = listFiles(path + suffix + "/")
        for file in files:
            with open(file, "r") as inputFile:
                seed.append(json.load(inputFile))
        collection_key = collection_prefix + suffix
    match client:
        case "MongoDB":
            db[collection_key].insert_many(seed)
            db[collection_key].create_index("name")
        case "Firebase":
            db.collection(collection_key).add(seed)


def clear_db(db, client, suffix):
    match client:
        case "MongoDB":
            for path, collection_prefix in paths.items():
                collection_key = collection_prefix + suffix
                db[collection_key].delete_many({})
        case "Firebase":
            if batch_size == 0:
                return

            docs = coll_ref.list_documents(page_size=batch_size)
            deleted = 0

            for doc in docs:
                print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
                doc.delete()
                deleted = deleted + 1

            if deleted >= batch_size:
                return delete_collection(coll_ref, batch_size)


def main():
    database_selection = pyinput.inputMenu(["MongoDB", "Firebase"], lettered=True, numbered=False)
    database_action = pyinput.inputMenu(["Seed", "Clear"], lettered=True, numbered=False)

    db = None

    match database_selection:
        case "MongoDB":
            import pymongo
            client = pymongo.MongoClient("mongodb://%s:%s@%s" % (config["MONGODB_USER"], config["MONGODB_PASSWORD"], config["MONGODB_URL"]))
            db = client["rentalreviews"]
        case "Firebase":
           import firebase_admin
           from firebase_admin import credentials, firestore
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
