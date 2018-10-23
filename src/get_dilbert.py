#!/usr/bin/env python3
from datetime import datetime, timedelta
from urllib import request
import re
import argparse
import sys

parser = argparse.ArgumentParser(description="Get a dilbert comic")
parser.add_argument("comic", type=str, help="certain comic")
args = parser.parse_args()

FIRST = "1989-04-16"

if args.comic == "latest":
    new_date = datetime.now()
else:
    try:
        new_date = datetime.strptime(args.comic[-10:], "%Y-%m-%d")
        new_date = min(
            max(new_date, datetime.strptime(FIRST, "%Y-%m-%d")), datetime.now()
        )
    except ValueError:
        new_date = get_random_date()

is_first = False
is_latest = False

if new_date.strftime("%Y-%m-%d") == FIRST:
    is_first = True

try:
    request.urlopen(
        "http://dilbert.com/strip/" + datetime.now().strftime("%Y-%m-%d")
    )
    latest = datetime.now().strftime("%Y-%m-%d")
except request.HTTPError:  # Timezone issues
    latest = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if args.comic == "latest":
        new_date = datetime.strptime(latest, "%Y-%m-%d")

if new_date.strftime("%Y-%m-%d") == latest:
    is_latest = True

left = (new_date + timedelta(days=-1)).strftime("%Y-%m-%d")
right = (new_date + timedelta(days=1)).strftime("%Y-%m-%d")

while True:
    original = "http://dilbert.com/strip/" + new_date.strftime("%Y-%m-%d")
    try:
        resp = request.urlopen(original)
        break
    except request.HTTPError:
        print("404")
        sys.exit(1)

html = resp.read().decode("utf8")
tag = re.findall('<img[^>]*class="img-[^>]*>', html)[0]

url = re.findall('src="[^"]+"', tag)[0][5:-1]

print(url)
print(original)
print(FIRST)
print(left)
print(right)
print(latest)
print(is_first)
print(is_latest)
