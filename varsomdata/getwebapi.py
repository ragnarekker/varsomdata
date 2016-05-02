# -*- coding: utf-8 -*-
__author__ = 'raek'



import requests

url = 'https://api.nve.no/hydrology/regobs/webapi_latest/Search/Rss'
rssquery = {}
rssquery = {'LangKey': None,                        # int
            'RegId': None,                          # int
            'SelectedRegistrationTypes': None,      # string?
            'SelectedRegions': None,                # ??
            'SelectedGeoHazards': 10,               # int
            'ObserverId': None,                     # int
            'GroupId': None,                        # int
            'LocationId': None,                     # int
            'FromDate': '2015-11-01',               # string 'yyyy-mm-dd'
            'ToDate': None,                         # string 'yyyy-mm-dd'
            'NumberOfRecords': None                 # int
            }

r = requests.post(url, json=rssquery)
data = r.json()
first = data[0]
last = data[-1]

'''
if package to big, make two requests?

'''

b = 1
