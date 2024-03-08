from requests import Request, Session
import json
import random
from io import BytesIO

requestObj = [
    {
        "operationName": "GetBusinessReviewFeed",
        "variables": {
            "encBizId": "gzhgngNDpomvSO2CQsxLnQ",
            "reviewsPerPage": 10,
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
            "guv": "DAAFCD0158DCB3F2",
            "minConfidenceLevel": "HIGH_CONFIDENCE",
            "highlightType": "",
            "highlightIdentifier": "",
            "isHighlighting": False,
        },
        "extensions": {
            "operationType": "query",
            "documentId": "ef51f33d1b0eccc958dddbf6cde15739c48b34637a00ebe316441031d4bf7681",
        },
    },
    {
        "operationName": "GetMessagingWidgetDetails",
        "variables": {"BizEncId": "gzhgngNDpomvSO2CQsxLnQ", "deviceType": "WWW"},
        "extensions": {
            "operationType": "query",
            "documentId": "555af6ca04af99054b4a8cc8482079459d0e4235d9bde0f9dc4e45a1d46e11d8",
        },
    },
]

header = {
    "Host": "www.yelp.com",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "content-type": "application/json",
    "x-apollo-operation-name": "GetBusinessReviewFeed,GetMessagingWidgetDetails",
    "Origin": "https://www.yelp.com",
    "DNT": "1",
    "Sec-GPC": "1",
    "Alt-Used": "www.yelp.com",
    "Connection": "keep-alive",
    "Referer": "https://www.yelp.com/biz/landmark-real-estate-management-bellingham?osq=Property+Management+Companies",
    "Cookie": "location=%7B%22place_id%22%3A+%222087%22%2C+%22location_type%22%3A+%22locality%22%2C+%22country%22%3A+%22US%22%2C+%22latitude%22%3A+48.759074%2C+%22address1%22%3A+%22%22%2C+%22display%22%3A+%22Bellingham%2C+WA%22%2C+%22state%22%3A+%22WA%22%2C+%22longitude%22%3A+-122.476935%2C+%22max_latitude%22%3A+48.808291%2C+%22county%22%3A+%22Whatcom+County%22%2C+%22unformatted%22%3A+%22Bellingham%2C+WA%22%2C+%22accuracy%22%3A+4%2C+%22provenance%22%3A+%22YELP_GEOCODING_ENGINE%22%2C+%22min_latitude%22%3A+48.709857%2C+%22max_longitude%22%3A+-122.4395777%2C+%22parent_id%22%3A+%22iLLTK46DbXJUMXp9HcZfvA%22%2C+%22address2%22%3A+%22%22%2C+%22city%22%3A+%22Bellingham%22%2C+%22min_longitude%22%3A+-122.514293%2C+%22zip%22%3A+%22%22%2C+%22address3%22%3A+%22%22%2C+%22borough%22%3A+%22%22%2C+%22isGoogleHood%22%3A+false%2C+%22language%22%3A+null%2C+%22neighborhood%22%3A+%22%22%2C+%22polygons%22%3A+null%2C+%22usingDefaultZip%22%3A+false%2C+%22confident%22%3A+null%7D; hl=en_US; wdi=2|DAAFCD0158DCB3F2|0x1.8d2bcbf47cf46p+30|11c22e05ac9783b2; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Mar+20+2023+12%3A02%3A28+GMT-0700+(Pacific+Daylight+Time)&version=6.34.0&isIABGlobal=false&hosts=&consentId=bd7890cb-b22b-4e58-9d95-b7a1ebc06843&interactionCount=1&landingPath=NotLandingPage&groups=BG51%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1%2CC0004%3A0&AwaitingReconsent=false; zss=6BlkSOj-U8XRlSyuk-fkCtN3WdGcZA; xcj=1|uNeqzPPL9j84J8--rbgnB8TyKn4VBHE4wOfJ0f1HZR4; bsi=1%7Cd7865518-ac02-45f3-93b2-f40b68e13a7d%7C1709062187905%7C1709062149911; spid.d161=9bb8c225-f15d-4c68-9287-6333dc588035.1708730622.3.1709062187.1708738536.1a64f77b-afba-465a-b928-6a98f55339d4.aac6bb66-d469-4d1f-8db8-dac354019fcd.09aa58ba-26f1-4f4d-950c-19592606fa47.1709062152604.9; hsfd=0; datadome=YxTgN4Gk0yNv15AFtytTf0F5CyFGNLKY8fvnEaVf7pJ96vG3Ty4zdHfj8fp0BpZawCISIuK0LyGEiZtFWUfAiliZGas7uJrq_177h11OP7JYbT2YXvFFt7Uku6JxesoF; bse=dc02f6050aa0468b952bec2d0f683043; spses.d161=*; recentlocations=",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
}

user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
]

url = "https://www.yelp.com/gql/batch"

content_length = len(json.dumps(requestObj))
print(content_length)

user_agent = user_agent_list[random.randint(0, len(user_agent_list) - 1)]

# header["Content-Length"] = str(content_length)
s = Session()
req = Request('POST', url, json=requestObj)
prepped = req.prepare()
response = s.send(prepped)
if response.status_code == 200:
    print(json.dumps(response.content.decode(), indent=2))
else:
    print(response.status_code)