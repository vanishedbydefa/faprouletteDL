# faproulette-downloader
A multi-threding downloader for roulettes and captions of faproulette.co

## Usage
1. Clone this repository or download it as zip
2. open a terminal and navigate to the repositorys content
3. run the script by calling main.py with the necessary arguments.
  * Do not set threads to high, otherwise you will get errors from faproulette.co. If the program detects that faproulette.co give bad responses (429 errors), it will let you know and terminate.
    * In case you are downloading too fast, just wait a few minutes and start with less threads 

```
$ python main.py -t 2 -p Q:\Faproulette\Faproulette.co\downloads -h


usage: Faproulette-Downloader [-h] -p PATH [-t {1,2,3,4,5,6,7,8,9,10}] [-f] [-b]

Download all faproulettes on faproulette.co

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to store downloaded images
  -t {1,2,3,4,5,6,7,8,9,10}, --threads {1,2,3,4,5,6,7,8,9,10}
                        Number of threads downloading images
  -f, --force           Overwrite existing images if True
  -b, --beginning       Start downloading from 0

https://github.com/vanishedbydefa
```
