# -*- coding: utf-8 -*-
"""This is an example of how varsomdata/getobservations.py may be used to get observations
from regObs webapi - http://api.nve.no/doc/regobs-webapi/

It takes time to make requests. Progress can be followed in the log files.
"""
__author__ = 'kmu'

from varsomdata import getforecastapi as gf

# Get mountain weather for single avalanche forecasting region
mw = gf.MountainWeather()
mw.from_api_region(3014, '2019-01-27')

print(mw)

