import json
import os


base_path = "./output/"
output_path = "./output/combined/"

companies_dir = "companies/"
properties_dir = "properties/"

companies_file = "./companies.json"
properties_file = "./properties.json"

curr_type = properties_dir
curr_file = properties_file

file_list = os.listdir(base_path + curr_type)

file_dict = {}

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

def write(data, path):
    with open(path, "w") as outputFile:
        json.dump(data, outputFile, ensure_ascii=True, indent=2)
        outputFile.close()  

for file in file_list:
    filePath = base_path + curr_type + file
    with open(filePath, "r") as inputFile:
        file_contents = inputFile.read()
        file_dict[file] = json.loads(file_contents)
    inputFile.close()

with open(curr_file, "r") as inputFile:
    input_dict = json.load(inputFile)
    for i in input_dict:
        curr_file_name = i["name"]
        try:
            corresponding_file = file_dict["%s.json" % curr_file_name]
            i["reviews"] = corresponding_file
            i = calculate_adjusted_review_count(i)
            write(i, output_path +  curr_type + curr_file_name + ".json")
        except:
            print("Skipping: %s" % curr_file_name)
            continue
        inputFile.close()
        



