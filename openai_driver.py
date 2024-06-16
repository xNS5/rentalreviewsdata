# I feel like this one is pretty self explanatory, but it pipes all of the data to OpenAI and adds the returned summary to a file


import json
import utilities
from sys import argv
from asyncio import Semaphore, gather, run, as_completed
from openai import AsyncOpenAI
from dotenv import dotenv_values

config = {
    **dotenv_values(".env")
}

async_client = AsyncOpenAI(
       api_key=config["OPENAI_KEY"]
)

reviews_path = "./merged_reviews"
output_path = "./articles"

def get_prompt(file_content):
     return f'''Create an article for the {file_content["company_type"]} {file_content["name"]} with the following requirements: 
              1. This article sub-sections should be: good, great, bad, and ugly. The content of sub-section should reflect the sentiment of the heading.
              2. Each section shall have 2 paragraphs comprised of 3-5 sentences for each paragraph.
              3. If there are not enough reviews to generate enough data, each section shall have only 1 paragraph comprised of 3-5 sentences.
              4. There shall be no identifiable information in the article, such as the name of the reviewer.
              5. Be as detailed as possible, citing specific examples of the property management company either neglecting their duties or exceeding expectations, and any common themes such as not addressing maintenance concerns, not returning security deposits, poor communication, as well as how many times the company has replied to user reviews. 
              6. When referring to the user-supplied reviews, call them "user reviews". When referring to the generated output from this request, call it "article", such as "in this article...", "this article's intent is to...", etc.
              7. The data shall be a single line string, without markdown-style backticks.
              8. The data shall not have any control characters, such as newlines or carriage returns. 

              The article structure shall have the following requirements:
              1. The resulting article shall be contained in a HTML <article class="review-summary"></article> tag.
              2. Each sub-section shall be contained in <section></section> tags. 
              3. A sub-section heading shall be contained in a <heading></heading> tag.
              4. The heading text shall be contained in <h2></h2> tag. 
              5. The sub-section content shall be contained in <p class="review-content"></p> tags.
              
              The data is as follows in JSON format, with the reviews contained in the "reviews" key: ### {json.dumps(file_content, ensure_ascii=True, indent=2)} ###'''
        
        
async def create_articles_async(file_json):
     prompt = get_prompt(file_json)
     return await async_client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant whose job is to summarize real company reviews to create well-balanced articles on local property management companies."},
                    {"role": "user", "content": prompt}
                ],
              )
        
async def rate_limiter(file_path: str, semaphore: Semaphore):
     async with semaphore:
          with open(file_path, "r") as input_file:
            file_json = json.load(input_file)
            print(f"{file_json['name']}")
            input_file.close()
            result = await create_articles_async(file_json)
            return {
                 **file_json,
                "summary": result.choices[0].message.content.replace('\n', '')
            }
     

async def async_driver(path, out):
  file_list = utilities.list_files(path)
  semaphore = Semaphore(5)
  tasks = [rate_limiter(f"{path}/{file}", semaphore) for file in file_list]
  result = await gather(*tasks)
  for res in result:
      with open(f"{out}/{res['slug']}.json", 'w') as output_file:
          json.dump(res, output_file, indent=2, ensure_ascii=True)
          output_file.close()
          

run(async_driver(reviews_path, output_path))