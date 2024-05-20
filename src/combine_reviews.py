import json
import os
import utilities

def getPrefix(input, delimiter):
     return input.split(delimiter)[0]

output_path = "all_combined/"

google_path = "google_input/output/combined/"
yelp_path = "yelp_input/output/"

companies_dir = "companies/"
properties_dir = "properties/"

def main(curr_input, other_input, curr_type):
    google_file_list = utilities.listFiles(google_path + curr_type)
    yelp_file_list = utilities.listFiles(yelp_path + curr_type)
    
    other_prefix = getPrefix(other_input, "_")

    curr_file_list = google_file_list if other_prefix == "yelp" else yelp_file_list
    other_file_list = yelp_file_list if other_prefix == "yelp" else google_file_list


    # Current plan is to do away with the fuzzy search, and essentially create a map in the event there are kind-of duplicates
    file_list = {str(x): utilities.search_fuzzy(x, curr_file_list) for x in other_file_list}

    for file in file_list:
        # No match
        if file_list[file] == None:
            os.system("cp ./'%s' ./all_combined/'%s'" % (curr_input + curr_type + file, file))
        else:
            # If the file already exists
            if os.path.exists(output_path + curr_type + file):
                    continue
            # If the file doesn't exist
            with open(file, "r") as inputFile:
                with open(file_list[file], "r") as otherFile:
                    
                    input_json = json.load(inputFile)
                    other_json = json.load(otherFile)

                    input_json[f"{other_prefix}_reviews"] = other_json["{other_prefix}_reviews"]
                    input_json["review_count"] += other_json["review_count"]
                    input_json["avg_rating"] = utilities.average_rating(input_json)
                    input_json = utilities.calculate_adjusted_review_count(input_json)
                    if len(input_json["address"]) == 0:
                        print(input_json["name"], input_json["address"])
                        input_json["address"] = other_json["address"]
                    with open(output_path + curr_type + file, "w") as outputFile:
                        json.dump(input_json, outputFile, ensure_ascii=True, indent=2)
                        outputFile.close()
                    otherFile.close()
                inputFile.close()


main(yelp_path, google_path, companies_dir)
main(google_path, yelp_path, companies_dir)
