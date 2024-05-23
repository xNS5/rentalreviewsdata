import json
import os
import utilities

def getPrefix(input, delimiter):
     return input.split(delimiter)[0]

output_path = "./reviews/"
google_path = "./google_input/output/"
yelp_path = "./yelp_input/output/"

#calculate values here
def merge(file1, file2):
    with open(file1, "r") as inputFile1, open(file2, "r") as inputFile2:
        obj1 = json.load(inputFile1)
        obj2 = json.load(inputFile2)
        obj1["reviews"] = {**obj1["reviews"], **obj2[f"reviews"]}
        inputFile1.close()
        inputFile2.close()
        return obj1

def write(obj, path):
    with open(path, "w") as outputFile:
        json.dump(obj, outputFile, indent=2, ensure_ascii=True)
        outputFile.close()

def filter(input_path, alt_path):
    input_list = utilities.list_files(input_path)
    alt_list = utilities.list_files(alt_path)
    input_prefix = "google" if "google" in input_path else "yelp"
    alt_prefix = "yelp" if "yelp" in alt_path else "google"
    
    company_map = utilities.company_map(input_prefix)

    for file in input_list:
        # If file has a counterpart that's slightly different
        file_without_extension = file[:-5]
        if file_without_extension in company_map:
            # If the file already exists in the output dir
            if os.path.isfile(f"{output_path}{company_map[file_without_extension]}.json") or os.path.isfile(f"{output_path}{file}"):
                continue
            else:
                # Merge the files
                print(file)
                file_json = merge(f"{input_path}{file}", f"{alt_path}{company_map[file_without_extension]}.json", alt_prefix)
                write(file_json, f"{output_path}{file}")
                
        elif not os.path.isfile(f"{alt_list}{file}"):
            utilities.copy_file(f"{input_path}{file}", f"{output_path}{file}")
        else:
            file_json = merge(f"{input_path}{file}", f"{alt_path}{file}", alt_prefix)
            write(file_json, f"{output_path}{file}")
    

filter(google_path, yelp_path)
filter(yelp_path, google_path)