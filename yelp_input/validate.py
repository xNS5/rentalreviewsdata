import os
import json

#  Validate and clean up

google_set = set()

with open("/Users/michaelkennedy/Git/osp/rentalreviewsdata-driver/google_input/propertymanagementcompanies.json", 'r') as google:
    ret = []
    google_data = json.load(google)
    for business in google_data:
        google_set.add(business["name"])
    google.close()

with open("./bellingham_property_management.json", "r") as yelp:
    yelp_data = json.load(yelp)["businesses"]
    ret = []
    for business in yelp_data:
        if business["name"] not in google_set:
            print(business["name"])
    
  
    