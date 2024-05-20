# Requires a Yelp Fusion account + API key https://fusion.yelp.com/
# Shouldn't require payment/payment method

import json
import pyinputplus as pyinput
from dotenv import dotenv_values
from requests import Request, Session, get
import http.client as http_client
import utilities

config = {**dotenv_values("yelp.env")}

query_obj = {
    "companies": "property management companies",
    "properties": "apartment complexes",
}

my_headers = {
    "Authorization": f'Bearer {config["YELP_FUSION_KEY"]}',
}

def filter(jsonObj):
    ret = []
    whitelist = utilities.get_yelp_whitelist()
    for obj in jsonObj:
        if obj["location"]["country"] != "US":
            continue
        for category in obj["categories"]:
            if category["alias"] in whitelist:
                print(obj["name"])
                ret.append(obj)
                break
    return ret


def query(query_type_arr):
    ret = []
    seen = set()
    for type in query_type_arr:
        session = Session()
        query_value = query_obj[type].replace(" ", "%20")
        i = 0
        while True:
            url = f"https://api.yelp.com/v3/businesses/search?location=Bellingham%2C%20WA&term={query_value}&sort_by=best_match&limit=20&offset={i}"
            i += 10
            req = Request("GET", url, headers=my_headers)
            prepared_request = req.prepare()
            response = session.send(prepared_request)
            response_json = json.loads(response.text)
            if len(response_json["businesses"]) == 0:
                break
            else:
                for business in response_json["businesses"]:
                    if business["name"] in seen:
                        continue
                    seen.add(business["name"])
                    ret.append(business)
    ret = filter(ret)
    with open(f"yelp_input/query_response.json", "w") as outFile:
        json.dump(ret, outFile, ensure_ascii=True, indent=2)
        outFile.close()


type = pyinput.inputMenu(["Companies", "Properties", "All"], lettered=True, numbered=False).lower()

input_arr = []

if type == "all" or type.lower() == "companies":
    input_arr.append("companies")
if type == "all" or type.lower() == "properties":
    input_arr.append("properties")

query(input_arr)
