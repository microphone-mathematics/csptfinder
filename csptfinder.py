#!/usr/bin/python3
import seleniumwire.undetected_chromedriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidCookieDomainException
from selenium.common.exceptions import UnexpectedAlertPresentException
from urllib.parse import urlparse, parse_qs, urlencode
from http.cookies import SimpleCookie
import sys
import time
import argparse
import json
import logging


# Define logger for debugging messages
logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)


def interceptor(request):
    if args.headers:
        # Add custom headers
        for h in args.headers.keys():
            del request.headers[h]  # Delete the header first
            request.headers[h] = args.headers[h]


# Parse Cmdline Arguments
description = 'Flags possible Client-Side Path Traversals from a list of URLs.'
parser = argparse.ArgumentParser(
    description=description
)

# Make file OR url required
parser_group = parser.add_mutually_exclusive_group(required=True)

parser_group.add_argument(
    '-f', '--file', dest='file', metavar='file', type=str,
    help='file with url list  (type: str)'
)
parser_group.add_argument(
    '-u', '--url', dest='url', metavar='url', type=str,
    help='URL  (type: str)'
)
# Optional arguments
parser.add_argument(
    '-o', '--outfile', dest='outfile', metavar='outfile', type=str,
    help='output file path  (type: str)'
)
parser.add_argument(
    '-s', '--sleep', dest='sleep', metavar='sleeptime', type=float,
    help='sleep time in seconds  (type: float)'
)
cookie_help = 'CookieName=CookieValue; CookieName2=CookieValue2..  (type: str)'
parser.add_argument(
    '-b', '--cookies', dest='cookies', metavar='cookie_string', type=str,
    help=cookie_help
)
parser.add_argument(
    '-x', dest='proxy', metavar='--proxy', type=str,
    help='(http|https|socks5)://PROXYHOST:PROXYPORT  (type: str)'
)
header_help = (
    '{"HeaderName": "HeaderValue", "HeaderName2": "HeaderValue2"} '
    '(type: json)'
)
parser.add_argument(
    '-H', dest='headers', metavar='--header', type=json.loads,
    help=header_help
)
parser.add_argument(
    '-v', dest='informative', metavar='informative',
    action=argparse.BooleanOptionalAction,
    help='informative debug mode  (type: bool)'
)
parser.add_argument(
    '-vv', dest='verbose', metavar='verbose',
    action=argparse.BooleanOptionalAction,
    help='verbose debug mode  (type: bool)'
)
args = parser.parse_args()

if args.outfile:
    # Create output file
    with open(args.outfile, 'w') as outfile:
        pass


# Set Selenium Driver Options
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--headless')
if args.proxy:
    # Set custom proxy
    seleniumwire_options = {'proxy': {'https': args.proxy, 'http': args.proxy}}
else:
    seleniumwire_options = {}


# Start webdriver
driver = webdriver.Chrome(
    options=options, seleniumwire_options=seleniumwire_options
)

if args.headers:
    # Set interceptor for custom headers
    driver.request_interceptor = interceptor

cookie = SimpleCookie()
if args.cookies:
    # Create cookie dict from cookie string
    cookie.load(args.cookies)
    cookies = {k: v.value for k, v in cookie.items()}
else:
    cookies = {}
headers = {}
flagged_messages = []


def get_ajax_requests(url, sleep, cookies, last_parsed_hostname):
    parsed_url = urlparse(url)
    url_query = parse_qs(parsed_url.query, keep_blank_values=True)
    del driver.requests
    try:
        # Iterate over URL query parameters
        for k in url_query.keys():
            new_param = {k: f'{url_query[k][0]}mfdoom'}
            new_url_query = parse_qs(parsed_url.query, keep_blank_values=True)
            new_url_query.update(new_param)
            url = parsed_url._replace(
                query=urlencode(new_url_query, doseq=True)
            ).geturl()
            if args.verbose:
                log.warning(
                    f'[****] query param: {k}={new_url_query[k]}'
                )
            if not args.cookies:
                driver.get(url)
            else:
                if last_parsed_hostname != parsed_url.hostname:
                    # Navigate once to domain to be able to add cookies
                    driver.get(f'{parsed_url.scheme}://{parsed_url.hostname}/')
                for c in cookies.keys():
                    if parsed_url.hostname != '':
                        # Add custom cookies to webdriver
                        try:
                            driver.add_cookie({
                                'name': c,
                                'domain': parsed_url.hostname,
                                'value': cookies[c],
                            })
                        except InvalidCookieDomainException as e:
                            log.warning(f'[!!] Error: {e}')
                            log.warning(parsed_url.hostname)
                del driver.requests
                driver.get(url)
            time.sleep(sleep)
            for request in driver.requests:
                flagged = False
                flagged_params = []
                parsed_req_url = urlparse(request.url)
                req_path = parsed_req_url.path
                if args.verbose:
                    log.warning(
                        f'[****] req_path: {req_path}'
                    )
                    log.warning(
                        f'[****] new_url_query: {new_url_query[k]}'
                    )
                # Check if query value is reflected in path
                if new_url_query[k] in req_path:
                    # Avoid flagging browser redirects
                    if driver.current_url != request.url:
                        flagged = True
                        flagged_params.append(k)
                if flagged:
                    if request.response:
                        flag_msg = (
                            f'[*] [{request.method}]  '
                            f'{request.url}'
                            f'  [{str(request.response.status_code)}]  '
                            f'Parameters: {flagged_params}  '
                            f'| Opener: {url}'
                        )
                    else:
                        flag_msg = (
                            f'[*] [{request.method}]  '
                            f'{request.url}  [No response]  '
                            f'Parameters: {flagged_params}  '
                            f'| Opener: {url}'
                        )
                    if flag_msg not in flagged_messages:
                        print(flag_msg)
                        flagged_messages.append(flag_msg)
                        if args.outfile:
                            with open(args.outfile, 'a') as outfile:
                                outfile.write(f'{flag_msg}\n')
                        sys.stdout.flush()
    except TimeoutException as ex:
        log.warning('[!!] Error: ', url, ex)
    except UnexpectedAlertPresentException as ex:
        log.warning('[!!] Error: ', url, ex)


if args.file:
    urls_file_path = args.file
    with open(urls_file_path, 'r') as urls_file:
        urls = urls_file.read().splitlines()
if args.url:
    urls = [args.url]
if args.sleep:
    sleep = args.sleep
else:
    sleep = 5
last_parsed_hostname = ''
for url in urls:
    if args.informative:
        log.warning(f'[**] url: {url}')
    get_ajax_requests(url, sleep, cookies, last_parsed_hostname)
    last_parsed_hostname = urlparse(url).hostname

