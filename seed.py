import json
import traceback
import sys
import argparse
import pyinputplus as pyinput
from git import Repo
from utilities import list_files, get_seed_config, get_db_env
from dotenv import dotenv_values
from collections import defaultdict

config = {**dotenv_values(".env")}

seed_config = get_seed_config()

def list_collections(db, client):
    match client:
        case "mongodb":
            return db.list_collection_names()
        case "firebase":
            return [collection.id for collection in db.collections()]


def construct_obj(seed, seed_key_arr, client):
    ret = {}
    for key in seed_key_arr:
        if type(seed[key]) is dict:
            for sub_key in seed[key]:
                ret[sub_key] = seed[key][sub_key]
        else:
            ret[key] = seed.get(key, None)
    return ret

def squash_file(db, client, pathObj):
    seed_obj = {}
    input_path = pathObj["path"]
    files = list_files(input_path)
    squash_config = pathObj['squash_config']

    for file in files:
        with open(f"{input_path}/{file}", "r") as inputFile:
            input_json = json.load(inputFile)
            seed_obj[file[:-5]] = input_json
            inputFile.close()
    try:
        match client:
            case "mongodb":
                seed_obj["_id"] = squash_config['document_name']
                db[squash_config['collection']].insert_one(seed_obj) 
            case "firebase":
                db.collection(squash_config["collection"]).document(squash_config['document_name']).set(seed_obj)                    
    
        print(f'Squashed \033[1m{pathObj["path"]}\033[0m in {client}')
    except:
        print(f"Failed to squash on {client} with error: {traceback.print_exc()}")
        return

def create_index(db, client, pathObj):
    seed_arr = []
    input_path = pathObj["path"]
    files = list_files(input_path)
    index_config = pathObj["index_config"]

    for file in files:
        with open(f"{input_path}/{file}", "r") as inputFile:
            input_json = json.load(inputFile)
            seed_arr.append(input_json)
            inputFile.close()
    try:
        match client:
            case "mongodb":
                ret_obj = {}
                for seed in seed_arr:
                    temp_obj = construct_obj(seed, index_config["values"], client)
                    if index_config["key"] in seed:
                        ret_obj[seed[index_config["key"]]] = temp_obj
                    else:
                        ret_obj[seed['slug']] = temp_obj
                ret_obj["_id"] = f'{index_config["document_name"]}_index'
                db[index_config["collection"]].insert_one(ret_obj) 
            case "firebase":
                ret_obj = {}
                for seed in seed_arr:
                    temp_obj = construct_obj(seed, index_config["values"], client)
                    if index_config['key'] in seed:
                        ret_obj[seed[index_config['key']]] = temp_obj
                    else:
                        ret_obj[seed['slug']] = temp_obj
                db.collection(index_config["collection"]).document(f'{index_config["document_name"]}_index').set(ret_obj)                    
    
        print(f'Created index on {client} for {pathObj["path"]}')
    except:
        print(f"Failed to seed {client} with error: {traceback.print_exc()}")
        return
   

def populate(db, client, pathObj):

    seed_arr = []
    input_path = pathObj["path"]
    files = list_files(input_path)

    for file in files:
        with open(f"{input_path}/{file}", "r") as inputFile:
            input_json = json.load(inputFile)
            seed_arr.append(input_json)
            inputFile.close()

    if pathObj["index"] == True:
        create_index(db, client, pathObj)

    try:
        match client:
            case "mongodb":
                ret_obj = defaultdict(lambda: [])
                for seed in seed_arr:
                    for key, key_arr in pathObj["collection_keys"].items():
                        temp_obj = {}
                        id_str = seed["slug" if "slug" in seed else "name"]
                        if pathObj["simple"] == True:
                            temp_obj = seed
                        else:
                            temp_obj = construct_obj(seed, key_arr, client)
                        temp_obj["_id"] = id_str
                        ret_obj[key].append(temp_obj)
                for key, value in ret_obj.items():
                    db[key].insert_many(value)
            case "firebase":
                batch = db.batch()
                for seed in seed_arr:
                    for key, key_arr in pathObj["collection_keys"].items():
                        temp_obj = {}
                        if pathObj["simple"] == True:
                            temp_obj = seed
                        else:
                            temp_obj = construct_obj(seed, key_arr, client)
                        doc_ref = db.collection(key).document(
                            seed["slug" if "slug" in seed else "name"]
                        )
                        batch.set(doc_ref, temp_obj)
                batch.commit()
    except:
        print(f"Failed to seed {client} with error: {traceback.print_exc()}")
        return
    print(f'Seeded {client} with {len(seed_arr)} records from {pathObj["path"]}.')


def clear_db(db, client):
    collection_key_arr = list_collections(db, client)
    try:
        match client:
            case "mongodb":
                for key in collection_key_arr:
                    db.drop_collection(key)
            case "firebase":
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
        print(f"Failed to clear {client} with error {e}")
        return

    print(f"Cleared {client}")


def update(db, client, pathObj):
    repo_obj = Repo("./")
    files = []
    updatePath = pathObj["path"].split("/")[1]
    for item in repo_obj.index.diff(None):
        if updatePath in item.a_path:
            files.append(item.a_path)
    if len(files) > 0:
        match client:
            case "mongodb":
                update_obj = defaultdict(lambda: [])
                for file in files:
                    with open(f"./{file}", "r") as inputFile:
                        input_json = json.load(inputFile)
                        for key, key_arr in pathObj["collection_keys"].items():
                            temp_obj = {}
                            if pathObj["simple"] == True:
                                temp_obj = input_json
                            else:
                                temp_obj = construct_obj(input_json, key_arr, client)
                            db[key].update_one(
                                {
                                    "_id": input_json[
                                        "slug" if "slug" in input_json else "name"
                                    ]
                                },
                                {"$set": temp_obj},
                                upsert=True,
                            )
                        inputFile.close()
            case "firebase":
                for file in files:
                    with open(f"./{file}", "r") as inputFile:
                        input_json = json.load(inputFile)
                        for key, key_arr in pathObj["collection_keys"].items():
                            temp_obj = {}
                            if pathObj["simple"] == True:
                                temp_obj = input_json
                            else:
                                temp_obj = construct_obj(input_json, key_arr, client)
                            doc_ref = db.collection(key).document(
                                input_json["seed" if "seed" in input_json else "name"]
                            )
                            doc_ref.update(temp_obj)

        print(f"Updated {client} with {len(files)} records")
    else:
        print(f"No updates available in {updatePath}")
           

def main(database_selection, database_action):
    db = None
    try:
        match database_selection:
            case "mongodb":
                import pymongo

                client = pymongo.MongoClient(
                    "mongodb://%s:%s@%s"
                    % (
                        config["MONGODB_USER"],
                        config["MONGODB_PASSWORD"],
                        config["MONGODB_URL"],
                    )
                )
                db = client["rentalreviews"]
            case "firebase":
                import firebase_admin
                from firebase_admin import credentials, firestore
            
                certificate_path = get_db_env(config['DB_ENV'])
                print(f'Firebase Certificate: \033[1m{certificate_path}\033[0m')
                cred = credentials.Certificate(certificate_path)
                app = firebase_admin.initialize_app(cred)
                db = firestore.client(app)
               
        print(f"Initialized connection to {database_selection}")
    except Exception as e:
        print(f"Failed to initialize source {database_selection} with exception:\n{e}")
        return
    
    def exec(action):
        for path in seed_config:
            if path['squash'] == True:
                squash_file(db, database_selection, path)
            else:
                match action:
                    case "seed" | "re-seed":
                        populate(db, database_selection, path)
                    case "update":
                        update(db, database_selection, path)

    actions = {
        "clear": lambda: clear_db(db, database_selection),
        "re-seed": lambda: (clear_db(db, database_selection), exec(database_action)),
        'update': lambda: exec(database_action),
        'seed': lambda: exec(database_action),
        'list': lambda: print(list_collections(db, database_selection))
    }

    if database_action in actions:
        actions[database_action]()

if __name__ == "__main__":
    database_selection = None 
    database_action = None
    database_options = ["mongodb", "firebase"]
    action_options = ["seed", "clear", "list", "update", "re-seed"]
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("-db", "--database", required=True, help="Database Name")
        parser.add_argument("-a", "--action", required=True, help="Action to perform on the database")

        args = parser.parse_args()

        if args.database.lower() not in database_options:
            print("Invalid database selection")
            exit(1)
        else:
            database_selection = args.database.lower()

        if args.action.lower() not in action_options:
            print("Invalid database action")
            exit(1)
        else:
            database_action = args.action.lower()

    else: 
        database_selection = pyinput.inputMenu(
            database_options , lettered=True, numbered=False
        ).lower()

        database_action = pyinput.inputMenu(
            action_options, lettered=True, numbered=False
        ).lower()

    main(database_selection, database_action)
