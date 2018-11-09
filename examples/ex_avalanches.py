# -*- coding: utf-8 -*-
"""This is an example of how to retrieve avalanche observations by using the varsomdata/getobservations.py
module.

It takes time to make requests. Progress can be followed in the log files.
"""

from varsomdata import getobservations as go

__author__ = 'Ragnar Ekker'

# The first avalanche activity form was used between 2012 and 2016.
avalanche_activity = go.get_avalanche_activity('2015-03-01', '2015-03-10')

# The second avalanche activity form was introduces in 2015 and is currently in use (nov 2018).
avalanche_activity_2 = go.get_avalanche_activity_2('2017-03-01', '2017-03-10')

print('Std.out from AvalancheActivityObs2 object')
print('\t', avalanche_activity_2[0].DestructiveSizeName)


# Observations of singe avalanches
avalanche_obs = go.get_avalanche('2015-03-01', '2015-03-10')

print('Std.out from AvalancheObs object')
print('\t', avalanche_obs[0].HeightStartZone, avalanche_obs[0].DestructiveSizeName)

# Observations of avalanches given as a danger sign (DangerSignTID = 2).
# A query might be specified on region, eg region_id=3011 is Tromsø.
all_danger_signs = go.get_danger_sign('2018-03-01', '2018-03-10', region_ids=3011)
avalanche_danger_signs = []
for o in all_danger_signs:
    if o.DangerSignTID == 2:  # danger sign is avalanche activity
        avalanche_danger_signs.append(o)

print('Std.out from DangerSign object')
print('\t', avalanche_danger_signs[0].DangerSignName)

# Note that in this example dates are given as strings, but may also be given as date objects.
# Se ex_observations for more examples on queries.

# Picture url and metadata are in the pictures list on each observation.
# note that the picture of danger signs does not know which danger sign the picture is of, so some pictures
# might be of other danger signs.
all_pictures = []
for a in avalanche_activity + avalanche_activity_2 + avalanche_obs + avalanche_danger_signs:
    for p in a.Pictures:
        all_pictures.append(p)

pass
