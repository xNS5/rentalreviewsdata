import os
import json
import tempfile
import re

def get_config():
    with open("utilities/config.json", "r") as inputFile:
        input_json = json.load(inputFile)
        inputFile.close()
        return input_json

def get_db_env(mode):
    config = get_config()
    return config["db_config"][mode]

def get_yelp_category_whitelist():
    config = get_config()
    return set(
        config["yelp_category_whitelist"]
    )

def get_yelp_config():
    config = get_config()
    return config['yelp_config']

def get_seed_config():
    config = get_config()
    return config["seed_config"]

def get_google_config():
    config = get_config()
    return config["google_config"]

def get_disclaimer_map():
    map = get_config()
    return map["disclaimer"]

def company_map(key):
    map = get_config()
    return map["company_map"][key] if key in map else {}

def get_company_blacklist():
    return set(
        get_config()["company_blacklist"]
    )

def get_google_category_whitelist():
    return set(
        get_config()["google_category_whitelist"]
    )

def get_whitelist_types(categories):
    map = get_config()["category_map"]
    if isinstance(categories, list):
        for cat in categories:
            if cat["alias"] in map:
                return map[cat["alias"]]
    else:
        if categories in map:
            return map[categories]

    return None

#  Converts string to slug by first replacing non-alphanumeric characters with a space, then removing 2+ spaces
def get_slug(string):
    return re.sub(
        r"\s{2,}", " ", re.sub(r"[^a-zA-Z0-9\s]", "", string.lower())
    ).replace(" ", "-")


def list_files(path):
    ret = []
    input = os.listdir(path)
    for file in input:
        if file is not None:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                ret.append(get_file_name(file_path))
    return sorted(ret)


def list_directories(path):
    ret = []
    input = os.listdir(path)
    for file in input:
        if file is not None:
            file_path = os.path.join(path, file)
            if not os.path.isfile(file_path):
                ret.append(get_file_name(file_path))
    return sorted(ret)

def get_file_tuple(path):
    return os.path.split(path)

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def get_file_paths():
    config = get_config()
    return config['file_paths']

def remove_path(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(file)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    else:
        raise ValueError(f'File {path} does not exist')
            

def get_file_name(path):
    return str(get_file_tuple(path)[1])


def search(data, key, value):
    for d in data:
        if d[key] is not None and d[key] == value:
            return d
    return None


def get_all_reviews(data):
    reviews_obj = data["reviews"]
    keys = reviews_obj.keys()
    ret = []
    for key in keys:
        ret.extend(reviews_obj[key])
    return ret


def calculate_adjusted_reviews(data):
    reviews = get_all_reviews(data)
    adjusted_count = 0
    adjusted_rating = 0.0

    for review in reviews:
        if len(review["review"]) > 0:
            adjusted_count += 1
            adjusted_rating += review["rating"]

    return {
        "adjusted_review_count": adjusted_count,
        "adjusted_average_rating": (
            round(adjusted_rating / adjusted_count, 2)
            if adjusted_count > 0
            else data["average_rating"]
        ),
    }


def calculate_actual_rating(data):
    reviews = get_all_reviews(data)
    review_count = 0
    rolling_average_sum = 0
    for review in reviews:
        review_count += 1
        rolling_average_sum += review["rating"]
    return {
        "review_count": review_count,
        "average_rating": round(rolling_average_sum / review_count, 2),
    }

def get_file_count(path):
    input = os.listdir(path)
    return len(input)