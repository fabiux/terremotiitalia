"""
Export data from MongoDB to CSV file.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)

Examples.
Export all data: python export_to_csv.py
Export all data in a given year: python export_to_csv.py <year>
"""
from sys import argv
from lib.utils import get_event_cursor, get_row_for_csv
from csv import DictWriter, QUOTE_NONNUMERIC

if __name__ != '__main__':
    exit()

year = None if len(argv) < 2 else int(argv[1])
if year is None:
    fname = 'eqitaly_all.csv'
else:
    fname = 'eqitaly_' + str(year) + '.csv'
fieldnames = ['id', 'datetime', 'latitude', 'longitude', 'depth', 'magnitude']
res = get_event_cursor(year)
with open(fname, 'wb') as f:
    wr = DictWriter(f, fieldnames=fieldnames, quotechar='"', quoting=QUOTE_NONNUMERIC)
    wr.writeheader()
    for item in res:
        wr.writerow(get_row_for_csv(item))
f.close()
