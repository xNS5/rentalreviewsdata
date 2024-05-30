# Google Reviews

This is a more traditional web scraping script in that this uses Selenium to automate scraping the reviews as opposed to simply using HTTP requests like in the Yelp script. 

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