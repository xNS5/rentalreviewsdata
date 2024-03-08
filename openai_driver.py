import os
import json
import asyncio
from openai import OpenAI
from aiodecorators import Semaphore
from dotenv import dotenv_values

config = {
    **dotenv_values(".env")
}

client = OpenAI(
  organization=config["OPENAI_ORG"],
  api_key=config["OPENAI_KEY"]
)

property_input = "combined/properties/"
property_output = "./summaries/property_md/"

company_input = "combined/companies/"
company_output = "./summaries/company_md/"



def createArticles(path, out):
        dir_list = os.listdir(path)
        for file in dir_list:
          print(file)
          path_to_file = path + file
          with open(path_to_file, "r") as input_file:
              file_content = json.load(input_file)
              prompt = f'''Create an article in markdown for property management company or apartment complex ${file_content["name"]} with the following requirements: 
              1. This article sub-sections should be: good, great, bad, and ugly. The content of sub-section should reflect the sentiment of the heading. 
              2. Each section shall have 2 paragraphs comprised of 5 sentences for each paragraph.
              3. There shall be no identifiable information, such as the name of the reviewer.
              4. Be as detailed as possible, citing specific examples of the property management company either neglecting their duties or exceeding expectations, and any common themes such as not addressing maintenance concerns, not returning security deposits, poor communication, as well as how many times the company has replied to user reviews. 
              5. Ensure to mention either at the beginning or end of the article that these reviews are generated by ChatGPT, and is only intended to be a tool to help them find a property management company or rental property. 
              6. When referring to the user-supplied reviews, call them "user reviews". When referring to the generated output from this request, call it "article", such as "in this article...", "this article's intent is to...", etc.
              The data is as follows in JSON format: ### ${json.dumps(file_content, ensure_ascii=True, indent=2)} ###'''
              result = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful, eager assistant, helping to summarize real company reviews to create well-balanced articles on local property management companies."},
                    {"role": "user", "content": prompt}
                ]
              )
              with open(f'{out}/{file_content["name"]}.md', 'w') as output_file:
                  output_file.write(result.choices[0].message.content)
                  output_file.close()
          input_file.close()

createArticles(company_input, company_output)