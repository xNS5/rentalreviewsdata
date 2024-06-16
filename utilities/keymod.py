import utilities
import re
import tempfile
import shutil
import json

# Only works on first-level keys because I'm lazy
path = "../articles"
key = "summary"
oldValue = "<article>"
newValue = "<article class='review-summary'>"


def main(path, key, oldValue, newValue):
    input_list = utilities.list_files(path)

    if len(input_list) == 0:
        print("No files in path")
        return
    
    with tempfile.TemporaryDirectory() as tempDir:
        for file in input_list:
            with open(f'{path}/{file}', 'r') as inputFile:
                input_json = json.load(inputFile)
                input_value = input_json[key]
                new_value = input_value.replace(oldValue, newValue)
                with open(f'{tempDir}/{file}', 'w') as outputFile:
                    json.dump({**input_json, key: new_value},
                    outputFile,
                    ensure_ascii=True,
                    indent=2
                    )
                    outputFile.close()
                inputFile.close()
        tmp_files = utilities.list_files(tempDir)
        for file in tmp_files:
            shutil.move(f'{tempDir}/{file}', f'{path}/{file}')
        shutil.rmtree(tempDir)


main(path, key, oldValue, newValue)

