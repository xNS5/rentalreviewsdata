import json
import pyinputplus as pyinput
from git import Repo
from utilities import list_files
from dotenv import dotenv_values


input_path = "./articles/"
certificate_path = "./firebase_certificate.json"

collection_keys = {
    "articles": ["summary"],
    "reviews": ["reviews"],
    "companies": ["name", "slug", "company_type", "address", "review_count", "average_rating",  "adjusted_review_count", "adjusted_average_rating"]
}

config = {
    **dotenv_values(".env")
}

def list_collections(db, client):
    match client:
        case "MongoDB":
            return db.list_collection_names()
        case "Firebase":
            return [collection.id for collection in db.collections()]

def populate(db, client, files = []):

    def construct_obj(seed, seed_key_arr, client):
        ret = {}
        for key in seed_key_arr:
            if type(seed[key]) is dict:
                for sub_key in seed[key]:
                    ret[sub_key] = seed[key][sub_key]
            else:
                ret[key] = seed.get(key, None)
        return ret

    seed_arr = []

    if len(files) == 0:
        files = list_files(input_path)
        for file in files:
            with open(f"{input_path}{file}", "r") as inputFile:
                input_json = json.load(inputFile)
                seed_arr.append(input_json)
                    
    else:
         for file in files:
            with open(f"{input_path}/{file}", "r") as inputFile:
                seed_arr.append(json.load(inputFile))

    try:
        match client:
            case "MongoDB":
                ret_obj = {key : [] for key in collection_keys.keys()}
                for seed in seed_arr:
                    for key, key_arr in collection_keys.items():
                        temp_obj = construct_obj(seed, key_arr, client)
                        temp_obj['_id'] = seed["slug"]
                        ret_obj[key].append(temp_obj)
                for key, value in ret_obj.items():
                    db[key].insert_many(value)
            case "Firebase":
                batch = db.batch()
                for seed in seed_arr:
                    for key, key_arr in collection_keys.items():
                        modified_seed = construct_obj(seed, key_arr, client)
                        doc_ref = db.collection(key).document(seed['slug'])
                        batch.set(doc_ref, modified_seed)
                batch.commit()
    except Exception as e:
        print(f'Failed to seed {client} with error: {e}')
        return
    print(f'Seeded {client} with {len(seed_arr)} records.')
    
            
def clear_db(db, client):
    collection_key_arr = list_collections(db, client)
    try:
        match client:
            case "MongoDB":
                for key in collection_key_arr:
                    db.drop_collection(key)
            case "Firebase":
                batch = db.batch()
                for key in collection_key_arr:
                    collection = db.collection(key)
                    docs = collection.stream()
                    for doc in docs:
                        # print(f"Deleting {doc.id}")
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
        if "articles" in item.a_path:
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
        case "List":
            collection_list = list_collections(db, database_selection)
            print(collection_list)

if __name__ == "__main__":
    database_selection = pyinput.inputMenu(["MongoDB", "Firebase"], lettered=True, numbered=False)
    database_action = pyinput.inputMenu(["Seed", "Clear", "List", "Update", "Re-seed"], lettered=True, numbered=False)

    main(database_selection, database_action)