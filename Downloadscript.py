from turtle import down
from bs4 import *
import requests
import json
import re

with open("Q:\Faproulette\Faproulette.co\settings.json", "r") as f:
    settings = json.load(f)
downloaded = int(settings["last_downloaded"])
print("You already downloaded: "+str(downloaded))
downloaded += 1
print("continue...")

for i in range(downloaded,51371):
    error_stack = 0
    url = "https://faproulette.co/"+str(i)
	
    # content of URL
    r = requests.get(url)

    # Parse HTML Code
    soup = BeautifulSoup(r.text, 'html.parser')

    # find all images in URL
    images = soup.findAll('img')

    # find title
    title = soup.find('title')

    if not title:
        title = "image" + str(i)
    else:
        title = title.get_text().replace(" - Fap Roulette", "")
        title = re.sub(r'[?|:<>]', '', title)

    #select folder
    folder_name = "all"

    # checking if images is not zero
    if len(images) != 0:
        if len(images) == 1:
            continue
        if len(images) < 2:
            print(images)
            continue
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

        # After getting Image Source URL
        # We will try to get the content of image
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



            # After checking above condition, Image Download start
            with open(f"{folder_name}/{title}.{file_extension}", "wb+") as f:
                f.write(r)

            downloaded += 1
            settings["last_downloaded"] = downloaded
            with open("Q:\Faproulette\Faproulette.co\settings.json", "w") as f:
                json.dump(settings, f)

            print("Downloaded: ", str(int(downloaded-1)))
        else:
            error_stack += 1
            print("Download failed")
            if error_stack == 3:
                exit(1)
