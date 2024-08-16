import os
import shutil
import json
import tempfile
import re

# sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def get_config():
    with open("utilities/config.json", "r") as inputFile:
        input_json = json.load(inputFile)
        inpputFile.close()
        return input_json


def get_yelp_category_whitelist():
    config = get_config()
    return set(
        config["yelp_category_whitelist"]
    )

def get_seed_config():
    config = get_config()
    return config["seed_config"]

def company_map(key):
    map = get_config()
    return map["company_map"][key] if key in map else {}

def get_company_blacklist():
    return set(
        get_config["company_blacklist"]
    )

def get_google_category_whitelist():
    return set(
        get_config("google_category_whitelist")
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


def copy_file(src, dest):
    shutil.copy(src, dest)


def get_file_tuple(path):
    return os.path.split(path)


def get_file_name(path):
    return str(get_file_tuple(path)[1])


def search(data, key, value):
    for d in data:
        if d[key] != None and d[key] == value:
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


def merge_dir(inputPath, summaryPath):
    input_list = list_files(inputPath)
    with tempfile.TemporaryDirectory() as tempDir:
        for file in input_list:
            file_name = get_file_name(file)[1]
            with open(file, "r") as inputFile:
                input_file_json = json.load(inputFile)
                summary_file_path = summaryPath + file_name
                with open(summary_file_path, "r") as summaryFile:
                    summary_json = json.load(summaryFile)
                    temp_file_path = tempDir + "/" + file_name
                    with open(temp_file_path, "w") as outputFile:
                        json.dump(
                            {**input_file_json, "summary": summary_json["summary"]},
                            outputFile,
                            ensure_ascii=True,
                            indent=2,
                        )
                        outputFile.close()
                    summaryFile.close()
                inputFile.close()
        tmp_files = list_files(tempDir)
        for tmp_file in tmp_files:
            tmp_file_name = get_file_name(tmp_file)[1]
            shutil.copy(tmp_file, summaryPath + tmp_file_name)
        shutil.rmtree(tempDir)


def merge_file(inputPath, summaryPath):
    with tempfile.TemporaryDirectory() as tempDir:
        file_name = get_file_name(inputPath)[1]
        with open(inputPath, "r") as inputFile:
            input_file_json = json.load(inputFile)
            with open("%s" % summaryPath, "r") as summaryFile:
                summary_json = json.load(summaryFile)
                with open("%s" % tempDir + "/" + file_name, "w") as outputFile:
                    print(summary_json)
                    json.dump(
                        {**input_file_json, "summary": summary_json["summary"]},
                        outputFile,
                        ensure_ascii=True,
                        indent=2,
                    )
                    outputFile.close()
                summaryFile.close()
            inputFile.close()
        tmp_files = list_files(tempDir)
        for file in tmp_files:
            shutil.move(file, summaryPath)
        shutil.rmtree(tempDir)
