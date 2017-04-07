"""
Utilities and helper functions.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from lib.cfg import *
import requests
import xml.etree.ElementTree as ET
from lib.cfg import eq
from pymongo import ASCENDING
import datetime
from calendar import monthrange
from xmltodict import parse
from json import dumps


def get_end_of_today():
    return str(datetime.date.today()) + 'T23:59:59'


def get_last_event_date():
    """
    Get last event date (+1 sec).
    :return: last event date (string)
    """
    return str(eq.find_one(sort=[('time', -1)])['time'] + datetime.timedelta(0, 1))[:19].replace(' ', 'T')


def get_url(fromdatetime=None, todatetime=None, limits=True):
    """
    Compose and return web service URL.
    :param fromdatetime: initial date and time (YYYY-MM-DDTHH:MM:SS)
    :type fromdatetime: str
    :param todatetime: final date and time (YYYY-MM-DDTHH:MM:SS - None is today)
    :type todatetime: str
    :param limits: use configured limits (magnitude and coordinates) set in config file
    :type limits: bool
    :return: URL
    """
    if fromdatetime is None:
        fromdatetime = get_last_event_date()

    if todatetime is None:
        todatetime = get_end_of_today()

    url = 'http://webservices.ingv.it/fdsnws/event/1/query?starttime=' + fromdatetime + '&endtime=' + todatetime
    if limits:
        url += '&minmag=' + minmag + '&maxmag=10&mindepth=0&maxdepth=1000&minlat=' + minlat + '&maxlat=' + maxlat + \
               '&minlon=' + minlon + '&maxlon=' + maxlon + '&format=xml'

    return url


def get_xml(fromdatetime=None, todatetime=None, limits=True):
    """
    Get remote XML.
    :param fromdatetime: initial date and time (YYYY-MM-DDTHH:MM:SS)
    :type fromdatetime: str
    :param todatetime: final date and time (YYYY-MM-DDTHH:MM:SS - None is today)
    :type todatetime: str
    :param limits: use configured limits (magnitude and coordinates) set in config file
    :type limits: bool
    :return: XML (string)
    """
    r = requests.get(get_url(fromdatetime=fromdatetime, todatetime=todatetime, limits=limits))
    if r.status_code == 200:
        return r.text
    return ''


# def get_xml_from_file():
#     with open('res.xml', 'rb') as f:
#         return ''.join(f.readlines())


def get_json(fromdatetime=None, todatetime=None, limits=True):
    """
    Get remote JSON (converted from remote XML).
    :param fromdatetime:  initial date and time (YYYY-MM-DDTHH:MM:SS)
    :type fromdatetime: str
    :param todatetime: final date and time (YYYY-MM-DDTHH:MM:SS - None is today)
    :type todatetime: str
    :param limits: use configured limits (magnitude and coordinates) set in config file
    :return: formatted JSON (string)
    """
    o = parse(get_xml(fromdatetime=fromdatetime, todatetime=todatetime, limits=limits))
    return dumps(o, indent=4)


def get_id(node):
    return int(node.attrib['publicID'].split('=')[1])


def get_value(node):
    for child in node:
        if child.tag.split('}')[1] == 'value':
            return child.text
    return None


def is_earthquake(node):
    for child in node:
        if child.tag.split('}')[1] == 'type':
            return child.text == 'earthquake'
    return False


def is_hypocenter(node):
    for child in node:
        if child.tag.split('}')[1] == 'type':
            return child.text == 'hypocenter'
    return False


def get_child_value(node, name):
    for child in node:
        if child.tag.split('}')[1] == name:
            return get_value(child)
    return None


def get_origin_data(node):
    d = {}
    for child in node:
        if child.tag.split('}')[1] == 'origin':
            d['time'] = datetime.datetime.strptime(get_child_value(child, 'time')[:19], '%Y-%m-%dT%H:%M:%S')
            d['loc'] = {'type': 'Point',
                        'coordinates': [float(get_child_value(child, 'longitude')),
                                        float(get_child_value(child, 'latitude'))]}
            d['depth'] = float(get_child_value(child, 'depth'))
    return d


def get_magnitude(node):
    for child in node:
        if child.tag.split('}')[1] == 'magnitude':
            # if is_ml(child):
            for item in child:
                if item.tag.split('}')[1] == 'mag':
                    return float(get_value(item))
    return None


def get_events(year=None, month=1, limits=True):
    """
    Get a list of events. Each event is a dict.
    :param year: year
    :type year: int
    :param month: month
    :type month: int
    :param limits: use configured limits (magnitude and coordinates) set in config file
    :type limits: bool
    :return: list of events
    """
    if year is None:
        fromdatetime = None
        todatetime = None
    else:
        m = ('0' + str(month))[-2:]
        fromdatetime = str(year) + '-' + m + '-01T00:00:00'
        todatetime = str(year) + '-' + m + '-' + str(monthrange(year, month)[1]) + 'T23:59:59'

    result = []
    try:
        r = ET.fromstring(get_xml(fromdatetime=fromdatetime, todatetime=todatetime, limits=limits))
    except Exception as e:
        return result
    for item in r.iter('*'):
        if item.text is not None and not item.text.strip():
            if item.tag.split('}')[1] == 'event':  # new event
                data = dict()
                data['_id'] = get_id(item)
                if is_earthquake(item):
                    data = dict(data.items() + get_origin_data(item).items())
                    data['magnitude'] = get_magnitude(item)
                    result.append(data)
    return result


def save_events(events):
    """
    Save a list of events on a MongoDB database.
    :param events: list ov events
    :type events: list
    """
    for event in events:
        try:
            eq.insert_one(event)
        except Exception as e:
            pass


def get_event_cursor(year=None, month=None):
    """
    Return a MongoDB cursor for events in the specified year.
    :param year: year (None for all events in the collection)
    :type year: int
    :param month: month (None for all events in the specified year)
    :type month: int
    :return: MongoDB cursor for selected events
    """
    qfilter = {}
    if year is not None:
        if month is not None:
            y2 = year
            m2 = month + 1
            if m2 > 12:
                m2 = 1
                y2 += 1
            qfilter = {'time': {'$gte': datetime.datetime(year, month, 1, 0, 0, 0),
                                '$lt': datetime.datetime(y2, m2, 1, 0, 0, 0)}}
        else:
            qfilter = {'time': {'$gte': datetime.datetime(year, 1, 1, 0, 0, 0),
                                '$lt': datetime.datetime(year + 1, 1, 1, 0, 0, 0)}}
    eq = MongoClient().ingv.earthquakes
    try:
        return eq.find(qfilter).sort('time', ASCENDING)
    except Exception as e:
        return None


def convert_row_for_csv(d):
    """
    Convert an event dict for saving a row in a CSV file.
    See also: convert_row_for_mongo()
    :param d: event dict from MongoDB collection
    :type d: dict
    :return: converted event dict (for CSV)
    """
    return dict(id=d['_id'],
                datetime=str(d['time'])[:19],
                longitude=d['loc']['coordinates'][0],
                latitude=d['loc']['coordinates'][1],
                depth=d['depth'],
                magnitude=d['magnitude'])


def convert_row_for_mongo(d):
    """
    Convert an event dict for saving a new doc in a MongoDB collection.
    See also: convert_row_for_csv()
    :param d: event dict from CSV file
    :type d: dict
    :return: converted event dict (for MongoDB)
    """
    cd = dict(time=datetime.datetime.strptime(d['datetime'], '%Y-%m-%d %H:%M:%S'),
              loc=dict(type='Point', coordinates=[float(d['longitude']), float(d['latitude'])]),
              depth=float(d['depth']),
              magnitude=float(d['magnitude']))
    cd['_id'] = int(d['id'])
    return cd


def get_feature(d):
    """
    Convert an event dict to a GeoJSON feature.
    :param d: event dict from MongoDB collection
    :type d: dict
    :return: GeoJSON dict
    """
    # geometry dict
    g = dict(type='Point',
             coordinates=[d['loc']['coordinates'][0], d['loc']['coordinates'][1], -d['depth']])
    # properties dict
    p = dict(magnitude=d['magnitude'], datetime=str(d['time'])[:19].replace(' ', 'T') + 'Z')
    return dict(type='Feature', geometry=g, properties=p)
