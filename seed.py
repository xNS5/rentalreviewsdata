import json
import pyinputplus as pyinput
from utilities import list_files
from dotenv import dotenv_values


input_path = "./articles/"
collection_key = "articles"
certificate_path = "./production_certificate.json"

config = {
    **dotenv_values(".env")
}

def populate(db, client):
    seed_arr = []
    files = list_files(input_path)
    for file in files:
        with open(f"{input_path}{file}", "r") as inputFile:
            seed_arr.append(json.load(inputFile))
    try:
        match client:
            case "MongoDB":
                db[collection_key].insert_many(seed_arr)
                db[collection_key].create_index("name")
            case "Firebase":
                batch = db.batch()
                for seed in seed_arr:
                    doc_ref = db.collection(collection_key).document()
                    batch.set(doc_ref, seed)
                batch.commit()
    except Exception as e:
        print(f'Failed to seed {client} with error {e}')
        return
        
    print(f'Seeded {client}')
    
            
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
        case "Re-seed":
            clear_db(db, database_selection)
            populate(db, database_selection)

if __name__ == "__main__":
    database_selection = pyinput.inputMenu(["MongoDB", "Firebase"], lettered=True, numbered=False)
    database_action = pyinput.inputMenu(["Seed", "Clear", "Re-seed"], lettered=True, numbered=False)

    main(database_selection, database_action)
