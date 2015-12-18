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


def make_plots_for_region(region_id, problems, dangers, start_date, end_date):
    """
    This method prepares data for plotting and calls on the plot methods. Pure administration.

    :param region_id:       [int]   Forecast region ID as given in ForecastRegionKDV
    :param start_date:      [string]
    :param end_date:        [string]

    :return:
    """

    region_name = gro.get_forecast_region_name(region_id)

    o_danger_dates = []
    o_danger_levels = []
    w_danger_dates = []             # list of dates as datetime structures
    w_danger_levels = []            # list of danger levels as ints

    o_cause_with_date = []          # list of dates and causes
    w_cause_with_date = []

    for p in problems:
        if p.source == 'Observasjon':
            o_cause_with_date.append([p.date, p.cause_tid])
        if p.source == 'Varsel':
            w_cause_with_date.append([p.date, p.cause_tid])

    for d in dangers:
        if d.nick != 'drift@svv' and d.danger_level > 0:
            if d.source == 'Observasjon':
                o_danger_levels.append(d.danger_level)
                o_danger_dates.append(d.date)
            if d.source == 'Varsel':
                w_danger_levels.append(d.danger_level)
                w_danger_dates.append(d.date)

    # No data, no plot
    if len(w_danger_dates) is not 0: #and len(o_danger_dates) is not 0:
        plot_danger_levels(region_name, w_danger_levels, w_danger_dates, o_danger_levels, o_danger_dates)
        plot_causes(region_name, w_cause_with_date, w_danger_dates, o_cause_with_date)


def plot_danger_levels(region_name, w_danger_levels, w_dates, o_danger_levels, o_dates):
    """Plots the danger levels as bars and makes a small cake diagram with distribution.

    :param region_name:     [String] Name of forecast region
    :param w_danger_levels:   [list] Forecasted danger levels as ints
    :param w_dates:          [list] Dates as datetime structures
    :param o_danger_levels:   [list] Observed danger levels as ints
    :param o_dates:          [list] Dates  as datetime structures

    :return:
    """

    filename = r"{0} faregrader {1}-{2}".format(region_name, w_dates[0].strftime('%Y'), w_dates[-1].strftime('%y'))
    print("Plotting {0}".format(filename))

    # Figure dimensions
    fsize = (16, 10)
    fig = plt.figure(figsize=fsize)
    plt.clf()

    # Making the main plot
    DL_labels = ['5 - Meget stor', '4 - Stor', '3 - Betydelig', '2 - Moderat', '1 - Liten', '0 - Ikke vurdert', '1 - Liten', '2 - Moderat', '3 - Betydelig', '4 - Stor', '5 - Meget stor']
    DL_colors = ['0.5', '#ccff66', '#ffff00', '#ff9900', '#ff0000', 'k']

    # Making a new dataset with both warned and evaluated data
    dates = w_dates + o_dates
    eDangerLevelsNeg = [e*-1 for e in o_danger_levels]       # I want them to point down. Making a negative datasett
    dangerLevels = w_danger_levels + eDangerLevelsNeg
    values = np.asarray(dangerLevels, int)

    colors = []
    for n in values:
        if abs(n) == 1:
            colors.append(DL_colors[1])
        elif abs(n) == 2:
            colors.append(DL_colors[2])
        elif abs(n) == 3:
            colors.append(DL_colors[3])
        elif abs(n) == 4:
            colors.append(DL_colors[4])
        elif abs(n) == 5:
            colors.append(DL_colors[5])
        else:
            colors.append(DL_colors[0])

    ax = plt.axes([.15, .05, .8, .9])
    ax.bar(dates, values, color=colors)

    wNumber, eNumber, fractSame = compareDangerLevels(w_dates, o_dates, w_danger_levels, o_danger_levels)

    title = fe.add_norwegian_letters("Snoeskredfaregrad for {0} ({1} - {2})".format(region_name, w_dates[0].strftime('%Y%m%d'), w_dates[-1].strftime('%Y%m%d')))

    plt.yticks(range(-len(DL_labels)/2+1, len(DL_labels)/2+1, 1), DL_labels)#, size='small')
    #plt.xlabel('Dato')
    plt.ylabel('Faregrad')
    plt.title(title)

    fig.text(0.18, 0.13, " Totalt {0} varslet faregrader og {1} observerte faregrader \n og det er {2}% samsvar mellom det som er observert og varslet."
             .format(wNumber, eNumber, int(round(fractSame*100, 0))), fontsize = 14)

    # this is an inset pie of the distribution of dangerlevels over the main axes
    xfrac = 0.15
    yfrac = (float(fsize[0])/float(fsize[1])) * xfrac
    xpos = 0.95-xfrac
    ypos = 0.95-yfrac
    a = plt.axes([xpos, ypos, xfrac, yfrac])
    wDistr = np.bincount(w_danger_levels)
    a.pie(wDistr, colors=DL_colors, autopct='%1.0f%%', shadow=False)
    plt.setp(a, xticks=[], yticks=[])

    # this is an inset pie of the distribution of dangerlevels UNDER the main axes
    xfrac = 0.15
    yfrac = (float(fsize[0])/float(fsize[1])) * xfrac
    xpos = 0.95-xfrac
    ypos = 0.29-yfrac
    b = plt.axes([xpos, ypos, xfrac, yfrac])
    eDistr = np.bincount(o_danger_levels)
    b.pie(eDistr, colors=DL_colors, autopct='%1.0f%%', shadow=False)
    plt.setp(b, xticks=[], yticks=[])

    # This saves the figure til file
    plt.savefig("{0}{1}".format(env.plot_folder, filename))#,dpi=90)
    plt.close(fig)


def plot_causes(region_name, w_cause_with_date, w_dates, o_cause_with_date):
    '''

    :param region_name:
    :param w_cause_with_date:      [list of date, cause]
    :param w_dates:
    :param o_cause_with_date:
    :return:
    '''

    filename = r"{0} skredproblemer {1}-{2}".format(region_name, w_dates[0].strftime('%Y'), w_dates[-1].strftime('%y'))
    print("Plotting {0}".format(filename))

    AvalCauseKDV = gkdv.get_kdv("AvalCauseKDV")

    # A variable to list all WARNED causes with a list of dates they occured
    DayNoPrAvalCause = [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]                       # the day number in the series. This variable is for plotting only
    for i in range(0,len(DayNoPrAvalCause),1):
        DayNoPrAvalCause[i] = [ DayNoPrAvalCause[i], [] ]       # Make a dataseries equal to DatesPrAvalCause but with integegers of number of days form first date.

    # Loop through all dates and causes and append the dates where causes match
    for causes in range(0, len(DayNoPrAvalCause), 1):
        for dates in range(0, len(w_cause_with_date), 1):
            if w_cause_with_date[dates][1] == DayNoPrAvalCause[causes][0]:
                DayNoPrAvalCause[causes][1].append((w_cause_with_date[dates][0] - w_cause_with_date[0][0]).days)

    # Same as above but for OBSERVED causes. The result is a list of daynumbers they occured
    DayNoPrObservedCause = [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    for i in range(0,len(DayNoPrObservedCause),1):
        DayNoPrObservedCause[i] = [ DayNoPrObservedCause[i], [] ]

    for causes in range(0, len(DayNoPrObservedCause), 1):
        for dates in range(0, len(o_cause_with_date), 1):
            if o_cause_with_date[dates][1] == DayNoPrObservedCause[causes][0]:
                DayNoPrObservedCause[causes][1].append((o_cause_with_date[dates][0] - w_cause_with_date[0][0]).days)      # wAvalCause..[0][0] is the first date in the plot and thus used as reference here

    correlation = compareAvalancheCauses(DayNoPrAvalCause, DayNoPrObservedCause)
    events = []
    causes = []         # Datasett to plot the lines where a cause appeard
    count = []
    rightTicks = []
    obsEvents = []
    obsCount = []
    correlationSUM = 0

    for i in range(0, len(DayNoPrAvalCause), 1):
        events.append(DayNoPrAvalCause[i][1])
        count.append(len(events[i]))
        causes.append(fe.add_norwegian_letters("{0}".format(AvalCauseKDV[DayNoPrAvalCause[i][0]].Name)))
        obsEvents.append(DayNoPrObservedCause[i][1])
        obsCount.append(len(obsEvents[i]))
        if count[i] == 0 and obsCount[i] == 0:
            rightTicks.append("")
        else:
            rightTicks.append("v{0} o{1} s{2}%".format(count[i], obsCount[i], int(correlation[i][1]*100)))
        correlationSUM = correlationSUM + correlation[i][1]*obsCount[i]

    wNum = len(w_cause_with_date)
    pNum = len(o_cause_with_date)
    if pNum == 0:
        correlationSUM = 0
    else:
        correlationSUM = correlationSUM/pNum

    # Making dataseries for ploting the observed data in horizontal lines
    obsx, obsy = [], []
    for i,event in enumerate(obsEvents):
        obsy.extend([i]*len(event))
        obsx.extend(event)
    obsx, obsy = np.array(obsx), np.array(obsy)

    # Making the dataseries for plotting warned data in horizontal lines
    x, y = [], []
    for i,event in enumerate(events):
        y.extend([i]*len(event))
        x.extend(event)
    x, y = np.array(x), np.array(y)

    # custom dates
    axisDates = []
    axisPositions = []
    for i in range(0, len(w_dates), 1):
        if w_dates[i].day == 1:
            axisDates.append(w_dates[i].strftime("%b %Y"))
            axisPositions.append(i)

    title = "Skredproblemer for {0} ({1} - {2}) \n Totalt {3} varslede problemer (roed) og {4} observerte problemer (blaa) \n og det er {5}% samsvar mellom det som er observert og det som er varselt."\
        .format(region_name, w_dates[0].strftime('%Y%m%d'), w_dates[-1].strftime('%Y%m%d'), wNum, pNum, int(correlationSUM*100))
    title = fe.add_norwegian_letters(title)

    #Start plotting
    fsize = (16 , 7)
    plt.figure(figsize=fsize)
    plt.clf()

    # plot lines and left and bottom ticks
    plt.hlines(y-0.1, x, x+1, lw = 4, color = 'red')        # ofset the line 0.1 up
    plt.hlines(obsy+0.1, obsx, obsx+1, lw = 4, color = 'blue')      # ofset the line 0.1 down
    #plt.ylim(max(y)+0.5, min(y)-0.5)
    plt.ylim(16, -1)                # 16 skredproblemer
    plt.yticks(range(len(causes)+1), causes)
    plt.xticks(axisPositions, axisDates) #, rotation = 17)

    # Plot the rightaxis ticks and lables
    plt.twinx()
    plt.ylim(16, -1)
    plt.yticks(range(len(rightTicks)+1), rightTicks)#, color = 'red')

    plt.title(title)

    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)

    plt.savefig("{0}{1}".format(env.plot_folder, filename))


def compareDangerLevels(wDates, eDates, wDangerLevels, eDangerLevels):
    """
    Method compares warned and observed dangerlevels data by date
    """

    wNumber = len(wDangerLevels)
    eNumber = len(eDangerLevels)
    numberSame = 0.
    for i in range(0, len(wDangerLevels), 1):
        for j in range(0, len(eDangerLevels), 1):
            if wDates[i].strftime("%Y-%m-%d") == eDates[j].strftime("%Y-%m-%d") and wDangerLevels[i] == eDangerLevels[j]:
                numberSame = numberSame + 1

    if eNumber == 0:
        fractSame = 0
    else:
        fractSame = numberSame/eNumber

    return wNumber, eNumber, fractSame


def compareAvalancheCauses(DayNoPrAvalCause, DayNoPrObservedCause):

    fractSame = [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]                       # the day number in the series. This variable is for plotting only
    for i in range(0,len(fractSame),1):
        fractSame[i] = [ fractSame[i] ]       # Make a dataseries equal to DatesPrAvalCause but with integegers of number of days form first date.

    for k in range(0, len(fractSame),1):
        numberSame = 0.
        wDoubleTest = 0         # There tests are for eliminating double counting in cases of same case in two problems occuring the same day
        pDoubleTest = 0
        for j in range(0, len(DayNoPrObservedCause[k][1]), 1):
            for i in range(0, len(DayNoPrAvalCause[k][1]), 1):
                w = DayNoPrAvalCause[k][1][i]
                p = DayNoPrObservedCause[k][1][j]
                if w == p:
                    if wDoubleTest != w or pDoubleTest != p:
                        numberSame = numberSame + 1
                        wDoubleTest = w
                        pDoubleTest = p

        if len(DayNoPrObservedCause[k][1]) == 0:
            fractSame[k].append(0.)
        else:
            fractSame[k].append(numberSame/len(DayNoPrObservedCause[k][1]))

    return fractSame


def get_data_from_api(region_id, start_date, end_date):
    """Gets all the data needed in the plots and pickles it so that I don't need to do requests to make plots.

    :param region_id:       [int]    Region ID is an int as given i ForecastRegionKDV
    :param start_date:      [string] Start date. Data for this date is not included in requests from OData
    :param end_date:
    :return:
    """

    problems = gp.get_all_problems(region_id, start_date, end_date)
    dangers = gd.get_all_dangers(region_id, start_date, end_date)

    return problems, dangers

if __name__ == "__main__":

    ##### Start small - do one region
    # get_data_from_api_and_pickle(129, "2014-12-01", "2015-06-01")
    # make_plots_for_region(129, "2014-12-01", "2015-06-01")

    ## Get all regions
    region_id = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
        if 100 < k < 150 and v.IsActive is True:
            region_id.append(v.ID)

    from_date = dt.date(2014, 12, 1)
    to_date = dt.date(2015, 6, 1)
    #to_date = dt.date.today() + dt.timedelta(days=2)

    # All regions span from 6 (Alta) to 33 (Salten).
    for i in region_id:
        problems, dangers = get_data_from_api(i, from_date, to_date)

        # # Saving the objects:
        # filename = "{3}runForPlots ID{0} {1} {2}.pickle".format(region_id, from_date, to_date, env.local_storage)
        # mp.pickle_anything([problems, dangers], filename)
        # problems, dangers = mp.unpickle_anything(filename)

        make_plots_for_region(i, problems, dangers, from_date, to_date)


