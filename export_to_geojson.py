"""
Export data from MongoDB to GeoJSON file.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from sys import argv
from pymongo import MongoClient
from lib.utils import get_event_cursor, get_feature
from json import dumps

if __name__ != '__main__':
    exit()

year = None if len(argv) < 2 else int(argv[1])
if year is None:
    fname = 'eqitaly_all.json'
else:
    fname = 'eqitaly_' + str(year) + '.json'

features = []
eq = MongoClient().ingv.earthquakes
res = get_event_cursor(year)
for item in res:
    features.append(get_feature(item))
geodict = dict(type='FeatureCollection', features=features)
with open(fname, 'wb') as f:
    f.write(dumps(geodict, indent=4, separators=(',', ': ')))
f.close()
