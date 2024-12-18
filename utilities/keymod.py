import utilities
import re
import tempfile
import shutil
import json
import os
from datetime import datetime

# Only works on first-level keys because I'm lazy
def replace():
    path = "articles"
    key = "created_timestamp"
    oldValue = "<article>"
    newValue = "<article class='review-summary'>"
    input_list = utilities.list_files(path)

    if len(input_list) == 0:
        print("No files in path")
        return
    
    with tempfile.TemporaryDirectory() as tempDir:
        for file in input_list:
            with open(f'{path}/{file}', 'r') as inputFile:
                input_json = json.load(inputFile)
                input_value = datetime.fromtimestamp(input_json[key])
                new_value = (input_value - datetime(1970, 1, 1)).total_seconds()
                with open(f'{tempDir}/{file}', 'w') as outputFile:
                    json.dump({**input_json, key: int(new_value)},
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

def add_key():
    path = "../articles"
    key = "timestamp"

    input_list = utilities.list_files(path)

    if len(input_list) == 0:
        print("No files in path")
        return

    with tempfile.TemporaryDirectory() as tempDir:
        for file in input_list:
            with open(f'{path}/{file}', 'r') as inputFile:
                input_json = json.load(inputFile)
                timestamp = os.stat(f'{path}/{file}')
                creation_time = timestamp.st_ctime
                formatted = datetime.fromtimestamp(creation_time)
                with open(f'{tempDir}/{file}', 'w') as outputFile:
                    json.dump({**input_json, key: formatted.strftime("%B %-d %Y")},
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
replace()
# add_key()
