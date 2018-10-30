# -*- coding: utf-8 -*-
"""The code for downloading and making the plots on ragnar.pythonanywhere.com/dangerandproblem/"""

import numpy as np
import pylab as plt
import datetime as dt
import os as os

import matplotlib
matplotlib.use('Agg')  # Generate images without having a window appear. See https://matplotlib.org/faq/howto_faq.html
import matplotlib.pyplot as pplt

from varsomdata import getdangers as gd
from varsomdata import getproblems as gp
from varsomdata import getmisc as gm
from utilities import makepickle as mp
from varsomdata import getkdvelements as gkdv
from utilities import makelogs as ml
import setenvironment as env

__author__ = 'raek'
log_reference = 'plotdangerandproblem.py -> '


def get_data(region_id, start_date, end_date, get_new=True):
    """Gets all the data needed in the plots and pickles it so that I don't need to do requests to make plots.

    :param region_id:       [int] Region ID is an int as given i ForecastRegionKDV
    :param start_date:      [string] Start date.
    :param end_date:        [string] End date.
    :param get_new:         [bool] If true, new data is requested. If false, a local pickle is used for data.
    :return problems, dangers, aval_indexes:
    """

    file_name = "{3}plotdangerandproblem_region{0}_{1}{2}.pickle".format(region_id, start_date.strftime('%Y'), end_date.strftime('%y'), env.local_storage)

    if not get_new and not os.path.exists(file_name):
        get_new = True
        ml.log_and_print("[info] {0}get_data: pickle missing, getting new data.".format(log_reference), print_it=True)

    if get_new:
        dangers = gd.get_all_dangers(region_id, start_date, end_date)

        # Early years don't have the avalanche problem we will be analyzing
        if start_date > dt.date(2014, 11, 1):
            problems = gp.get_all_problems(region_id, start_date, end_date, add_danger_level=False)
        else:
            problems = []

        aval_indexes = gm.get_avalanche_index(start_date, end_date, region_ids=region_id)
        mp.pickle_anything([problems, dangers, aval_indexes], file_name)

    else:
        problems, dangers, aval_indexes = mp.unpickle_anything(file_name)

    return problems, dangers, aval_indexes


class DangerLevel():


    def __init__(self, danger_level_inn, date_inn, source_inn, danger_object_inn):

        self.danger_level = danger_level_inn
        self.date = date_inn
        self.source = source_inn
        self.danger_object = danger_object_inn


class AvalanceCause():


    def __init__(self, cause_tid, date, source):

        self.cause_tid = cause_tid
        self.date = date
        self.source = source
        self.cause_name = None
        self.set_cause_name()


    def set_cause_name(self):

        AvalCauseKDV = gkdv.get_kdv("AvalCauseKDV")
        self.cause_name = AvalCauseKDV[self.cause_tid].Name


def plot_causes(region_name, from_date, to_date, causes):
    """

    :param causes:
    :return:
    """

    filename = u'{0} skredproblemer {1}-{2}'.format(region_name, from_date.strftime('%Y'), to_date.strftime('%y'))
    ml.log_and_print('[info] {0}plot_causes: Plotting {1}'.format(log_reference, filename), print_it=True)

    AvalCauseKDV = gkdv.get_kdv("AvalCauseKDV")
    list_of_causes = [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    #list_of_causes = set([c.cause_tid for c in causes])
    list_of_cause_names = [AvalCauseKDV[tid].Name for tid in list_of_causes]

    dict_of_causes = {}
    for c in list_of_causes:
        dict_of_causes[c] = []
    for c in causes:
        dict_of_causes[c.cause_tid].append(c)

    #Start plotting
    fsize = (16 , 7)
    plt.figure(figsize=fsize)
    plt.clf()

    # plot lines and left and bottom ticks
    y = 0
    for k,values in dict_of_causes.items():
        for v in values:
            x  = (v.date-from_date).days
            if 'Forecast' in v.source:
                plt.hlines(y-0.1, x, x+1, lw = 4, color = 'red')        # ofset the line 0.1 up
            if 'Observation' in v.source:
                plt.hlines(y+0.1, x, x+1, lw = 4, color = 'blue')      # ofset the line 0.1 down
        y += 1


    # Left y-axis labels
    plt.ylim(len(list_of_causes)-1, -1)                # 16 skredproblemer
    plt.yticks(range(len(list_of_causes)+1), list_of_cause_names)


    # x-axis labels
    axis_dates = []
    axis_positions = []
    for i in range(0, (to_date-from_date).days, 1):
        date = from_date + dt.timedelta(days = i)
        if date.day == 1:
            axis_dates.append(date.strftime("%b %Y"))
            axis_positions.append(i)
    plt.xticks(axis_positions, axis_dates)


    # Right hand side y-axis
    right_ticks = []
    correlation_sum = 0.
    for k,values in dict_of_causes.items():
        values_obs = [vo for vo in values if 'Observation' in vo.source]
        values_fc = [vf for vf in values if 'Forecast' in vf.source]
        correlation = 0.
        for obs in values_obs:
            for fc in values_fc:
                if obs.date == fc.date and obs.cause_tid == fc.cause_tid:
                    correlation += 1
        if len(values_obs) == 0 and len(values_fc) == 0:
            right_ticks.append("")
        else:
            if len(values_obs) == 0:
                right_ticks.append("v{0} o{1} s{2}%".format(len(values_fc), len(values_obs), 0))
            else:
                right_ticks.append("v{0} o{1} s{2}%".format(len(values_fc), len(values_obs), int(correlation/len(values_obs)*100)))
        correlation_sum += correlation
    right_ticks.reverse()
    plt.twinx()
    plt.ylim(-1, len(right_ticks)-1)
    plt.yticks(range(len(right_ticks)+1), right_ticks)


    # the title
    num_obs = len([c for c in causes if 'Observation' in c.source])
    num_fc = len([c for c in causes if 'Forecast' in c.source])
    if num_obs == 0:
        correlation_prct = 0
    else:
        correlation_prct = int(correlation_sum/num_obs*100)

    title = 'Skredproblemer for {0} ({1} - {2}) \n Totalt {3} varslede problemer (rød) og {4} observerte problemer (blå) \n og det er {5}% samsvar mellom det som er observert og det som er varselt.'\
        .format(region_name, from_date.strftime('%Y%m%d'), to_date.strftime('%Y%m%d'), num_fc, num_obs, correlation_prct)
    plt.title(title)

    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig(u'{0}{1}'.format(env.web_images_regiondata_folder, filename))
    plt.close(fig)


def plot_danger_levels(region_name, start_date, end_date, danger_levels, aval_indexes):
    """Plots the danger levels as bars and makes a small cake diagram with distribution.

    :param region_name:     [String] Name of forecast region
    :param start_date:
    :param end_date:
    :param danger_levels:
    :param aval_indexes:
    :return:
    """

    filename = '{0} faregrader {1}-{2}'.format(region_name, start_date.strftime('%Y'), end_date.strftime('%y'))
    ml.log_and_print("[info] {0}plot_danger_levels: Plotting {1}".format(log_reference, filename), print_it=True)

    # Figure dimensions
    fsize = (16, 16)
    fig = plt.figure(figsize=fsize)
    plt.clf()

    ##########################################
    ###### First subplot with avalanche index
    ##########################################
    pplt.subplot2grid((6, 1), (0, 0), rowspan=1)

    index_dates = []
    data_indexes = []
    index_colors = []

    for i in aval_indexes:
        date = i.date
        index_dates.append(date)
        data_indexes.append(i.index)
        # color on the marker
        if i.index == 0:
            index_colors.append('white')
        elif i.index == 1:
            index_colors.append('pink')
        elif i.index >= 2 and i.index <= 5:
            index_colors.append('green')
        elif i.index >= 6 and i.index <= 9:
            index_colors.append('yellow')
        elif i.index >= 10 and i.index <= 12:
            index_colors.append('orange')
        elif i.index >= 13:
            index_colors.append('red')
        else:
            index_colors.append('black')
            # TODO: this option should not happen. Test for no black markers

    index_values = np.asarray(data_indexes, int)

    plt.scatter(index_dates, index_values, s=50., c=index_colors, alpha=0.5)
    plt.yticks([1, 4, 6, 11, 17, 22], ['Ingen - 1', 'Ett str2 - 4', 'Ett str3 - 6', 'Noen str3 - 11', 'Mange str3 - 17', ''])
    plt.ylabel("Skredindex")
    plt.xlim(start_date, end_date)

    title = "Faregrad og skredindeks for {0} ({1}-{2})".format(region_name, start_date.strftime('%Y'), end_date.strftime('%y'))
    plt.title(title)

    ##########################################
    ## Second subplot with avalanche danger forecast
    ##########################################
    pplt.subplot2grid((6, 1), (1, 0), rowspan=2)

    # Making the main plot
    dl_labels = ['', '1 - Liten', '2 - Moderat', '3 - Betydelig', '4 - Stor', '']
    dl_colors = ['0.5', '#ccff66', '#ffff00', '#ff9900', '#ff0000', 'k']

    # Making a new dataset with both warned and evaluated data
    data_dates = []
    data_dangers = []

    for d in danger_levels:
        data_dates.append(d.date)
        if 'Forecast' in d.source:
            data_dangers.append(d.danger_level)
        else:
            data_dangers.append(0.*d.danger_level)

    values = np.asarray(data_dangers, int)

    colors = []
    for n in values:
        if abs(n) == 1:
            colors.append(dl_colors[1])
        elif abs(n) == 2:
            colors.append(dl_colors[2])
        elif abs(n) == 3:
            colors.append(dl_colors[3])
        elif abs(n) == 4:
            colors.append(dl_colors[4])
        elif abs(n) == 5:
            colors.append(dl_colors[5])
        else:
            colors.append(dl_colors[0])

    plt.bar(data_dates, values, color=colors)
    plt.yticks(range(0, len(dl_labels), 1), dl_labels) #, size='small')
    plt.ylabel("Varslet faregrad2")
    plt.xlim(start_date, end_date)

    ##########################################
    ######### Third subplot with avalanche danger observed
    ##########################################
    pplt.subplot2grid((6, 1), (3, 0), rowspan=2)

    dl_labels = ['', '1 - Liten', '2 - Moderat', '3 - Betydelig', '4 - Stor', '']
    dl_colors = ['0.5', '#ccff66', '#ffff00', '#ff9900', '#ff0000', 'k']

    # Making a new dataset with both warned and evaluated data
    data_dates = []
    data_dangers = []

    for d in danger_levels:
        data_dates.append(d.date)
        if not 'Forecast' in d.source:
            data_dangers.append(-1.*d.danger_level)
        else:
            data_dangers.append(0.*d.danger_level)

    values = np.asarray(data_dangers, int)

    colors = []
    for n in values:
        if abs(n) == 1:
            colors.append(dl_colors[1])
        elif abs(n) == 2:
            colors.append(dl_colors[2])
        elif abs(n) == 3:
            colors.append(dl_colors[3])
        elif abs(n) == 4:
            colors.append(dl_colors[4])
        elif abs(n) == 5:
            colors.append(dl_colors[5])
        else:
            colors.append(dl_colors[0])

    plt.bar(data_dates, values, color=colors)
    plt.yticks(range(0, -len(dl_labels), -1), dl_labels)
    plt.ylabel('Observert faregrad')
    plt.xticks([])
    plt.xlim(start_date, end_date)

    ##########################################
    ######### Forth subplot with how well the forecast is
    ##########################################
    pplt.subplot2grid((6, 1), (5, 0), rowspan=1)
    plt.xlim(start_date, end_date)

    forecast_correct_values = []
    forecast_correct_colours = []
    forecast_correct_dates = []
    for d in danger_levels:
        if 'Observation' in d.source:
            forecast_correct = d.danger_object.forecast_correct
            if forecast_correct is not None and not 'Ikke gitt' in forecast_correct:
                forecast_correct_dates.append(d.date)
                if 'riktig' in forecast_correct:
                    forecast_correct_values.append(0)
                    forecast_correct_colours.append('green')
                elif 'for lav' in forecast_correct:
                    forecast_correct_values.append(-1)
                    forecast_correct_colours.append('red')
                elif 'for høy' in forecast_correct:
                    forecast_correct_values.append(1)
                    forecast_correct_colours.append('red')
                else:
                    forecast_correct_values.append(0)
                    forecast_correct_colours.append('black')
                    # TODO: Check if no black markers

    forecast_correct_np_values = np.asarray(forecast_correct_values, int)
    plt.scatter(forecast_correct_dates, forecast_correct_np_values, s=50., c=forecast_correct_colours, alpha=0.5)
    plt.yticks(range(-1, 2, 1), ['For lav','Riktig','    For høy'])
    plt.ylabel('Stemmer varslet faregrad?')

    # this is an inset pie of the distribution of dangerlevels OVER the main axes
    xfrac = 0.15
    yfrac = (float(fsize[0])/float(fsize[1])) * xfrac
    xpos = 0.45-xfrac
    ypos = 0.95-yfrac
    a = plt.axes([0.8, 0.66, 0.10, 0.10])
    #a = plt.axes([xpos, ypos, xfrac, yfrac])
    wDistr = np.bincount([d.danger_level for d in danger_levels if 'Forecast' in d.source])
    a.pie(wDistr, colors=dl_colors, autopct='%1.0f%%', shadow=False)
    plt.setp(a, xticks=[], yticks=[])

    # this is an inset pie of the distribution of dangerlevels UNDER the main axes
    xfrac = 0.15
    yfrac = (float(fsize[0])/float(fsize[1])) * xfrac
    xpos = 0.95-xfrac
    ypos = 0.29-yfrac
    b = plt.axes([0.8, 0.24, 0.10, 0.10])
    #b = plt.axes([xpos, ypos, xfrac, yfrac])
    eDistr = np.bincount([d.danger_level for d in danger_levels if 'Observation' in d.source])
    b.pie(eDistr, colors=dl_colors, autopct='%1.0f%%', shadow=False)
    plt.setp(b, xticks=[], yticks=[])

    # figuretext in observed dangerlevels subplot
    w_number, e_number, fract_same = compare_danger_levels(danger_levels)
    fig.text(0.15, 0.25, ' Totalt {0} varslet faregrader og {1} observerte faregrader \n og det er {2}% samsvar mellom det som er observert og varslet.'
             .format(w_number, e_number, int(round(fract_same*100, 0))), fontsize = 14)

    # fractions to the right in the forecast correct subplot
    forecast_correct_distr = {}
    for f in forecast_correct_values:
        if f in forecast_correct_distr.keys():
            forecast_correct_distr[f] += 1
        else:
            forecast_correct_distr[f] = 1

    if 1 in forecast_correct_distr.keys():  fig.text(0.91, 0.19, '{0}%'.format(  int(round(forecast_correct_distr[1]/float(len(forecast_correct_values))*100, 0)))  ,fontsize = 14)
    if 0 in forecast_correct_distr.keys():  fig.text(0.91, 0.15, '{0}%'.format(  int(round(forecast_correct_distr[0]/float(len(forecast_correct_values))*100, 0)))  ,fontsize = 14)
    if -1 in forecast_correct_distr.keys(): fig.text(0.91, 0.11, '{0}%'.format(  int(round(forecast_correct_distr[-1]/float(len(forecast_correct_values))*100, 0))) ,fontsize = 14)

    # This saves the figure to file
    plt.savefig(u'{0}{1}'.format(env.web_images_regiondata_folder, filename))#,dpi=90)
    fig.tight_layout()
    plt.close(fig)


def compare_danger_levels(danger_levels):
    """Method compares warned and observed danger levels date by date"""

    forecasts = [d for d in danger_levels if 'Forecast' in d.source]
    observations = [d for d in danger_levels if 'Observation' in d.source]

    number_same = 0.

    for f in forecasts:
        for o in observations:
            if f.date == o.date and f.danger_level == o.danger_level:
                number_same += 1

    if len(observations) is 0:
        fract_same = 0
    else:
        fract_same = number_same/len(observations)

    return len(forecasts), len(observations), fract_same


def make_plots_for_region(region_id, problems, dangers, aval_indexes, start_date, end_date):
    """This method prepares data for plotting and calls on the plot methods. Pure administration.

    :param region_id:       [int]   Forecast region ID as given in ForecastRegionKDV
    :param start_date:      [string]
    :param end_date:        [string]

    :return:
    """

    region_name = gm.get_forecast_region_name(region_id)

    causes = []     # list of dates and causes
    for p in problems:
        causes.append( AvalanceCause(p.cause_tid, p.date, p.source) )

    danger_levels = []
    for d in dangers:
        if d.nick != 'drift@svv' and d.danger_level > 0:        # for these plots elrapp wil make noise.
            danger_levels.append(DangerLevel(d.danger_level, d.date, d.source, d))

    # Only data with danger levels are plotted
    if len(danger_levels) is not 0:

        # Danger level histograms
        plot_danger_levels(region_name, start_date, end_date, danger_levels, aval_indexes)

        # Cause horizontal line plots
        if end_date > dt.date(2014, 11, 1) and start_date > dt.date(2014, 11, 1): # Early years dont have this avalanche problem
            plot_causes(region_name, start_date, end_date, causes)


def make_2017_18_plots():
    """Makes all plots for all regions and saves to web-app folder."""

    from_date = dt.date(2017, 11, 15)
    to_date = dt.date.today() + dt.timedelta(days=2)
    if dt.date.today().year == 2017:
        to_date = dt.date(2018, 1, 1)

    region_ids = gm.get_forecast_regions('2017-18')

    for i in region_ids:
        problems, dangers, aval_indexes = get_data(i, from_date, to_date, get_new=True)
        make_plots_for_region(i, problems, dangers, aval_indexes, from_date, to_date)


def make_2016_17_plots():
    """Makes all plots for all regions and saves to web-app folder."""

    from_date = dt.date(2016, 11, 15)
    to_date = dt.date.today() + dt.timedelta(days=2)

    region_ids = gm.get_forecast_regions('2016-17')

    for i in region_ids:
        problems, dangers, aval_indexes = get_data(i, from_date, to_date, get_new=True)
        make_plots_for_region(i, problems, dangers, aval_indexes, from_date, to_date)


if __name__ == "__main__":

    # make_2017_18_plots()

    from_date = dt.date(2018, 10, 1)
    to_date = dt.date(2019, 6, 1)
    to_date = dt.date.today() + dt.timedelta(days=2)

    # #### Start small - do one region
    i = 3029 # Nordensköld Land
    problems, dangers, aval_indexes = get_data(i, from_date, to_date, get_new=True)
    make_plots_for_region(i, problems, dangers, aval_indexes, from_date, to_date)

    # All regions pr 2016-2017
    # region_ids = [3003,3007,3009,3010,3011,3012,3013,3014,3015,3016,3017,3022,3023,3024,3027,3028,3029,3031,3032,3034,3035]  # two first years had more regions. Uncomment if making plots for 2012-13 and 2013-14

    # for i in region_ids:
    # problems, dangers, aval_indexes = get_data(i, from_date, to_date, data_from="request")
    # make_plots_for_region(i, problems, dangers, aval_indexes, from_date, to_date)

    pass
