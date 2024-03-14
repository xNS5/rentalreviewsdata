import json
import os
import utilities

output_path = "output/"

google_path = "google_input/output/combined/"
yelp_path = "yelp_input/output/"

companies_dir = "companies/"
properties_dir = "properties/"

curr_type = companies_dir
curr_input = yelp_path
other_input = google_path

file_dict = {}
output = []

google_file_list = utilities.listFiles(google_path + curr_type)
yelp_file_list = utilities.listFiles(yelp_path + curr_type)

file_list = {str(x): utilities.search_fuzzy(x, google_file_list) for x in yelp_file_list}

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
                input_json["avg_rating"] = utilities.average_rating(input_json["reviews"])
                input_json = utilities.calculate_adjusted_review_count(input_json)
                if len(input_json["address"]) == 0:
                    print(input_json["name"])
                    input_json["address"] = other_json["address"]
                input_json = utilities.calculate_adjusted_review_count(input_json)

                with open(output_path + curr_type + file, "w") as outputFile:
                    json.dump(input_json, outputFile, ensure_ascii=True, indent=2)
                    outputFile.close()
                otherFile.close()
            inputFile.close()
