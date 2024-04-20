# Requires a Yelp Fusion account + API key https://fusion.yelp.com/
# Shouldn't require payment/payment method

import json
import re
import pyinputplus as pyinput
from dotenv import dotenv_values
from os.path import exists
from requests import Request, Session, get
import http.client as http_client

config = {
    **dotenv_values("yelp.env")
}

query_obj = {
    "companies": "property management companies",
    "properties": "apartment complexes"
}

headers = {
    "accept": "application/json",
    "Authorization": f'{config["YELP_FUSION_HEADER_TYPE"]} {config["YELP_FUSION_KEY"]}'
}

def query(query_type):
    query_value = query_obj[query_type].replace("\s+", "%20")
    ret = []
    seen = set()
    i = 0
    while True:
        url = f'https://api.yelp.com/v3/businesses/search?location=Bellingham%2C%20WA&term={query_value}&categories=&sort_by=best_match&limit=50&offset={i}'
        i+=10
        response = get(url, headers=headers)
        response_json = json.loads(response.text)
        if len(response_json["businesses"]) == 0:
            break
        else:
            for business in response_json['businesses']:
                if business['alias'] in seen:
                    continue
                ret.append(business)        

    with open(f'yelp_input/{query_type}.json', "w") as outFile:
        json.dump({"businesses": ret}, outFile,  ensure_ascii=True, indent=2)
        outFile.close()
    


type = pyinput.inputMenu(["Companies", "Properties", "All"], lettered=True, numbered=False).lower()
if type == "all":
    query("companies")
    query("properties")
else:
    query(type)