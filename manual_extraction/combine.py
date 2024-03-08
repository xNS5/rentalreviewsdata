import json
import os

input_path = "lark"
input_name = "Lark Bellingham"
output_path = "output"

file_list = os.listdir("./%s/" % input_path)
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

with open("./%s/%s.json" % (output_path, input_name), "w") as outputFile:
    json.dump(master_file_json, outputFile, ensure_ascii=True, indent=2)
    outputFile.close()  