"""
(Quick and dirty) data retriever for INGV Terremoti Italia.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from time import sleep
from lib.utils import save_events, get_events

leapyears = ['2012', '2008', '2004', '2000', '1996', '1992']
years = ['2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001',
         '2000', '1999', '1998', '1997', '1996', '1995', '1994', '1993', '1992', '1991', '1990']
months = {'12': 31, '11': 30, '10': 31, '09': 30, '08': 31, '07': 31, '06': 30, '05': 31, '04': 30, '03': 31, '02': 28,
          '01': 31}

for y in years:
    for m in months.keys():
        days = months[m]
        if (y in leapyears) and (m == '02'):
            days += 1
        days = ('0' + str(days))[-2:]
        save_events(get_events(month=y + '-' + m, daysinmonth=days))
        sleep(20)
