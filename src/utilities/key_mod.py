## Utility script to change the names of keys in the .json files
# So far I've only gotten it to work for top-level keys, and frankly I'm a little too lazy to 
# figure out how to fix it. Maybe a second function for the "reviews" array. 

import tempfile
import json
import sys
import os
import shutil
import utilities

def is_company(val):
    company_set = set(["Property Management", "Property management company", "Real estate agent", "Short term apartment rental agency", "Real Estate Services", "Real estate services", "University Housing", "Commercial real estate","Commercial real estate agency","Real estate rental agency", "Real estate agency"])
    if val in company_set:
        return "company"
    return "property"

def key_swap(old_key, new_key, path):
    file_list = utilities.listFiles(path)
    with tempfile.TemporaryDirectory() as tempDir:
        for file in file_list:
            with open(file, "r") as inputFile:
                input_file_json = json.load(inputFile)
                if old_key in input_file_json:
                    input_file_json[new_key] = input_file_json[old_key]
                    del input_file_json[old_key]
                with open(tempDir + "/" + input_file_json["name"] + ".json", "w") as outputFile:
                    json.dump(input_file_json, outputFile, ensure_ascii=True, indent=2)
                    outputFile.close()
                inputFile.close()
        tmp_files = utilities.listFiles(tempDir)
        for file in tmp_files:
            basepath = os.path.basename(file)
            print(basepath)
            shutil.move(file, path + basepath)
        shutil.rmtree(tempDir)

def value_swap(key, func, path):
    file_list = utilities.listFiles(path)
    with tempfile.TemporaryDirectory() as tempDir:
        for file in file_list:
            with open(file, "r") as inputFile:
                input_file_json = json.load(inputFile)
                if key in input_file_json:
                    input_file_json[key] = func(input_file_json[key])
                else: 
                    print(f'Key not present in { input_file_json["name"] }')
                with open(tempDir + "/" + input_file_json["name"] + ".json", "w") as outputFile:
                    json.dump(input_file_json, outputFile, ensure_ascii=True, indent=2)
                    outputFile.close()
                inputFile.close()
        tmp_files = utilities.listFiles(tempDir)
        for file in tmp_files:
            basepath = os.path.basename(file)
            print(basepath)
            shutil.move(file, path + basepath)
        shutil.rmtree(tempDir)


def validate(key, expected_value, path):
        file_list = utilities.listFiles(path)
        for file in file_list:
            with open(file, "r") as inputFile:
                input_file_json = json.load(inputFile)
                if key in input_file_json:
                    if input_file_json[key] != expected_value:
                        print(f'\r\nFile: { input_file_json["name"] }\r\nKey Mismatch for {key}: Expected: {expected_value}\r\nFound:{ input_file_json[key] }\r\n')
                else: 
                    print(f'Key not present in { input_file_json["name"] }')
                inputFile.close()
        
if __name__ == "__main__":
    args = sys.argv
    if len(args) == 3:
        key_swap(args[1], args[2], args[3])
    else:
        value_swap("company_type", is_company, "/Users/michaelkennedy/Git/osp/rentalreviewsdata/summaries/properties/")
        validate("company_type", "property", "/Users/michaelkennedy/Git/osp/rentalreviewsdata/summaries/properties/")
