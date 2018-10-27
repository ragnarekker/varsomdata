# -*- coding: utf-8 -*-
"""This is an example of how varsomdata/getobservations.py may be used to get observations
from regObs webapi - http://api.nve.no/doc/regobs-webapi/

It takes time to make requests. Progress can be followed in the log files.
"""

from varsomdata import getobservations as go

__author__ = 'raek'

# # One observation with a given ID may
# one_obs = go.get_data(reg_ids=130548)
#
# # If multiple id's wil be used, give them as list. Result may be returned as a list of forms (default) or
# # nested, i.e. all forms are listed under their respective observations.
# two_obs = go.get_data(reg_ids=[130548, 130328], output='Nest')
#
# # A request may specify a time period and specific geohazards.
# # Snow is 10 and ice is 70. Water is 60. Dirt is [20, 30, 40]
# all_data_snow = go.get_data('2016-12-30', '2017-01-01', geohazard_tids=10)
# ice_data = go.get_data(from_date='2016-10-01', to_date='2016-11-01', geohazard_tids=70, output='Nest')
#
# # The data may be returned as a list of classes, as opposed to the default return in get_data which are dictionaries
# # raw as given on regObs webapi.
# data_as_classes = go.get_data_as_class('2018-05-01', '2018-08-01')
#
# # We may get observation forms directly. Note, from and to date are first and may also be given as
# # positional arguments, even though Is recommend keyword arguments.
# land_slides = go.get_land_slide_obs('2018-01-01', '2018-02-01')
# incident = go.get_incident('2012-03-01', '2012-03-10')
# ice_thicks = go.get_ice_thickness('2018-01-20', '2018-02-10')
# snow_surface = go.get_snow_surface_observation('2018-01-28', '2018-02-01')
# problems = go.get_avalanche_problem_2('2017-03-01', '2017-03-10')

# We may request an observation count.
# Remember: if forms are grouped under the observation, its a nest.
# If the forms are separate items in the list, its a list.
seasonal_count_regs = go.get_data('2016-08-01', '2017-08-01', output='Count nest')

# And give date as a date time, and not a string.
# Note the argument specifying a part of an Observer Nick.
import datetime as dt
count_registrations_snow_10 = go.get_data(dt.date(2018, 10, 1), dt.date.today(), geohazard_tids=10, output='Count list', observer_nick='obskorps')

pass
