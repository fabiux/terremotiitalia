"""
Utilities and helper functions.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from lib.cfg import *
import requests
import xml.etree.ElementTree as ET
from pymongo import MongoClient
import datetime

eq = MongoClient().ingv.earthquakes


def get_end_of_today():
    return str(datetime.date.today()) + 'T23:59:59'


def get_last_event_date():
    """
    Get last event date (+1 sec).
    :return: last event date (string)
    """
    return str(eq.find_one(sort=[('time', -1)])['time'] + datetime.timedelta(0, 1))[:19].replace(' ', 'T')


def get_url(fromdatetime=None, todatetime=None):
    """
    Compose and return web service URL.
    :param fromdatetime: initial date and time (YYYY-MM-DDTHH:MM:SS)
    :param todatetime: final date and time (YYYY-MM-DDTHH:MM:SS - None is today)
    :return: URL
    """
    if fromdatetime is None:
        fromdatetime = get_last_event_date()

    if todatetime is None:
        todatetime = get_end_of_today()

    return 'http://webservices.ingv.it/fdsnws/event/1/query?starttime=' + fromdatetime + '&endtime=' + todatetime +\
           '&minmag=' + minmag + '&maxmag=10&mindepth=0&maxdepth=1000&minlat=' + minlat + '&maxlat=' + maxlat +\
           '&minlon=' + minlon + '&maxlon=' + maxlon + '&format=xml'


def get_xml(fromdatetime=None, todatetime=None):
    """
    Get remote XML.
    :param fromdatetime: initial date and time (YYYY-MM-DDTHH:MM:SS)
    :param todatetime: final date and time (YYYY-MM-DDTHH:MM:SS - None is today)
    :return: XML (string)
    """
    r = requests.get(get_url(fromdatetime=fromdatetime, todatetime=todatetime))
    if r.status_code == 200:
        return r.text
    return ''


def get_xml_from_file():
    with open('res.xml', 'rb') as f:
        return ''.join(f.readlines())


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


# def is_ml(node):
#     return True
    # for child in node:
    #     if child.tag.split('}')[1] == 'type':
    #         return child.text == 'ML'
    # return False


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
                        'coordinates': [float(get_child_value(child, 'latitude')),
                                        float(get_child_value(child, 'longitude'))]}
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


def get_events(day=None):
    """
    Get a list of events. Each event is a dict.
    :param day: day (YYYY-MM-DD)
    :return: list of events
    """
    if day is None:
        fromdatetime = None
        todatetime = None
    else:
        fromdatetime = day + 'T00:00:00'
        todatetime = day + 'T23:59:59'
    result = []
    r = ET.fromstring(get_xml(fromdatetime=fromdatetime, todatetime=todatetime))
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
    """
    for event in events:
        try:
            eq.insert_one(event)
        except Exception as e:
            pass
