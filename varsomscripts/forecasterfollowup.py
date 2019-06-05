# -*- coding: utf-8 -*-
"""

"""

import datetime as dt
from varsomdata import getvarsompickles as gvp
from varsomdata import getobservations as go
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

    def __init__(self, author_in):

        self.author = author_in

        # About the warning production for current author
        self.warnings = []                  # all warnings made by this forecaster
        self.warning_count = 0           # int number of warnings
        self.warning_publish_dates = {}     # dict of {date: number of warnings}
        self.work_days = 0

        # About the warning content for current author
        self.danger_levels = []             # ints
        self.main_texts = []                # strings
        self.avalanche_dangers = []         # strings
        self.snow_surfaces = []             # strings
        self.current_weak_layers = []       # strings
        self.problems_pr_warnings = []      # ints

        # About observations for current author
        self.observer_id = None             # int observer id in regObs
        self.observer_nick = None
        self.observations = []
        self.observation_count = 0
        self.avalanche_evaluation_count = 0
        self.avalanche_problem_count = 0
        self.snow_profile_count = 0

    def add_warning(self, warning_in):
        # add warning
        self.warnings.append(warning_in)
        self._update_warning_key_figures()

    def _update_warning_key_figures(self):
        # update numbers on the authors production
        self.warning_count += 1

        publish_date = self.warnings[-1].publish_time.date()
        if publish_date in self.warning_publish_dates.keys():
            self.warning_publish_dates[publish_date] += 1
        else:
            self.warning_publish_dates[publish_date] = 1

        self.work_days = len(self.warning_publish_dates.keys())

    def add_observation(self, observation_in):
        # add observations and update numbers for about authors observations
        self.observations.append(observation_in)
        self.observer_id = observation_in.ObserverID
        self.observer_nick = observation_in.NickName
        self.observation_count = len(self.observations)

        for f in observation_in.Observations:

            if isinstance(f, go.AvalancheEvaluation3):
                self.avalanche_evaluation_count += 1

            if isinstance(f, go.AvalancheEvalProblem2):
                self.avalanche_problem_count += 1

            if isinstance(f, go.SnowProfile):
                self.snow_profile_count += 1

    def add_danger_levels(self, danger_levels_in, danger_levels_all_in):
        self.danger_levels = _WarningPartInt(danger_levels_in, danger_levels_all_in)

    def add_main_texts(self, main_texts_in, main_texts_all_in):
        self.main_texts = _WarningPartString(main_texts_in, main_texts_all_in)

    def add_avalanche_dangers(self, avalanche_dangers_in, avalanche_dangers_all_in):
        self.avalanche_dangers = _WarningPartString(avalanche_dangers_in, avalanche_dangers_all_in)

    def add_snow_surfaces(self, snow_surface_in, snow_surface_all_in):
        self.snow_surfaces = _WarningPartString(snow_surface_in, snow_surface_all_in)

    def add_current_weak_layers(self, current_weak_layers_in, current_weak_layers_all_in):
        self.current_weak_layers = _WarningPartString(current_weak_layers_in, current_weak_layers_all_in)

    def add_problems_pr_warnings(self, problems_pr_warnings_in, problems_pr_warnings_all_in):
        self.problems_pr_warnings = _WarningPartInt(problems_pr_warnings_in, problems_pr_warnings_all_in)

    def to_dict(self):

        _dict = {'Author': self.author,
                 'WarningCount': self.warning_count,
                 'WorkDays': self.work_days,
                 'ObserverNick': self.observer_nick,
                 'ObserverID': self.observer_id,
                 'ObservationCount': self.observation_count,
                 'AvalancheEvaluationCount': self.avalanche_evaluation_count,
                 'AvalancheProblemCount': self.avalanche_problem_count,
                 'SnowProfileCount': self.snow_profile_count
                 }

        return _dict


def make_forecaster_data(year):
    """
    For one season, make the forecaster dictionary with all the necessary data.
    :param year:    [string] Eg. season '2018-19'
    """

    # The data
    all_warnings = gvp.get_all_forecasts(year, max_file_age=23)
    all_observation_forms = gvp.get_all_observations(year, geohazard_tids=10, max_file_age=23)

    forecaster_data = {}

    for w in all_warnings:
        if w.author in forecaster_data.keys():
            forecaster_data[w.author].add_warning(w)
        else:
            forecaster_data[w.author] = Forecaster(w.author)
            forecaster_data[w.author].add_warning(w)

    # number_by_author_sorted = sorted(number_by_author.items(), key=lambda kv: kv[1], reverse=True)

    for o in all_observation_forms:
        if o.NickName in forecaster_data.keys():
            forecaster_data[o.NickName].add_observation(o)

    forecaster_list_of_dict = []
    for v in forecaster_data.values():
        forecaster_list_of_dict.append(v.to_dict())

    import csv
    with open('{0}forecaster_followup.txt'.format(env.output_folder), 'w', encoding='utf8') as f:
        dict_writer = csv.DictWriter(f, delimiter=';', fieldnames=forecaster_list_of_dict[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(forecaster_list_of_dict)

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