# faproulette-downloader
A multi-threding downloader for roulettes and captions of faproulette.co

## Usage
1. Clone this repository or download it as zip
2. open a terminal and navigate to the repositorys content
3. run the script by calling main.py with the necessary arguments.
  * In case you want to use speed mode, make sure to place "image_data_source.db" to the folder in which you want to download.
  * Do not set threads to high, otherwise you will get errors from faproulette.co. If the program detects that faproulette.co give bad responses (429 errors), it will let you know and terminate.
    * In case you are downloading too fast, just wait a few minutes and start with less threads

```
$ python main.py -t 2 -p Q:\Faproulette\Faproulette.co\downloads -h

usage: Faproulette-Downloader [-h] [-p PATH] [-t {1,2,3,4,5,6,7,8,9,10}] [-f] [-b] [-s] [-x PROXIE]
Download all faproulettes on faproulette.co

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to store downloaded images
  -t {1,2,3,4,5,6,7,8,9,10}, --threads {1,2,3,4,5,6,7,8,9,10}
                        Number of threads downloading images
  -f, --force           Overwrite existing images if True
  -b, --beginning       Start downloading from 0
  -s, --speed           Use an existing Database as source for existing IDs/URLs.
                        This will speed up downloading arround >60 percent. See README.md for more informations
  -x PROXIE, --proxie PROXIE
                        Enter proxies IP/domain to circumvent 429 errors. Http Proxies only!

https://github.com/vanishedbydefa
```

### Parameter option -s --speed
Use this parameter to drastically speed up the download process. Faproulette.co is using increasing IDs for the roulette.
Because it's not public which are valid IDs, the downloader normally tries every ID. Once scraped all images, we know which IDs
are used. This allows us to ignore the unused IDs in the future. The parameter -s --speed takes an existing database as data source
for the IDs. The program will only download the images, which IDs are stored in the database. This maybe results in missing images.
When ever a new roulette is uploaded, it gets a new ID that's one higher than the previous image. In case a roulette wasn't visible/reachable
when the database got created, the roulette wouldn't be downloaded in speed mode. I never observed this, so I would recommend to use -s --speed.

Notice: Place "image_data_source.db" in the folder in which you want to download the images!
