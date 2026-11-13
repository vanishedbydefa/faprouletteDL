import os
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from logger import logger
from database import check_db_exists, get_all_ids_from_db


def get_timestamp():
    return time.time()


def sanitize_filename(input_string):
    """Remove characters that are unsafe for downloaded filenames."""
    pattern = re.compile(r'[^A-Za-z0-9\_\-\.]')
    return pattern.sub('', input_string)


def create_urls(url_from: int, url_to: int, db_source_path: str, speed=False):
    """Create image ID and roulette URL pairs."""
    if url_from is None:
        url_from = 0
    elif url_from <= 10:
        url_from = 0
    else:
        url_from -= 10
    if speed:
        return [[i, "https://faproulette.co/" + str(i)] for i in get_all_ids_from_db(db_source_path)]
    else:
        return [[i, "https://faproulette.co/" + str(i)] for i in range(url_from, url_to + 1)]


def check_path_exists(path: str, create=False):
    """Check whether a path exists and optionally create it."""
    if os.path.exists(path):
        return True

    if create:
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError as e:
            logger.error(f"Failed to create directory: {path}")
            logger.error(f"Error: {e}")
    return False


def initial_checks(param_path: str, db_path: str, db_path_source: str, speed=False, exe=False):
    if check_path_exists(param_path, create=True):
        logger.info(f'    * Folder path {param_path} is valid')
    else:
        logger.error(f"\nError:\nThe folder where to store downloaded images do not exist and couldn't be created.\n"
            f"Please check the correctness of the provided path: "
            f"{param_path}.")
        if exe:
            input("Press Enter to exit...")
        raise SystemExit(1)

    check_db_exists(db_path)
    if speed:
        if not check_path_exists(db_path_source, create=False):
            logger.error(f"ERROR: You want to use speed mode but there is no source database: 'image_data_source.db'\n"
                        f"Make sure to place 'image_data_source.db' here: {db_path_source}")

            if exe:
                input("Press Enter to exit...")
            raise SystemExit(1)


def process_url(url: str, proxie: dict):
    try:
        response = requests.get(
            url,
            headers={'User-agent': 'faproulette-dl'},
            proxies=proxie,
            timeout=(5, 30),
        )
    except requests.RequestException as error:
        logger.error(f"Request failed for {url}: {error}")
        return False, False

    if response.status_code == 429:
        return 429, 429
    if not response.ok:
        logger.error(f"Request failed for {url} with status code {response.status_code}")
        return False, False

    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img')
    title_element = soup.find('title')
    title = "faproulette"
    if title_element:
        title = title_element.get_text().replace(" - Fap Roulette", "")
        title = re.sub(r'[?|/:<>*\\]', '', title)

    for image in images:
        for attribute in ("data-srcset", "data-src", "data-fallback-src", "src"):
            image_link = image.get(attribute)
            if image_link and image_link.startswith("https://files.faproulette.co/images/fap/"):
                return title, urljoin(response.url, image_link)

    logger.error(f"No image source found for {url}")
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
                logger.error("Invalid input! Please enter a number between 1 and 10")
                continue
            logger.info(f"Threads set to: {threads}")
            break
        except ValueError:
            logger.error("Invalid input! Please enter a number between 1 and 10")

    while True:
        force = input("Do you want to force download even an image may already exist? [y/n]: ")
        if force.lower() in ["y", "j", "yes"]:
            force = True
            break
        elif force.lower() in ["n", "no"]:
            force = False
            break
        else:             
            logger.error("Type 'y' to force download or 'n' to do not: ")

    while True:
        beginning = input("Do you want to start downloading from 0? [y/n]: ")
        if beginning.lower() in ["y", "j", "yes"]:
            beginning = True
            break
        elif beginning.lower() in ["n", "no"]:
            beginning = False
            break
        else:             
            logger.error("Type 'y' to not continue where you stoped last time or 'n' to do so: ")

    while True:
        speed = input("Do you want to start downloading in speed mode? [y/n]: ")
        if speed.lower() in ["y", "j", "yes"]:
            speed = True
            break
        elif speed.lower() in ["n", "no"]:
            speed = False
            break
        else:             
            logger.error("Type 'y' to start downloading in speed mode or 'n' to do not: ")

    while True:
        proxie = input("Do you want to use a proxie? [y/n]: ")
        if proxie.lower() in ["y", "j", "yes"]:
            proxie = input("Input proxies IP: ")
            break
        elif proxie.lower() in ["n", "no"]:
            proxie = None
            break
        else:             
            logger.error("Type 'y' to use a proxie or 'n' to do not: ")

    return path, threads, force, beginning, speed, proxie
