# csptfinder.py
Python script to flag possible Client-Side Path Traversals


## Install
```
git clone https://github.com/microphone-mathematics/csptfinder.git
cd csptfinder && pip3 install -r requirements.txt
```

## Usage
```
$ ./csptfinder.py -h
usage: csptfinder.py [-h] (-f file | -u url) [-o outfile] [-s sleeptime] [-b cookie_string] [-x --proxy] [-H --header] [-v] [-vv]

Flags possible Client-Side Path Traversals from a list of URLs.

options:
  -h, --help            show this help message and exit
  -f file, --file file  file with url list (type: str)
  -u url, --url url     URL (type: str)
  -o outfile, --outfile outfile
                        output file path (type: str)
  -s sleeptime, --sleep sleeptime
                        sleep time in seconds (type: float)
  -b cookie_string, --cookies cookie_string
                        CookieName=CookieValue; CookieName2=CookieValue2.. (type: str)
  -x --proxy            (http|https|socks5)://PROXYHOST:PROXYPORT (type: str)
  -H --header           {"HeaderName": "HeaderValue", "HeaderName2": "HeaderValue2"} (type: json)
  -v                    informative debug mode (type: bool)
  -vv                   verbose debug mode (type: bool)
```
