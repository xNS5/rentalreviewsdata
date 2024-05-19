# Requires a Yelp Fusion account + API key https://fusion.yelp.com/
# Shouldn't require payment/payment method

import json
import re
import pyinputplus as pyinput
from dotenv import dotenv_values
from os.path import exists
from requests import Request, Session, get
import http.client as http_client

config = {**dotenv_values("yelp.env")}

query_obj = {
    "companies": "property%20management%20companies",
    "properties": "apartment%20complexes",
}

my_headers = {
    "Authorization": f'Bearer {config["YELP_FUSION_KEY"]}',
}


def query(query_type):
    session = Session()
    query_value = query_obj[query_type]
    ret = []
    seen = set()
    i = 0
    while True:
        url = f"https://api.yelp.com/v3/businesses/search?location=Bellingham%2C%20WA&term={query_value}&sort_by=best_match&limit=20&offset={i}"
        i += 10
        req = Request("GET", url, headers=my_headers)
        prepared_request = req.prepare()
        response = session.send(prepared_request)
        print(response.status_code)
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


type = pyinput.inputMenu(
    ["Companies", "Properties", "All"], lettered=True, numbered=False
).lower()
if type == "all":
    query("companies")
    query("properties")
else:
    query(type.lower())
