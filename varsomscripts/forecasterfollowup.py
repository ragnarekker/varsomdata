# -*- coding: utf-8 -*-
"""

"""

import datetime as dt
from varsomdata import getvarsompickles as gvp
from utilities import makepickle as mp
import setenvironment as env
import os as os
import numpy as np
import pandas as pd

__author__ = 'raek'


class _WarningPartInt:

    def __init__(self, for_this_author, for_all):

        self.values = [float(i) for i in for_this_author]
        self.values_all = [float(i) for i in for_all]

        self.avg_values = np.mean(np.array(self.values))
        self.avg_values_all = np.mean(np.array(self.values_all))

        self.std_values = np.std(np.array(self.values))
        self.std_values_all = np.std(np.array(self.values_all))


class _WarningPartString:

    def __init__(self, for_this_author, for_all):

        self.texts = for_this_author
        self.texts_all = for_all

        self.values = [len(str(t)) for t in self.texts]
        self.values_all = [len(str(t)) for t in self.texts_all]

        self.avg_values = np.mean(np.array(self.values))
        self.avg_values_all = np.mean(np.array(self.values_all))

        self.std_values = np.std(np.array(self.values))
        self.std_values_all = np.std(np.array(self.values_all))

        self.daily_text_diff = []
        self.daily_text_diff_all = []


class Forecaster:

    def __init__(self, author_inn):

        self.author = author_inn

        self.warnings = []              # all warnings made by this forecaster
        self.warning_count = None       # int number of of warnings
        self.dates_valid = {}           # dict of {date:#}
        self.work_days = None
        self.observer_id = None         # int observer id in regObs

        # for current author. all input in the warnings listed by input field
        self.danger_levels = []             # ints
        self.main_texts = []                # strings
        self.avalanche_dangers = []         # strings
        self.snow_surfaces = []             # strings
        self.current_weak_layers = []       # strings
        self.problems_pr_warnings = []      # ints

    def add_warning(self, warning_inn):
        self.warnings.append(warning_inn)

    def add_warnings_count(self, warning_count_inn):
        self.warning_count = warning_count_inn

    def add_dates_valid(self, dates_valid_inn):
        self.dates_valid = dates_valid_inn

    def add_work_days(self, work_days_inn):
        self.work_days = work_days_inn

    def add_observer_id(self, observer_id_inn):
        self.observer_id = observer_id_inn

    def add_danger_levels(self, danger_levels_inn, danger_levels_all_inn):
        self.danger_levels = _WarningPartInt(danger_levels_inn, danger_levels_all_inn)

    def add_main_texts(self, main_texts_inn, main_texts_all_inn):
        self.main_texts = _WarningPartString(main_texts_inn, main_texts_all_inn)

    def add_avalanche_dangers(self, avalanche_dangers_inn, avalanche_dangers_all_inn):
        self.avalanche_dangers = _WarningPartString(avalanche_dangers_inn, avalanche_dangers_all_inn)

    def add_snow_surfaces(self, snow_surface_inn, snow_surface_all_inn):
        self.snow_surfaces = _WarningPartString(snow_surface_inn, snow_surface_all_inn)

    def add_current_weak_layers(self, current_weak_layers_inn, current_weak_layers_all_inn):
        self.current_weak_layers = _WarningPartString(current_weak_layers_inn, current_weak_layers_all_inn)

    def add_problems_pr_warnings(self, problems_pr_warnings_inn, problems_pr_warnings_all_inn):
        self.problems_pr_warnings = _WarningPartInt(problems_pr_warnings_inn, problems_pr_warnings_all_inn)


def make_forecaster_data(year):
    """For one season, make the forecaster dictionary with all the necessary data.
    :param year:    [string] Eg. season '2017-18'
    """

    # get all valid forecasts
    warnings_all = gvp.get_all_forecasts(year, max_file_age=100)
    warnings_as_dict = [w.to_dict() for w in warnings_all]
    warnings = pd.DataFrame(warnings_as_dict)

    # get authors of all forecasters.
    authors = warnings.author.unique()

    forecasts_by_author = {}
    number_by_author = {}
    danger_levels_by_author = {}
    avalanche_problems_by_author = {}

    for a in authors:

        author_df = warnings.loc[warnings['author'] == a]

        forecasts_by_author[a] = author_df
        number_by_author[a] = int(warnings.loc[warnings['author'] == a].shape[0])
        danger_levels_by_author[a] = author_df['danger_level'].values

        avalanche_problems_by_author[a] = author_df[
            ['avalanche_problem_1_problem_type_name',
             'avalanche_problem_2_problem_type_name',
            'avalanche_problem_3_problem_type_name']
        ].replace({'Not given': None}).count(axis='columns')

    number_by_author_sorted = sorted(number_by_author.items(), key=lambda kv: kv[1], reverse=True)

    observations_all = gvp.get_all_observations(year, geohazard_tids=10, output='List')

    return


def make_forecaster_data_old(year):
    """For one season, make the forecaster dictionary with all the necessary data.
    :param year:    [string] Eg. season '2017-18'
    """

    # get all valid forecasts
    all_warnings = gvp.get_all_forecasts(year, max_file_age=100)

    # get authors of all forecasters.
    authors = []
    for w in all_warnings:
        if w.author not in authors:
            authors.append(w.author)

    # Make data set with dict {author: Forecaster}. Add warnings to Forecaster object.
    # Note: A list of all authors are all the keys in this dictionary.
    forecaster_dict = {}
    for w in all_warnings:
        if w.author not in forecaster_dict:
            forecaster_dict[w.author] = Forecaster(w.author)
            forecaster_dict[w.author].add_warning(w)
        else:
            forecaster_dict[w.author].add_warning(w)

    # need this below for forecaster statistics
    danger_levels_all = []             # ints
    main_texts_all = []                # strings
    avalanche_dangers_all = []         # strings
    snow_surfaces_all = []             # strings
    current_weak_layers_all = []       # strings
    problems_pr_warnings_all = []      # ints
    for w in all_warnings:
        danger_levels_all.append(w.danger_level)
        main_texts_all.append(w.main_text)
        avalanche_dangers_all.append(w.avalanche_danger)
        snow_surfaces_all.append(w.snow_surface)
        current_weak_layers_all.append(w.current_weak_layers)
        problems_pr_warnings_all.append(len(w.avalanche_problems))

    # Add data about the authors forecasts to forecaster objects in the dict
    for n, f in forecaster_dict.items():

        # add numbers of warnings made
        forecaster_dict[f.author].add_warnings_count(len(f.warnings))

        # find how many pr date valid
        dates_valid = {}
        for w in f.warnings:
            if w.date_valid not in dates_valid:
                dates_valid[w.date_valid] = 1
            else:
                dates_valid[w.date_valid] += 1
        forecaster_dict[f.author].add_dates_valid(dates_valid)

        # add data on the danger levels forecasted
        danger_levels_author = []
        for w in f.warnings:
            data = {'Date': w.date_valid,
                    'Region': w.region_name,
                    'DL': w.danger_level,
                    'Danger level': w.danger_level}
        forecaster_dict[f.author].add_danger_levels(danger_levels_author, danger_levels_all)

        # add data on the main texts made
        main_texts_author = [w.main_text for w in f.warnings]
        forecaster_dict[f.author].add_main_texts(main_texts_author, main_texts_all)

        # add data on the avalanche dangers made
        avalanche_dangers_author = [w.avalanche_danger for w in f.warnings]
        forecaster_dict[f.author].add_avalanche_dangers(avalanche_dangers_author, avalanche_dangers_all)

        # add data on the snow surfaces forecasted
        snow_surfaces_author = [w.snow_surface for w in f.warnings]
        forecaster_dict[f.author].add_snow_surfaces(snow_surfaces_author, snow_surfaces_all)

        # add data on the current weak layers made
        current_weak_layers_author = [w.current_weak_layers for w in f.warnings]
        forecaster_dict[f.author].add_current_weak_layers(current_weak_layers_author, current_weak_layers_all)

        # add data on the avalanche problems made
        problems_pr_warnings_author = [len(w.avalanche_problems) for w in f.warnings]
        forecaster_dict[f.author].add_problems_pr_warnings(problems_pr_warnings_author, problems_pr_warnings_all)

    return forecaster_dict


def make_plots(forecaster_dict, nick, path=''):

    import matplotlib.pyplot as plt
    import numpy
    import datetime as dt

    f = forecaster_dict[nick]

    plt.clf()
    bins = numpy.linspace(0, 1024, 20)
    plt.hist(f.nowcast_lengths_all, bins, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.nowcast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.nowcast_lengths, bins, alpha=0.5, color='b', label='{0}'.format(nick))
    plt.axvline(f.nowcast_lengths_avg, color='b', linestyle='dashed', linewidth=3, label='Snitt {0}'.format(nick))
    plt.title("Tegn brukt paa naasituasjonen")
    plt.xlabel("Antall")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper left')
    plt.savefig('{0}{1}_nowcast.png'.format(path, f.observer_id))


    plt.clf()
    bins = numpy.linspace(0, 1024, 20)
    plt.hist(f.forecast_lengths_all, bins, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.forecast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.forecast_lengths, bins, alpha=0.5, color='pink', label='{0}'.format(nick))
    plt.axvline(f.forecast_lengths_avg, color='pink', linestyle='dashed', linewidth=3, label='Snitt {0}'.format(nick))
    plt.title("Tegn brukt paa varsel")
    plt.xlabel("Antall")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_forecast.png'.format(path, f.observer_id))


    plt.clf()
    bins = numpy.linspace(0, 5, 6)
    plt.hist(f.danger_levels_all, bins, align='left', rwidth=0.5, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.danger_levels_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.danger_levels, bins, align='left', rwidth=0.5, color='pink', label='{0}'.format(nick))
    plt.axvline(f.danger_levels_avg, color='pink', linestyle='dashed', linewidth=3, label='Snitt {0}'.format(nick))
    plt.title("Fordeling paa faregrader")
    plt.xlabel("Faregrad")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_danger.png'.format(path, f.observer_id))


    plt.clf()
    bins = numpy.linspace(0, 4, 5)
    plt.hist(f.problems_pr_warning_all, bins, align='left', rwidth=0.5, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.problems_pr_warning_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.problems_pr_warning, bins, align='left', rwidth=0.5, color='pink', label='{0}'.format(nick))
    plt.axvline(f.problems_pr_warning_avg, color='pink', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.title("Skredproblemer pr varsel")
    plt.xlabel("Antall")
    plt.ylabel("Frequency")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_problems_pr_warning.png'.format(path, f.observer_id))


    plt.clf()
    antall_pr_dag = f.dates.values()
    if len(antall_pr_dag) != 0:
        snitt = sum(antall_pr_dag)/float(len(antall_pr_dag))
        plt.plot((dt.date(2016, 12, 1), dt.date(2017, 6, 1)), (snitt, snitt), color='g', linestyle='dashed', linewidth=3)
    # barplot needs datetimes not dates
    dates = [dt.datetime.combine(d, dt.datetime.min.time()) for d in f.dates.keys()]
    plt.bar(dates, antall_pr_dag, color='g')
    ymax = max(f.dates.values()) + 1
    plt.title("Antall varsler paa datoer")
    plt.ylim(0, ymax)
    plt.xlim(dt.date(2016, 12, 1), dt.date(2017, 6, 1))
    plt.xticks( rotation=17 )
    plt.savefig('{0}{1}_dates.png'.format(path, f.observer_id))

    return


def make_html(forecaster_dict, nick, path='', type='Simple'):
    """Makes a html with dates and links to the forecasts made by a given forecaster.

    :param forecaster_dict:
    :param nick:
    :param observer_id:
    :param path:
    :return:
    """

    fc = forecaster_dict[nick]

    if 'Simple' in type:

        html_file_name = '{0}{1}_forecasts_simple.html'.format(path, fc.observer_id)
        f = open(html_file_name, 'w', encoding='utf-8')

        f.write('<table class="table table-hover"><tbody><tr><td>')
        d_one_time = None
        for w in fc.warnings:
            region_name_varsom = w.region_name.replace('aa','a').replace('oe', 'o').replace('ae', 'a')
            if d_one_time != w.date:
                f.write('</td>\n</tr>\n<tr>\n')
                d_one_time = w.date
                f.write('   <td>{0}</td>\n'.format(d_one_time))
                f.write('   <td><a href="http://varsom.no/Snoskred/{1}/?date={2}">{0}</a>'.format(w.region_name, region_name_varsom, w.date.strftime('%d.%m.%Y')))
            else:
                f.write(', <a href="http://varsom.no/Snoskred/{1}/?date={2}">{0}</a>'.format(w.region_name, region_name_varsom, w.date.strftime('%d.%m.%Y')))
        f.write('</tr></tbody></table>')

    elif 'Advanced' in type:

        html_file_name = '{0}{1}_forecasts_advanced.html'.format(path, fc.observer_id)
        f = open(html_file_name, 'w', encoding='utf-8')

        f.write('<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#advanced">Tabell med info om faregrad og skredproblemer</button>\n'
            '<div id="advanced" class="collapse">\n')
        f.write('</br>\n')
        f.write('<table class="table table-hover"><tbody>')

        d_one_time = forecaster_dict[nick].warnings[0]
        for w in fc.warnings:
            region_name_varsom =  w.region_name.replace('aa','a').replace('oe', 'o').replace('ae', 'a')
            problem_highlights = ''
            for p in w.avalanche_problems:
                if not hasattr(p, 'aval_size'):
                    p.aval_size = 'Ikke gitt'
                problem_highlights += '<br>P{6}[{5}, {0}, {1}, {2}, {3}, {4}]'.format(p.cause_name, p.aval_size, p.aval_probability, p.aval_distribution, p.aval_trigger, p.aval_type, p.order+1 )
            forecast_highlights = 'Faregrad {0}'.format(w.danger_level) + problem_highlights
            f.write('<tr>\n')
            if d_one_time != w.date:
                d_one_time = w.date
                f.write('   <td>{0}</td>\n'.format(d_one_time))
            else:
                f.write('   <td></td>\n')
            f.write('   <td><a href="http://varsom.no/Snoskred/{1}/?date={2}">{0}</a></td>'.format(w.region_name, region_name_varsom, w.date.strftime('%d.%m.%Y')))
            f.write('   <td>{0}</td>'.format(forecast_highlights))
            f.write('</tr>\n')
        f.write('</tbody></table></div>')


    else:
        html_file_name = '{0}{1}_forecasts.html'.format(path, fc.observer_id)
        f = open(html_file_name, 'w', encoding='utf-8')
        f.write('<table class="table table-hover"><tbody><tr><td>Ble ikke spurt om  å lage noe data..')
        f.write('</td></tr></tbody></table>')

    f.close()

    return


def make_m3_figs(forecaster_dict, nick, path=''):
    """Makes m3 tables for each forecaster. Uses methods from the runmatrix module.

    :param forecaster_dict:
    :param nick:            is how I can select relevant warnings for this forecaster
    :param product_folder:  location where plots (endproduct) is saved
    :param project_folder:  many files generated; make project folder in product folder
    :return:
    """

    from varsomscripts import matrix as mx

    f = forecaster_dict[nick]
    # select only warnings for this forecaster
    one_forecaster_warnings = f.warnings

    # prepare dataset
    pickle_data_set_file_name = '{0}runforefollow data set {1}.pickle'.format(env.local_storage, f.observer_id)
    mx.pickle_data_set(one_forecaster_warnings, pickle_data_set_file_name, use_ikke_gitt=False)
    forecaster_data_set = mp.unpickle_anything(pickle_data_set_file_name)

    # prepare the m3 elementes (cell contents)
    pickle_m3_v2_file_name = '{0}runforefollow m3 {1}.pickle'.format(env.local_storage, f.observer_id)
    mx.pickle_M3(forecaster_data_set, 'matrixconfiguration.v2.csv', pickle_m3_v2_file_name)
    m3_v2_elements = mp.unpickle_anything(pickle_m3_v2_file_name)

    # plot
    plot_m3_v2_file_name = '{0}{1}_m3'.format(path, f.observer_id)
    mx.plot_m3_v2(m3_v2_elements, plot_m3_v2_file_name)

    return


def make_comparison_plots(forecaster_dict, path=''):

    import matplotlib.pyplot as plt; plt.rcdefaults()
    import numpy as np

    forecasters = [n for n,f in forecaster_dict.items()]
    y_pos = np.arange(len(forecasters))

    all_danger_levels = [f.danger_levels_avg for n,f in forecaster_dict.items()]
    all_danger_levels_std = [f.danger_levels_std for n,f in forecaster_dict.items()]

    all_problems_pr_warning = [f.problems_pr_warning_avg for n,f in forecaster_dict.items()]
    all_problems_pr_warning_std = [f.problems_pr_warning_std for n,f in forecaster_dict.items()]

    all_nowcast_lengths = [f.nowcast_lengths_avg for n,f in forecaster_dict.items()]
    all_nowcast_lengths_std = [f.nowcast_lengths_std for n,f in forecaster_dict.items()]

    all_forecast_lengths = [f.forecast_lengths_avg for n,f in forecaster_dict.items()]
    all_forecast_lengths_std = [f.forecast_lengths_std for n,f in forecaster_dict.items()]

    # all danger levels
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_danger_levels, align='center', alpha=0.5, color='pink',
             xerr=all_danger_levels_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Gjennomsnittlig faregrad')
    plt.xlim(0., 4.5)
    plt.axvline(forecaster_dict['Ragnar@NVE'].danger_levels_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Sammenlignet varselt faregrad sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_danger_201617.png'.format(path))

    # all problems pr warning
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_problems_pr_warning, align='center', alpha=0.5, color='pink',
             xerr=all_problems_pr_warning_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Snitt antall skredproblemer')
    plt.xlim(0.5, 3.)
    plt.axvline(forecaster_dict['Ragnar@NVE'].problems_pr_warning_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Antall skredproblemer pr varsel sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_problems_pr_warning_201617.png'.format(path))

    # all nowcast lengths
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_nowcast_lengths, align='center', alpha=0.5, color='b',
             xerr=all_nowcast_lengths_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Snitt tegn paa naasituasjon')
    plt.xlim(0., 1024.)
    plt.axvline(forecaster_dict['Ragnar@NVE'].nowcast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Antall tegn brukt i naasituasjonen sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_nowcast_lengths_201617.png'.format(path))

    # all forecast lengths
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_forecast_lengths, align='center', alpha=0.5, color='b',
             xerr=all_forecast_lengths_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Snitt tegn paa varselet')
    plt.xlim(0., 1024.)
    plt.axvline(forecaster_dict['Ragnar@NVE'].forecast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Antall tegn brukt i varselet sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_forecast_lengths_201617.png'.format(path))

    return


if __name__ == "__main__":

    make_forecaster_data('2018-19')

    pass