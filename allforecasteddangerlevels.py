# -*- coding: utf-8 -*-
import datetime as dt
from varsomdata import makepickle as mp
from varsomdata import getdangers as gd
from varsomdata import getobservations as go
from varsomdata import makelogs as ml
from varsomdata import getmisc as gm
import setenvironment as ste
import pylab as plt

__author__ = 'raek'


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


def get_all_ofoten():
    """Dangers and problems for Ofoten (former Narvik). Writes file to .csv"""

    get_new = True
    get_observations = False
    write_csv = True
    plot_dangerlevels_simple = False

    select_years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18']
    region_id_Narvik = 114      # Narvik used from 2012 until nov 2016
    region_id_Ofoten = 3015     # Ofoten introduced in november 2016

    warnings_pickle = '{0}allforecasteddangerlevels_Ofoten_201218.pickle'.format(ste.local_storage)
    warnings_csv = '{0}Faregrader Ofoten 2012-18.csv'.format(ste.output_folder)
    warnings_plot = '{0}Faregrader Ofoten 2012-18.png'.format(ste.output_folder)

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

    get_all_ofoten()
