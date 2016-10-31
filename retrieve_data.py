"""
(Quick and dirty) data retriever for INGV Terremoti Italia.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from time import sleep
from lib.utils import save_events, get_events

leapyears = [2012, 2008, 2004, 2000, 1996, 1992, 1988, 1984, 1980, 1976, 1972, 1968, 1964, 1960]
startyear = 1995
endyear = 1999
months = {'12': 31, '11': 30, '10': 31, '09': 30, '08': 31, '07': 31, '06': 30, '05': 31, '04': 30, '03': 31, '02': 28,
          '01': 31}

for y in range(startyear, endyear + 1):
    for m in months.keys():
        days = months[m]
        if (y in leapyears) and (m == '02'):
            days += 1
        days = ('0' + str(days))[-2:]
        save_events(get_events(month=str(y) + '-' + m, daysinmonth=days))
        sleep(20)
