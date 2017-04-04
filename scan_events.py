"""
Retrieve latest earthquake events in Italy from INGV Terremoti Italia.
Author: Fabio Pani <fabiux AT fabiopani DOT it>
License: GNU/GPL version 3 (see file LICENSE)
"""
from sys import argv
from lib.utils import save_events, get_events

if __name__ != '__main__':
    exit()

if len(argv) > 2:
    save_events(get_events(year=int(argv[1]), month=int(argv[2])))
if len(argv) > 1:
    save_events(get_events(year=int(argv[1])))
else:
    save_events(get_events())
