import argparse
import threading
import queue
import requests
import re
import signal
import time

from helper import get_time,initial_checks, create_urls, get_timestamp, process_url, check_path_exists
from database import insert_or_update_entry, check_db_entry_exists

IMAGES = 51686
STOP_THREADS = False

threads = []

db_semaphore = threading.Semaphore(1)
threads_semaphore = None

def download_image(url:list, path:str, db_path:str, force:bool):
    global db_semaphore
    img_id = url[0]
    url = url[1]

    # Check if db entry exist in case download is not forced
    if not force and check_db_entry_exists(db_path, img_id):
        return True
    
    # Get title and image source
    title, image_link = process_url(url)
    if not title and not image_link:
        print("No image found for this URL")
        return True
    elif title == 429 and image_link == 429:
        return False

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

def image_downloader(path:str, db_path:str, force:bool, url_queue):
    '''
    Put a url from the queue of urls and
    download it. Return and join thread if queue
    is empty. 
    '''
    global STOP_THREADS
    if not STOP_THREADS:
        try:
            url = url_queue.get(timeout=1)  # Get a URL from the queue
            if not download_image(url, path, db_path, force):
                url_queue.task_done()
                print("Downloading to fast. Shutting down now!")
                stop_program(None, None, url_queue)
            url_queue.task_done()
        except queue.Empty:
            pass
    threads_semaphore.release()
    return

# Function to gracefully stop the program on CTRL + C
def stop_program(signum, frame, url_queue):
    global STOP_THREADS
    STOP_THREADS = True
    print("Ctrl + C detected. Emptying queue")

    print("Clearing queue: ", end="")
    url_queue.mutex
    while not url_queue.empty():
        url_queue.get()
        url_queue.task_done()
    print("Done")

    print("Clearing threads", end="")
    for thread in threads:
        thread.join()
        threads.remove(thread)
    print("Done")

    print(f"{get_time()} Thanks for using Faproulette-Downloader")
    exit(0)


def main():
    parser = argparse.ArgumentParser(prog='Faproulette-Downloader', description='Download all faproulettes on faproulette.co', epilog='https://github.com/vanishedbydefa')
    parser.add_argument('-p', '--path', required=True, type=str, help='Path to store downloaded images')
    parser.add_argument('-t', '--threads', choices=range(1, 11), default=4, type=int, help='Number of threads downloading images')
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
    print('\n\nExit the Program with CTRL + C - This exits safely but may needs some time to finish running threads\n\n')

    # Create a queue with the image URLs
    url_queue = queue.Queue()
    urls = create_urls(IMAGES)
    for url in urls:
        url_queue.put(url)

    # Thread logic
    global threads_semaphore, threads
    threads_semaphore = threading.Semaphore(param_threads)

    while int(url_queue.qsize()) != 0:
        print(f"Remaining images: {str(url_queue.qsize())}      ", end='\r')
        threads_semaphore.acquire()
        thread = threading.Thread(target=image_downloader, args=(param_path, db_path, param_force, url_queue,))
        thread.start()
        threads.append(thread)
        
        for thread in threads:
            if not thread.is_alive():
                thread.join()
                threads.remove(thread)

        # Register signal handler for Ctrl + C
        signal.signal(signal.SIGINT, lambda sig, frame: stop_program(sig, frame, url_queue))

    for thread in threads:
        thread.join()
        threads.remove(thread)
    
    print(f"{get_time()} All threads terminated")
    print(f"{get_time()} Thanks for using Faproulette-Downloader")

main()    
