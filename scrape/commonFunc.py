from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import threading
import json
import random

THREAD_COUNT = 8

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    ORANGE = '\033[38;5;208m'
    BLUE = '\033[94m'
    PINK = '\033[95m'  # Light pink
    YELLOW = '\033[93m'
    GREY = '\033[90m'

def load_json(filename):
    with open(filename) as file:
        return json.load(file)

class multiThreadExec:
    def __init__(self, input_func, input_list, output_json, output_json_loc, drivers=None):
        self.input_func = input_func
        self.input_list = input_list
        self.output_json = output_json
        self.output_json_loc = output_json_loc
        self.drivers = drivers
        self.thread_count = THREAD_COUNT if drivers is None else len(drivers)
        self.exiting = threading.Event()
        self.tasks = []  # Initialize task list

        random.shuffle(input_list)

    def start(self):
        with ThreadPoolExecutor(self.thread_count) as executor:
            self.executor = executor  # Store the executor for later shutdown
            try:
                for current_task, imdbID in enumerate(self.input_list, start=1):
                    if self.exiting.is_set():
                        break

                    # Submit tasks based on presence of drivers
                    if self.drivers is None:
                        self.tasks.append(executor.submit(self.input_func, imdbID, current_task, len(self.input_list), self.output_json, self.output_json_loc))
                    else:
                        self.tasks.append(executor.submit(self.input_func, imdbID, current_task, len(self.input_list), self.output_json, self.drivers[current_task % self.thread_count]))

                # Handle completed tasks
                for future in as_completed(self.tasks):
                    if self.exiting.is_set():
                        break
                    try:
                        future.result()  # Ensure result is obtained (to catch exceptions)
                    except Exception as e:
                        print(f"Error occurred: {e}")

            except KeyboardInterrupt:
                print(f"{Colors.PINK}===== request for shut down ====={Colors.RESET}")
                self.terminate()
            except Exception as e:
                print(f"{Colors.RED} ThreadPoolExecutor failed due to <{e}>{Colors.RESET}")

    def terminate(self):
        # Cancel all tasks and shut down the executor
        self.exiting.set()  # Signal the termination
        for task in self.tasks:
            task.cancel()

        self.executor.shutdown(wait=False)
        print(f"{Colors.PINK}===== Shutting down the executor ====={Colors.RESET}")





# def multiThreadExec(inputFunc, input_list, output_json, drivers=None):
#     # expects a function that can manage the data and give value (movie or series data)
#     # for a given imdbID. inputFunc also expects
    
#     threadCount = 8 if drivers is None else len(drivers)
#     tasks = []
#     exiting = threading.Event()

#     def signal_handler(signum, frame):
#         print("Setting exiting event")
#         exiting.set()

#     signal.signal(signal.SIGINT, signal_handler)
#     signal.signal(signal.SIGTERM, signal_handler)

#     with ThreadPoolExecutor(threadCount) as pool:
#         try:
#             for current_task, imdbID in enumerate(input_list, start=1):
#                 if exiting.is_set():
#                     break
#                 if drivers is None:
#                     tasks.append(pool.submit(inputFunc, imdbID, current_task, len(input_list), output_json  ))
#                 else:
#                     tasks.append(pool.submit(inputFunc, imdbID, current_task, len(input_list), output_json, drivers[current_task % threadCount]))

#             for future in as_completed(tasks):
#                 if exiting.is_set():
#                     break
#                 try:
#                     future.result()
#                 except Exception as e:
#                     print(f"Error occurred: {e}")   

#         finally:
#             for task in tasks:
#                 task.cancel()
#             print(f"{Colors.PINK}=====Shutting down due to signal====={Colors.RESET}")
#             pool.shutdown(wait=False)
