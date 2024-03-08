import json

with open("./output/Lark Bellingham.json", "r") as inputFile:
    input_json = json.load(inputFile)
    reviews = input_json[0]["data"]["business"]["reviews"]["edges"]
    print("NUMBER OF REVIEWS: %s" % len(reviews))