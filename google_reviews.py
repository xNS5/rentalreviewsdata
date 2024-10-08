# Uses selenium webdriver to get information about companies and apartment complexes

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import re
import json
import traceback
import utilities
import pyinputplus as pyinput
from utilities import Review, Business

custom = False

def get_attribute(strategy):
    strategies = {
        "xpath": By.XPATH,
        "css_selector": By.CSS_SELECTOR,
        "id": By.ID,
        "name": By.NAME,
        "class_name": By.CLASS_NAME,
        "tag_name": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }
    return strategies[strategy]


def validate():
    path = "google"
    files = utilities.list_Files(path)
    for file in files:
        if file.lower().endswith(".json"):
            with open(file, "r") as inputFile:
                file_json = json.load(inputFile)
                for key in ["name", "slug", "company_type", "google_reviews"]:
                    assert (
                        file_json[key] is not None and len(file_json[key]) > 0
                    ), f"{file_json['name']}: {key} zero length"
                inputFile.close()


def scroll(driver, obj):
    scrollTop = driver.execute_script("return arguments[0].scrollTop", obj)
    scrollTopSet = set()
    while scrollTop not in scrollTopSet:
        scrollTopSet.add(scrollTop)
        # If the review has a "See More" button, click it
        more_buttons = driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")

        for button in more_buttons:
            button.click()

        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", obj)
        scrollTop = driver.execute_script("return arguments[0].scrollTop", obj)
        time.sleep(3)


def check_if_exists(driver, elem_type, selector):
    try:
        return WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((elem_type, selector))
        )
    except:
        return None


def get_reviews(driver, config):
    try:
        # Reviews Button
        review_button_selector = config["reviews_button"]
        check_if_exists(
            driver,
            get_attribute(review_button_selector["by"]),
            review_button_selector["selector"],
        ).click()
        # Reviews Scrollable
        time.sleep(3)
        review_scrollable_selector = config["reviews_scrollable"]
        scrollable = check_if_exists(
            driver,
            get_attribute(review_scrollable_selector["by"]),
            review_scrollable_selector["selector"],
        )

        scroll(driver, scrollable)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        review_elements = soup.find_all("div", class_=re.compile("jftiEf"))

        reviews = []
        for review_element in review_elements:
            review_text = review_element.find("span", class_=re.compile("wiI7pd"))
            author = review_element.find("div", class_=re.compile("d4r55")).text
            owner_response_element = review_element.find(
                "div", class_=re.compile("CDe7pd")
            )

            owner_response_msg = None
            if owner_response_element is not None:
                owner_response_msg = owner_response_element.find(
                    "div", class_=re.compile("wiI7pd")
                ).text

            review_rating = review_element.find("span", class_=re.compile("kvMYJc"))[
                "aria-label"
            ].split(" ")[0]

            review_text = review_text.text if review_text else ""

            reviews.append(
                Review(author, review_rating, review_text, owner_response_msg)
            )

        return reviews
    except Exception as e:
        traceback.print_exc()
        return []


def get_company(driver, config):
    nameSet = set()
    name_blacklist = utilities.get_company_blacklist()

    company_title_selector = config["company_title"]
    company_title = check_if_exists(
        driver,
        get_attribute(company_title_selector["by"]),
        company_title_selector["selector"],
    )

    if company_title is not None:
        if company_title.text not in nameSet:
            company_title = company_title.text
            print(company_title)

            company_type_selector = config["company_type"]
            company_type = check_if_exists(
                driver,
                get_attribute(company_type_selector["by"]),
                company_type_selector["selector"],
            )

            location_selector = config["location"]
            location = check_if_exists(
                driver,
                get_attribute(location_selector["by"]),
                location_selector["selector"],
            )

            review_count_selector = config["review_count"]
            review_count = check_if_exists(
                driver,
                get_attribute(review_count_selector["by"]),
                review_count_selector["selector"],
            )

            avg_rating_selector = config["avg_rating"]
            avg_rating = check_if_exists(
                driver,
                get_attribute(avg_rating_selector["by"]),
                avg_rating_selector["selector"],
            )

            if company_type == None:
                print(f"Company Type for {company_title} is Null")
                return

            # Just because the address element isn't present doesn't mean it isn't in Bellingham -- e.g. ACP Property Managment + Fast Property Management. 
            if location == None:
                print(f"Location for {company_title} missing")
            elif "WA" not in location.text and "Washington" not in location.text:
                print(f"Location for {company_title} is not based in WA")
                return

            if review_count is None:
                print(f"No reviews for {company_title}")
                return
            
            # Removing non alphanumeric + whitespace characters (e.g. CompanyName Inc.) would have the "." removed
            slug = utilities.get_slug(company_title)
            
            if slug in name_blacklist:
                print(f"{company_title} is a blacklisted company. Skipping...")
                return

            location = location.text if location != None else ""
            company_type = company_type.text
            avg_rating = avg_rating.text
            review_count = review_count.text

            nameSet.add(company_title)

            with open("google/%s.json" % slug, "w") as outputFile:
                reviews = get_reviews(driver, config)

                json.dump(
                    Business(
                        company_title,
                        avg_rating,
                        company_type,
                        location,
                        review_count,
                        None,
                        {"google_reviews": reviews},
                    ).to_dict(),
                    outputFile,
                    ensure_ascii=True,
                    indent=2,
                )
                outputFile.close()
        else:
            print("%s already seen -- skipping" % company_title.text)
    else:
        print("Missing company title")


def scrape_google_companies(search_param, url, config):

    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    time.sleep(2)

    if custom == False:
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
        company_element_selector = config["company_elements"]
        companyElements = scrollable.find_elements(
            get_attribute(company_element_selector["by"]),
            company_element_selector["selector"],
        )

        for element in companyElements:
            try:
                element.click()
                time.sleep(4)
                get_company(driver, config)
            except Exception:
                traceback.print_exc()
    else:
        get_company(driver, config)
    driver.quit()


config = utilities.get_google_config()

type = pyinput.inputMenu(
    ["Companies", "Properties", "Custom", "All"], lettered=True, numbered=False
).lower()

utilities.create_directory("data/google")


if type == "companies":
    scrape_google_companies(
        config["queries"][0]["query"], config["queries"][0]["url"], config["queries"][0]["selectors"]
    )
elif type == "properties":
    scrape_google_companies(
        config["queries"][1]["query"], config["queries"][1]["url"], config["queries"][1]["selectors"]
    )
elif type == "custom":
    # Space Separated
    url_list = pyinput.inputStr("Url List (space separated): ").split(" ")
    custom = True
    for url in url_list:
        scrape_google_companies(None, url, config["custom"]["selectors"])
else:
    for query in config['queries']:
        scrape_google_companies(query["query"], query["url"], query["selectors"])
