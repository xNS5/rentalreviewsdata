## Utility script to change the names of keys in the .json files

import tempfile
import json
import sys
import os
import shutil

def listFiles(path):
    ret = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            ret.append(file_path)
    return ret

def main(old_key, new_key, path):
    file_list = listFiles(path)
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
        tmp_files = listFiles(tempDir)
        for file in tmp_files:
            if ".json" in file:
                basepath = os.path.basename(file)
                print(basepath)
                shutil.move(file, path + basepath)
        shutil.rmtree(tempDir)
        
    

if __name__ == "__main__":
    args = sys.argv
    main(args[1], args[2], args[3])