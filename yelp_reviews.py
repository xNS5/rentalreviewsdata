import http.client as http_client
import os.path

import pyinputplus as pyinput
import json
import logging
import random
import sys
import argparse
import time
import utilities
import traceback
from dotenv import dotenv_values
from utilities import Review, Business
from requests import Request, Session

http_client.HTTPConnection.debuglevel = 0

config = {**dotenv_values(".env")}

file_paths = utilities.get_file_paths()

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

# This is essentially the "index" value used for paginating Yelp reviews
after = [
    None, "eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjozOX0=","eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0Ijo3OX0=","eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjoxMTl9","eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjoxNTl9","eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjoxOTl9", "eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjoyMzl9", "eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjoyNzl9", "eyJ2ZXJzaW9uIjoxLCJ0eXBlIjoib2Zmc2V0Iiwib2Zmc2V0IjozMTl9",
]

my_headers = {
    "Authorization": f'Bearer {config["YELP_FUSION_KEY"]}',
}


verbose = False


output_path = f"{file_paths['parent_path']}/{file_paths['yelp']}"


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

def get_request_obj(variables):
    return {
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
                **variables
            },
            "extensions": {
                "operationType": "query",
                "documentId": "ef51f33d1b0eccc958dddbf6cde15739c48b34637a00ebe316441031d4bf7681",
            },
        }

def get_business(input_list):
    whitelist = utilities.get_yelp_category_whitelist()
    if isinstance(input_list, list):
        ret = []
        for input_obj in input_list:
            if input_obj["location"]["country"] != "US":
                continue
            for category in input_obj["categories"]:
                if category["alias"] in whitelist:
                    ret.append(
                        Business(
                            input_obj["name"],
                            input_obj["rating"],
                            input_obj["categories"],
                            " ".join(input_obj["location"]["display_address"]),
                            input_obj["review_count"],
                            input_obj["id"],
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
                        input_obj["reviewCount"],
                        input_obj["id"],
                    )

def get_comments(jsonObj):
    _ret = []
    business = jsonObj["data"]["business"]
    review_count = business["reviewCount"]
    if review_count is not None and review_count > 0:
        reviews = business["reviews"]["edges"]
        for review in reviews:
            data = review["node"]
            text = data["text"]["full"]
            author = data["author"]["displayName"]
            rating = data["rating"]
            owner_response = ""
            if data["bizUserPublicReply"] is not None:
                owner_response = data["bizUserPublicReply"]["text"]
            _ret.append(Review(author, rating, text, owner_response))

    # Returns array of Review objects
    return _ret

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

        request_obj = get_request_obj({"encBizId":  business.id})

        ret_arr = []

        if business.review_count < 43 :
            request_obj["variables"]["reviewsPerPage"] = business.review_count
            response = make_request(Request("POST", url), session, request_obj, user_agent)
            if response.ok:
                res_json = json.loads(response.content.decode())
                ret_arr.extend(get_comments(res_json))
            else:
                print("ERROR: ", response.status_code)
                break
        else:
            request_obj["variables"]["reviewsPerPage"] = 40
            temp = []
            # "After" array is how Yelp indexes/paginates the reviews in increments of 10 reviews/page. 
            for i in range(len(after)):
                request_obj["variables"]["after"] = after[i]
                response = make_request(Request("POST", url), session, request_obj, user_agent)
                if response.ok:
                    res_json = json.loads(response.content.decode())
                    res_reviews = get_comments(res_json)
                    temp.extend(res_reviews)
                    if len(res_reviews) < 40:
                        ret_arr.extend(temp)
                        break    
                else:
                    print(response.status_code, json.dumps(response.content.decode(), indent=2))
                    break

        if len(ret_arr) > 0:
            business.reviews = {"yelp_reviews": ret_arr}

            with open(f"{output_path}/{business.slug}.json", "w") as out_file:
                json.dump(business.to_dict(), out_file, ensure_ascii=True, indent=2)
                out_file.close()

        time.sleep(3 + random.randint(1, 3))

def search_businesses(query_type_arr):
    ret = []
    seen = set()
    session = Session()
    name_blacklist = utilities.get_company_blacklist()

    for query_value in query_type_arr:
        i = 0
        while True:
            url = f'https://api.yelp.com/v3/businesses/search?latitude=48.7519&longitude=-122.4787&term={query_value.replace(" ", "%20")}&sort_by=best_match&limit=50&offset={i}'
            i += 50
            response = make_request(Request("GET", url, headers=my_headers), session)
            if response.ok:
                response_json = json.loads(response.content.decode())
                if len(response_json["businesses"]) == 0 or i > response_json['total']:
                    break
                else:
                    for business in response_json["businesses"]:
                        temp_slug = utilities.get_slug(business["name"])
                        if business["name"] in seen or temp_slug in name_blacklist or 'remax' in temp_slug or "muljat" in temp_slug:
                            continue
                        seen.add(business["name"])
                        ret.append(business)
            else:
                break
    
    # Returns array of Business objects
    return get_business(ret)

def search_list(input):
    ret = []
    seen = set()
    session = Session()
    name_blacklist = utilities.get_company_blacklist()

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
                        temp_slug = utilities.get_slug(business["name"])
                        if business["name"] in seen or temp_slug in name_blacklist or 'remax' in temp_slug:
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

def get_params():
    query_type_list = ["companies", "properties", "custom", "all"]
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--type", required=True, help="Query type: Companies, Properties, Custom, All")
        parser.add_argument("-v", "--verbose", required=False, help="Verbose Output flat", action="store_true")

        args = parser.parse_args()

        global verbose
        verbose = args.verbose is not None and args.verbose == True

        if args.type.lower() not in query_type_list:
            print("Invalid Query Type", file=sys.stderr)
            exit(-1)

        return args.type.lower()

    return pyinput.inputMenu(
            query_type_list, lettered=True, numbered=False
        ).lower()


if __name__ == "__main__":
    if not utilities.path_exists(output_path):
        utilities.create_directory(output_path)

    query_obj = utilities.get_yelp_config()['query_obj']
    query_type = get_params()
    match query_type:
        case "custom":
            input_list = pyinput.inputStr("Business IDs (Space-Separated): ", blank=False)
            input_list = input_list.replace(r'\s+', r'\s')
            ret = search_list(input_list)
        case "all":
            ret = search_businesses(list(query_obj.values()))
        case _:
            ret = search_businesses([query_obj[query_type]])

    query(ret)
