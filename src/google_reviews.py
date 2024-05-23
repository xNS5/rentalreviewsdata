# Uses selenium webdriver to get information about companies and apartment complexes

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from sys import argv
import time
import re
import html
import json
import traceback
import utilities
from utilities import Review, Business


NUMS = re.compile("[^0-9]")

CLEANR = re.compile("<.*?>")

whitelist = utilities.get_google_whitelist()


def clean(string):
    cleaned = html.unescape(re.sub(CLEANR, "", string))
    encoded = cleaned.encode("ascii", "ignore")
    decoded = encoded.decode()
    return decoded

def validate():
    path = "./google_input/output"
    files = utilities.listFiles(path)
    for file in files:
        with open(file, "r") as inputFile:
            file_json = json.load(inputFile)
            for key in ["name", "slug", "company_type", "google_reviews"]:
                assert file_json[key] is not None and len(file_json[key]) > 0, f"{file_json['name']}: {key} zero length"


def scroll(driver, obj):
    scrollTop = driver.execute_script("return arguments[0].scrollTop", obj)
    scrollTopSet = set()
    while scrollTop not in scrollTopSet:
        scrollTopSet.add(scrollTop)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", obj)
        scrollTop = driver.execute_script("return arguments[0].scrollTop", obj)
        time.sleep(3)


def check_if_exists(driver, elem_type, selector):
    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((elem_type, selector))
        )
    except:
        return None


def get_reviews(driver):
    try:
        # Reviews Button
        check_if_exists(
            driver,
            By.XPATH,
            '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[3]/div/div/button[2]',
        ).click()
        # Reviews Scrollable
        time.sleep(3)
        scrollable = check_if_exists(
            driver,
            By.XPATH,
            '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]',
        )
        
        scroll(driver, scrollable)
        
        # If the review has a "See More" button, click it
        more_buttons = scrollable.find_elements(By.CSS_SELECTOR, '.w8nwRe.kyuRq')

        for button in more_buttons:
            button.click()

        soup = BeautifulSoup(driver.page_source, "html.parser")

        review_elements = soup.find_all("div", class_=re.compile("jftiEf"))

        reviews = []
        for review_element in review_elements:
            review_text = review_element.find("span", class_=re.compile("wiI7pd"))
            author = review_element.find("div", class_=re.compile("d4r55")).text
            owner_response_element = review_element.find("div", class_=re.compile("CDe7pd"))

            owner_response_msg = None
            if owner_response_element is not None:
                owner_response_msg = owner_response_element.find("div", class_=re.compile("wiI7pd")).text

            review_rating = review_element.find("span", class_=re.compile("kvMYJc"))["aria-label"].split(" ")[0]

            review_text = review_text.text if review_text else ""

            reviews.append(Review(author, review_rating, review_text, owner_response_msg))

        return reviews
    except Exception as e:
        traceback.print_exc()
        return []


def scrape_google_companies(search_param, url, element_selector):
    chrome_options = Options()
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=chrome_options, service=service)

    driver.get(url)
    time.sleep(2)

    search = driver.find_element(By.ID, "searchboxinput")
    search.send_keys(search_param)
    time.sleep(1)
    search.send_keys(Keys.RETURN)
    time.sleep(3)

    # Loads all elements in scroll bar
    scrollable = check_if_exists(
        driver,
        By.XPATH,
        '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]',
    )
    scroll(driver, scrollable)

    driver.execute_script(
        'var element = document.querySelector(".RiRi5e"); if (element)element.parentNode.removeChild(element);'
    )

    # Gets all elements that represent a business
    companyElements = scrollable.find_elements(By.CSS_SELECTOR, element_selector)

    nameSet = set()

    for element in companyElements:
        try:
            element.click()
            time.sleep(4)

            company_title = check_if_exists(
                driver,
                By.XPATH,
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1',
            )

            if company_title is not None and company_title.text not in nameSet:
                company_title = company_title.text
                print(company_title)
                nameSet.add(company_title)

                company_type = check_if_exists(
                    driver,
                    By.XPATH,
                    '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/span/span/button',
                )

                location = check_if_exists(
                    driver,
                    By.XPATH,
                    '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[3]/button/div/div[2]/div[1]',
                )
                review_count = check_if_exists(
                    driver,
                    By.XPATH,
                    '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span',
                )
                avg_rating = check_if_exists(
                    driver,
                    By.XPATH,
                    '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]',
                )
                
                if company_type == None:
                    continue
                 
                if location == None or ("WA" not in location.text and "Washington" not in location.text):
                    continue
                
                if review_count is None:
                    continue
                
                
                location = location.text
                company_type = utilities.get_whitelist_types(company_type.text)
                avg_rating = avg_rating.text
                review_count = review_count.text
                
                # Removing non alphanumeric + whitespace characters (e.g. CompanyName Inc.) would have the "." removed
                slug = utilities.get_slug(company_title)

                with open("./google_input/output/%s.json" % slug, "w") as outputFile:
                    json.dump(Business(company_title, avg_rating, company_type, location, review_count, None, {"google_reviews": get_reviews(driver)}).to_dict(), outputFile, ensure_ascii=True, indent=2)
                    outputFile.close()
            else:
                print("%s already seen -- skipping" % company_title.text)
        except Exception:
            traceback.print_exc()
    driver.quit()


with open("./google_input/config.json", "r") as configFile:
    config = json.load(configFile)
    for conf in config[0]:
        scrape_google_companies(conf["query"], conf["url"], conf["css_selector"])