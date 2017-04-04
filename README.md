# Simple Earthquake Data Retriever

<em>Author: Fabio Pani - <tt>fabiux AT fabiopani DOT it</tt></em><br />
<em>License: GNU/GPL v.3 (see file <tt>LICENSE</tt>)</em>

This is a data retriever for earthquakes in Italy written in Python, using [INGV](http://www.ingv.it/) public web services.

This script can be scheduled on your <tt>/etc/crontab</tt>. It saves a small subset of significant data about latest earthquakes in Italy in a <tt>MongoDB</tt> collection.

## <tt>scan_events.py</tt>
This script retrieves latest earthquake events in Italy from INGV Terremoti Italia.

It can be scheduled in <tt>/etc/crontab</tt> .

## <tt>retrieve_data.py</tt>
This script retrieves old earthquake events in Italy from INGV Terremoti Italia.

## <tt>export_to_csv.py</tt>
This script exports data from <tt>MongoDB</tt> collection to <tt>CSV</tt> file.

## <tt>import_from_csv.py</tt>
This script imports data from <tt>CSV</tt> file to <tt>MongoDB</tt> collection.

## <tt>export_to_geojson.py</tt>
This script exports data from <tt>MongoDB</tt> collection to <tt>GeoJSON</tt> file.

Hypocenter depth is the third spatial coordinate (z-axis) under the sea level (meters).

Datasets are actually large for a map representation: take a look at the code in order to customize your datasets.

## Data format
Example of a document stored in our <tt>MongoDB</tt> collection:

    {
        "_id" : 8868791,
        "loc" : {
            "type" : "Point",
            "coordinates" : [ 
                42.8578, 
                13.0613
            ]
        },
        "depth" : 9500,
        "magnitude" : 3.5,
        "time" : ISODate("2016-10-30T08:10:51.000Z")
    }

- <tt><b>_id</b></tt>: event id as reported by INGV
- <tt><b>loc</b></tt>: geolocalization of hypocenter (you must define a <tt>2dsphere</tt> index for this field)
- <tt><b>depth</b></tt>: depth of hypocenter (meters)
- <tt><b>magnitude</b></tt>: magnitude of the event
- <tt><b>time</b></tt>: UTC time of the event

## Historical data
A dump of historical data is available [here](http://bit.ly/eqitalydata).

