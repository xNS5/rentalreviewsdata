import os
from openai import OpenAI
from dotenv import dotenv_values

config = {
    **dotenv_values(".env")
}

client = OpenAI(
  organization=config["OPENAI_ORG"],
  api_key=config["OPENAI_KEY"]
)

apartment_complex_input = "./summaries/apartment_complex"
apartment_complex_output = "./summaries/apartment_complex_md"

property_management_input = "./summaries/property_management"
property_management_output = "./summaries/property_management_md"


def createArticles(path, out):
    dir_list = os.listdir(path)
    for file in dir_list:
        full_path = f'{path}/{file}'
        with open(full_path, "r") as input_file:
            file_content = input_file.read();
            prompt = f'Create an article in markdown based on this data. 
            This article should include good, great, bad, and ugly things about this property management company named ${file[:-5]}. 
            Make note of the average review rating at the very top of the article, and any common themes such as not addressing maintenance concerns, not returning security deposits, communication, as well as how many times the company has replied to user reviews. 
            Ensure that there is no identifiable information present, and to be as detailed as possible. 
            The data is as follows in JSON format: {file_content}'
            result = client.chat.completions.create(
              model="gpt-4-1106-preview",
              messages=[
                  {"role": "system", "content": "You are a helpful assistant to a journalist writing articles on local property management companies."},
                  {"role": "user", "content": prompt}
              ]
            )
            with open(f'{out}/{file}.md', 'w') as output_file:
                output_file.write(result.choices[0].message.content)
                output_file.close()
        input_file.close()

createArticles(property_management_input, property_management_output)