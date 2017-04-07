"""
Configuration.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from pymongo import MongoClient

minlat = '38'  # min latitude
maxlat = '48'  # max latitude
minlon = '5'   # min longitude
maxlon = '21'  # max longitude
minmag = '2'   # min magnitude

csv_fieldnames = ['id', 'datetime', 'latitude', 'longitude', 'depth', 'magnitude']

eq = MongoClient().ingv.earthquakes
