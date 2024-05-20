import http.client as http_client
import json
from dotenv import dotenv_values
import pyinputplus as pyinput
import logging
import html
import re
import random
import time
import utilities
from requests import Request, Session

http_client.HTTPConnection.debuglevel = 0

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/100.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36 OPR/100.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36 Edg/100.0.0.0",
    "Mozilla/5.0 (iPad; CPU OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Mobile/15E148 Safari/604.1",
]

requestObj = [
    {
        "operationName": "GetBusinessReviewFeed",
        "variables": {
            "encBizId": None,
            "reviewsPerPage": None,
            "selectedReviewEncId": "",
            "hasSelectedReview": False,
            "sortBy": "RELEVANCE_DESC",
            "ratings": [
                5,
                4,
                3,
                2,
                1
            ],
            "queryText": "",
            "isSearching": False,
            "after": None,
            "isTranslating": False,
            "translateLanguageCode": "en",
            "reactionsSourceFlow": "businessPageReviewSection",
            "minConfidenceLevel": "HIGH_CONFIDENCE",
            "highlightType": "",
            "highlightIdentifier": "",
            "isHighlighting": False
        },
        "extensions": {
            "operationType": "query",
            "documentId": "ef51f33d1b0eccc958dddbf6cde15739c48b34637a00ebe316441031d4bf7681"
        }
    }
]

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
                    {
                        "text": clean(data["bizUserPublicReply"]["text"]),
                    }
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
        "slug": business["alias"],
        "avg_rating": float(business["rating"]),
        "review_count": business["reviewCount"],
        "yelp_reviews": ret,
    }


config = {**dotenv_values("yelp.env")}


def query():
    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = False

    with open("./yelp_input/query_response.json", "r") as inputFile:
        data = json.load(inputFile)
        session = Session()
        url = "https://www.yelp.com/gql/batch"
        req = Request(
            "POST",
            url,
        )
        for biz in data:
            if biz["review_count"] < 55:
                user_agent = user_agent_list[
                    random.randint(0, len(user_agent_list) - 1)
                ]
                print(biz["name"])
                requestObj[0]["variables"]["encBizId"] = biz["id"]
                requestObj[0]["variables"]["reviewsPerPage"] = biz["review_count"]
                req.json = requestObj
                req.user_agent = user_agent
                prepared_request = req.prepare()
                response = session.send(prepared_request)
                if response.status_code == 200:
                    res_json = json.loads(response.content.decode())
                    details = {
                        "company_type": utilities.get_whitelist_types(
                            biz["categories"]
                        ),
                        "address": " ".join(biz["location"]["display_address"]),
                    }
                    ret = getComments(res_json)
                    if len(ret["yelp_reviews"]) > 0:
                        filePath = "./yelp_input/output/%s.json" % (biz["alias"].replace("/", ""),)
                        with open(filePath, "w") as outFile:
                            json.dump(
                                {**ret, **details}, outFile, ensure_ascii=True, indent=2
                            )
                            outFile.close()
                    else:
                        print("%s review count below threshold" % biz["name"])
                else:
                    print("ERROR: ", response.status_code)
                    break
            else:
                print("Skipping ", biz["name"])

            time.sleep(3 + random.randint(1, 3))


query()
