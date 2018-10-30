# -*- coding: utf-8 -*-
"""This is an example of how to get forecasted avalanche problems and danger levels from varsom and
observed avalanvhe probelms and danger levels from regObs.

Example uses varsomdata/getproblems.py and varsomdata/getdangers.py which are modules for accessing
problems and dangers indifferent if they are forecasted or observed and thus if thsy are for varsom-api or
from regObs. Data are mapped to the classes AvalancheProblem and AvalancheDanger which make the data sets
comparable.

Over the years, forecast regions have been changed. To read about these changes, see documentation in
get_forecast_regions in varsomdata/getmisc.py.

All observations in regObs are mapped to new regions
when new regions are introduced. To make a data set of observations which may be compared to old forecasts
all observations are mapped to the old regions with the method get_forecast_region_for_coordinate in
varsomdata/getmisc.py.

It takes time to make requests. Approx 20min pr year requested. Progress can be followed in the log files.
"""

import datetime as dt
from varsomdata import getproblems as gp
from varsomdata import getdangers as gd
from varsomdata import getmisc as gm
from utilities import fencoding as fe
import setenvironment as env

__author__ = 'raek'

years = ['2014-15', '2015-16', '2016-17', '2017-18']

forecast_problems = []
forecast_dangers = []
observed_dangers = []
observed_problems = []

for y in years:
    # Get forecast data. Different region ids from year to year.
    region_ids = gm.get_forecast_regions(year=y)
    from_date, to_date = gm.get_forecast_dates(y)
    forecast_problems += gp.get_forecasted_problems(region_ids, from_date, to_date, lang_key=1)
    forecast_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date, lang_key=1)

    # Get observed data. All older data in regObs have been mapped to new regions.
    region_ids = gm.get_forecast_regions(year='2016-17')
    from_date, to_date = gm.get_forecast_dates(y, padding=dt.timedelta(days=20))
    current_years_observed_dangers = gd.get_observed_dangers(region_ids, from_date, to_date, lang_key=1)
    current_years_observed_problems = gp.get_observed_problems(region_ids, from_date, to_date, lang_key=1)

    # Update observations with forecast region ids and names used the respective years.
    for od in current_years_observed_dangers:
        utm33x = od.metadata['Original data'].UTMEast
        utm33y = od.metadata['Original data'].UTMNorth
        region_id, region_name = gm.get_forecast_region_for_coordinate(utm33x, utm33y, y)
        od.region_regobs_id = region_id
        od.region_name = region_name

    for op in current_years_observed_problems:
        utm33x = op.metadata['Original data']['UtmEast']
        utm33y = op.metadata['Original data']['UtmNorth']
        region_id, region_name = gm.get_forecast_region_for_coordinate(utm33x, utm33y, y)
        op.region_regobs_id = region_id
        op.region_name = region_name

    observed_dangers += current_years_observed_dangers
    observed_problems += current_years_observed_problems

"""When all problems and dangers are received and mapped to their original regions, we can make an additional mapping
to the EAWS problems. Note that observations in regObs do not focus on the classification of the problem, but
the week layer and its properties in the snow pack and its ability give avalanches. To read more about this problem
see the documentation in AvalancheProblem.map_to_eaws_problems()"""

for p in forecast_problems:
    p.map_to_eaws_problems()

for p in observed_problems:
    p.map_to_eaws_problems()

"""Write to file by using collections to map the objects to dictionaries before writing out strings line by line 
to file."""

output_forecast_problems = '{0}example forecast problems.csv'.format(env.output_folder)
output_forecast_dangers = '{0}example forecast dangers.csv'.format(env.output_folder)
output_observed_problems = '{0}example observed problems.csv'.format(env.output_folder)
output_observed_dangers = '{0}example observed dangers.csv'.format(env.output_folder)

import collections as coll

# Write observed dangers to file
with open(output_observed_dangers, 'w', encoding='utf-8') as f:
    make_header = True
    for d in observed_dangers:
        out_data = coll.OrderedDict([
                ('Date', dt.date.strftime(d.date, '%Y-%m-%d')),
                ('Reg time', dt.datetime.strftime(d.registration_time, '%Y-%m-%d %H:%M')),
                ('Region id', d.region_regobs_id),
                ('Region', d.region_name),
                ('Municipal', d.municipal_name),
                ('Nick', d.nick),
                ('Competence', d.competence_level),
                ('DL', d.danger_level),
                ('Danger level', d.danger_level_name),
                ('Forecast correct', d.forecast_correct)
            ])
        if make_header:
            f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
            make_header = False
        f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')

# Write forecasted dangers to file
with open(output_forecast_dangers, 'w', encoding='utf-8') as f:
    make_header = True
    for d in forecast_dangers:
        out_data = coll.OrderedDict([
                ('Date', dt.date.strftime(d.date, '%Y-%m-%d')),
                ('Region id', d.region_regobs_id),
                ('Region', d.region_name),
                ('Nick', d.nick),
                ('DL', d.danger_level),
                ('Danger level', d.danger_level_name),
                ('Main message', ' '.join(d.main_message_en.split()))
            ])
        if make_header:
            f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
            make_header = False
        f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')

# Write forecasted problems to file
with open(output_forecast_problems, 'w', encoding='utf-8') as f:
    make_header = True
    for p in forecast_problems:
        out_data = coll.OrderedDict([
                ('Date', dt.date.strftime(p.date, '%Y-%m-%d')),
                ('Region id', p.region_regobs_id),
                ('Region', p.region_name),
                ('Nick', p.nick_name),
                ('Problem order', p.order),
                ('Problem', p.problem),
                ('EAWS problem', p.eaws_problem),
                ('Cause/ weaklayer', p.cause_name),
                ('Type', p.aval_type),
                ('Size', p.aval_size),
                ('Trigger', p.aval_trigger),
                ('Probability', p.aval_probability),
                ('Distribution', p.aval_distribution),
                ('DL', p.danger_level),
                ('Danger level', p.danger_level_name)
            ])
        if make_header:
            f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
            make_header = False
        f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')

# Write observed problems to file
with open(output_observed_problems, 'w', encoding='utf-8') as f:
    make_header = True
    for p in observed_problems:
        out_data = coll.OrderedDict([
                ('Date', dt.date.strftime(p.date, '%Y-%m-%d')),
                ('Reg time', dt.datetime.strftime(p.registration_time, '%Y-%m-%d %H:%M')),
                ('Region id', p.region_regobs_id),
                ('Region', p.region_name),
                ('Municipal', p.municipal_name),
                ('Nick', p.nick_name),
                ('Competence', p.competence_level),
                ('EAWS problem', p.eaws_problem),
                ('Cause/ weaklayer', p.cause_name),
                ('Type', p.aval_type),
                ('Catch 1', p.cause_attribute_crystal),
                ('Catch 2', p.cause_attribute_light),
                ('Catch 3', p.cause_attribute_soft),
                ('Catch 4', p.cause_attribute_thin),
                ('Size', p.aval_size),
                ('Trigger', p.aval_trigger)
            ])
        if make_header:
            f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
            make_header = False
        f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')
