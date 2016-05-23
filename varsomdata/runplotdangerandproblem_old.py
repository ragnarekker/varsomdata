# -*- coding: utf-8 -*-
__author__ = 'raek'

import matplotlib
matplotlib.use('Agg')
import numpy as np
import pylab as plt
import getdangers as gd
import getproblems as gp
import makepickle as mp
import getregobs as gro
import fencoding as fe
import getkdvelements as gkdv
import setenvironment as env
import datetime as dt


def plot_causes(region_name, from_date, to_date, causes):
    '''

    :param causes:
    :return:
    '''

    filename = r"{0} skredproblemer {1}-{2}".format(region_name, from_date.strftime('%Y'), to_date.strftime('%y'))
    print("Plotting {0}".format(filename))

    AvalCauseKDV = gkdv.get_kdv("AvalCauseKDV")
    list_of_causes = [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    #list_of_causes = set([c.cause_tid for c in causes])
    list_of_cause_names = [fe.add_norwegian_letters(AvalCauseKDV[tid].Name) for tid in list_of_causes]

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
    for k,values in dict_of_causes.iteritems():
        for v in values:
            x  = (v.date-from_date).days
            if 'Varsel' in v.source:
                plt.hlines(y-0.1, x, x+1, lw = 4, color = 'red')        # ofset the line 0.1 up
            if 'Observasjon' in v.source:
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
    for k,values in dict_of_causes.iteritems():
        values_obs = [vo for vo in values if 'Observasjon' in vo.source]
        values_fc = [vf for vf in values if 'Varsel' in vf.source]
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
    num_obs = len([c for c in causes if 'Observasjon' in c.source])
    num_fc = len([c for c in causes if 'Varsel' in c.source])
    if num_obs == 0:
        correlation_prct = 0
    else:
        correlation_prct = int(correlation_sum/num_obs*100)

    title = "Skredproblemer for {0} ({1} - {2}) \n Totalt {3} varslede problemer (roed) og {4} observerte problemer (blaa) \n og det er {5}% samsvar mellom det som er observert og det som er varselt."\
        .format(region_name, from_date.strftime('%Y%m%d'), to_date.strftime('%Y%m%d'), num_fc, num_obs, correlation_prct)
    title = fe.add_norwegian_letters(title)
    plt.title(title)

    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig("{0}{1}".format(env.web_images_folder, filename))
    plt.close(fig)

    return


def compare_danger_levels(danger_levels):
    """
    Method compares warned and observed dangerlevels data by date
    """

    forecasts = [d for d in danger_levels if 'Varsel' in d.source]
    observations = [d for d in danger_levels if 'Observasjon' in d.source]

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


def plot_danger_levels(region_name, start_date, end_date, danger_levels):
    """Plots the danger levels as bars and makes a small cake diagram with distribution.

    :param region_name:     [String] Name of forecast region
    :param

    :return:
    """

    filename = r"{0} faregrader {1}-{2}".format(region_name, start_date.strftime('%Y'), end_date.strftime('%y'))
    print("Plotting {0}".format(filename))

    # Figure dimensions
    fsize = (16, 10)
    fig = plt.figure(figsize=fsize)
    plt.clf()

    # Making the main plot
    dl_labels = ['5 - Meget stor', '4 - Stor', '3 - Betydelig', '2 - Moderat', '1 - Liten', '0 - Ikke vurdert', '1 - Liten', '2 - Moderat', '3 - Betydelig', '4 - Stor', '5 - Meget stor']
    dl_colors = ['0.5', '#ccff66', '#ffff00', '#ff9900', '#ff0000', 'k']

    # Making a new dataset with both warned and evaluated data
    data_dates = []
    data_dangers = []

    for d in danger_levels:
        data_dates.append(d.date)
        if 'Varsel' in d.source:
            data_dangers.append(d.danger_level)
        else:
            data_dangers.append(-1*d.danger_level)

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

    ax = plt.axes([.15, .05, .8, .9])
    ax.bar(data_dates, values, color=colors)

    w_number, e_number, fract_same = compare_danger_levels(danger_levels)

    title = fe.add_norwegian_letters("Snoeskredfaregrad for {0} ({1}-{2})".format(region_name, start_date.strftime('%Y'), end_date.strftime('%y')))

    plt.yticks(range(-len(dl_labels)/2+1, len(dl_labels)/2+1, 1), dl_labels)#, size='small')
    #plt.xlabel('Dato')
    plt.ylabel('Faregrad')
    plt.title(title)

    fig.text(0.18, 0.13, " Totalt {0} varslet faregrader og {1} observerte faregrader \n og det er {2}% samsvar mellom det som er observert og varslet."
             .format(w_number, e_number, int(round(fract_same*100, 0))), fontsize = 14)

    # this is an inset pie of the distribution of dangerlevels OVER the main axes
    xfrac = 0.15
    yfrac = (float(fsize[0])/float(fsize[1])) * xfrac
    xpos = 0.95-xfrac
    ypos = 0.95-yfrac
    a = plt.axes([xpos, ypos, xfrac, yfrac])
    wDistr = np.bincount([d.danger_level for d in danger_levels if 'Varsel' in d.source])
    a.pie(wDistr, colors=dl_colors, autopct='%1.0f%%', shadow=False)
    plt.setp(a, xticks=[], yticks=[])

    # this is an inset pie of the distribution of dangerlevels UNDER the main axes
    xfrac = 0.15
    yfrac = (float(fsize[0])/float(fsize[1])) * xfrac
    xpos = 0.95-xfrac
    ypos = 0.29-yfrac
    b = plt.axes([xpos, ypos, xfrac, yfrac])
    eDistr = np.bincount([d.danger_level for d in danger_levels if 'Observasjon' in d.source])
    b.pie(eDistr, colors=dl_colors, autopct='%1.0f%%', shadow=False)
    plt.setp(b, xticks=[], yticks=[])

    # This saves the figure til file
    plt.savefig("{0}{1}".format(env.web_images_folder, filename))#,dpi=90)
    plt.close(fig)

    return


class DangerLevel():


    def __init__(self, danger_level, date, source):

        self.danger_level = danger_level
        self.date = date
        self.source = source


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


def make_plots_for_region(region_id, problems, dangers, start_date, end_date):
    """
    This method prepares data for plotting and calls on the plot methods. Pure administration.

    :param region_id:       [int]   Forecast region ID as given in ForecastRegionKDV
    :param start_date:      [string]
    :param end_date:        [string]

    :return:
    """

    region_name = gro.get_forecast_region_name(region_id)

    danger_levels = []
    causes = []          # list of dates and causes

    for p in problems:
        causes.append( AvalanceCause(p.cause_tid, p.date, p.source) )

    for d in dangers:
        if d.nick != 'drift@svv' and d.danger_level > 0:
            danger_levels.append( DangerLevel(d.danger_level, d.date, d.source))

    # No data, no plot
    if len(danger_levels) is not 0:
        plot_danger_levels(region_name, start_date, end_date, danger_levels)
        if end_date > dt.date(2014, 11, 01) and start_date > dt.date(2014, 11, 01): # Early years dont have this avalanche problem
            plot_causes(region_name, start_date, end_date, causes)


def get_data(region_id, start_date, end_date, data_from="request"):
    """Gets all the data needed in the plots and pickles it so that I don't need to do requests to make plots.

    :param region_id:       [int]    Region ID is an int as given i ForecastRegionKDV
    :param start_date:      [string] Start date. Data for this date is not included in requests from OData
    :param end_date:
    :param data_from:       [string] Default "request". Other options: "request and save" and "local storage"
    :return:
    """

    filename = "{3}dangerandproblemplot_id{0} {1}-{2}.pickle".format(region_id, start_date.strftime('%Y'), end_date.strftime('%y'), env.local_storage)

    if "request" in data_from:
        if end_date > dt.date(2014, 11, 01) and start_date > dt.date(2014, 11, 01): # Early years dont have this avalanche problem
            problems = gp.get_all_problems(region_id, start_date, end_date, add_danger_level=False)
        else:
            problems = []

        dangers = gd.get_all_dangers(region_id, start_date, end_date)

        if "request and save" in data_from:
            mp.pickle_anything([problems, dangers], filename)

    elif "local storage" in data_from:
        problems, dangers = mp.unpickle_anything(filename)

    else:
        print "rundagerandproblem.py -> get_data: unknown data handler."
        problems = None
        dangers = None


    return problems, dangers


def make_2015_16_plots():
    """Makes all plots for all regions and saves to web-app folder

    :return:
    """

    from_date = dt.date(2015, 11, 15)
    to_date = dt.date.today() + dt.timedelta(days=2)

    ## Get all regions
    region_id = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
        if 100 < k < 150 and v.IsActive is True:
            region_id.append(v.ID)

    # All regions span from 6 (Alta) to 33 (Salten).
    for i in region_id:
        problems, dangers = get_data(i, from_date, to_date, data_from="request")
        make_plots_for_region(i, problems, dangers, from_date, to_date)

    return


if __name__ == "__main__":


    from_date = dt.date(2015, 11, 15)
    to_date = dt.date(2015, 6, 1)


    # #### Start small - do one region
    # i = 121
    # problems, dangers = get_data(i, from_date, to_date, data_from="request and save")
    # make_plots_for_region(i, problems, dangers, from_date, to_date)

    ## Get all regions
    region_id = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
        if 100 < k < 150 and v.IsActive is True:
            region_id.append(v.ID)

    # region_id += [113,125,126]  # two first years had more regions. Uncomment if making plots for 2012-13 and 2013-14

    # All regions span from 6 (Alta) to 33 (Salten).
    for i in region_id:
        problems, dangers = get_data(i, from_date, to_date, data_from="request")
        make_plots_for_region(i, problems, dangers, from_date, to_date)


