# -*- coding: utf-8 -*-
import datetime as dt
import requests as rq

__author__ = 'ragnarekker'


def getgts(utm33x, utm33y, element_id, from_date, to_date):
    """Retrieves data from the grid time series application (GTS) and prints dates and values to screen.

    :param utm33x:              [int] X coordinate in utm33N
    :param utm33y:              [int] Y coordinate in utm33N
    :param element_id:          [string] Element ID in seNorge. Ex: elementID = 'fsw' is 24hr new snow depth in [cm]
    :param from_date:           [datetime or string YYYY-mm-dd] method returns data [fromDate, toDate]
    :param to_date:             [datetime or string YYYY-mm-dd] method returns data [fromDate, toDate]

    Eg. URL:
    http://h-web02.nve.no:8080/api/GridTimeSeries/gridtimeserie?theme=tm&startdate=2017-11-20&enddate=2017-11-22&x=109190&y=6817490

    element_id's used:
        fws:                new snow last 24hrs in mm water equivalents
        sd:                 snow depth in cm
        tm:                 temperature average 24hrs
        sdfsw:              new snow last 24hrs in cm
    """

    url = 'http://h-web02.nve.no:8080/api/GridTimeSeries/gridtimeserie?theme={0}&startdate={1}&enddate={2}&x={3}&y={4}'\
        .format(element_id, from_date, to_date, utm33x, utm33y)

    responds = rq.get(url)
    data_and_metadata = responds.json()
    data = data_and_metadata['Data']

    # Initial values
    date = dt.datetime.strptime(data_and_metadata['StartDate'], '%d.%m.%Y %H:%M:%S')
    time_resolution = dt.timedelta(minutes=data_and_metadata['TimeResolution'])

    # Value used in the data set if there is no value for this date and time
    no_data_value = int(data_and_metadata['NoDataValue'])

    # go through all data an print to screen date and value
    for d in data:
        value = float(d)
        if value == no_data_value:
            value = None
        print('{}\t{}'.format(date, value))
        date += time_resolution


if __name__ == "__main__":

    getgts(109190, 6817490, 'tm', '2018-01-01', '2018-01-30')
