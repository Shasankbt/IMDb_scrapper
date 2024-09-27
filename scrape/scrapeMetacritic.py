from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import json
import requests 
import time
import traceback

s = Service("./chromedriver")
driver = webdriver.Chrome(service=s)

from imdbFunctions import getBSfromURL
from commonFunc import load_json
from commonFunc import Colors
from commonFunc import multiThreadExec

targetFile = "../extractedData/metacritic.json"

def getFeaturedReview(imdbID):
    featured_review = {
        "tagline" : "",
        "reviewer" : "",
        "review" : ""
    }
    try:
        mainpage = getBSfromURL("https://www.imdb.com/title/" + imdbID)
        featuredReviewBoxFromWeb = mainpage.find("div", class_="sc-f65f65be-0 bBlII")
        featured_review["tagline"] = featuredReviewBoxFromWeb.find("div", class_="sc-27d2f80b-0 byaXLe").text
        featured_review["reviewer"] = featuredReviewBoxFromWeb.find("div" ,class_="sc-bb68c52e-0 dsJate").text
        featured_review["review"] = featuredReviewBoxFromWeb.find("div", class_="ipc-html-content-inner-div").text
        # print(featured_review)
    except Exception as e:
        print(f"{Colors.GREY}unable to get featured review due to {e} at {traceback.extract_tb(e.__traceback__)[0][1]} for {imdbID}")
    return featured_review

def getCriticReviews(url, imdbID, driver):
    critic_reviews = {
        "score" : "",
        "positive" : [],
        "mixed" : [],
        "negative" : []
    }
    try:
        driver.get(url + "/critic-reviews/")
        time.sleep(3)   # MetaCritic loading buffer time

        source_code = driver.page_source
        critic_soup = BeautifulSoup(source_code, "html.parser")

        try:
            critic_reviews["score"] = critic_soup.find("div", class_= "c-siteReviewScore u-flexbox-column u-flexbox-alignCenter u-flexbox-justifyCenter g-text-bold c-siteReviewScore_green g-color-gray90 c-siteReviewScore_large" ).text
        except Exception as e:
            print(f"{Colors.GREY}unable to obtain critic score for {imdbID}{Colors.RESET}")

        review_list = critic_soup.find("div", class_= "c-pageProductReviews_row g-outer-spacing-bottom-xxlarge")
        reviews_div = review_list.find_all("div", class_="c-siteReview g-bg-gray10 u-grid g-outer-spacing-bottom-large")
        reviews_count, error_count = len(reviews_div), 0
        for review_box in reviews_div:
            try:
                review = {}
                review["score"] = review_box.find("div", class_="c-siteReviewHeader_reviewScore").text
                review["reviewer"] = review_box.find("div", class_="c-siteReviewHeader_publisherLogo").text.strip()
                review["review"] = review_box.find("div", class_="c-siteReview_quote g-outer-spacing-bottom-small").text
                if int(review["score"]) > 60:
                    critic_reviews["positive"].append(review)
                elif int(review["score"]) > 30:
                    critic_reviews["mixed"].append(review)
                else:
                    critic_reviews["negative"].append(review)
            except Exception as e:
                error_count += 1
        if error_count > 0:
            print(f"{Colors.GREY}unable to obtain {error_count}/{reviews_count} critic reviews for {imdbID}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.ORANGE}unable to get critic reveiws due to {e} at {traceback.extract_tb(e.__traceback__)[0][1]} for {imdbID}{Colors.RESET}")

    return critic_reviews

def getUserReviews(url, imdbID, driver):
    user_reviews = {
        "score" : "",
        "positive" : [],
        "mixed" : [],
        "negative" : []
    }
    try:
        driver.get(url + "/user-reviews/")
        time.sleep(3)   # MetaCritic loading buffer time

        source_code = driver.page_source
        soup = BeautifulSoup(source_code, "html.parser")
        try:
            user_reviews["score"] = soup.find("div",class_="c-siteReviewScore u-flexbox-column u-flexbox-alignCenter u-flexbox-justifyCenter g-text-bold c-siteReviewScore_green c-siteReviewScore_user g-color-gray90 c-siteReviewScore_large" ).text
        except Exception as e:
            print(f"{Colors.GREY}unable to obtain user score{Colors.RESET}")
        
        review_list = soup.find("div", class_= "c-pageProductReviews_row g-outer-spacing-bottom-xxlarge")
        reviews_div = review_list.find_all("div", class_="c-siteReview g-bg-gray10 u-grid g-outer-spacing-bottom-large")
        reviews_count, error_count = len(reviews_div) , 0
        for review_box in reviews_div:
            try:
                review = {}
                review["score"] = review_box.find("div", class_="c-siteReviewHeader_reviewScore").text
                review["reviewer"] = review_box.find("a", class_="c-siteReviewHeader_username g-text-bold g-color-gray90").text.strip()
                review["review"] = review_box.find("div", class_="c-siteReview_quote g-outer-spacing-bottom-small").text

                spoiler_alert = "SPOILER ALERT: This review contains spoilers."
                if spoiler_alert in review["review"]:
                    continue
                # user_reviews.append(review)
                if int(review["score"]) > 6:
                    user_reviews["positive"].append(review)
                elif int(review["score"]) > 3:
                    user_reviews["mixed"].append(review)
                else:
                    user_reviews["negative"].append(review)
            except Exception as e:
                error_count += 1
        if error_count > 0:
            print(f"{Colors.GREY}unable to obtain {error_count}/{reviews_count} critic reviews for {imdbID}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.ORANGE}unable to get critic reveiws due to {e} at {traceback.extract_tb(e.__traceback__)[0][1]} for {imdbID}{Colors.RESET}")

    return user_reviews

def writeReviewsData(imdbID, task_idx, total_tasks, reviewsData, exiting, driver):
    if exiting.is_set():
        return
    print(f"{Colors.BLUE}starting ({task_idx}/{total_tasks}) : {imdbID}{Colors.RESET}")
    start_time = time.time()
    try:
        # --------------------------------- featured review -------------------------------------------------
        featured_review = getFeaturedReview(imdbID)
        # --------------------------------- getting metacritic website -----------------------------------------
        try:
            driver.get("https://www.imdb.com/title/" + imdbID + "/criticreviews")
            time.sleep(3)
            temp_soup = BeautifulSoup(driver.page_source, "html.parser")

            link_tag = temp_soup.find("li",class_="ipc-metadata-list__item ipc-metadata-list-item--link", attrs={"data-testid" : "metacritic-link"}).find("a")

            url = link_tag.get("href").split("?")[0]
            critic_reviews = getCriticReviews(url, imdbID, driver)
            user_reviews = getUserReviews(url, imdbID, driver)

            time.sleep(1)
            print(f"{Colors.GREEN}({task_idx})/({total_tasks}) : Scrapped successfully for {imdbID}{Colors.RESET}")
            reviewsData[imdbID] = {
                "featured-review" : featured_review,
                "critic-reviews" : critic_reviews,
                "user-reviews" : user_reviews
            }
        except Exception as e:
            print(f"{Colors.ORANGE}unable to get metacritic website due to {e} at {traceback.extract_tb(e.__traceback__)[0][1]} for {imdbID}{Colors.RESET}")
            reviewsData[imdbID] =  {
                "featured-review" : featured_review,
                "critic-reviews" : { "score" : "","positive" : [] , "mixed" : [], "negative" : [] },
                "user-reviews" : { "score" : "","positive" : [] , "mixed" : [], "negative" : [] }        
            }   
    except Exception as e:
        print(f"{Colors.RED}an error {e} has occurred for {imdbID}{Colors.RESET}")
    print(f"completed in {time.time() - start_time} sec")
    print("-------------------------------------------------------")
    
def cleanup(newData):
    with open(targetFile, "w") as file:
        file.write(json.dumps(newData))

def fullReview(review):
    #print(review)
    if review["featured-review"] == { "tagline": "", "reviewer": "", "review": "" }:
        return False
    if review["critic-reviews"] == { "score" : "","positive" : [] , "mixed" : [], "negative" : [] }:
        return False
    if review["user-reviews"] == { "score" : "","positive" : [] , "mixed" : [], "negative" : [] }:
        return False
    return True
    



with open("imdbID.txt") as file:
    imdbID_list_input = file.read().splitlines()

reviewsData = load_json(targetFile)
req_imdbID_list = list(set(imdbID_list_input) - set(reviewsData.keys()))

length = len(req_imdbID_list)

try:
    drivers = [webdriver.Chrome(service=Service("./chromedriver")) for _ in range(8)]
    multiThreadExec(writeReviewsData, req_imdbID_list, reviewsData, drivers)
except KeyboardInterrupt:
    print('Program exiting gracefully...')
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    cleanup(reviewsData)



driver.quit()
        
    