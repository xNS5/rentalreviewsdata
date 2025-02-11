# I feel like this one is pretty self explanatory, but it pipes all of the data to OpenAI and adds the returned summary to a file


import json
import math
import sys

import utilities
from sys import argv
from asyncio import Semaphore, gather, run, as_completed
from openai import AsyncOpenAI, RateLimitError
from dotenv import dotenv_values
from datetime import datetime

config = {
    **dotenv_values(".env")
}

async_client = AsyncOpenAI(
       api_key=config["OPENAI_KEY"]
)

epoch = datetime(1970, 1, 1)



disclaimer_file = utilities.get_disclaimer_map()
file_paths = utilities.get_file_paths()

input_path = f"{file_paths['parent_path']}/{file_paths['merged']}"
output_path = f"{file_paths['articles']}"

def get_prompt(file_content):
     return f'''Create an article for the {file_content["company_type"]} {file_content["name"]} with the following requirements: 
              1. This article sub-sections should be: good, great, bad, and ugly. The content of sub-section should reflect the sentiment of the heading.
              2. Each section shall have 2 paragraphs comprised of 3-5 sentences for each paragraph.
              3. If there are not enough detailed reviews to generate enough data, each section shall have only 1 paragraph comprised of 3-5 sentences.
              4. There shall be no identifiable information in the article, such as the name of the reviewer.
              5. Be as detailed as possible, citing specific examples of the property management company either neglecting their duties or exceeding expectations, and any common themes such as not addressing maintenance concerns, not returning security deposits, poor communication, as well as how many times the company has replied to user reviews.
              6. If there are specific examples that describe a previous tenant's experience, paraphrase their experience and include it in the corresponding section.
              7. When referring to the user-supplied reviews, call them "user reviews". When referring to the generated output from this request, call it "article", such as "in this article...", "this article's intent is to...", etc.
              8. The data shall be a single line string, without markdown-style backticks.
              9. The data shall not have any control characters, such as newlines or carriage returns. 
              10. The article structure shall have the following template: "<section id=\"good\"><h2>Good</h2><p>#section_content#</p></section><section id=\"great\"><h2>Great</h2><p>#section_content#</p></section><section id=\"bad\"><h2>Bad</h2><p>#section_content#</p></section><section id=\"ugly\"><h2>Ugly</h2><p>#section_content#</p></section>" where "#section_content#" should be replaced with the article section text. 

              The data is as follows in JSON format, with the reviews contained in the "reviews" key: 
              ### 
              {json.dumps(file_content, ensure_ascii=True, indent=2)} 
              ###'''
               
async def create_articles_async(file_json):
     prompt = get_prompt(file_json)
     return await async_client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant whose job is to summarize real company reviews to create well-balanced articles on local property management companies and rental properties."},
                    {"role": "user", "content": prompt}
                ],
              )
        
async def rate_limiter(file_path: str, semaphore: Semaphore):
     try:
         async with semaphore:
             with open(file_path, "r") as input_file:
                 file_json = json.load(input_file)
                 print(f"{file_json['name']}")
                 input_file.close()
                 result = await create_articles_async(file_json)

                 now = datetime.now()
                 now_in_seconds = math.ceil((now - epoch).total_seconds())

                 summary_dict = {
                     "created_timestamp": now_in_seconds,
                     "text": result.choices[0].message.content.replace('\n', ''),
                 }

                 if file_json["slug"] in disclaimer_file:
                     summary_dict["disclaimer"] = disclaimer_file[file_json["slug"]]

                 return {
                     **file_json,
                     "summary": summary_dict
                 }
     except RateLimitError as e:
         print(f"Rate Limit Error: {e.message}")
         sys.exit(-1)

     
async def async_driver(path, out, file_list = []):
    if len(file_list) == 0:
        file_list = utilities.list_files(path)
    semaphore = Semaphore(10)
    tasks = [rate_limiter(f"{path}/{file}", semaphore) for file in file_list]
    result = await gather(*tasks)
    for res in result:
        with open(f"{out}/{res['slug']}.json", 'w') as output_file:
            json.dump(res, output_file, indent=2, ensure_ascii=True)
            output_file.close()
          
run(async_driver(input_path, output_path))