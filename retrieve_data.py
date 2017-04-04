"""
Data retriever for INGV Terremoti Italia.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from time import sleep
from lib.utils import save_events, get_events

startyear = 1995
endyear = 1999

for y in range(startyear, endyear + 1):
    for m in range(1, 13):
        save_events(get_events(year=y, month=m))
        sleep(20)
