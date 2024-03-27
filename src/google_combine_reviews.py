# Combines the reviews from Google and Yelp


import json
import os
import sys
import utilities

output_path = "./google_input/combined/"

companies_dir = "companies/"
properties_dir = "properties/"

companies_file = "./google_input/companies.json"
properties_file = "./google_input/properties.json"

curr_type = properties_dir
curr_file = properties_file

def write(data, path):
    with open(path, "w") as outputFile:
        json.dump(data, outputFile, ensure_ascii=True, indent=2)
        outputFile.close()  

def get_file_list(path): 
    file_list = utilities.listFiles(path)
    file_dict = {}
    for file in file_list:
        with open(file, "r") as inputFile:
            file_contents = inputFile.read()
            file_dict[file] = json.loads(file_contents)
        inputFile.close()
    return file_dict

def main(base_path, curr_file, curr_type):
    with open(curr_file, "r") as inputFile:
        input_dict = json.load(inputFile)
        file_dict = get_file_list(base_path)
        for i in input_dict:
            curr_file_name = i["name"]
            try:
                corresponding_file = file_dict["%s.json" % curr_file_name]
                i["reviews"] = corresponding_file
                i = utilities.calculate_adjusted_review_count(i)
                write(i, output_path +  curr_type + curr_file_name + ".json")
            except:
                print("Skipping: %s" % curr_file_name)
                continue
            inputFile.close()
        

if __name__ == "__main__":
    args = sys.argv
    main(args[1], companies_file, companies_dir)
    main(args[1], properties_file, properties_dir)
