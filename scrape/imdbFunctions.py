import requests
from bs4 import BeautifulSoup
import traceback
import re


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    ORANGE = '\033[38;5;208m'
    BLUE = '\033[94m'
    PINK = '\033[95m'  # Light pink
    YELLOW = '\033[93m'
    GREY = '\033[90m'

def getBSfromURL(url):
    response = requests.get(url, headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
    }, timeout=60)
    return BeautifulSoup(response.content, "html.parser")

def getEpisodes(imdbID):
    
    episodes_page = getBSfromURL("https://www.imdb.com/title/" + imdbID + "/episodes/") 
    seasons_count = len(episodes_page.find("ul", class_="ipc-tabs ipc-tabs--base ipc-tabs--align-left", attrs={"role" : "tablist"}).find_all("a"))

    obj= {}
    for season_idx in range(seasons_count):
        temp_obj = {}
        episodes_page = getBSfromURL("https://www.imdb.com/title/" + imdbID + f"/episodes/?season={season_idx+1}")
        episode_sections = episodes_page.find_all("div", class_="sc-ccd6e31b-1 fabWnN")   
        for ep_idx , section in enumerate(episode_sections):
            ep_id = section.find("a").get("href").split("/")[2]
            temp_obj[f"episode-{ep_idx+1}"] = ep_id

        obj[f"season-{season_idx+1}"] = temp_obj
    return obj

def getPlotSummary(imdbID, movie):
    try:
        plotSummaryPage = getBSfromURL("https://www.imdb.com/title/" + imdbID + "/plotsummary")
        try:
            movie["plot"] = plotSummaryPage.find_all("li" , class_ ="ipc-metadata-list__item")[1].text
        except IndexError:
            movie["plot"] = plotSummaryPage.find("li" , class_ ="ipc-metadata-list__item").text
        except AttributeError:
            movie["plot"] = ""
    except Exception as e:
        print(f"{Colors.GREY}unable to get plot summary due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET}")

def getQuotes(imdbID, movie):
    try:
        taglinePage = getBSfromURL("https://www.imdb.com/title/" + imdbID + "/taglines")
        try:
            movie["Quotes"] = [x.text for x in taglinePage.find("ul", class_= "ipc-metadata-list ipc-metadata-list--dividers-between sc-d1777989-0 FVBoi meta-data-list-full ipc-metadata-list--base").find_all("li")]
        except IndexError:
            movie["Quotes"] = []
        except AttributeError:
            movie["Quotes"] = []
    except Exception as e:
        print(f"{Colors.GREY}unable to get quotes due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET}")

def getFilmType(line):
    # Define regular expressions for each category
    episode_pattern = re.compile(r'\bEpisode\b.*\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b \d{1,2}, \d{4}', re.IGNORECASE)
    tv_mini_series_pattern = re.compile(r'\b(Tv Mini Series|TV Mini Series)\b', re.IGNORECASE)
    tv_series_pattern = re.compile(r'\b(Tv Series|TV Series)\b', re.IGNORECASE)
    year_pattern = re.compile(r'\b(19|20)\d{2}\b')

    # Check the line against each pattern and return the corresponding category
    if episode_pattern.search(line):
        return "episode"
    elif tv_mini_series_pattern.search(line):
        return "tv_mini_series"
    elif tv_series_pattern.search(line):
        return "tv_series"
    elif year_pattern.search(line):
        return "movie"
    else:
        return "other"

def getDataFromImdbID(imdbID, print_feedback = True, item_type="", episode_details = {}):
    if print_feedback:
        print(imdbID, end=" : ")

    try:   
        mainpage = getBSfromURL("https://www.imdb.com/title/" + imdbID)
        movie = {}
        movie["imdbID"] = imdbID

        movie["Title"] = mainpage.find("span" , class_ ="hero__primary-text").text
        if print_feedback:
            print(movie["Title"])
        try:    # Released
            movie["Released"] = mainpage.find("div", class_="sc-f65f65be-0 bBlII", attrs={"data-testid" : "title-details-section"}).find("ul", class_ = "ipc-inline-list ipc-inline-list--show-dividers ipc-inline-list--inline ipc-metadata-list-item__list-content base").text
        except Exception as e:
            print(f"{Colors.GREY}unable to get release date of item due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET} for id:{imdbID}")
        try:    # imdbRating
            movie["imdbRating"] = mainpage.find("div", class_ = "sc-bde20123-2 cdQqzc").find("span").text
        except Exception as e:
            print(f"{Colors.GREY}unable to get imdb rating of item due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET} for id:{imdbID}")
        try:
            movie["Genre"] = [x.text for x in mainpage.find("div" , class_ = "ipc-chip-list__scroller").find_all("a")]
        except Exception as e:
            movie["Genre"] = []
            print(f"{Colors.GREY}unable to get Genre rating of item due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET} for id:{imdbID}")
               
        try: # Type, Year, Rated, Runtime and Episodes(for tv series)
            tempVar = mainpage.find("ul", class_ ="ipc-inline-list ipc-inline-list--show-dividers sc-d8941411-2 cdJsTz baseAlt").find_all("li")
            if item_type == "":
                item_type = getFilmType(tempVar[0].text)
            if item_type == "movie":
                movie["Type"] = "Movie"
                movie["Year"] = tempVar[0].text
                movie["Rated"] =tempVar[1].text
                movie["Runtime"] = tempVar[2].text

            elif item_type == "tv_series":
                movie["Runtime"] = ""
                movie["Type"] = "TV Series"
                movie["Year"] = tempVar[1].text
                movie["Rated"] = tempVar[2].text
                movie["Episodes"] = getEpisodes(imdbID)
            elif item_type == "tv_mini_series":
                movie["Runtime"] = ""
                movie["Type"] = "TV Mini Series"
                movie["Year"] = tempVar[1].text
                movie["Rated"] = tempVar[2].text
                movie["Episodes"] = getEpisodes(imdbID)
            elif item_type == "episode":
                movie["Type"] = "Episode"
                movie["Episode-details"] = episode_details
                if len(episode_details) == 0:
                    print(f"{Colors.YELLOW}Episode data incomplete for {imdbID}{Colors.RESET}")
                movie["Year"] = tempVar[0].text
                movie["Rated"] =tempVar[1].text
                movie["Runtime"] = tempVar[2].text
        except IndexError:
            if "Year" not in movie:
                movie["Year"] = None
            if "Rated" not in movie:
                movie["Rated"] =None
            if "Runtime" not in movie:
                movie["Runtime"] =None
            print(f"{Colors.GREY}unable to get year, release , runtime of item due to Index Error on line for id:{imdbID}")
        except Exception as e:
            print(f"{Colors.GREY}unable to get year, release , runtime of item due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET} for id:{imdbID}")

        try:    # Poster
            if item_type != "episode":
                imagesSiteUrl = "https://www.imdb.com/" + mainpage.find("a", class_="ipc-lockup-overlay ipc-focusable").get("href")
                imageSoup = getBSfromURL(imagesSiteUrl)
                try:
                    movie["Poster"] = imageSoup.find("img", class_="sc-7c0a9e7c-0 eWmrns").get("src")
                except AttributeError:
                    movie["Poster"] = imageSoup.find("div", class_="sc-7c0a9e7c-3 cISuCS").find("img").get("src")
                except Exception as e:
                    movie["poster"] = ""
                    print(f"{Colors.GREY}(from imdbFunction) unable to get poster due to {e} for {imdbID}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.GREY}unable to get Poster of item due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET} for id:{imdbID}")

        try:    # Cast
            movie["Actors"] = {}
            cast = mainpage.find_all("div", class_ = "sc-bfec09a1-7 gWwKlt")
            for actor in cast:
                try:
                    movie["Actors"][actor.find("a").text] = actor.find("div").text 
                except Exception as e:
                    if print_feedback:
                        print(f"unable to get the cast member's role due to {e}")
        except:
            print(f"{Colors.YELLOW}unable to get Entire cast of item due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET} for id:{imdbID}")

        try:    # Crew
            
            tempVar = mainpage.find("ul", class_ = "ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt", attrs={"role" : "presentation"}).find_all("div", class_="ipc-metadata-list-item__content-container")
            # the ul contains li which contains one div each, for director(s) and writer(s)
            movie["Director"] = [x.text for x in tempVar[0].find_all("li")]
            try:    
                if item_type == "tv_series" or item_type == "tv_mini_series":
                    movie["Stars"] = [x.text for x in tempVar[1].find_all("li")]
                else:
                    movie["Writers"] = [x.text for x in tempVar[1].find_all("li")]
                    movie["Stars"] = [x.text for x in tempVar[2].find_all("li")]
            except Exception as e:
                print(f"{Colors.GREY}unable to get crew due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.GREY}unable to get crew due to -{e}-  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET}")
    
        getPlotSummary(imdbID, movie)
        getQuotes(imdbID, movie)
        
        if print_feedback:
            print("scrapped sucessfully")
        return movie

    except Exception as e:
        print(f"{Colors.RED}unable to get movie due to --{e}--  on line {traceback.extract_tb(e.__traceback__)[0][1]}{Colors.RESET}")


def getIMDBextras(imdbID, driver, print_feedback = True):
    print("fasdkfaf")

    obj = {
        "movie-platform" : "",
        "movie-url" : "",
        "trivia" : "",
        "goofs" : "",
        "quotes" : []
    }
    try:
        import time    
        driver.get("https://www.imdb.com/title/" + imdbID)
        time.sleep(3)
        mainpage = BeautifulSoup(driver.page_source, "html.parser")

        watch_sec = mainpage.find("div",class_="ipc-sub-grid-item ipc-sub-grid-item--span-2 sc-ca09d136-0 hlUZZv ipc-shoveler__item")
        try:
            obj["movie-platform"] = watch_sec.find("img").get("src")
        except AttributeError:
            print(f"{Colors.GREY}{imdbID} : unable to get movie platform{Colors.RESET}")

        try:
            obj["movie-url"] = watch_sec.find("a").get("href")
        except AttributeError:
            print(f"{Colors.GREY}{imdbID} : unable to get movie-url{Colors.RESET}")

        did_you_know_sec = mainpage.find("section", class_="ipc-page-section ipc-page-section--base celwidget", attrs={"data-testid" :"DidYouKnow"})
        try:
            subparts = did_you_know_sec.find_all("div", class_="ipc-list-card--border-line ipc-list-card--tp-none ipc-list-card--bp-none ipc-list-card sc-3026fe52-1 guJwyD ipc-list-card--base")
            obj["trivia"] = subparts[0].find("div").text
            obj["goofs"] = subparts[1].find("div").text
            for quote in subparts[2].find("div").find_all("p"):
                obj["quotes"].append(quote.text)
        except IndexError:
            print(f"{Colors.GREY}{imdbID} : unable to get some parts of 'do you know' section{Colors.RESET}")
        except AttributeError:
            print(f"{Colors.ORANGE}{imdbID} : unable to get 'do you know' section entirely{Colors.RESET}")

        if print_feedback:
            print(f"{Colors.GREEN}{imdbID} : DONE sucessfully {Colors.RESET}")
        return obj
    except Exception as e:
        print(f"{Colors.RED}{imdbID} : unable to get due to {e} for {imdbID}{Colors.RESET}")
                


# ------------------------------------------------------------------------------------------------
# -------------------------------------- getting by Name -----------------------------------------

def extract_alphanumeric(input_str):
    # Using regular expression to find alphanumeric characters
    return re.sub(r'[^a-zA-Z0-9]', '', input_str)

def titlesMatch(str1, str2):
    return (extract_alphanumeric(str1.lower()) == extract_alphanumeric(str2.lower()))


def getIDbyName(title, year, strict = True):
    imdbID = ""
    search_results = getBSfromURL("https://www.imdb.com/find/?q=" + title).find_all("li", class_="ipc-metadata-list-summary-item ipc-metadata-list-summary-item--click find-result-item find-title-result")

    for search_res in search_results:

        result_title = search_res.find("a" ,  class_="ipc-metadata-list-summary-item__t").text
        result_release_year = search_res.find("ul").text[:4]
        if titlesMatch(result_title , title) and int(result_release_year) <= year and strict:
            imdbID = search_res.find("a" ,  class_="ipc-metadata-list-summary-item__t").get("href").split("/")[-2]
            return imdbID
        if not strict and int(result_release_year) <= year:
            imdbID = search_res.find("a" ,  class_="ipc-metadata-list-summary-item__t").get("href").split("/")[-2]
            return imdbID
    return imdbID
