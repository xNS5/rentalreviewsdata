import json
import traceback
import sys
import argparse
from datetime import datetime
import pyinputplus as pyinput
from git import Repo

from utilities import list_files, get_seed_config, get_db_env, get_file_metadata, create_json_file
from dotenv import dotenv_values
from collections import defaultdict

config = {**dotenv_values(".env")}

seed_config = get_seed_config()

verbose = False

testConnection = False

def get_params():
    database_selection = None
    database_action = None
    database_environment = None
    database_options = ["mongodb", "firebase"]
    action_options = ["seed", "clear", "list", "update", "test", "re-seed"]
    env_options = ["test", "production"]
    confirmation_options = ["Yes", "No"]

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("-db", "--database", required=True, help="Database Name")
        parser.add_argument(
            "-a", "--action", required=True, help="Action to perform on the database"
        )
        parser.add_argument(
            "-env",
            "--env",
            type=str,
            required=False,
            help="Database Environment [test|production]`",
        )
        parser.add_argument(
            "-verbose",
            "--verbose",
            required=False,
            help="Verbose output",
            action="store_true",
        )
        parser.add_argument(
            "-sitemap",
            required=False,
            help="Generates Sitemap",
            action="store_true"
        )

        args = parser.parse_args()

        if args.database.lower() not in database_options:
            print("Invalid database selection", file=sys.stderr)
            exit(-1)
        else:
            database_selection = args.database.lower()

        if args.action.lower() not in action_options:
            print("Invalid database action", file=sys.stderr)
            exit(-1)
        else:
            database_action = args.action.lower()

        if args.database.lower() == "firebase":
            if args.env is not None:
                if args.env.lower() not in env_options:
                    print("Invalid database environment", file=sys.stderr)
                    exit(1)
                else:
                    database_environment = args.env.lower()
            else:
                print("Environment required for Firebase", file=sys.stderr)
                exit(-1)

        global verbose
        verbose = args.verbose is not None and args.verbose == True

        if args.sitemap is not None and args.sitemap == True:
            create_sitemap()
            if verbose:
                print("Generated Sitemap", file=sys.stdout)

    else:
        database_environment = None
        database_selection = pyinput.inputMenu(
            database_options, lettered=True, numbered=False
        ).lower()

        database_action = pyinput.inputMenu(
            action_options, lettered=True, numbered=False
        ).lower()

        if database_selection == "firebase":
            database_environment = pyinput.inputMenu(
                env_options, lettered=True, numbered=False
            ).lower()

    if database_environment == "production":
        confirmation = pyinput.inputMenu(
            confirmation_options,
            lettered=True,
            numbered=False,
            prompt='You selected the "production" option -- this will affect the production database. Are you sure you wish to continue?\r\n',
        ).lower()
        if confirmation == "no":
            exit(1)
    return database_selection, database_action, database_environment

def create_sitemap():
    pages = []
    output_path = "./sitemap/sitemap.json"
    config_files = list_files("config")
    for file in config_files:
        config_file_path = f"config/{file}"
        metadata = get_file_metadata(config_file_path)
        metadata_modified_timestamp = datetime.fromtimestamp(metadata['modified']).strftime("%Y-%m-%d")
        with open(config_file_path, 'r', encoding='utf-8') as input_file:
            input_json = json.load(input_file)
            if 'type' in input_json and input_json['type'] == 'page':
                pages.append({
                    "url": f"{input_json['url']}",
                    "lastModified": metadata_modified_timestamp,
                    "changeFrequency": "monthly",
                    "priority": 1
                })
            input_file.close()
    article_files = list_files("articles")
    for file in article_files:
        with open(f"articles/{file}", 'r', encoding='utf-8') as input_file:
            input_json = json.load(input_file)
            created_timestamp = datetime.fromtimestamp(input_json['summary']['created_timestamp']).strftime("%Y-%m-%d")
            pages.append({
                "url": f"reviews/{input_json['slug']}",
                "lastModified": created_timestamp,
                "changeFrequency": "monthly",
                "priority": 0.9
            })
            pages.append({
                "url": f"reviews/{input_json['slug']}/data",
                "lastModified": created_timestamp,
                "changeFrequency": "monthly",
                "priority": 0.2
            })
            input_file.close()
    create_json_file(output_path, pages)
    return

def list_collections(db, client):
    match client:
        case "mongodb":
            return db.list_collection_names()
        case "firebase":
            return [collection.id for collection in db.collections()]


def construct_obj(seed, seed_key_arr, client):
    ret = {}
    for key in seed_key_arr:
        # if type(seed[key]) is dict:
        #     for sub_key in seed[key]:
        #         ret[sub_key] = seed[key][sub_key]
        # else:
        ret[key] = seed.get(key, None)
    return ret


def squash_file(db, client, path_obj):
    seed_obj = {}
    input_path = path_obj["path"]
    files = list_files(input_path)
    squash_config = path_obj["squash_config"]

    for file in files:
        with open(f"{input_path}/{file}", "r", encoding="utf-8") as inputFile:
            input_json = json.load(inputFile)
            seed_obj[file[:-5]] = input_json
            inputFile.close()
    try:
        match client:
            case "mongodb":
                seed_obj["_id"] = squash_config["document_name"]
                db[squash_config["collection"]].insert_one(seed_obj)
            case "firebase":
                db.collection(squash_config["collection"]).document(
                    squash_config["document_name"]
                ).set(seed_obj)

        if verbose:
            print(f'Squashed {path_obj["path"]} in {client}')
    except Exception as e:
        print(
            f"Failed to squash on {client} with error: {traceback.print_exc()} {e}",
            file=sys.stderr,
        )
        return


def create_index(db, client, path_obj):
    seed_arr = []
    input_path = path_obj["path"]
    files = list_files(input_path)
    index_config = path_obj["index_config"]
    index_file_name = f'{index_config["document_name"]}_index'
    ret_obj = {"data": []}

    for file in files:
        with open(f"{input_path}/{file}", "r", encoding="utf-8") as inputFile:
            input_json = json.load(inputFile)
            seed_arr.append(input_json)
            inputFile.close()
    try:
        for seed in seed_arr:
            temp_obj = construct_obj(seed, index_config["values"], client)
            ret_obj["data"].append(temp_obj)
        match client:
            case "mongodb":
                ret_obj["_id"] = index_file_name
                db[index_config["collection"]].insert_one(ret_obj)
            case "firebase":
                db.collection(index_config["collection"]).document(index_file_name).set(
                    ret_obj
                )

        if verbose:
            print(f'Created index on {client} for {path_obj["path"]}', file=sys.stdout)
    except Exception as e:
        print(
            f"Failed to seed {client} with error: {traceback.print_exc()} {e}",
            file=sys.stderr,
        )
        return


def populate(db, client, path_obj):
    seed_arr = []
    input_path = path_obj["path"]
    files = list_files(input_path)

    for file in files:
        with open(f"{input_path}/{file}", "r", encoding="utf-8") as inputFile:
            input_json = json.load(inputFile)
            seed_arr.append(input_json)
            inputFile.close()

    if path_obj["index"]:
        create_index(db, client, path_obj)

    try:
        match client:
            case "mongodb":
                ret_obj = defaultdict(lambda: [])
                for seed in seed_arr:
                    for key, key_arr in path_obj["collection_keys"].items():
                        ret_obj[key].append(
                            {
                                **(
                                    seed
                                    if path_obj["simple"]
                                    else construct_obj(seed, key_arr, client)
                                ),
                                "_id": seed["slug" if "slug" in seed else "name"],
                            }
                        )
                for key, value in ret_obj.items():
                    db[key].insert_many(value)
            case "firebase":
                batch = db.batch()
                for seed in seed_arr:
                    for key, key_arr in path_obj["collection_keys"].items():
                        temp_obj = (
                            seed
                            if path_obj["simple"]
                            else construct_obj(seed, key_arr, client)
                        )
                        doc_ref = db.collection(key).document(
                            seed["slug" if "slug" in seed else "name"]
                        )
                        batch.set(doc_ref, temp_obj)
                batch.commit()
    except Exception as e:
        print(
            f"Failed to seed {client} with error: {traceback.print_exc()} {e}",
            file=sys.stderr,
        )
        return
    if verbose:
        print(f'Seeded {client} with {len(seed_arr)} records from {path_obj["path"]}')


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
        print(f"Failed to clear {client} with error {e}", file=sys.stderr)
        return
    if verbose:
        print(f"Cleared {client}")


def update(db, client, path_obj):
    repo_obj = Repo("./")
    files = []
    update_path = path_obj["path"]
    for item in repo_obj.index.diff(None):
        if update_path in item.a_path:
            files.append(item.a_path)
    if len(files) > 0:
        match client:
            case "mongodb":
                for file in files:
                    with open(f"./{file}", "r", encoding="utf-8") as inputFile:
                        input_json = json.load(inputFile)
                        for key, key_arr in path_obj["collection_keys"].items():
                            temp_obj = (
                                input_json
                                if path_obj["simple"]
                                else construct_obj(input_json, key_arr, client)
                            )
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
                    with open(f"./{file}", "r", encoding="utf-8") as inputFile:
                        input_json = json.load(inputFile)
                        for key, key_arr in path_obj["collection_keys"].items():
                            temp_obj = (
                                input_json
                                if path_obj["simple"]
                                else construct_obj(input_json, key_arr, client)
                            )
                            doc_ref = db.collection(key).document(
                                input_json["seed" if "seed" in input_json else "name"]
                            )
                            doc_ref.update(temp_obj)

        print(f"Updated {client} with {len(files)} records")
    else:
        print(f"No updates available in {update_path}")


def main(db_name, db_action, db_env=None):
    try:
        db = None
        match db_name:
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
                db = client[config["MONGODB_DB_NAME"]]

            case "firebase":
                import firebase_admin
                from firebase_admin import credentials, firestore

                certificate_path = get_db_env(db_env)
                if verbose:
                    print(f"Firebase Certificate: {certificate_path}")
                cred = credentials.Certificate(certificate_path)
                app = firebase_admin.initialize_app(cred)
                db = firestore.client(app)

        if verbose:
            print(f"Initialized connection to {db_name}")
        if db_action == 'test':
            print(f"Successfully connected to {db_name}")
            exit()

        def exec_action(action):
            for path in seed_config:
                if path["squash"]:
                    squash_file(db, db_name, path)
                else:
                    match action:
                        case "seed" | "re-seed":
                            populate(db, db_name, path)
                        case "update":
                            update(db, db_name, path)

        actions = {
            "clear": lambda: clear_db(db, db_name),
            "re-seed": lambda: (clear_db(db, db_name), exec_action(db_action)),
            "update": lambda: exec_action(db_action),
            "seed": lambda: exec_action(db_action),
            "list": lambda: print(list_collections(db, db_name), file=sys.stdout),
        }

        if db_action in actions:
            actions[db_action]()
        else:
            print("Invalid Action", file=sys.stderr)
            exit(-1)
    except Exception as e:
        print(
            f"Failed to initialize source {db_name} with exception:\n{e}",
            file=sys.stderr,
        )
        return


if __name__ == "__main__":
    db_name, db_action, db_env = get_params()
    main(db_name, db_action, db_env)
