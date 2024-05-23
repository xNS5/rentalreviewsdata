import os
import shutil
import json
import tempfile
import shutil
import re
from thefuzz import process

# sys.path.append(os.path.dirname(os.path.realpath(__file__)))

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


def company_map(key):
    map = {
        "yelp": {
            "access-real-estate-services": "access-real-estate-services-llc",
            "brampton-court-apts": "brampton-court-apartments",
            "canterbury-court-apts": "canterbury-court-apartments",
            "integra-condominium-association-management": "integra-condominium-association-management-inc",
            "lakeway-rentals": "lakeway-rentals-work",
            "maplewood-apartments": "maplewood-apartments-lp",
            "optimus-property-solutions": "optimus-property-solutions-property-sales-management",
            "pomeroy-court-appartments": "pomeroy-court-apartments",
            "sonrise-property-management": "pure-property-management-of-washington",
            "stateside-bellingham": "stateside",
            "sunset-pond-apts": "sunset-pond-apartments",
            "windermere-property-management": "windermere-property-management-bellingham",
            "woodrose-senior-affordable-apartments": "woodrose-apartments",
        },
        "google": {
            "access-real-estate-services-llc": "access-real-estate-services",
            "brampton-court-apartments": "brampton-court-apts",
            "canterbury-court-apartments": "canterbury-court-apts",
            "integra-condominium-association-management-inc": "integra-condominium-association-management",
            "lakeway-rentals-work": "lakeway-rentals",
            "maplewood-apartments-lp": "maplewood-apartments",
            "optimus-property-solutions-property-sales-management": "optimus-property-solutions",
            "pomeroy-court-apartments": "pomeroy-court-appartments",
            "pure-property-management-of-washington": "sonrise-property-management",
            "stateside": "stateside-bellingham",
            "sunset-pond-apartments": "sunset-pond-apts",
            "windermere-property-management-bellingham": "windermere-property-management",
            "woodrose-apartments": "woodrose-senior-affordable-apartments",
        },
    }
    return map[key] if key in map else {}


def get_google_whitelist():
    return set(
        [
            "Property management company",
            "Commercial real estate agency",
            "Real estate rental agency",
            "Real estate agency",
            "Short term apartment rental agency",
            "Apartment building",
            "Apartment complex",
            "Apartment rental agency",
            "Furnished apartment building",
            "Housing complex",
        ]
    )


def get_whitelist_types(categories):
    map = {
        "propertymgmt": "company",
        "apartments": "property",
        "condominiums": "property",
        "realestateagents": "company",
        "realestatesvcs": "company",
        "university_housing": "property",
        "Property management company": "company",
        "Commercial real estate agency": "company",
        "Real estate rental agency": "company",
        "Real estate agency": "company",
        "Short term apartment rental agency": "company",
        "Apartment building": "property",
        "Apartment complex": "property",
        "Apartment rental agency": "property",
        "Furnished apartment building": "property",
        "Housing complex": "property",
    }
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
                ret.append(getFileName(file_path))
    return ret


def copy_file(src, dest):
    shutil.copy(src, dest)


def getFileTuple(path):
    return os.path.split(path)


def getFileName(path):
    return getFileTuple(path)[1]


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
    
def calculate_adjusted_review_count(data, prefix_list):
    adjusted_count = 0
    adjusted_rating = 0.0
    for prefix in prefix_list:
        for review in data[f"{prefix}_reviews"]:
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


def merge_dir(inputPath, summaryPath):
    input_list = list_files(inputPath)
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
        tmp_files = list_files(tempDir)
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
        tmp_files = list_files(tempDir)
        for file in tmp_files:
            shutil.move(file, summaryPath)
        shutil.rmtree(tempDir)
