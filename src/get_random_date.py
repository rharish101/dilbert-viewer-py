#!/usr/bin/env python
from random import randint
from datetime import datetime, timedelta

FIRST = "1989-04-16"
first = datetime.strptime(FIRST, "%Y-%m-%d")
span = (datetime.now() - first).days
days = randint(0, span)
print((first + timedelta(days=days)).strftime("%Y-%m-%d"))
