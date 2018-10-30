# -*- coding: utf-8 -*-
"""Requests all forecasts (danger levels and problems) from the forecast api and writes to .csv file or plot."""

import datetime as dt
import os as os
import pylab as plt
import setenvironment as env
from utilities import fencoding as fe, makelogs as ml, makepickle as mp
from varsomdata import getproblems as gp
from varsomdata import getdangers as gd
from varsomdata import getmisc as gm
from varsomdata import getobservations as go

__author__ = 'ragnarekker'


def _save_problems(problems, file_path):
    """

    :param problems:
    :param file_path:
    :return:
    """

    if not os.path.exists(file_path):
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
    """

    :param problems:
    :param file_path:
    :return:
    """

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


def _save_danger_and_problem_to_file(warnings, file_path):
    """Saves a list of warning and problems to file.

    :param warnings:
    :param file_path:
    :return:
    """

    # Write to .csv
    with open(file_path, "w", encoding='utf-8') as myfile:
        myfile.write('Dato;Region;FG;Faregrad;Hovedskredproblem;Skredproblem;Skredproblem\n')

        for w in warnings:
            date = w.date
            region = w.region_name
            danger_level = w.danger_level
            danger_level_name = w.danger_level_name
            problems = ''

            for p in w.avalanche_problems:
                if not 'Ikke gitt' in p.problem:
                    problems += p.problem + ';'

            myfile.write('{0};{1};{2};{3};{4}\n'.format(date, region, danger_level, danger_level_name, problems))


def _make_plot_dangerlevels_simple(warnings, all_avalanche_evaluations, file_path, from_date, to_date):
    """Works best for plotting multiple regions over one season.

    :param warnings:
    :param all_avalanche_evaluations:
    :param file_path:
    :param from_date:
    :param to_date:
    :return:
    """

    # count corrects
    correct_not_given = 0
    correct_to_low = 0
    correct_correct = 0
    correct_to_high = 0

    for e in all_avalanche_evaluations:
        if e.ForecastCorrectTID == 0:
            correct_not_given += 1
        elif e.ForecastCorrectTID == 1:
            correct_correct += 1
        elif e.ForecastCorrectTID == 2:
            correct_to_low += 1
        elif e.ForecastCorrectTID == 3:
            correct_to_high += 1
        else:
            ml.log_and_print("allforecasteddangerlevels.py -> _make_plot_dangerlevels_simple: Illegal ForecastCorrectTID given.", log_it=True, print_it=False)

    correct_total = correct_correct + correct_to_high + correct_to_low

    # find dangerlevels pr day
    all_danger_levels = []

    for w in warnings:
        all_danger_levels.append(w.danger_level)

    dl1 = all_danger_levels.count(1)
    dl2 = all_danger_levels.count(2)
    dl3 = all_danger_levels.count(3)
    dl4 = all_danger_levels.count(4)
    dl5 = all_danger_levels.count(5)

    dict_of_dates = {}
    list_of_dates = [from_date + dt.timedelta(days=x) for x in range(0, (to_date-from_date).days)]

    for d in list_of_dates:
        date_with_data_obj = AllDangersAndCorrectsOnDate(d)

        for w in warnings:
            if w.date == d:
                # if w.region_regobs_id < 149:    # ordinay forecast
                date_with_data_obj.add_danger(w.danger_level)
                # else:                           # county forecast on dangerlevel 4 or 5
                #    date_with_data_obj.add_county_danger(w.danger_level)

        dict_of_dates[d] = date_with_data_obj

    # Figure dimensions
    fsize = (12, 8)
    fig = plt.figure(figsize=fsize)
    plt.clf()

    head_x = 0.23
    head_y = 0.9

    fig.text(head_x + 0.018, head_y, "Varsom snøskredvarsel for sesongen {0}-{1}"
             .format(from_date.strftime('%Y'), to_date.strftime('%y')), fontsize = 19)
    fig.text(head_x + 0.05, head_y - 0.05, "Antall:  {0} fg1.  {1} fg2.  {2} fg3.  {3} fg4.  {4} fg5."
             .format(dl1, dl2, dl3, dl4, dl5), fontsize = 15)
    fig.text(head_x - 0.06, head_y - 0.09, "Treffsikkerhet av {0} vurderinger: {1:.0f}% riktig ({2:.0f}% for høy og {3:.0f}% for lav)"
             .format(correct_total,
                     100*correct_correct/correct_total,
                     100*correct_to_high/correct_total,
                     100*correct_to_low/correct_total), fontsize=15)

    dl_colors = ['0.5', '#ccff66', '#ffff00', '#ff9900', '#ff0000', 'k']

    for v in dict_of_dates.values():
        if len(v.dangers) > 0:
            line_start = 0 # -1*(v.dangers.count(1) + v.dangers.count(2))
            line_end = line_start
            for dl in range(0, 6, 1):
                line_end += v.dangers.count(dl)
                plt.vlines(v.date, line_start, line_end, lw=3.9, colors=dl_colors[dl])
                line_start = line_end

    plt.ylabel("Antall varsel")

    fig = plt.gcf()
    fig.subplots_adjust(top=0.75)
    fig.subplots_adjust(bottom=0.15)

    # full control of the axis
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.grid(True)
    # ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    ax.set_ylim([0, 28])
    ax.set_xlim([from_date, to_date])

    # fig.text(0.1, 0.1, 'Title', fontsize=14, zorder=6, color='k', bbox={'facecolor': 'silver', 'alpha': 0.5, 'pad': 4})
    legend_x = 0.20
    legend_y = 0.05
    fig.text(0.01+legend_x, 0.005+legend_y, 'lll', color=dl_colors[1], fontsize=5, bbox={'facecolor': dl_colors[1]})
    fig.text(0.03+legend_x, 0+legend_y, 'fg1 - Liten')
    fig.text(0.12+legend_x, 0.005+legend_y, 'lll', color=dl_colors[2], fontsize=5, bbox={'facecolor': dl_colors[2]})
    fig.text(0.14+legend_x, 0+legend_y, 'fg2 - Moderat')
    fig.text(0.26+legend_x, 0.005+legend_y, 'lll', color=dl_colors[3], fontsize=5, bbox={'facecolor': dl_colors[3]})
    fig.text(0.28+legend_x, 0+legend_y, 'fg3 - Betydelig')
    fig.text(0.40+legend_x, 0.005+legend_y, 'lll', color=dl_colors[4], fontsize=5, bbox={'facecolor': dl_colors[4]})
    fig.text(0.42+legend_x, 0+legend_y, 'fg4 - Stor')
    fig.text(0.50+legend_x, 0.005+legend_y, 'lll', color=dl_colors[5], fontsize=5, bbox={'facecolor': dl_colors[5]})
    fig.text(0.52+legend_x, 0+legend_y, 'fg5 - Meget stor')

    plt.savefig("{0}".format(file_path))
    plt.close(fig)


class AllDangersAndCorrectsOnDate:

    def __init__(self, date_inn):
        self.date = date_inn
        self.dangers = []
        self.county_dangers = []

    def add_danger(self, danger_inn):
        self.dangers.append(danger_inn)

    def add_county_danger(self, county_danger_inn):
        # counties get warnings on danger level 4 and 5
        # if county_danger_inn > 0:
        self.county_dangers.append(county_danger_inn)

    def sum_up_dangers(self):

        self.dangers += self.county_dangers


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
    de to siste årene (2015-2017).    """

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


def make_avalanche_problemes_for_techel():
    """Gets forecastes and observed avalanche problems and dangers for Frank Techel.

    Takes 20-30 min to run a year.

    :return:
    """

    pickle_file_name = '{0}runavalancheproblems_techel.pickle'.format(env.local_storage)

    years = ['2014-15', '2015-16', '2016-17', '2017-18']
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

            # Get observed data. All older data in regObs have been mapped to new regions.
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
                    # ('Table', d.data_table),
                    # ('URL', d.url),
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
                f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')


def make_forecasts_for_Christian():
    """Christian Jaedicke ønsker oversikt over varsel og skredproblemer siste tre år i Narvik."""

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
                    f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
                    make_header = False
                f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')


def make_forecasts_for_Heidi():
    """July 2018: Make list of avalanche forecasts for regions Voss, Svartisen og Fauske (and those before them)
    for Heidi Bjordal SVV"""

    pickle_file_name = '{0}201807_avalanche_forecasts_heidi.pickle'.format(env.local_storage)

    get_new = False
    all_dangers = []

    if get_new:
        # Get Voss. ForecastRegionTID 124 form 2012-2016 and 3031 since.
        # Get Svartisen. ForecastRegionTID 131 form 2012-2016 and 3017 since.
        # Get Salten. ForecastRegionTID 133 form 2012-2016 and 3016 since.

        years = ['2012-13', '2013-14', '2014-15', '2015-16']
        region_ids = [124, 131, 133]

        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            all_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date)

        years = ['2016-17', '2017-18']
        region_ids = [3031, 3017, 3016]

        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            all_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date)

        mp.pickle_anything(all_dangers, pickle_file_name)

    else:
        all_dangers = mp.unpickle_anything(pickle_file_name)

    output_forecast_problems = '{0}201807 Snøskredvarsel for Heidi.txt'.format(env.output_folder)

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
                    f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
                    make_header = False
                f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')

    pass


def make_forecasts_for_Thea():
    """July 2018: Make list of avalanche forecasts danger levels for regions Voss, Romsdalen, Svartisen
    and Salten (and those before them) for Thea Møllerhaug Lunde (Jernbanedirektoratet).

    Voss-Bergen ligger i for det meste i Voss-regionen vår.
    Mo i Rana-Fauske ligger i Svartisen og Salten.
    Åndalsnes-Bjorli ligger i varslingsregionen Romsdalen."""

    pickle_file_name = '{0}201807_avalanche_forecasts_thea.pickle'.format(env.local_storage)

    get_new = False
    all_dangers = []

    if get_new:
        # Get Voss. ForecastRegionTID 124 form 2012-2016 and 3031 since.
        # Get Romsdalen. ForecastRegionTID 118 from 2012-2016 and 3023 since.
        # Get Svartisen. ForecastRegionTID 131 from 2012-2016 and 3017 since.
        # Get Salten. ForecastRegionTID 133 form 2012-2016 and 3016 since.

        years = ['2012-13', '2013-14', '2014-15', '2015-16']
        region_ids = [124, 118, 131, 133]

        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            all_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date)

        years = ['2016-17', '2017-18']
        region_ids = [3031, 3023, 3017, 3016]

        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            all_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date)

        mp.pickle_anything(all_dangers, pickle_file_name)

    else:
        all_dangers = mp.unpickle_anything(pickle_file_name)

    output_forecast_problems = '{0}201807 Snøskredvarsel for Thea.txt'.format(env.output_folder)

    import collections as coll

    # Write forecasts to file
    with open(output_forecast_problems, 'w', encoding='utf-8') as f:
        make_header = True
        for d in all_dangers:
            out_data = coll.OrderedDict([
                    ('Date', dt.date.strftime(d.date, '%Y-%m-%d')),
                    ('Region id', d.region_regobs_id),
                    ('Region', d.region_name),
                    ('DL', d.danger_level),
                    ('Danger level', d.danger_level_name),
                ])
            if make_header:
                f.write(' ;'.join([fe.make_str(d) for d in out_data.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([fe.make_str(d) for d in out_data.values()]) + '\n')

    pass


def make_forecasts_for_Sander():
    """2018 August: Hei igjen Ragnar.
    Har du statistikk på varsla faregrad over ein heil sesong for Noreg? Eit snitt. XX dagar med faregrad 1,
    XX dagar med faregrad 2, XX dagar med faregrad 3.... fordelt på XX varslingsdagar.

    :return:
    """

    pickle_file_name = '{0}201808_avalanche_forecasts_sander.pickle'.format(env.local_storage)

    get_new = False
    all_dangers = []

    if get_new:

        years = ['2012-13', '2013-14', '2014-15', '2015-16']
        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            region_ids = gm.get_forecast_regions(y, get_b_regions=True)
            all_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date)

        years = ['2016-17', '2017-18']
        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            region_ids = gm.get_forecast_regions(y, get_b_regions=True)
            all_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date)

        mp.pickle_anything(all_dangers, pickle_file_name)

    else:
        all_dangers = mp.unpickle_anything(pickle_file_name)

    output_forecast_problems = '{0}201808 Faregrader for Sander.txt'.format(env.output_folder)

    import pandas as pd

    all_dangers_dict = []
    for a in all_dangers:
        all_dangers_dict.append(a.__dict__)

    col_names = list(all_dangers_dict[0].keys())
    all_dangers_df = pd.DataFrame(all_dangers_dict, columns=col_names, index=range(0, len(all_dangers_dict),1))



    a = 1


def get_all_ofoten():
    """Dangers and problems for Ofoten (former Narvik). Writes file to .csv"""

    get_new = True
    get_observations = False
    write_csv = True
    plot_dangerlevels_simple = False

    select_years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18']
    region_id_Narvik = 114      # Narvik used from 2012 until nov 2016
    region_id_Ofoten = 3015     # Ofoten introduced in november 2016

    warnings_pickle = '{0}allforecasteddangerlevels_Ofoten_201218.pickle'.format(env.local_storage)
    warnings_csv = '{0}Faregrader Ofoten 2012-18.csv'.format(env.output_folder)
    warnings_plot = '{0}Faregrader Ofoten 2012-18.png'.format(env.output_folder)

    if get_new:
        all_warnings = []
        all_evaluations = []

        for y in select_years:

            if y in ['2016-17', '2017-18']:
                region_id = region_id_Ofoten
            else:
                region_id = region_id_Narvik

            from_date, to_date = gm.get_forecast_dates(year=y)

            all_warnings += gd.get_forecasted_dangers(region_id,  from_date, to_date)
            if get_observations:
                all_evaluations += go.get_avalanche_evaluation_3(from_date, to_date, region_id)

        mp.pickle_anything([all_warnings, all_evaluations], warnings_pickle)

    else:
        [all_warnings, all_evaluations] = mp.unpickle_anything(warnings_pickle)

    if write_csv:
        # write to csv files
        _save_danger_and_problem_to_file(all_warnings, warnings_csv)

    elif plot_dangerlevels_simple:
        # Make simple plot
        from_date = gm.get_forecast_dates(select_years[0])[0]
        to_date = gm.get_forecast_dates(select_years[-1])[1]
        _make_plot_dangerlevels_simple(all_warnings, all_evaluations, warnings_plot, from_date, to_date)

    else:
        print("No output selected")

    return all_warnings, all_evaluations


if __name__ == "__main__":

    # make_problems_for_BritSiv()
    # make_avalanche_problemes_for_techel()
    # make_forecasts_for_Christian()
    # make_forecasts_for_Thea()
    make_forecasts_for_Sander()
