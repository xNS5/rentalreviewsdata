# Rental Reviews Data

It's no secret that property management companies and landlords have a bad reputation. These entities are in a position of power, where they control the flow of housing. It is because of this power
that many leverage their positions to take advantage of their tenants -- by raising prices, failing to ensure that the dwelling is habitable, or sometimes even violating state law. However, not all 
property management companies or landlords sink that low. Some are very attentive, and treat their tenants fairly. It would be virtually impossible to gather enough data to provide a holistic review
of private landlords, however there is plenty of data out there about property management companies and apartment complexes to give a potential renter a good idea of what they would be getting 
themselves into. 

In order to give a holistic overview of a given property management company or apartment complex, a decent amount of data is needed. After the data is gathered, there needs to be a way to process it
and make it digestible to the average person. Fortunately, the recent spike in AI popularity offered a convenient solution. AI can sometimes be hit-or-miss depending on what one asks of it, however
it's very good at ingesting data and giving insights based on that data. 

The general steps for gathering and processing this data is as follows:

1. Reviews for companies needed to be gathered. 
2. The gathered data is cleaned, and presented in a uniform format. 
3. The processed data from both websites needs to be combined to eliminate duplication. 
4. Create rules for how AI should evaluate the data, and the format the output should take.

---

## The Problem

There are two main, popular sites for leaving reviews for a company: Google and Yelp. Google chunks their data, which makes it virtually impossible for me to get the information I need via HTTP requests alone. Yelp has an "official" API, however requests only return 3 reviews per company -- not ideal for my purposes. For each website, data on both property management companies and apartment complexes needs to be gathered. There is a high likelihood that there will be overlap between the results, and a non-zero chance of the company names being slightly different between the two websites. For example, one company on Google might have "LLC" at the end while the same result on Yelp might not. Despite this minor difference, both results correspond to the same company.

# Yelp

Yelp has an official API, however it only returns 3 reviews per business -- not super helpful for my specific purposes. It is important to note that in order to get the list of businesses for Yelp and the business IDs one needs to use the official API. As it happens, Yelp also has unofficial REST API -- which I was able to use to my advantage. Technically speaking they had a REST API when I started this project, and within the last year or so switched to a GraphQL-based API. This required me to start my scripts from scratch, but I was able to get all of the data I needed regardless. To prevent my requests from getting flagged and subsequently blocked, I ensured that the requests used a pseudo-random user agent in addition to adding time-outs that sent requests at pseudo-random intervals. Once I had the data, I needed to process it. Yelp's search results returned a mix of relevant and semi-relevant results -- meaning if I were to search for "Property Management Company", it would not only return property management companies but also real estate agents, agencies, rental maintenance companies, real estate photographers, etc. 

## Usage

There are technically two parts to this script: first, finding the businesses and second getting the reviews for those businesses. The first part will require one to get a [Yelp Fusion API key](https://fusion.yelp.com/). The account + key is free, however there is a request limit of 500/day which shouldn't be a problem unless these scripts are being used for an alternate purpose. Once the API key is acquired, place it in `src/yelp.env` with the key "YELP_FUSION_KEY". Create an additional key "YELP_FUSION_HEADER_TYPE" which will be "bearer". The end result will look something like "Authorization: **\[bearer\]** **\[yelp_fusion_api_key\]**". 

The second part of the script requires a valid request header. Perform a search on Yelp and navigate to the business page. In the developer tools networking tab, search for a `batch` request that has `"operationName": "GetBusinessReviewFeed"`, and copy the request header. Switch every boolean to "False" as "false" isn't valid in Python, and either remove the "encBizId" and "reviewsPerPage" or set the values to "None". 


# Google

As mentioned previously, Google chunks their data. Inspecting the network requests doesn't return anything meaningful, so the next (and most tedious, in my experience) course of action would be to use Selenium to automate the process, as well as some kind of HTML parser to extract the data I need. Due to the fragile nature of using Selenium in this way, the process needed to be broken down into two parts: first, a list of business names is needed. Second, the reviews for those companies needed to be gathered. Using Selenium introduced a number of tedious steps that the average person wouldn't have needed to take into account; steps such as checking to see if the company has an address, checking to see if a company has reviews, clicking on the "reviews" button to bring the reviews into focus, scrolling through those reviews and waiting for subsequent reviews to load, etc. 

## Usage

Simply run `google_reviews.py` from within `src/`. The `config.json` file has all of the input parameters and XPATH/CSS selectors to get the corresponding elements on the UI. 

The "General Search" paramters share all selectors **except** for the `company_elements` CSS selector. The selectors are as follows:

* `company_elements`: when doing a "general search", a list of results are returned and each element will correspond to the `company_elements`. 
* `company_title`: this one should be pretty self explanatory, it's the name of the business. 
* `company_type`: the type of company, whether it's a property management company, real eastate agent, apartment building/complex, etc.
* `location`: the address of the company. Note: if the location *isn't* in Washington it'll skip the listing.
* `review_count`: the total number of reviews.
* `avg_rating`: the listed average review rating. 
* `reviews_button`: the button that one clicks to view the text reviews for a given company.
* `reviews_scrollable`: the part of the UI with the scroll bar, which will allow the script to load all of the review elements. 

### Note

* If the XPATH/CSS selectors need to be updated, open up Google Chrome, grab the correct XPATH selector, and paste it in the "selector" key in `config.json`. If making updates to the general searches, ensure that the selector is updated in both config objects. 
* The `custom` option is strictly for companies/searches that were missed in the initial scrape. If the input isn't a URL, it'll error out.

## Common Issues

1. The XPATH/CSS selectors need to be updated in `config.json`. Simply go into Google Chrome, copy the correct ones, and update them in the config object(s).
2. The correct `chromedriver` and/or Google Chrome isn't installed. To install `chromedriver`, see [this guide](https://skolo.online/documents/webscrapping/#pre-requisites) for Linux/MacOS specific instructions. 

#### 


### OpenAI

Once the data has been gathered and cleaned up, the next step becomes fine tuning the OpenAI prompt to yield the best results. This is the prompt:

```
Create an article for the {company type} {name} with the following requirements: 
1. This article sub-sections should be: good, great, bad, and ugly. The content of sub-section should reflect the sentiment of the heading.
2. Each section shall have 2 paragraphs comprised of 3-5 sentences for each paragraph.
3. If there are not enough detailed reviews to generate enough data, each section shall have only 1 paragraph comprised of 3-5 sentences.
4. There shall be no identifiable information in the article, such as the name of the reviewer.
5. Be as detailed as possible, citing specific examples of the property management company either neglecting their duties or exceeding expectations, and any common themes such as not addressing maintenance concerns, not returning security deposits, poor communication, as well as how many times the company has replied to user reviews.
6. If there are specific examples that describe a previous tenant's experience, paraphrase their experience and include it in the corresponding section.
7. When referring to the user-supplied reviews, call them "user reviews". When referring to the generated output from this request, call it "article", such as "in this article...", "this article's intent is to...", etc.
8. The data shall be a single line string, without markdown-style backticks.
9. The data shall not have any control characters, such as newlines or carriage returns. 
10. The article structure shall have the following template: 

"<section><h2>Good</h2><p>#section_content#</p></section>
<section><h2>Great</h2><p>#section_content#</p></section>
<section><h2>Bad</h2><p>#section_content#</p></section>
<section><h2>Ugly</h2><p>#section_content#</p></section>" 

where "#section_content#" should be replaced with the article section text. 

The data is as follows in JSON format, with the reviews contained in the "reviews" key: 
### 
{JSON file content} 
###
```

All that needs to happen after this point is add the response to the original JSON object so it can be accessed at any point. 

## Beyond Property Management Companies

In theory this code can be used for any industry. Whether it's insurance agencies, hotels, even pizza joints -- all that's required is a few tweaks to the various text-based prompts used throughout the scripts. If the company has a presence on Google or Yelp, the scripts will get the data all the same.
