import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


from imdbFunctions import getIMDBextras
from commonFunc import Colors
from commonFunc import multiThreadExec
from commonFunc import load_json



def writeImdbExtras(imdbID, task_idx, total_tasks, movieData, exiting, driver):
    if exiting.is_set():
        return

    print(f"{Colors.BLUE}starting ({task_idx}/{total_tasks}) : {imdbID}{Colors.RESET}")
    start_time = time.time()
    try:
        movieData[imdbID] = getIMDBextras(imdbID,driver, print_feedback=False)
        print(f"{Colors.GREEN}({task_idx})/({total_tasks}) : Scrapped successfully for {imdbID}{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.RED}an error {e} as occured for {imdbID}{Colors.RESET}")

    print(f"completed in {time.time()-start_time} sec")
    print("-------------------------------------------------------")

def cleanup(data):
    
    with open("../extractedData/imdbData_extra.json", "w") as file:
        file.write(json.dumps(data))
    if 'drivers' in locals():
        for driver in drivers:
            driver.quit()

with open("imdbID.txt") as file:
    imdbID_list = file.read().splitlines()

movieData = load_json("../organisedData/movies/movies_extra.json")
seriesData = load_json("../organisedData/series/series_extra.json")
# episodeData = load_json("../organisedData/episodes/episodes_extra.json")
newData = load_json("../extractedData/imdbData_extra.json")



imdbID_list_extracted = set(movieData.keys()) | set(seriesData.keys()) | set([id for id , data in newData.items() if data != None])
# Calculate the difference between the input list and the extracted list
req_imdbID = list(set(imdbID_list) - imdbID_list_extracted)

try:
    drivers = [webdriver.Chrome(service=Service("./chromedriver")) for _ in range(8)]
    multiThreadExec(writeImdbExtras, req_imdbID, newData, drivers)
    cleanup(newData)
except KeyboardInterrupt:
    print('You pressed Ctrl+C! Exiting gracefully...')
    cleanup(newData)
except Exception as e:
    print(f"Unexpected error: {e}")
    cleanup(newData)