import json
import os
from thefuzz import process

output_path = "output/"

google_path = "google_input/output/combined/"
yelp_path = "yelp_input/output/"

companies_dir = "companies/"
properties_dir = "properties/"

curr_type = properties_dir
curr_input = google_path
other_input = yelp_path

file_dict = {}
output = []

def listFiles(path):
    return os.listdir(path)

# If the review doesn't contain values, not valid.
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
        if ret[1] > 95:
            # print(ret[0])
            return ret[0]
        return None
    except:
        return None

google_file_list = listFiles(google_path + curr_type)
yelp_file_list = listFiles(yelp_path + curr_type)

file_list = {str(x): search_fuzzy(x, yelp_file_list) for x in google_file_list}

for file in file_list:
    if file_list[file] == None:
        os.system("cp ./'%s' ./output/'%s'" % (curr_input + curr_type + file, curr_type + file))
    else:
        if os.path.exists(output_path + curr_type + file):
                continue
        with open(curr_input + curr_type + file, "r") as inputFile:
            with open(other_input + curr_type + file_list[file], "r") as otherFile:
                input_json = json.load(inputFile)
                other_json = json.load(otherFile)
                input_json["reviews"] += other_json["reviews"]
                input_json["review_count"] += other_json["review_count"]
                input_json["avg_review"] = average_rating(input_json["reviews"])
                if len(input_json["address"]) == 0:
                    print(input_json["name"])
                    input_json["address"] = other_json["address"]
                input_json = calculate_adjusted_review_count(input_json)

                with open(output_path + curr_type + file, "w") as outputFile:
                    json.dump(input_json, outputFile, ensure_ascii=True, indent=2)
                    outputFile.close()
                otherFile.close()
            inputFile.close()
