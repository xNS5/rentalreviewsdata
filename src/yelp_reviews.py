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
from utilities import Review, Business
from requests import Request, Session

http_client.HTTPConnection.debuglevel = 0

config = {**dotenv_values("yelp.env")}

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

# Might need to copy the request headers from an existing request prior to initiating
requestObj = [
    {
        "operationName": "GetBusinessReviewFeed",
        "variables": {
            "encBizId": None,
            "reviewsPerPage": None,
            "selectedReviewEncId": "",
            "hasSelectedReview": False,
            "sortBy": "RELEVANCE_DESC",
            "ratings": [5, 4, 3, 2, 1],
            "queryText": "",
            "isSearching": False,
            "after": None,
            "isTranslating": False,
            "translateLanguageCode": "en",
            "reactionsSourceFlow": "businessPageReviewSection",
            "minConfidenceLevel": "HIGH_CONFIDENCE",
            "highlightType": "",
            "highlightIdentifier": "",
            "isHighlighting": False,
        },
        "extensions": {
            "operationType": "query",
            "documentId": "ef51f33d1b0eccc958dddbf6cde15739c48b34637a00ebe316441031d4bf7681",
        },
    }
]

query_obj = {
    "companies": "property management companies",
    "properties": "apartment complexes",
}

my_headers = {
    "Authorization": f'Bearer {config["YELP_FUSION_KEY"]}',
}

CLEANR = re.compile("<.*?>")

def filter(jsonObj):
    ret = []
    whitelist = utilities.get_yelp_whitelist()
    for obj in jsonObj:
        if obj["location"]["country"] != "US":
            continue
        for category in obj["categories"]:
            if category["alias"] in whitelist:
                ret.append(
                    Business(
                        obj["name"],
                        obj["rating"],
                        utilities.get_whitelist_types(obj["categories"]),
                        " ".join(obj["location"]["display_address"]),
                        obj["review_count"],
                        obj["id"],
                    )
                )
                break
    return ret

def clean(string):
    cleaned = html.unescape(re.sub(CLEANR, "", string))
    encoded = cleaned.encode("ascii", "ignore")
    decoded = encoded.decode()
    return decoded

def make_request(request, session, request_obj = None, user_agent = None):
    if request_obj:
        request.json = request_obj
    if user_agent:
        request.user_agent = user_agent

    prepared_request = request.prepare()
    response = session.send(prepared_request)
    return response

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
            ownerResponse = ""
            if data["bizUserPublicReply"] != None:
                ownerResponse = data["bizUserPublicReply"]["text"]
            ret.append(Review(author, rating, text, ownerResponse))

    # Returns array of Review objects
    return ret

def query(data):
    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = False

    session = Session()
    url = "https://www.yelp.com/gql/batch"

    for business in data:
        if business.review_count <= 53:
            user_agent = user_agent_list[random.randint(0, len(user_agent_list) - 1)]

            print(business.name)

            requestObj[0]["variables"]["encBizId"] = business.id
            requestObj[0]["variables"]["reviewsPerPage"] = business.review_count

            response = make_request(Request("POST", url), session, requestObj, user_agent)

            if response.ok:

                res_json = json.loads(response.content.decode())
                ret = getComments(res_json)

                business.reviews = {"yelp_reviews": ret}

                filePath = "./yelp_input/output/%s.json" % business.slug

                with open(filePath, "w") as outFile:
                    json.dump(business.to_dict(), outFile, ensure_ascii=True, indent=2)
                    outFile.close()
            else:
                print("ERROR: ", response.status_code)
                break
        else:
            print("Skipping ", business.name)

        time.sleep(3 + random.randint(1, 3))

def search_businesses(query_type_arr):
    ret = []
    seen = set()
    session = Session()

    for type in query_type_arr:
        query_value = query_obj[type].replace(" ", "%20")
        i = 0
        while True:
            url = f"https://api.yelp.com/v3/businesses/search?latitude=48.7519&longitude=-122.4787&term={query_value}&sort_by=best_match&limit=50&offset={i}"
            i += 50
            response = make_request(Request("GET", url, headers=my_headers), session)
            if response.ok:
                response_json = json.loads(response.text)
                if len(response_json["businesses"]) == 0:
                    break
                else:
                    for business in response_json["businesses"]:
                        if business["name"] in seen:
                            continue
                        seen.add(business["name"])
                        ret.append(business)
    
    # Returns array of Business objects
    return filter(ret)

type = pyinput.inputMenu(
    ["Companies", "Properties", "All"], lettered=True, numbered=False
).lower()

input_arr = []

if type == "all" or type.lower() == "companies":
    input_arr.append("companies")
if type == "all" or type.lower() == "properties":
    input_arr.append("properties")

ret = search_businesses(input_arr)

query(ret)
