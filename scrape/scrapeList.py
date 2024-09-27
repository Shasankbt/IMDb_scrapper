from imdbFunctions import getDataFromImdbID
from imdbFunctions import getBSfromURL
import json
import time
from commonFunc import multiThreadExec, load_json, Colors

class FileMap:
    movieData = "movies.json"
    seriesData = "tvSeries.json"
    episodeData = "episodes.json"


# def saveData(newData):
#     with open(f"../extractedData/{FileMap[newData]}", "w") as file:
#         file.write(json.dumps(newData))

def saveData(newData, data_type):
    file_map = {
        "movie": FileMap.movieData,
        "series": FileMap.seriesData,
        "episode": FileMap.episodeData
    }
    
    if data_type in file_map:
        with open(f"../extractedData/{file_map[data_type]}", "w") as file:
            file.write(json.dumps(newData))
        print(f"{Colors.GREEN} Saved {file_map[data_type]}{Colors.RESET}")
    else:
        raise ValueError(f"Invalid data type: {data_type}")

def writeDatafromList(imdbID, task_idx, total_tasks, newData, data_type, driver=None):
    # if exiting.is_set():
    #     return
    if task_idx % 100 == 0: # save to file for every 100 tasks
        saveData(newData, data_type)
        print(f"{Colors.PINK} ({task_idx}/{total_tasks}) : saving the loaded data onto file at {task_idx}/{total_tasks}")
    if imdbID in newData.keys():
        print(f"{Colors.GREY} ({task_idx}/{total_tasks}) : already in the data, returning{Colors.RESET}")
        return
    print(f"{Colors.BLUE}starting ({task_idx}/{total_tasks}) : {imdbID}{Colors.RESET}")
    start_time = time.time()
    try:
        if driver:
            newData[imdbID] = getDataFromImdbID(imdbID, driver, print_feedback=False)
        else:
            newData[imdbID] = getDataFromImdbID(imdbID, print_feedback=False)
        print(f"{Colors.GREEN}({task_idx})/({total_tasks}) : Scrapped successfully for {imdbID}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}an error {e} has occurred for {imdbID}{Colors.RESET}")

    
    print(f"completed in {time.time() - start_time} sec")
    print("-------------------------------------------------------")

if __name__ == "__main__":
    # with open("imdbID.txt") as file:
    #     imdbID_list_input = file.read().splitlines()

    # already extracted data to avoid rescrapping
    movieData = load_json("../extractedData/movies.json")
    seriesData = load_json("../extractedData/tvSeries.json")
    episodeData = load_json("../extractedData/episodes.json")
    # newData = load_json("../extractedData/imdbData.json")

    movie_imdbID_listfile = "movies_imdbID.txt"
    tvSeries_imdbID_listfile = "tvSeries_imdbID.txt"
    with open(movie_imdbID_listfile) as f:
        movie_imdbID_list = f.read().splitlines()

    with open(tvSeries_imdbID_listfile) as f:
        tvSeries_imdbID_list = f.read().splitlines()


    # imdbID_list_extracted = set(movieData.keys()) | set(seriesData.keys()) | set(episodeData.keys()) | set(newData.keys())
    # req_imdbID = list(set(imdbID_list_input) - imdbID_list_extracted)
    # total_tasks = len(req_imdbID)

    print("------------------------------extracting for movies----------------------------------")
    try:
        executor = multiThreadExec(writeDatafromList, movie_imdbID_list, movieData, "movie")
        executor.start()
    except KeyboardInterrupt:
        print('Program exiting gracefully...')
        executor.terminate()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        saveData(movieData, "movie")

    # print("------------------------------------extracting for tvSeries-------------------------------------")
    # try:
    #     executor = multiThreadExec(writeDatafromList, tvSeries_imdbID_list, seriesData)
    #     executor.start()
    # except KeyboardInterrupt:
    #     print('Program exiting gracefully...')
    #     executor.terminate()
    # except Exception as e:
    #     print(f"Unexpected error: {e}")
    # finally:
    #     saveData(seriesData, "series")
