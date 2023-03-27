from turtle import down
from bs4 import *
import requests
import json

with open("Q:\Faproulette\Faproulette.co\settings.json", "r") as f:
    settings = json.load(f)
downloaded = int(settings["last_downloaded"])
print("You already downloaded: "+str(downloaded))
downloaded += 1
print("continue...")

for i in range(downloaded,46496):
    url = "https://faproulette.co/"+str(i)


    downloaded += 1
    settings["last_downloaded"] = downloaded
    with open("Q:\Faproulette\Faproulette.co\settings.json", "w") as f:
        json.dump(settings, f)
	
    # content of URL
    r = requests.get(url)

    # Parse HTML Code
    soup = BeautifulSoup(r.text, 'html.parser')

    # find all images in URL
    images = soup.findAll('img')

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
        try:
            r = requests.get(image_link).content
            try:

                # possibility of decode
                r = str(r, 'utf-8')

            except UnicodeDecodeError:

                # After checking above condition, Image Download start
                with open(f"{folder_name}/images{i}.jpg", "wb+") as f:
                    f.write(r)

        except:
            pass

        print("Downloaded: ", downloaded)
