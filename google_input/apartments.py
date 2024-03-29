from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sys import argv
import time
import re
import html
import json
import traceback


NUMS = re.compile("[^0-9]")

CLEANR = re.compile('<.*?>') 

def clean(string):
    cleaned = html.unescape(re.sub(CLEANR, '', string))
    encoded = cleaned.encode("ascii", "ignore")
    decoded = encoded.decode()
    return decoded

def scroll(driver, obj):
    scrollTop = driver.execute_script('return arguments[0].scrollTop', obj)
    scrollTopSet = set()
    while scrollTop not in scrollTopSet:
        scrollTopSet.add(scrollTop)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", obj)
        scrollTop = driver.execute_script('return arguments[0].scrollTop', obj)
        time.sleep(3)

def check_if_exists(driver, elem_type, selector):
    try:
        return WebDriverWait(driver, 5).until(EC.visibility_of_element_located((elem_type, selector)))
    except:
        return None
    
def scrape_google_companies(search_param):
    chrome_options = Options()
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options,service=service)

    driver.get('https://www.google.com/maps/@48.799556,-122.544531,11.67z?entry=ttu')
    time.sleep(2)

    search = driver.find_element(By.ID, 'searchboxinput')
    search.send_keys(search_param)
    time.sleep(1)
    search.send_keys(Keys.RETURN)
    time.sleep(3)

    # Loads all elements in scroll bar
    scrollable = check_if_exists(driver, By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
    scroll(driver, scrollable)

    driver.execute_script('var element = document.querySelector(\".RiRi5e\"); if (element)element.parentNode.removeChild(element);')
    
    # Gets all elements that represent a business
    companyElements = scrollable.find_elements(By.CSS_SELECTOR, '.Nv2PK.THOPZb.CpccDe')

    companyArr = []
    nameSet = set()

    for element in companyElements:
         try:
            element.click()
            time.sleep(4)
            company_title = check_if_exists(driver, By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1').text
            if company_title not in nameSet:
                nameSet.add(company_title)
                company_type =  check_if_exists(driver, By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]')
                location = check_if_exists(driver, By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[3]/button/div/div[2]/div[1]')
                review_count =  check_if_exists(driver, By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span')
                avg_review =  check_if_exists(driver, By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]')
                if location is not None:
                    location = location.text
                
                print(company_title, location)

                companyArr.append({
                            "name": company_title,
                            "address": "" if not location else location,
                            "company_type": "None" if not company_type else company_type.text.replace("/", "\/"),
                            "review_count": 0 if review_count is None else int(re.sub(NUMS, '', review_count.text)),
                            "avg_review": "None" if not avg_review else float(avg_review.text)
                        })
            else:
                print("%s already seen -- skipping" % company_title)
                continue
         except Exception:
              traceback.print_exc()
              
    driver.quit()
    return companyArr

with open('./properties.json', "w") as outputFile:
    ret = scrape_google_companies("Apartment Complexes in Whatcom County")
    json.dump(ret, outputFile, ensure_ascii=True, indent=2)
    outputFile.close()


