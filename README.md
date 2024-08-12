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

### Yelp

Yelp has an official API, however it only returns 3 reviews per business -- not super helpful for my specific purposes. It is important to note that in order to get the list of businesses for Yelp and the business IDs one needs to use the official API. As it happens, Yelp also has unofficial REST API -- which I was able to use to my advantage. Technically speaking they had a REST API when I started this project, and within the last year or so switched to a GraphQL-based API. This required me to start my scripts from scratch, but I was able to get all of the data I needed regardless. To prevent my requests from getting flagged and subsequently blocked, I ensured that the requests used a pseudo-random user agent in addition to adding time-outs that sent requests at pseudo-random intervals. Once I had the data, I needed to process it. Yelp's search results returned a mix of relevant and semi-relevant results -- meaning if I were to search for "Property Management Company", it would not only return property management companies but also real estate agents, agencies, rental maintenance companies, real estate photographers, etc. 


### Google

As mentioned previously, Google chunks their data. Inspecting the network requests doesn't return anythin meaningful, so the next (and most tedious, in my experience) course of action would be to use Selenium to automate the process, as well as some kind of HTML parser to extract the data I need. Due to the fragile nature of using Selenium in this way, the process needed to be broken down into two parts: first, a list of business names is needed. Second, the reviews for those companies needed to be gathered. Using Selenium introduced a number of tedious steps that the average person wouldn't have needed to take into account; steps such as checking to see if the company has an address, checking to see if a company has reviews, clicking on the "reviews" button to bring the reviews into focus, scrolling through those reviews and waiting for subsequent reviews to load, etc.


### OpenAI

Once the data has been gathered and cleaned up, the next step becomes fine tuning the OpenAI prompt to yield the best results. This is the prompt that is presently used:

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
