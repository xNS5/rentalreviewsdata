## Utility script to change the names of keys in the .json files

import tempfile
import json
import sys
import shutil
import utilities

def merge_dir(inputPath, summaryPath):
    input_list = utilities.listFiles(inputPath)
    with tempfile.TemporaryDirectory() as tempDir:
        for file in input_list:
            file_name = utilities.getFileName(file)[1]
            with open(file, "r") as inputFile:
                input_file_json = json.load(inputFile)
                summary_file_path = summaryPath + file_name
                with open(summary_file_path , "r") as summaryFile:
                    summary_json = json.load(summaryFile)
                    temp_file_path = tempDir + "/" + file_name
                    with open(temp_file_path, "w") as outputFile:
                        json.dump({**input_file_json, "summary" : summary_json["summary"]}, outputFile, ensure_ascii=True, indent=2)
                        outputFile.close()
                    summaryFile.close()
                inputFile.close()
        tmp_files = utilities.listFiles(tempDir)
        for tmp_file in tmp_files:
            tmp_file_name = utilities.getFileName(tmp_file)[1]
            shutil.copy(tmp_file, summaryPath + tmp_file_name)
        shutil.rmtree(tempDir)

def merge_file(inputPath, summaryPath):
    with tempfile.TemporaryDirectory() as tempDir:
        file_name = utilities.getFileName(inputPath)[1]
        with open(inputPath, "r") as inputFile:
            input_file_json = json.load(inputFile)
            with open("%s" % summaryPath, "r") as summaryFile:
                summary_json = json.load(summaryFile)
                with open("%s" % tempDir + "/" + file_name, "w") as outputFile:
                    print(summary_json)
                    json.dump({**input_file_json, "summary" : summary_json["summary"]}, outputFile, ensure_ascii=True, indent=2)
                    outputFile.close()
                summaryFile.close()
            inputFile.close()
        tmp_files = utilities.listFiles(tempDir)
        for file in tmp_files:
            shutil.move(file, summaryPath)
        shutil.rmtree(tempDir)


if __name__ == "__merge_dir__":
    args = sys.argv
    merge_dir(args[1], args[2])