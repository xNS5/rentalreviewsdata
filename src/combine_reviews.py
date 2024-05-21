import json
import os
import utilities

def getPrefix(input, delimiter):
     return input.split(delimiter)[0]

output_path = "./reviews/"
google_path = "./google_input/output/"
yelp_path = "./yelp_input/output/"

def main():

    def filter(input_path, alt_path):
        input_list = utilities.list_files(input_path)
        alt_list = utilities.list_files(alt_path)
        ret = []
        # print(file_list)
        for file in input_list:
            if not os.path.isfile(f"{alt_list}{file}"):
                utilities.copy_file(f"{input_path}{file}", f"{output_path}{file}")
            else:
                ret.append(file)
        return ret

    yelp_ret = filter(yelp_path, google_path)
    google_ret = filter(google_path, yelp_path)

    print("YELP")
    for ret in yelp_ret:
        print(ret)
    print("GOOGLE")
    for ret in google_ret:
        print(ret)


main()
