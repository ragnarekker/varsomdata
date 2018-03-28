import os.path
import datetime as dt
from varsomdata import setcoreenvironment as env
from varsomdata import makepickle as mp
from varsomdata import getproblems as gp
from varsomdata import getdangers as gd
from varsomdata import getmisc as gm

# -*- coding: utf-8 -*-
__author__ = 'ragnarekker'


def _save_problems(problems, file_path):
    '''

    :param problems:
    :param file_path:
    :return:
    '''


    if os.path.exists(file_path) == False:
        l = open(file_path, 'w', encoding='utf-8')
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\n'
                .format('Dato', 'region id', 'Region', 'FG', 'Faregrad', 'Opprinnelse',
                'Rekkefølge', 'Skredproblem', 'Årsak', 'Hovedskredproblem', 'Størrelse', 'regObs tabell', 'URL'))
    else:
        l = open(file_path, 'a', encoding='utf-8')

    for p in problems:
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\n'.format(
            p.date,
            p.region_regobs_id,
            p.region_name,
            p.danger_level,
            p.danger_level_name,
            p.source,
            p.order,
            p.problem,
            p.cause_name,
            p.main_cause,
            p.aval_size,
            p.regobs_table,
            p.url))
    l.close()


def _save_problems_simple(problems, file_path):
    '''

    :param problems:
    :param file_path:
    :return:
    '''

    l = open(file_path, 'w')
    l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'
            .format('Dato', 'RegionNavn', 'Faregrad', 'ProblemOprinnelse',
            'Rekkefoelge', 'Aarsak'))

    for p in problems:
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(
            p.date,
            p.region_name,
            p.danger_level_name,
            p.source,
            p.order,
            p.cause_name))

    l.close()


def make_avalanche_problemes():

    data_output_filename = '{0}Alle skredproblemer.csv'.format(env.output_folder)
    pickle_file_name = '{0}runavalancheproblems.pickle'.format(env.local_storage)

    get_new = True

    if get_new:
        region_ids = [118, 128, 117]
        from_date = dt.date(2012, 12, 31)
        to_date = dt.date(2015, 7, 1)
        data = gp.get_all_problems(region_ids, from_date, to_date)

        mp.pickle_anything(data, pickle_file_name)

    else:
        data = mp.unpickle_anything(pickle_file_name)

    _save_problems_simple(data, data_output_filename)

    return


def make_problems_for_BritSiv():
    """Brit Siv ønsket oversikt over varslede skredprobelemr og faregrader for Indre Fjordane of Fjordane
    de to siste årene (2015-2017).

    :return:
    """

    output_filename = '{0}Skredproblemer Indre Fjordane for BritSiv.csv'.format(env.output_folder)
    pickle_file_name = '{0}runavalancheproblems_britsiv.pickle'.format(env.local_storage)

    get_new = False
    all_dangers = []

    if get_new:
        # Get Fjordane 2015-16
        region_id = 121
        from_date, to_date = gm.get_forecast_dates('2015-16')
        all_dangers += gd.get_forecasted_dangers(region_id, from_date, to_date)

        # Get Indre fjordane 2016-17
        region_id = 3027
        from_date, to_date = gm.get_forecast_dates('2016-17')
        all_dangers += gd.get_forecasted_dangers(region_id, from_date, to_date)

        mp.pickle_anything(all_dangers, pickle_file_name)

    else:
        all_dangers = mp.unpickle_anything(pickle_file_name)

    all_problems = []
    for d in all_dangers:
        all_problems += d.avalanche_problems
    all_problems.sort(key=lambda AvalancheProblem: AvalancheProblem.date)

    _save_problems(all_problems, output_filename)

    return


def make_avalanche_problemes_for_techel():
    """
    Tar 15-20 min å kjøre
    :return:


    """

    pickle_file_name = '{0}runavalancheproblems_techel.pickle'.format(env.local_storage)

    years = ['2014-15', '2015-16', '2016-17']
    get_new = False

    if get_new:
        forecast_problems = []
        forecast_dangers = []
        observed_dangers = []
        observed_problems = []

        for y in years:
            # Get forecast data. Different region ids from year to year.
            region_ids = gm.get_forecast_regions(year=y)
            from_date, to_date = gm.get_forecast_dates(y)
            forecast_problems += gp.get_forecasted_problems(region_ids, from_date, to_date, lang_key=2)
            forecast_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date, lang_key=2)

            # Get observed data. All data is mapped to new set of regions.
            region_ids = gm.get_forecast_regions(year='2016-17')
            from_date, to_date = gm.get_forecast_dates(y, padding=dt.timedelta(days=20))
            this_years_observed_dangers = gd.get_observed_dangers(region_ids, from_date, to_date, lang_key=2)
            this_years_observed_problems = gp.get_observed_problems(region_ids, from_date, to_date, lang_key=2)

            # Update observations with forecast region ids and names used the respective years
            for od in this_years_observed_dangers:
                utm33x = od.metadata['Original data'].UTMEast
                utm33y = od.metadata['Original data'].UTMNorth
                region_id, region_name = gm.get_forecast_region_for_coordinate(utm33x, utm33y, y)
                od.region_regobs_id = region_id
                od.region_name = region_name

            for op in this_years_observed_problems:
                utm33x = op.metadata['Original data']['UtmEast']
                utm33y = op.metadata['Original data']['UtmNorth']
                region_id, region_name = gm.get_forecast_region_for_coordinate(utm33x, utm33y, y)
                op.region_regobs_id = region_id
                op.region_name = region_name

            observed_dangers += this_years_observed_dangers
            observed_problems += this_years_observed_problems

        mp.pickle_anything([forecast_problems, forecast_dangers, observed_dangers, observed_problems], pickle_file_name)

    else:
        [forecast_problems, forecast_dangers, observed_dangers, observed_problems] = mp.unpickle_anything(pickle_file_name)

    # Run EAWS mapping on all problems
    for p in forecast_problems:
        p.map_to_eaws_problems()

    for p in observed_problems:
        p.map_to_eaws_problems()

    output_forecast_problems = '{0}Techel forecast problems.csv'.format(env.output_folder)
    output_forecast_dangers = '{0}Techel forecast dangers.csv'.format(env.output_folder)
    output_observed_problems = '{0}Techel observed problems.csv'.format(env.output_folder)
    output_observed_dangers = '{0}Techel observed dangers.csv'.format(env.output_folder)

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
                    ('Forecast correct', d.forecast_correct),
                    # ('Table', d.data_table),
                    # ('URL', d.url),
                ])
            if make_header:
                f.write(' ;'.join([make_str(d) for d in out_data.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([make_str(d) for d in out_data.values()]) + '\n')

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
                    # ('Table', d.data_table),
                    # ('URL', d.url),
                    ('Main message', ' '.join(d.main_message_en.split()))
                ])
            if make_header:
                f.write(' ;'.join([make_str(d) for d in out_data.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([make_str(d) for d in out_data.values()]) + '\n')

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
                    # ('TypeTID', p.aval_type_tid),
                    ('Type', p.aval_type),
                    ('Size', p.aval_size),
                    ('Trigger', p.aval_trigger),
                    ('Probability', p.aval_probability),
                    ('Distribution', p.aval_distribution),
                    ('DL', p.danger_level),
                    ('Danger level', p.danger_level_name),
                    # ('Table', p.regobs_table),
                    # ('URL', p.url)
                ])
            if make_header:
                f.write(' ;'.join([make_str(d) for d in out_data.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([make_str(d) for d in out_data.values()]) + '\n')

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
                    # ('Problem order', p.order),
                    ('EAWS problem', p.eaws_problem),
                    ('Cause/ weaklayer', p.cause_name),
                    # ('TypeTID', p.aval_type_tid),
                    ('Type', p.aval_type),
                    ('Catch 1', p.cause_attribute_crystal),
                    ('Catch 2', p.cause_attribute_light),
                    ('Catch 3', p.cause_attribute_soft),
                    ('Catch 4', p.cause_attribute_thin),
                    ('Size', p.aval_size),
                    ('Trigger', p.aval_trigger),
                    # ('Probability', p.aval_probability),
                    # ('Distribution', p.aval_distribution),
                    # ('RegID', p.regid),
                    # ('Table', p.regobs_table),
                    # ('URL', p.url)
                ])
            if make_header:
                f.write(' ;'.join([make_str(d) for d in out_data.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([make_str(d) for d in out_data.values()]) + '\n')

    return


def make_forecasts_for_Christian():
    """Christian Jaedicke ønsker oversikt over varsel og skredproblemer siste tre år i Narvik.

     :return:
    """

    pickle_file_name = '{0}forecasts_ofoten_christian.pickle'.format(env.local_storage)

    get_new = False
    all_dangers = []

    if get_new:
        # Get Narvik 2014-15 and 2015-16
        region_id = 114

        from_date, to_date = gm.get_forecast_dates('2014-15')
        all_dangers += gd.get_forecasted_dangers(region_id, from_date, to_date)

        from_date, to_date = gm.get_forecast_dates('2015-16')
        all_dangers += gd.get_forecasted_dangers(region_id, from_date, to_date)

        # Get Indre fjordane 2016-17
        region_id = 3015
        from_date, to_date = gm.get_forecast_dates('2016-17')
        all_dangers += gd.get_forecasted_dangers(region_id, from_date, to_date)

        mp.pickle_anything(all_dangers, pickle_file_name)

    else:
        all_dangers = mp.unpickle_anything(pickle_file_name)

    output_forecast_problems = '{0}Varsel Ofoten for Christian.csv'.format(env.output_folder)

    import collections as coll

    # Write forecasts to file
    with open(output_forecast_problems, 'w', encoding='utf-8') as f:
        make_header = True
        for d in all_dangers:
            for p in d.avalanche_problems:
                out_data = coll.OrderedDict([
                        ('Date', dt.date.strftime(p.date, '%Y-%m-%d')),
                        ('Region id', p.region_regobs_id),
                        ('Region', p.region_name),
                        ('DL', p.danger_level),
                        ('Danger level', p.danger_level_name),
                        ('Problem order', p.order),
                        ('Problem', p.problem),
                        ('Cause/ weaklayer', p.cause_name),
                        ('Type', p.aval_type),
                        ('Size', p.aval_size),
                        ('Trigger', p.aval_trigger),
                        ('Probability', p.aval_probability),
                        ('Distribution', p.aval_distribution)
                    ])
                if make_header:
                    f.write(' ;'.join([make_str(d) for d in out_data.keys()]) + '\n')
                    make_header = False
                f.write(' ;'.join([make_str(d) for d in out_data.values()]) + '\n')

    return


def make_forecasts_at_incidents_for_anniken_and_emma():
    """Hei!

    Vi vil gjerne ha faregradene tilbake til 2014/2015 for de dagene ulykkene inntraff, samt skredtype.
    I denne omgang fokuserer vi ikke på skredproblem.

    Ja vi ser på dødsulykker og har brukt tallene fra linken, takk for henvisningen.

    Ta gjerne ut en full liste med faregrad for skredhendelser fra 2016-2017 til 2014-2015
    (de skredhendelsene som er på linken du la ved, det er disse vi tar utgangspunkt i) .

    Takk for hjelpen!

    Mvh Emma Gamme og Anniken Helene Aalerud

    :return:

    get forecasts and problems way back
    get all incidents from varsom
    pick out dl and avlatype
    add dl and avaltype to the dates
    """

    pickle_file_name = '{0}dl_inci_anniken_and_emma.pickle'.format(env.local_storage)
    output_incident_and_dl = '{0}Hendelse og faregrad til Anniken og Emma.csv'.format(env.output_folder)

    years = ['2014-15', '2015-16', '2016-17']
    get_new = True

    if get_new:
        forecast_problems = []      # the problems have the danger level
        varsom_incidents = gm.get_varsom_incidents(add_forecast_regions=True)

        for y in years:
            # Get forecast data. Different region ids from year to year.
            region_ids = gm.get_forecast_regions(year=y)
            from_date, to_date = gm.get_forecast_dates(y)
            forecast_problems += gp.get_forecasted_problems(region_ids, from_date, to_date, lang_key=1)

        mp.pickle_anything([forecast_problems, varsom_incidents], pickle_file_name)

    else:
        [forecast_problems, varsom_incidents] = mp.unpickle_anything(pickle_file_name)

    incident_and_dl = []
    for i in varsom_incidents:
        incident_date = i.date
        incident_region = i.region_id
        for p in forecast_problems:
            problem_date = p.date
            problem_region = p.region_regobs_id
            if incident_date == problem_date and incident_region == problem_region:
                if p.order == 1:
                    incident_and_dl.append({'Dato':incident_date,
                                            'Region':i.region_name,
                                            'Kommune':i.municipality,
                                            'Dødsfall':i.fatalities,
                                            'Involverte':i.people_involved,
                                            'Aktivitet':i.activity,
                                            'Faregrad':p.danger_level,
                                            'Skredtype':p.aval_type,
                                            'regObs id':i.regid})

    # Write observed problems to file
    with open(output_incident_and_dl, 'w', encoding='utf-8') as f:
        make_header = True
        for i in incident_and_dl:
            if make_header:
                f.write(' ;'.join([make_str(d) for d in i.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([make_str(d) for d in i.values()]).replace('[', '').replace(']', '') + '\n')


    a = 1


def make_str(s):

    if s == 'Not given':
        return ''
    if s == 'Ikke gitt':
        return ''
    if s is None:
        return ''
    return str(s)


if __name__ == "__main__":

    # make_problems_for_BritSiv()
    # make_avalanche_problemes_for_techel()
    # make_forecasts_for_Christian()
    make_forecasts_at_incidents_for_anniken_and_emma()