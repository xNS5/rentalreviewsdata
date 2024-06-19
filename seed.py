import json
import pyinputplus as pyinput
from git import Repo
from utilities import list_files
from dotenv import dotenv_values


input_path = "./articles/"
collection_key = "articles"
certificate_path = "./firebase_certificate.json"

config = {
    **dotenv_values(".env")
}

def populate(db, client, files = []):
    seed_arr = []
    if len(files) == 0:
        files = list_files(input_path)
        for file in files:
            with open(f"{input_path}{file}", "r") as inputFile:
                input_json = json.load(inputFile)
                if client == "MongoDB":
                    seed_arr.append({**input_json, "_id": input_json['slug']})
                else:
                    seed_arr.append(input_json)
                    
    else:
         for file in files:
            with open(f"{file}", "r") as inputFile:
                seed_arr.append(json.load(inputFile))

    try:
        match client:
            case "MongoDB":
                db[collection_key].insert_many(seed_arr)
                db[collection_key].create_index("name")
            case "Firebase":
                batch = db.batch()
                for seed in seed_arr:
                    doc_ref = db.collection(collection_key).document(seed['slug'])
                    batch.set(doc_ref, seed)
                batch.commit()
    except Exception as e:
        print(f'Failed to seed {client} with error {e}')
        return
    print(f'Seeded {client} with {len(seed_arr)} records.')
    
            
def clear_db(db, client):
    try:
        match client:
            case "MongoDB":
                db[collection_key].delete_many({})
            case "Firebase":
                batch = db.batch()
                collection = db.collection(collection_key)
                docs = collection.stream()
                for doc in docs:
                    print(f"Deleting {doc.id}")
                    doc_ref = collection.document(doc.id)
                    batch.delete(doc_ref)
                batch.commit()
    except Exception as e:
            print(f'Failed to clear {client} with error {e}')
            return
    
    print(f'Cleared {client}')

def update(db, client):
    repo_obj = Repo("./")
    files = []
    for item in repo_obj.index.diff(None):
        if collection_key in item.a_path:
            files.append(item.a_path)
    if len(files) > 0:
         populate(db, client, files)
    else:
        print("No updates available")


def main(database_selection, database_action):
    db = None
    try:
        match database_selection:
            case "MongoDB":
                import pymongo
                client = pymongo.MongoClient("mongodb://%s:%s@%s" % (config["MONGODB_USER"], config["MONGODB_PASSWORD"], config["MONGODB_URL"]))
                db = client["rentalreviews"]
            case "Firebase":
                import firebase_admin
                from firebase_admin import credentials, firestore
                cred = credentials.Certificate(certificate_path)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
        print(f'Initialized connection to {database_selection}')
    except Exception as e:
        print(f'Failed to initialize source {database_selection} with exception {e}')
        return

    match database_action:
        case "Seed":
            populate(db, database_selection)
        case "Clear":
            clear_db(db, database_selection)
        case "Update":
            update(db, database_selection)
        case "Re-seed":
            clear_db(db, database_selection)
            populate(db, database_selection)

if __name__ == "__main__":
    database_selection = pyinput.inputMenu(["MongoDB", "Firebase"], lettered=True, numbered=False)
    database_action = pyinput.inputMenu(["Seed", "Clear", "Update", "Re-seed"], lettered=True, numbered=False)

    main(database_selection, database_action)