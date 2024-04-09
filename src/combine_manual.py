# This is strictly for Yelp data

import json
import os
import sys
import utilities


def main(input_path, output_path):
    file_list = utilities.listFiles("./%s/" % input_path)
    master_file_path = file_list[0]
    master_file = open("./%s/%s" % (input_path, master_file_path), "r")
    master_file_json = json.load(master_file)
    master_file_reviews = master_file_json[0]["data"]["business"]["reviews"]["edges"]
    
    for i in range(1, len(file_list)):
        file = file_list[i]
        with open("./%s/%s" % (input_path, file), "r") as inputFile:
            input_file_json = json.load(inputFile)
            input_reviews = input_file_json[0]["data"]["business"]["reviews"]["edges"]
            master_file_reviews += input_reviews
            inputFile.close()

    with open("./%s/%s.json" % (output_path, utilities.getFileName(input_path)), "w") as outputFile:
        json.dump(master_file_json, outputFile, ensure_ascii=True, indent=2)
        outputFile.close()  

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("Expected: arg1, arg2. Received: %s" % args)
    else:
        main(args[1], args[2])