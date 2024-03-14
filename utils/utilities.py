import os
import json
from thefuzz import process

def listFiles(path):
    ret = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            ret.append(file_path)
    return ret


def getFileName(path):
    return os.path.split(path)


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