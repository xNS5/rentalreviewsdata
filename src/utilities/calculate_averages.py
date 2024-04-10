import json
import os
import sys
import shutil
import tempfile
import utilities


def main(file):
    with open(file, "r") as inputFile:
        with tempfile.TemporaryDirectory() as tempDir:
            input_json = json.load(inputFile)
            input_json["avg_rating"] = utilities.average_rating(input_json["reviews"])
            input_json["review_count"] = len(input_json["reviews"])
            input_json = utilities.calculate_adjusted_review_count(input_json)
            # print(json.dumps(input_json, indent=2))
            with open(tempDir + "/" + input_json["name"] + ".json", "w") as outFile:
                json.dump(input_json, outFile, ensure_ascii=True, indent=2)
                parent = os.path.dirname(file)
                shutil.move(tempDir + "/" + input_json["name"] + ".json", parent + "/" + input_json["name"] + ".json")
                outFile.close()
            
if __name__ == "__main__":
    main(sys.argv[1])