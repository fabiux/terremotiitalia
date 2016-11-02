"""
Import data from CSV file to MongoDB.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from sys import argv
from csv import DictReader, QUOTE_NONNUMERIC
from lib.utils import csv_fieldnames, convert_row_for_mongo
from pymongo import MongoClient

if __name__ != '__main__':
    exit()

if len(argv) < 2:
    print('Usage: python import_from_csv.py <csv_file>')
    exit()

eq = MongoClient().ingv.earthquakes

with open(argv[1], 'rb') as f:
    reader = DictReader(f, fieldnames=csv_fieldnames, quotechar='"', quoting=QUOTE_NONNUMERIC)
    reader.next()  # skip header
    for event in reader:
        try:
            eq.insert_one(convert_row_for_mongo(event))
        except Exception as e:
            pass
f.close()
