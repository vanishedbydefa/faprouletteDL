import os
import time
import re
import requests
from bs4 import *

from database import check_db_exists

def get_time():
    return time.strftime('[%H:%M:%S]')

def get_timestamp():
    return time.time()

def create_urls(url_from:int, url_to:int):
    if url_from <= 10:
        url_from = 0
    else:
        url_from -= 10
    return [[i,"https://faproulette.co/"+str(i)] for i in range(url_from, url_to+1)]


def check_path_exists(path:str, create=False):
    '''
    Check wether path exists or not.
    If path do not exist but create=True,
    create a directory.
    '''
    path_exist = os.path.exists(path)
    if path_exist:
        return True

    #path do not exist, try to create it
    if create:
        try:
            os.makedirs(path)
            return True
        except OSError as e:
            print(f"Failed to create directory: {path}")
            print(f"Error: {e}")
            return False
    return False


def initial_checks(param_path:str, db_path:str):
    ##check specified path to folder and create if it do not exist
    if check_path_exists(param_path, create=True):
        print(f'    - Folder path at {param_path} is valid')
    else:
        print(f"\nError:\nThe folder where to store downloaded images "
            f"do not exist and couldn't be created. Please check \n"
            f"the correctness of the provided path: "
            f"{param_path}.")
        exit(1)
    
    ##check if the db exist and create if it do not exist
    check_db_exists(db_path)


def process_url(url:str, proxie:dict):
    # content of URL
    r = requests.get(url, headers = {'User-agent': 'faproulette-dl'}, proxies=proxie)
    if r.status_code == 429:
        return 429, 429
    # Parse HTML Code
    soup = BeautifulSoup(r.text, 'html.parser')
    # find all images in URL
    images = soup.findAll('img')
    
    # Find title
    title = soup.find('title')
    if not title:
        title = "faproulette"
    else:
        title = title.get_text().replace(" - Fap Roulette", "")
        title = re.sub(r'[?|/:<>*\\]', '', title)

    # checking if images is not zero
    if len(images) != 0:
        if len(images) == 1:
            return False, False
        if len(images) < 2:
            print(images)
            return False, False
        image = images[2]
        try:
            # In image tag ,searching for "data-srcset"
            image_link = image["data-srcset"]
        # then we will search for "data-src" in img
        # tag and so on..
        except:
            try:
                # In image tag ,searching for "data-src"
                image_link = image["data-src"]
            except:
                try:
                    # In image tag ,searching for "data-fallback-src"
                    image_link = image["data-fallback-src"]
                except:
                    try:
                        # In image tag ,searching for "src"
                        image_link = image["src"]
                    # if no Source URL found
                    except:
                        pass

        return title, image_link
    print("debug 1")
    return False, False
