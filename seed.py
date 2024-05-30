import json
import pyinputplus as pyinput
from utilities import listFiles
from dotenv import dotenv_values


yelp_path = "yelp_input/output/"
google_path = "google_input/output/combined/"
summary_path = "../summaries/"

config = {
    **dotenv_values("db.env")
}

paths = {
    yelp_path: "yelp_",
    google_path: "google_",
    summary_path: "summary_"
}

# Certificates for staging + production databases
server_certificates = {
    "Production": "./production_certificate.json",
    "Staging": "./staging_certificate.json"
}

def populate(db, client, suffix):
    for path, collection_prefix in paths.items():
        seed_arr = []
        files = listFiles(path + suffix + "/")
        for file in files:
            with open(file, "r") as inputFile:
                seed_arr.append(json.load(inputFile))
        collection_key = collection_prefix + suffix
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
        
    print(f'Seeded {client} for {suffix}')
    
            
def clear_db(db, client, suffix):
    for path, collection_prefix in paths.items():
        collection_key = collection_prefix + suffix
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
        
    print(f'Cleared {client} for {suffix}')



def main(database_selection, database_action, database_environment):
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
                cred = credentials.Certificate(server_certificates[database_environment])
                firebase_admin.initialize_app(cred)
                db = firestore.client()
        print(f'Initialized connection to {database_selection}')
    except Exception as e:
        print(f'Failed to initialize source {database_selection} with exception {e}')
        return

    match database_action:
        case "Seed":
            populate(db, database_selection, "companies")
            populate(db, database_selection, "properties")
        case "Clear":
            clear_db(db, database_selection, "companies")
            clear_db(db, database_selection, "properties")
        case "Re-seed":
            clear_db(db, database_selection, "companies")
            populate(db, database_selection, "companies")
            clear_db(db, database_selection, "properties")
            populate(db, database_selection, "properties")

if __name__ == "__main__":
    database_selection = pyinput.inputMenu(["MongoDB", "Firebase"], lettered=True, numbered=False)
    database_action = pyinput.inputMenu(["Seed", "Clear", "Re-seed"], lettered=True, numbered=False)
    database_environment = ""
    if database_selection != "MongoDB":
        database_environment = pyinput.inputMenu(["Production", "Staging"], lettered=True, numbered=False)

    main(database_selection, database_action, database_environment)
