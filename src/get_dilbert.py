#!/usr/bin/env python3
from datetime import datetime, timedelta
from urllib import request
import re
import argparse
import sys
from pqdict import pqdict
import pickle

parser = argparse.ArgumentParser(description="Get a dilbert comic")
parser.add_argument("comic", type=str, help="certain comic")
args = parser.parse_args()

FIRST = "1989-04-16"
FORMAT = "%Y-%m-%d"
CACHE_FILE = "/tmp/cache.pickle"
CACHE_LIMIT = 1000

if args.comic == "latest":
    new_date = datetime.now()
    args.comic = new_date.strftime(FORMAT)
else:
    try:
        new_date = datetime.strptime(args.comic, FORMAT)
        new_date = min(
            max(new_date, datetime.strptime(FIRST, FORMAT)), datetime.now()
        )
    except ValueError:
        print("404")
        sys.exit(1)


def key_func(data):
    return data[-1]


try:
    with open(CACHE_FILE, "rb") as cfile:
        cache = pickle.load(cfile)
except FileNotFoundError:
    cache = pqdict(key=key_func)

if args.comic in cache:
    if (datetime.now() - cache[args.comic][-1]).seconds < 12 * 60 * 60:
        for item in cache[args.comic]:
            print(item)
        sys.exit(0)

is_first = False
is_latest = False

if new_date.strftime(FORMAT) == FIRST:
    is_first = True

resp = request.urlopen(
    "http://dilbert.com/strip/" + datetime.now().strftime(FORMAT)
)
if resp.url.split("/")[-1] == datetime.now().strftime(FORMAT):
    latest = datetime.now().strftime(FORMAT)
else:  # Timezone issues
    latest = (datetime.now() - timedelta(days=1)).strftime(FORMAT)

if args.comic == "latest":
    new_date = datetime.strptime(latest, FORMAT)

if new_date.strftime(FORMAT) == latest:
    is_latest = True

left = (new_date + timedelta(days=-1)).strftime(FORMAT)
right = (new_date + timedelta(days=1)).strftime(FORMAT)

original = "http://dilbert.com/strip/" + new_date.strftime(FORMAT)
try:
    resp = request.urlopen(original)
except request.HTTPError:
    print("404")
    sys.exit(1)

html = resp.read().decode("utf8")
url = re.findall('<img[^>]*class="img-[^>]*src="([^"]+)"[^>]*>', html)[0]
date = " ".join(
    re.findall(
        '<date class="comic-title-date" item[pP]rop="datePublished">'
        '[^<]*<span>([^<]*)</span>[^<]*<span item[pP]rop="copyrightYear">'
        "([^<]+)</span>",
        html,
    )[0]
)
name = re.findall('<span class="comic-title-name">([^<]+)</span', html)
if len(name) > 0:
    name = name[0]
else:
    name = ""

actual_date = datetime.strptime(
    " ".join(date.split()[1:]), "%B %d, %Y"
).strftime(FORMAT)

data = [
    url,
    original,
    FIRST,
    left,
    right,
    latest,
    is_first,
    is_latest,
    date,
    name,
    actual_date,
    datetime.now(),
]
cache[actual_date] = data
if len(cache) > CACHE_LIMIT:
    cache.pop()
with open(CACHE_FILE, "wb") as cfile:
    pickle.dump(cache, cfile)

for item in data:
    print(item)
