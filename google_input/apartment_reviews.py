from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from os.path import exists
from sys import argv
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import re
import html
import json

CLEANR = re.compile('<.*?>') 

def clean(string):
    cleaned = html.unescape(re.sub(CLEANR, '', string))
    encoded = cleaned.encode("ascii", "ignore")
    decoded = encoded.decode()
    return decoded

def scroll(driver, elem_type, selector):
    check_if_exists(driver, By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[7]/div[1]/div[1]/div[1]')
    obj = check_if_exists(driver, elem_type, selector)
    scrollTop = driver.execute_script('return arguments[0].scrollTop', obj)
    prev = -1
    obj.send_keys(Keys.END)
    while scrollTop != prev:
        time.sleep(3)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", obj)
        # obj.send_keys(Keys.END)
        prev = scrollTop
        scrollTop = driver.execute_script('return arguments[0].scrollTop;', obj)
        # print("SCROLL TOP: ", scrollTop)

def check_if_exists(driver, elem_type, selector):
    try:
        # print("SELECTOR: ", selector)
        return WebDriverWait(driver, 20).until(EC.visibility_of_element_located((elem_type, selector)))
    except:
        print("Element not found")
        return None

def scrape_google_reviews(company_name):
    chrome_options = Options()
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options,service=service)

    driver.get('https://maps.google.com')
    time.sleep(2)

    search = check_if_exists(driver, By.ID, 'searchboxinput')
    search.send_keys(company_name)
    time.sleep(3)
        
    try:
        dropdown = check_if_exists(driver, By.XPATH, '//*[@id="ydp1wd-haAclf"]')
        results = dropdown.find_elements(By.CLASS_NAME, 'sW9vGe')
        if len(results) < 2:
            search.send_keys(Keys.ENTER)
        else:
            for i in range(0, len(results)):
                resultDiv = results[i]
                result = resultDiv.find_element(By.ID, 'cell%dx0' % i)
                matchFound = re.search(company_name, result.text) != None
                if matchFound:
                    result.click()
                    break
                
    
        # check_if_exists(driver, By.XPATH, '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div')
        review_count = check_if_exists(driver, By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]')
        if review_count != None:
            # Reviews Button
            check_if_exists(driver, By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]').click()
            # Reviews Scrollable
            time.sleep(3)
            scroll(driver, By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
    except Exception as e:
        print(e)
    
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
   
    review_elements = soup.find_all('div', class_=re.compile('jftiEf'))

    reviews = []
    for review_element in review_elements:
        review_text = review_element.find('span', class_=re.compile('wiI7pd'))
        author = review_element.find('div', class_=re.compile('d4r55')).text
        owner_response_element = review_element.find('div', class_=re.compile('CDe7pd'))
        owner_response_msg = []
        if owner_response_element:
            owner_response_text = owner_response_element.find('div', class_=re.compile('wiI7pd')).text
            owner_response_msg.append({
                "text": clean(owner_response_text)
                })

        review_rating = review_element.find('span', class_=re.compile('kvMYJc'))["aria-label"].split(" ")[0]
        reviews.append({
            "author": clean(author),
            "rating": float(review_rating),
            "review": "" if not review_text else clean(review_text.text),
            "ownerResponse": owner_response_msg
        })
    
    return reviews

def run():
    reviews = []
    if(len(argv) > 1):
        for i in range(1,len(argv)):
            arg = argv[i]
            filePath = './output/properties/%s.json' % arg.replace("/", "")
            # if not exists(filePath):
            print("Property: %s" % (arg))
            reviews = scrape_google_reviews(arg)
            if len(reviews) > 0:
                with open(filePath, "w") as outputFile:
                    json.dump(reviews, outputFile, ensure_ascii=True, indent=2)
                    outputFile.close() 
            # else:
            #     print("%s.json already exists\n" % arg)
    else:
        with open('./properties.json', "r") as inputFile:
            input = json.load(inputFile)
            for i in range(0, len(input)):
                company = input[i]
                companyName = company["name"]
                if company["review_count"] > 0:
                    filePath = './output/properties/%s.json' % companyName.replace("/", "")
                    if not exists(filePath):
                        print("Property %d: %s" % (i+1, companyName))
                        reviews = scrape_google_reviews(companyName)
                        if len(reviews) > 0:
                            with open(filePath, "w") as outputFile:
                                json.dump(reviews, outputFile, ensure_ascii=True, indent=2)
                                outputFile.close() 
run()