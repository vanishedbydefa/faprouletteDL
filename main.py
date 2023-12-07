import argparse
import threading
import queue
import requests
import re
import signal
import time

from helper import get_time,initial_checks, create_urls, get_timestamp, process_url, check_path_exists
from database import insert_or_update_entry, check_db_entry_exists

IMAGES = 100
STOP_THREADS = False

# Semaphore to control database access
db_semaphore = threading.Semaphore(1)

def download_image(url:list, path:str, db_path:str, force:bool):
    img_id = url[0]
    url = url[1]

    # Check if db entry exist in case download is not forced
    if not force and check_db_entry_exists(db_path, img_id):
        print("Image has entry in DB and was skipped")
        return
    
    # Get title and image source
    title, image_link = process_url(url)
    if STOP_THREADS or not title and not image_link:
        return

    # Download the image, save it and add entry to DB
    r = requests.get(image_link)
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
        if not check_path_exists(path + "/" + title + "." + file_extension):
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
    return

def image_downloader(path:str, db_path:str, force:bool, url_queue):
    '''
    Put a url from the queue of urls and
    download it. Return and join thread if queue
    is empty. 
    '''
    global STOP_THREADS
    while not STOP_THREADS:
        try:
            url = url_queue.get(timeout=1)  # Get a URL from the queue
            download_image(url, path, db_path, force)
            url_queue.task_done()
        except queue.Empty:
            break  # Exit the loop when queue is empty
    return

# Function to gracefully stop the program
def stop_program(signum, frame, url_queue, threads):
    global STOP_THREADS
    # In case ctrl + c, empty the queue to safely terminate the program
    print("Ctrl + C detected. Emptying queue")
    #with url_queue.mutex:  # Ensure thread safety for queue clearing
    STOP_THREADS = True
    while not url_queue.empty():
        url_queue.get()
        url_queue.task_done()

    print("All threads terminated, exiting now")
    exit(0)


def main():
    parser = argparse.ArgumentParser(prog='Faproulette-Downloader', description='Download all faproulettes on faproulette.co', epilog='https://github.com/vanishedbydefa')
    parser.add_argument('-p', '--path', required=True, type=str, help='Path to store downloaded images')
    parser.add_argument('-t', '--threads', choices=range(1, 7), default=4, type=int, help='Number of threads downloading images')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite existing images if True')

    args = parser.parse_args()
    param_path = args.path
    param_threads = args.threads
    param_force = args.force
    db_path = param_path + "\\image_data.db"

    # Startup checks
    print(f'{get_time()} Running startup checks to ensure correct downloading:')
    initial_checks(param_path, db_path)
    print(f'{get_time()} Start downloading with {param_threads} threads into "{param_path}"')

    # Create a queue with the image URLs
    url_queue = queue.Queue()
    urls = create_urls(IMAGES)
    for url in urls:
        url_queue.put(url)

    threads = []
    for _ in range(param_threads):
        thread = threading.Thread(target=image_downloader, args=(param_path, db_path, param_force, url_queue,))
        thread.start()
        threads.append(thread)

    # Register signal handler for Ctrl + C
    signal.signal(signal.SIGINT, lambda sig, frame: stop_program(sig, frame, url_queue, threads))

    for thread in threads:
        thread.join()
        print(f"Thread: {thread.name} terminated")
        threads.remove(thread)

main()    
