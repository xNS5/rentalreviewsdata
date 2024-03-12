import json
import os
import sys
import shutil
import tempfile


def listFiles(path):
    ret = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            ret.append(file_path)
    return ret

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
    num_reviews = len(data["reviews"])
    rolling_sum_average = 0
    for review in data["reviews"]:
        rolling_sum_average += review["rating"]
    return round(rolling_sum_average / num_reviews, 1)


def main(file):
    with open(file, "r") as inputFile:
        with tempfile.TemporaryDirectory() as tempDir:
            input_json = json.load(inputFile)
            input_json["avg_rating"] = average_rating(input_json)
            input_json["review_count"] = len(input_json["reviews"])
            input_json = calculate_adjusted_review_count(input_json)
            # print(json.dumps(input_json, indent=2))
            with open(tempDir + "/" + input_json["name"] + ".json", "w") as outFile:
                json.dump(input_json, outFile, ensure_ascii=True, indent=2)
                parent = os.path.dirname(file)
                shutil.move(tempDir + "/" + input_json["name"] + ".json", parent + "/" + input_json["name"] + ".json")
                outFile.close()
            


if __name__ == "__main__":
    main(sys.argv[1])