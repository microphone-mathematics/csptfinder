# csptfinder.py
Python script to flag possible Client-Side Path Traversals

Uses Selenium-Wire and Undetected-ChromeDriver under the hood.


## Install
```
git clone https://github.com/microphone-mathematics/csptfinder.git
cd csptfinder && pip3 install -r requirements.txt
```

## Usage
```
$ ./csptfinder.py -h
usage: csptfinder.py [-h] (-f file | -u url) [-o outfile] [-s sleeptime] [-b cookie_string] [--cookies-domain domain] [-x --proxy] [-H --header] [-v] [-vv] [--silent | --no-silent]

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
  --cookies-domain domain
                        use custom domain for cookies
  -x --proxy            (http|https|socks5)://PROXYHOST:PROXYPORT (type: str)
  -H --header           {"HeaderName": "HeaderValue", "HeaderName2": "HeaderValue2"} (type: json)
  -v                    informative debug mode (type: bool)
  -vv                   verbose debug mode (type: bool)
  --silent, --no-silent
                        silent mode - hide errors (type: bool)
```

## Example results
#### Using file with list of URLs
```
$ ./csptfinder.py -f urls.txt -s 1
[*] [GET]  https://huntdash.xyz/cspt/jamesmfdoom.jpg?query=true  [404]  Parameters: ['path']  | Opener: https://huntdash.xyz/static/clientsidepathtraversalpoc.html?path=jamesmfdoom&ext=jpg&random=true
[*] [GET]  https://huntdash.xyz/cspt/james.jpgmfdoom?query=true  [404]  Parameters: ['ext']  | Opener: https://huntdash.xyz/static/clientsidepathtraversalpoc.html?path=james&ext=jpgmfdoom&random=true
```

#### Using single inline URL
```
$ ./csptfinder.py -u "https://huntdash.xyz/static/clientsidepathtraversalpoc.html?path=james&ext=jpg&random=true" -s 1
[*] [GET]  https://huntdash.xyz/cspt/jamesmfdoom.jpg?query=true  [404]  Parameters: ['path']  | Opener: https://huntdash.xyz/static/clientsidepathtraversalpoc.html?path=jamesmfdoom&ext=jpg&random=true
[*] [GET]  https://huntdash.xyz/cspt/james.jpgmfdoom?query=true  [404]  Parameters: ['ext']  | Opener: https://huntdash.xyz/static/clientsidepathtraversalpoc.html?path=james&ext=jpgmfdoom&random=true
```
