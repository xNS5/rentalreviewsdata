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
import traceback
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
after = [
    None, "eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjoyOX0=","eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0Ijo2OX0="
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

def get_business(input_list):
    whitelist = utilities.get_yelp_whitelist()
    if isinstance(input_list, list):
        ret = []
        for obj in input_list:
            if obj["location"]["country"] != "US":
                continue
            for category in obj["categories"]:
                if category["alias"] in whitelist:
                    ret.append(
                        Business(
                            obj["name"],
                            obj["rating"],
                            obj["categories"],
                            " ".join(obj["location"]["display_address"]),
                            obj["review_count"],
                            obj["id"],
                        )
                    )
                    break
        return ret
    elif isinstance(input_list, dict):
        input_obj = input_list
        if input_obj["location"]["country"] != "US":
            return
        for category in input_obj["categories"]:
            if category["alias"] in whitelist:
               return Business(
                        input_obj["name"],
                        input_obj["rating"],
                        input_obj["categories"],
                        " ".join(input_obj["location"]["display_address"]),
                        input_obj["review_count"],
                        input_obj["id"],
                    )
                
    
def make_request(request, session, request_obj = None, user_agent = None):
    try:
        if request_obj:
            request.json = request_obj
        if user_agent:
            request.user_agent = user_agent

        prepared_request = request.prepare()
        response = session.send(prepared_request)
        return response
    except Exception:
        traceback.print_exc()


def get_comments(jsonObj):
    ret = []
    business = jsonObj[0]["data"]["business"]
    review_count = business["reviewCount"]
    if review_count != None and review_count > 0:
        reviews = business["reviews"]["edges"]
        for review in reviews:
            data = review["node"]
            text = data["text"]["full"]
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

    for i, business in enumerate(data):
        user_agent = user_agent_list[random.randint(0, len(user_agent_list) - 1)]

        print(business.name)

        requestObj[0]["variables"]["encBizId"] = business.id
        if business.review_count < 43 :
            requestObj[0]["variables"]["reviewsPerPage"] = business.review_count

            response = make_request(Request("POST", url), session, requestObj, user_agent)

            if response.ok:
                res_json = json.loads(response.content.decode())
                ret = get_comments(res_json)



                business.reviews = {"yelp_reviews": ret}

                with open(f"./yelp_input/output/{business.slug}.json", "w") as outFile:
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
                response_json = json.loads(response.content.decode())
                if len(response_json["businesses"]) == 0:
                    break
                else:
                    for business in response_json["businesses"]:
                        if business["name"] in seen:
                            continue
                        seen.add(business["name"])
                        ret.append(business)
    
    # Returns array of Business objects
    return get_business(ret)

def search_list(input):
    ret = []
    seen = set()
    session = Session()

    if isinstance(input, list):
        for id in input:
            url = f"https://api.yelp.com/v3/businesses/{id}"
            response = make_request(Request("GET", url, headers=my_headers), session)
            if response.ok:
                response_json = json.loads(response.content.decode())
                if len(response_json["businesses"]) == 0:
                    break
                else:
                    for business in response_json["businesses"]:
                        if business["name"] in seen:
                            continue
                        seen.add(business["name"])
                        ret.append(business)
        return get_business(ret)
    elif isinstance(input, str):
        url = f"https://api.yelp.com/v3/businesses/{input}"
        response = make_request(Request("GET", url, headers=my_headers), session)
        if response.ok:
            response_json = json.loads(response.content.decode())
            return get_business([response_json])


def combine_manual(path):
    file_list = utilities.list_files(path)
    master_file_path = file_list[0]
    master_file = open("./%s/%s" % (path, master_file_path), "r")
    master_file_json = json.load(master_file)
    master_file.close()
    master_file_data = master_file_json[0]["data"]["business"]
    master_file_reviews = master_file_data["reviews"]["edges"]

    businessObj = search_list(f"{master_file_data['encid']}")

    reviews = []

    for i in range(1, len(file_list)):
        file = file_list[i]
        with open("./%s/%s" % (path, file), "r") as inputFile:
            input_file_json = json.load(inputFile)
            inputFile.close()
            input_reviews = input_file_json[0]["data"]["business"]["reviews"]["edges"]
            reviews.extend(input_reviews)

    master_file_reviews.extend(reviews)
    review_obj = get_comments(master_file_json)
    businessObj.reviews = {"yelp_reviews": review_obj}

    with open(f"./yelp_input/output/{businessObj.slug}.json", "w") as outFile:
        json.dump(businessObj.to_dict(), outFile, ensure_ascii=True, indent=2)
        outFile.close()


type = pyinput.inputMenu(
    ["Companies", "Properties", "One-Off ID List", "Manual Combine", "All"], lettered=True, numbered=False
).lower()

input_arr = []
ret = []


if type == "manual combine":
    directories = utilities.list_directories("./manual_extraction/")
    directories.append("All")
    selected_manual_path = pyinput.inputMenu(directories, numbered=False, lettered=True).lower()
    if selected_manual_path == "all":
        for i in range(0, len(directories)-1):
            path = directories[i]
            combine_manual(f"./manual_extraction/{path}/")
    else:
        combine_manual(f"./manual_extraction/{selected_manual_path}/")
elif type == "one-off id list":
      #  Must be space-seprated list
    input_list = pyinput.inputStr("Business IDs: ", blank=False)
    input_list = input_list.replace(r'\s+', r'\s')
    ret = search_list(input_list)

else:
    if type == "all" or type.lower() == "companies":
        input_arr.append("companies")
    if type == "all" or type.lower() == "properties":
        input_arr.append("properties")

    ret = search_businesses(input_arr)
  

query(ret)
