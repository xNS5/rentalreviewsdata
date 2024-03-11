import os
import json
import sys
import ntpath

def listFiles(path):
    ret = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        # print(file_path)
        if os.path.isfile(file_path):
            ret.append(file_path)
    return ret


path = sys.argv[1]
fileList = listFiles(path)

for file in fileList:
    # print(file)
    basename = ntpath.split(file)[1][:-3]
    print(basename)
    with open(file, "r") as inputFile:
        with open(path + basename + ".json", "w") as outputFile:
            json.dump({
                "name": basename,
                "summary": inputFile.read()
            }, outputFile, ensure_ascii=True, indent=2)
            outputFile.close()
        inputFile.close()