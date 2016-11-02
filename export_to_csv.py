"""
Export data from MongoDB to CSV file.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)

Examples.
Export all data: python export_to_csv.py
Export all data in a given year: python export_to_csv.py <year>
"""
from sys import argv
from lib.utils import get_event_cursor, convert_row_for_csv
from csv import DictWriter, QUOTE_NONNUMERIC
from lib.utils import csv_fieldnames

if __name__ != '__main__':
    exit()

year = None if len(argv) < 2 else int(argv[1])
if year is None:
    fname = 'eqitaly_all.csv'
else:
    fname = 'eqitaly_' + str(year) + '.csv'
res = get_event_cursor(year)
with open(fname, 'wb') as f:
    writer = DictWriter(f, fieldnames=csv_fieldnames, quotechar='"', quoting=QUOTE_NONNUMERIC)
    writer.writeheader()
    for item in res:
        writer.writerow(convert_row_for_csv(item))
f.close()
