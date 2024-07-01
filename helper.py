import os
import logging
import time
import re
import requests
from bs4 import *

from logger import logger
from database import check_db_exists, get_all_ids_from_db

def get_timestamp():
    return time.time()

def sanitize_filename(input_string):
    '''
    Replace characters to get valid file
    names. Only a few chars are allowed.
    '''
    pattern = re.compile(r'[^A-Za-z0-9\_\-\.]')
    result_string = pattern.sub('', input_string)
    return result_string

def create_urls(url_from:int, url_to:int, db_source_path:str, speed=False):
    '''
    Create a list of lists containing the
    image id and the roulettes url.
    '''
    if url_from == None:
        url_from = 0
    elif url_from <= 10:
        url_from = 0
    else:
        url_from -= 10
    if speed:
        return [[i,"https://faproulette.co/"+str(i)] for i in get_all_ids_from_db(db_source_path)]
    else:
        return [[i,"https://faproulette.co/"+str(i)] for i in range(url_from, url_to+1)]


def check_path_exists(path:str, create=False):
    '''
    Check wether path exists or not.
    If path do not exist but create=True,
    create a directory.
    '''
    if os.path.exists(path):
        return True

    #path do not exist, try to create it
    if create:
        try:
            os.makedirs(path)
            return True
        except OSError as e:
            logger.error(f"Failed to create directory: {path}")
            logger.error(f"Error: {e}")
    return False


def initial_checks(param_path:str, db_path:str, db_path_source:str, speed=False, exe=False):
    ##check specified path to folder and create if it do not exist
    if check_path_exists(param_path, create=True):
        logger.info(f'    * Folder path {param_path} is valid')
    else:
        logger.error(f"\nError:\nThe folder where to store downloaded images ",
            f"do not exist and couldn't be created. Please check \n",
            f"the correctness of the provided path: ",
            f"{param_path}.")
        if exe:
            os.system("pause")
        exit(1)
    
    ##check if the db exist and create if it do not exist
    check_db_exists(db_path)
    if speed:
        if not check_path_exists(db_path_source, create=False):
            logger.error("\nERROR You want to use speed mode but there is no source database: 'image_data_source.db'\n",
                        f"      Make sure to place 'image_data_source.db' here: {db_path_source}")
            if exe:
                os.system("pause")
            exit(1)

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
            logger.info(images)
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
    logger.error(f"Unknown error for {url}")
    return False, False

def exe_helper():
    while True:
        path = input("Enter a path where to store the images: ")
        if os.path.isdir(path):
            break
        logger.error(f"{path} isn't a valid path")
    logger.info(f"Path set to: {path}")

    while True:
        try:
            threads = input("Enter a number of threads to use for downloading [1-10]: ")
            threads = int(threads)
            if threads <= 0 or threads >10:
                logging.error("Invalid input! Please enter a number between 1 and 10")
                continue
            logger.info(f"Threads set to: {threads}")
            break
        except ValueError:
            logger.error("Invalid input! Please enter a number between 1 and 10")

    while True:
        force = input("Do you want to force download even an image may already exist? [y/n]: ")
        if force not in ["y", "Y", "j", "J", "yes", "Yes", "n", "N", "no", "No"]:
            logger.error("Type 'y' to force download or 'n' to do not: ")
            continue
        elif force in ["y", "Y", "j", "J", "yes", "Yes"]:
            force = True
            break
        elif force in ["n", "N", "no", "No"]:
            force = False
            break
    
    while True:
        beginning = input("Do you want to start downloading from 0? [y/n]: ")
        if beginning not in ["y", "Y", "j", "J", "yes", "Yes", "n", "N", "no", "No"]:
            logger.error("Type 'y' to not continue where you stoped last time or 'n' to do so: ")
            continue
        elif beginning in ["y", "Y", "j", "J", "yes", "Yes"]:
            beginning = True
            break
        elif beginning in ["n", "N", "no", "No"]:
            beginning = False
            break

    while True:
        speed = input("Do you want to start downloading in speed mode? [y/n]: ")
        if speed not in ["y", "Y", "j", "J", "yes", "Yes", "n", "N", "no", "No"]:
            logger.error("Type 'y' to download based on an existing db otherwise type 'n': ")
            continue
        elif speed in ["y", "Y", "j", "J", "yes", "Yes"]:
            speed = True
            break
        elif speed in ["n", "N", "no", "No"]:
            speed = False
            break

    while True:
        proxie = input("Do you want to use a proxie? [y/n]: ")
        if proxie not in ["y", "Y", "j", "J", "yes", "Yes", "n", "N", "no", "No"]:
            logger.error("Type 'y' to force download or 'n' to do not: ")
            continue
        elif proxie in ["y", "Y", "j", "J", "yes", "Yes"]:
            proxie = input("Input proxies IP: ")
            break
        else:
            proxie = None
            break
    return path, threads, force, beginning, speed, proxie
        

