import json
import traceback
import sys
import argparse
import pyinputplus as pyinput
from git import Repo
from utilities import list_files, get_seed_config
from dotenv import dotenv_values
from collections import defaultdict

certificate_path = "./firebase_certificate.json"

config = {**dotenv_values(".env")}

seed_config = get_seed_config()

def list_collections(db, client):
    match client:
        case "MongoDB":
            return db.list_collection_names()
        case "Firebase":
            return [collection.id for collection in db.collections()]


def construct_obj(seed, seed_key_arr, client):
    ret = {}
    for key in seed_key_arr:
        if type(seed[key]) is dict:
            for sub_key in seed[key]:
                ret[sub_key] = seed[key][sub_key]
        else:
            ret[key] = seed.get(key, None)
    if client == "MongoDB":
        ret["_id"] = seed["slug" if "slug" in seed else "name"]
    return ret


def populate(db, client, pathObj):

    seed_arr = []
    input_path = pathObj["path"]
    files = list_files(input_path)

    for file in files:
        with open(f"{input_path}{file}", "r") as inputFile:
            input_json = json.load(inputFile)
            seed_arr.append(input_json)
            inputFile.close()

    try:
        match client:
            case "MongoDB":
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
            case "Firebase":
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
            case "MongoDB":
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
            case "Firebase":
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
            case "MongoDB":
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
            case "Firebase":
                import firebase_admin
                from firebase_admin import credentials, firestore

                cred = credentials.Certificate(certificate_path)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
        print(f"Initialized connection to {database_selection}")
    except Exception as e:
        print(f"Failed to initialize source {database_selection} with exception {e}")
        return

    # Clear first for both actions, otherwise it will clear -> seed, clear -> seed for each path object
    if database_action.lower() == "re-seed" or database_action.lower() == "clear":
        clear_db(db, database_selection)

    for path in seed_config:
        match database_action.lower():
            case "seed":
                populate(db, database_selection, path)
            case "update":
                update(db, database_selection, path)
            case "re-seed":
                populate(db, database_selection, path)
            case "list":
                collection_list = list_collections(db, database_selection)
                print(collection_list)


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
            database_selection = args.database

        if args.action.lower() not in action_options:
            print("Invalid database action")
            exit(1)
        else:
            database_action = args.action

    else: 
        database_selection = pyinput.inputMenu(
            database_options , lettered=True, numbered=False
        )
        database_action = pyinput.inputMenu(
            action_options, lettered=True, numbered=False
        )

    main(database_selection, database_action)
