# faproulette-downloader
A multi-threding downloader for roulettes and captions of faproulette.co

## Usage
In order to run the script, call main.py with the necessary arguments. 
```
$ python main.py -t 2 -p Q:\Faproulette\Faproulette.co\downloads -h


usage: Faproulette-Downloader [-h] -p PATH [-t {1,2,3,4,5,6,7,8,9,10}] [-f]

Download all faproulettes on faproulette.co
options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to store downloaded images
  -t {1,2,3,4,5,6,7,8,9,10}, --threads {1,2,3,4,5,6,7,8,9,10}
                        Number of threads downloading images
  -f, --force           Force download images, even when they already exist
```
