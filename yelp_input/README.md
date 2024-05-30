# Yelp Reviews

Yelp's reviews are acquired using an unofficial API. The official Yelp Fusion API allows the requestor to get reviews, however only **3** reviews total are returned. For the purposes of this project, that's wholly insufficient. Fortunaely, Yelp is a "traditional" web application that has a front end and back end application that communicates via REST requests. Initially they were using a series of `GET` requests to load data, but at some point in 2024 they switched to a GraphQL-based API.

## Usage

There are technically two parts to this script: first, finding the businesses and second getting the reviews for those businesses. The first part will require one to get a [Yelp Fusion API key](https://fusion.yelp.com/). The account + key is free, however there is a request limit of 500/day which shouldn't be a problem unless these scripts are being used for an alternate purpose. Once the API key is acquired, place it in `src/yelp.env` with the key "YELP_FUSION_KEY". Create an additional key "YELP_FUSION_HEADER_TYPE" which will be "bearer". The end result will look something like "Authorization: **\[bearer\]** **\[yelp_fusion_api_key\]**". 

The second part of the script requires a valid request header. Perform a search on Yelp and navigate to the business page. In the developer tools networking tab, search for a `batch` request that has `"operationName": "GetBusinessReviewFeed"`, and copy the request header. Switch every boolean to "False" as "false" isn't valid in Python, and either remove the "encBizId" and "reviewsPerPage" or set the values to "None". 