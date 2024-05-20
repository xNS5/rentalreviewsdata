import os, sys
import json
import tempfile
import shutil
from thefuzz import process

sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def get_yelp_whitelist():
    return set(
        [
            "propertymgmt",
            "apartments",
            "condominiums",
            "realestateagents",
            "realestatesvcs",
            "university_housing",
        ]
    )


def get_whitelist_types():
    return {
        "propertymgmt": "company",
        "apartments": "property",
        "condominiums": "property",
        "realestateagents": "company",
        "realestatesvcs": "company",
        "university_housing": "property",
    }


def listFiles(path):
    ret = []
    print(path)
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            ret.append(file_path)
    return ret


def getFileTuple(path):
    return os.path.split(path)


def getFileName(path):
    return getFileTuple(path)[1]


def calculate_adjusted_review_count(data):
    adjusted_count = 0
    adjusted_rating = 0.0
    for review in data["reviews"]:
        if len(review["review"]) > 0:
            adjusted_count += 1
            adjusted_rating += review["rating"]
    data["adjusted_review_count"] = adjusted_count
    data["adjusted_review_average"] = round(adjusted_rating / adjusted_count, 1)
    return data


def average_rating(data):
    num_reviews = len(data)
    rolling_sum_average = 0
    for review in data:
        rolling_sum_average += review["rating"]
    return round(rolling_sum_average / num_reviews, 1)


def search(data, key, value):
    for d in data:
        if d[key] != None and d[key] == value:
            return d
    return None


def search_fuzzy(value, data):
    try:
        ret = process.extractOne(value, data)
        if ret[1] >= 90:
            return ret[0]
        return None
    except:
        return None


def merge_dir(inputPath, summaryPath):
    input_list = listFiles(inputPath)
    with tempfile.TemporaryDirectory() as tempDir:
        for file in input_list:
            file_name = getFileName(file)[1]
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
        tmp_files = listFiles(tempDir)
        for tmp_file in tmp_files:
            tmp_file_name = getFileName(tmp_file)[1]
            shutil.copy(tmp_file, summaryPath + tmp_file_name)
        shutil.rmtree(tempDir)


def merge_file(inputPath, summaryPath):
    with tempfile.TemporaryDirectory() as tempDir:
        file_name = getFileName(inputPath)[1]
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
        tmp_files = listFiles(tempDir)
        for file in tmp_files:
            shutil.move(file, summaryPath)
        shutil.rmtree(tempDir)
