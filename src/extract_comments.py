import json
import re
import html
import os

CLEANR = re.compile("<.*?>")

def clean(string):
    cleaned = html.unescape(re.sub(CLEANR, "", string))
    encoded = cleaned.encode("ascii", "ignore")
    decoded = encoded.decode()
    return decoded

def getComments(jsonObj):
    ret = []
    business = jsonObj[0]["data"]["business"]
    review_count = business["reviewCount"]
    if review_count != None and review_count > 0:
        reviews = business["reviews"]["edges"]
        for review in reviews:
            data = review["node"]
            text = clean(data["text"]["full"])
            author = data["author"]["displayName"]
            rating = data["rating"]
            ownerResponse = []
            if data["bizUserPublicReply"] != None:
                ownerResponse.append(
                    {"text": clean(data["bizUserPublicReply"]["text"])}
                )
            ret.append(
                {
                    "author": author,
                    "rating": float(rating),
                    "review": clean(text),
                    "ownerResponse": ownerResponse,
                }
            )
    return {
        "name": business["name"],
        "review_count": business["reviewCount"],
        "avg_rating": float(business["rating"]),
        "adjusted_review_count": business["reviewCount"],
        "adjusted_review_average": float(business["rating"]),
        "reviews": ret,
    }


with open ("./Lark Bellingham.json", "r") as inputFile:
    input_file_json = json.load(inputFile)
    extracted_data = getComments(input_file_json)
    with open("./output/%s" % os.path.basename(inputFile.name), "w") as outputFile:
        json.dump(extracted_data, outputFile, ensure_ascii=True, indent=2)
        outputFile.close()
    inputFile.close()