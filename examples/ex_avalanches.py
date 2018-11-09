# -*- coding: utf-8 -*-
"""This is an example of how to retrieve avalanche observations by using the varsomdata/getobservations.py
module.

It takes time to make requests. Progress can be followed in the log files.
"""

from varsomdata import getobservations as go

__author__ = 'Ragnar Ekker'

# The first avalanche activity form was used between 2012 and 2016.
avalanche_activity = go.get_avalanche_activity('2015-03-01', '2015-03-10')

# The second avalanche activity from was introduces in 2015 and is currently in use (nov 2018).
avalanche_activity_2 = go.get_avalanche_activity_2('2017-03-01', '2017-03-10')

# Observations of singe avalanches
avalanche_obs = go.get_avalanche('2015-03-01', '2015-03-10')

# Note that in this example dates are given as strings, but may also be given as date objects.
# Se ex_observations for more examples on queries.

# Picture url and metadata are in the pictures list on each observation.
all_pictures = []
for a in avalanche_activity + avalanche_activity_2 + avalanche_obs:
    for p in a.Pictures:
        all_pictures.append(p)

pass