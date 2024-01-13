import argparse
import threading
import queue
import requests
import re
import signal
import time
import sys
import os

from helper import get_time,initial_checks, create_urls, get_timestamp, process_url, check_path_exists, exe_helper
from database import insert_or_update_entry, check_db_entry_exists, get_max_id_from_db

IMAGES = 51686
STOP_THREADS = False

threads = []

db_semaphore = threading.Semaphore(1)
threads_remove_semaphore = threading.Semaphore(1)
threads_semaphore = None

def download_image(url:list, path:str, db_path:str, force:bool, proxie:dict):
    global db_semaphore
    img_id = url[0]
    url = url[1]

    # Check if db entry exist in case download is not forced
    if not force and check_db_entry_exists(db_path, img_id):
        return True
    
    # Get title and image source
    title, image_link = process_url(url, proxie)
    if not title and not image_link:
        print(f"No image found for this URL: {url}")
        return True
    elif title == 429 and image_link == 429:
        return False

    # Download the image, save it and add entry to DB
    r = requests.get(image_link, headers = {'User-agent': 'faproulette-dl'}, proxies=proxie)
    if r.status_code == 200: 
        r = r.content

        pattern = r'\.(\w+)(\?|$)'
        extension = re.search(pattern, image_link)
        
        if extension:
            file_extension = extension.group(1)  # Extract the matched file extension
        else:
            file_extension = "unknown"
            print("File extension not found in the URL.")

        # Check if image with this name already exist
        if check_path_exists(path + "/" + title + "." + file_extension):
            title += str(img_id)

        # After checking above condition, Image Download start
        with open(f"{path}/{title}.{file_extension}", "wb+") as f:
            f.write(r)

        # Write data to db
        db_semaphore.acquire()
        insert_or_update_entry(db_path, img_id, title, "test category", get_timestamp(), url)
        db_semaphore.release()
    else:
        print("Download failed")
    return True

def image_downloader(path:str, db_path:str, force:bool, url_queue, proxie):
    '''
    Put a url from the queue of urls and
    download it. Return and join thread if queue
    is empty. 
    '''
    global STOP_THREADS
    if not STOP_THREADS:
        try:
            time.sleep(2)
            url = url_queue.get(timeout=1)  # Get a URL from the queue
            if not download_image(url, path, db_path, force, proxie):
                url_queue.task_done()
                if STOP_THREADS:
                    return
                print("Downloading too fast. Shutting down now!                               ")
                STOP_THREADS = True
                threads_semaphore.release()
                return
            url_queue.task_done()
        except queue.Empty:
            pass
    threads_semaphore.release()
    return

# Function to gracefully stop the program on CTRL + C
def stop_program(signum, frame, url_queue):
    global STOP_THREADS, threads, threads_semaphore, threads_remove_semaphore
    STOP_THREADS = True
    if signum != None:
        print("Ctrl + C detected. Emptying queue")
    else:
        print("Internal Call for program termination")

    print("Clearing queue: ", end="")
    url_queue.mutex
    while not url_queue.empty():
        url_queue.get()
        url_queue.task_done()
    print("Done")

    print("Clearing threads: ", end="")
    time.sleep(2)
    threads_remove_semaphore.acquire()
    for thread in threads:
            thread.join()
            threads.remove(thread)
            threads_semaphore.release()
    threads_remove_semaphore.release()
    print("Done")

    print(f"{get_time()} Thanks for using Faproulette-Downloader")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(prog='Faproulette-Downloader', description='Download all faproulettes on faproulette.co', epilog='https://github.com/vanishedbydefa')
    parser.add_argument('-p', '--path', default=str(os.getcwd()), type=str, help='Path to store downloaded images')
    parser.add_argument('-t', '--threads', choices=range(1, 11), default=3, type=int, help='Number of threads downloading images')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite existing images if True')
    parser.add_argument('-b', '--beginning', action='store_true', help='Start downloading from 0')
    parser.add_argument('-s', '--speed', action='store_true', help='Use an existing Database as source for existing IDs/URLs. This will speed up downloading arround >60 percent. See README.md for more informations')
    parser.add_argument('-x', '--proxie', type=str, default=None, help='Enter proxies IP/domain to circumvent 429 errors. Http Proxies only!')

    args = parser.parse_args()
    param_path = args.path       
    param_threads = args.threads
    param_force = args.force
    param_beginning = args.beginning
    param_speed = args.speed
    param_proxie = args.proxie

    # Check if running as exe
    exe = False
    if sys.argv[0][-4:] == ".exe":
        exe = True
        if not check_path_exists(param_path+"\\main.exe", create=False):
            print("Please start program in the folder where main.exe is stored")
            return
        param_path, param_threads, param_force, param_beginning, param_speed, param_proxie = exe_helper()

    # Set remaining args, may modified in case running the exe
    db_path = param_path + "\\image_data.db"
    db_path_source = param_path + "\\image_data_source.db"
    if param_proxie != None: 
        proxie = {'http': 'http://' + param_proxie + ':80'}
    else:
        proxie = None

    # Startup checks
    print(f'{get_time()} Running startup checks to ensure correct downloading:')
    initial_checks(param_path, db_path, db_path_source, exe=exe)
    print(f'{get_time()} Start downloading with {param_threads} threads into "{param_path}"')
    print('\n\nExit the Program with CTRL + C - This exits safely but may needs some time to finish running threads\n\n')

    # Create a queue with the image URLs
    start_id = 0
    if not param_beginning:
        start_id = get_max_id_from_db(db_path)

    url_queue = queue.Queue()
    urls = create_urls(url_from=start_id, url_to=IMAGES, db_source_path=db_path_source, speed=param_speed)
    for url in urls:
        url_queue.put(url)

    # Thread logic
    global threads_semaphore, threads, threads_remove_semaphore
    threads_semaphore = threading.Semaphore(param_threads)

    while int(url_queue.qsize()) != 0:
        print(f"Remaining images: {str(url_queue.qsize())} get downloaded by {str(param_threads)}/{str(len(threads))} Threads      ", end='\r')
        threads_semaphore.acquire()
        thread = threading.Thread(target=image_downloader, args=(param_path, db_path, param_force, url_queue, proxie,))
        thread.start()
        threads.append(thread)
        
        for thread in threads:
            if not thread.is_alive():
                thread.join()
                threads_remove_semaphore.acquire()
                threads.remove(thread)
                threads_remove_semaphore.release()

        # Register signal handler for Ctrl + C
        signal.signal(signal.SIGINT, lambda sig, frame: stop_program(sig, frame, url_queue))

        if STOP_THREADS:
            stop_program(None, None, url_queue)

    threads_remove_semaphore.acquire()
    for thread in threads:
        thread.join()
        threads.remove(thread)
        threads_semaphore.release()
    threads_remove_semaphore.release()
    
    print(f"{get_time()} All threads terminated")
    print(f"{get_time()} Thanks for using Faproulette-Downloader")

main()    
