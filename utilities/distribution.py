import json

import utilities

with open("articles/triple-rock-apartments.json", 'r') as input_file:
    input_json = json.load(input_file)
    if "distribution" not in input_json:
        distribution = utilities.calculate_distribution(input_json)
        print(json.dumps(distribution, indent=2))