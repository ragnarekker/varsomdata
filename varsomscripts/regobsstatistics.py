# -*- coding: utf-8 -*-
"""Module for calculating and plotting overall performance of Regobs."""

import setenvironment as env
from varsomdata import getvarsompickles as gvp
from varsomdata import getmisc as gm
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import os as os
import numpy as np
import datetime as dt

__author__ = 'ragnarekker'


def _str(int_inn):
    """Change the int to string but make sure it has two digits. The int represents a month og day."""

    if len(str(int_inn)) < 2:
        int_as_string = '0' + str(int_inn)
    else:
        int_as_string = str(int_inn)

    return int_as_string


def _sum_list(list_inn):
    """Returns a new list where every entry is the sum of entries thus far in list_inn."""

    sum_this_far = 0
    sum_list = []
    for l in list_inn:
        if l is None:
            sum_list.append(None)
        else:
            sum_this_far += l
            sum_list.append(sum_this_far)

    return sum_list


def _smooth(list_of_numbers, crop_for_season=False):
    """Smooths a list of numbers with a sliding hanning window. If list_of_numbers represents the current
    season, days after today are cropped away.

    :param list_of_numbers:
    :param crop_for_season:
    :return:
    """

    length_of_season = len(list_of_numbers)

    if crop_for_season:
        number_of_days_to_crop = (dt.date.today() - dt.date(2019, 9, 1)).days
        list_of_numbers = list_of_numbers[:number_of_days_to_crop]

    window_size = 11
    window = np.hanning(window_size)
    shift = int(window_size/2)

    # make np array
    np_array_with_none = np.asarray(list_of_numbers)
    # replace None to 0
    np_array = [i if i is not None else 0 for i in np_array_with_none]
    # convoulution with hann window (the smoothing)
    smoothed_array = np.convolve(window / window.sum(), np_array, mode='valid')

    # shift smoothing half hanning window to the right
    smoothed_array_shift = np.append([None] * shift, smoothed_array)
    # add nones to the rest so length array is the same as inn
    full_list_smooth = np.append(smoothed_array_shift, [None] * (length_of_season - len(smoothed_array_shift)))
    full_np_array = np.append(np_array, [None] * (length_of_season - len(np_array)))

    return full_np_array, full_list_smooth


class DailyNumbers:

    def __init__(self, month_inn, day_inn):

        self.month = month_inn
        self.day = day_inn
        self._set_date_as_string()

        self.regs_this_season = []
        self.regs_this_season_num = None
        self.regs_prev_season = []
        self.regs_prev_season_num = None
        self.regs_two_seasons_ago = []
        self.regs_two_seasons_ago_num = None

        self.obs_this_season = []
        self.obs_this_season_num = None
        self.obs_prev_season = []
        self.obs_prev_season_num = None
        self.obs_two_seasons_ago = []
        self.obs_two_seasons_ago_num = None

        self.numbs_this_season = None
        self.numbs_prev_season = None
        self.numbs_two_seasons_ago = None

    def add_regs_this_season(self, o):
        self.regs_this_season.append(o)
        self.regs_this_season_num = len(self.regs_this_season)
        self._update_numbs()

    def add_regs_prev_season(self, o):
        self.regs_prev_season.append(o)
        self.regs_prev_season_num = len(self.regs_prev_season)
        self._update_numbs()

    def add_regs_two_seasons_ago(self, o):
        self.regs_two_seasons_ago.append(o)
        self.regs_two_seasons_ago_num = len(self.regs_two_seasons_ago)
        self._update_numbs()

    def add_obs_this_season(self, o):
        self.obs_this_season.append(o)
        self.obs_this_season_num = len(self.obs_this_season)
        self._update_numbs()

    def add_obs_prev_season(self, o):
        self.obs_prev_season.append(o)
        self.obs_prev_season_num = len(self.obs_prev_season)
        self._update_numbs()

    def add_obs_two_seasons_ago(self, o):
        self.obs_two_seasons_ago.append(o)
        self.obs_two_seasons_ago_num = len(self.obs_two_seasons_ago)
        self._update_numbs()

    def _set_date_as_string(self):
        """Make a sting variant of the date."""

        if self.month == 1:
            month = 'Jan'
        elif self.month == 2:
            month = 'Feb'
        elif self.month == 3:
            month = 'Mar'
        elif self.month == 4:
            month = 'Apr'
        elif self.month == 5:
            month = 'May'
        elif self.month == 6:
            month = 'Jun'
        elif self.month == 7:
            month = 'Jul'
        elif self.month == 8:
            month = 'Aug'
        elif self.month == 9:
            month = 'Sep'
        elif self.month == 10:
            month = 'Oct'
        elif self.month == 11:
            month = 'Nov'
        elif self.month == 12:
            month = 'Dec'
        else:
            month = 'Unknown'

        if self.day == 1:
            day = '1st'
        elif self.day == 2:
            day = '2nd'
        elif self.day == 3:
            day = '3rd'
        else:
            day = '{}st'.format(self.day)

        self.date_as_string = '{} {}'.format(day, month)

    def _update_numbs(self):
        if self.obs_this_season_num and self.regs_this_season_num:
            if self.regs_this_season_num > 0:
                self.numbs_this_season = self.obs_this_season_num / self.regs_this_season_num
            else:
                self.numbs_this_season = 0

        if self.obs_prev_season_num and self.regs_prev_season_num:
            if self.regs_prev_season_num > 0:
                self.numbs_prev_season = self.obs_prev_season_num / self.regs_prev_season_num
            else:
                self.numbs_prev_season = 0

        if self.obs_two_seasons_ago_num and self.regs_two_seasons_ago_num:
            if self.regs_two_seasons_ago_num > 0:
                self.numbs_two_seasons_ago = self.obs_two_seasons_ago_num / self.regs_two_seasons_ago_num
            else:
                self.numbs_two_seasons_ago = 0


def plot_numbers_of_3_seasons(output_folder=env.plot_folder+'regobsplots/'):
    """Plots the last tree seasons of regObs data to 4 subplots the daily total of observations,
    forms, forms pr observation and the seasonal total.

    :param output_folder:
    :return:
    """

    # Get data
    all_obs_201819_list = gvp.get_all_observations('2018-19', output='FlatList', max_file_age=23)
    all_obs_201819_nest = gvp.get_all_observations('2018-19', output='List', max_file_age=23)
    all_obs_201718_list = gvp.get_all_observations('2017-18', output='FlatList')
    all_obs_201718_nest = gvp.get_all_observations('2017-18', output='List')
    all_obs_201617_list = gvp.get_all_observations('2016-17', output='FlatList')
    all_obs_201617_nest = gvp.get_all_observations('2016-17', output='List')

    # Make dict with all dates and a empty DailyNumbers object
    all_year = {}
    for m in [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]:
        if m in [1, 3, 5, 7, 8, 10, 12]:
            for d in range(1, 32, 1):
                all_year[_str(m) + _str(d)] = DailyNumbers(m, d)
        if m in [4, 6, 9, 11]:
            for d in range(1, 31, 1):
                all_year[_str(m) + _str(d)] = DailyNumbers(m, d)
        if m in [2]:
            for d in range(1, 30, 1):
                all_year[_str(m) + _str(d)] = DailyNumbers(m, d)

    # Add data to the DailyNumbers
    for o in all_obs_201819_list:
        all_year[_str(o.DtObsTime.month) + _str(o.DtObsTime.day)].add_obs_this_season(o)

    for o in all_obs_201819_nest:
        all_year[_str(o.DtObsTime.month) + _str(o.DtObsTime.day)].add_regs_this_season(o)

    for o in all_obs_201718_list:
        all_year[_str(o.DtObsTime.month) + _str(o.DtObsTime.day)].add_obs_prev_season(o)

    for o in all_obs_201718_nest:
        all_year[_str(o.DtObsTime.month) + _str(o.DtObsTime.day)].add_regs_prev_season(o)

    for o in all_obs_201617_list:
        all_year[_str(o.DtObsTime.month) + _str(o.DtObsTime.day)].add_obs_two_seasons_ago(o)

    for o in all_obs_201617_nest:
        all_year[_str(o.DtObsTime.month) + _str(o.DtObsTime.day)].add_regs_two_seasons_ago(o)

    obs_this_season, obs_this_season_smooth = _smooth([v.obs_this_season_num for k, v in all_year.items()], crop_for_season=True)
    regs_this_season, regs_this_season_smooth = _smooth([v.regs_this_season_num for k, v in all_year.items()], crop_for_season=True)
    numbs_this_season, numbs_this_season_smooth = _smooth([v.numbs_this_season for k, v in all_year.items()], crop_for_season=True)

    obs_prev_season, obs_prev_season_smooth = _smooth([v.obs_prev_season_num for k, v in all_year.items()])
    regs_prev_season, regs_prev_season_smooth = _smooth([v.regs_prev_season_num for k, v in all_year.items()])
    numbs_prev_season, numbs_prev_season_smooth = _smooth([v.numbs_prev_season for k, v in all_year.items()])

    obs_two_seasons_ago, obs_two_seasons_ago_smooth = _smooth([v.obs_two_seasons_ago_num for k, v in all_year.items()])
    regs_two_seasons_ago, regs_two_seasons_ago_smooth = _smooth([v.regs_two_seasons_ago_num for k, v in all_year.items()])
    numbs_two_seasons_ago, numbs_two_seasons_ago_smooth = _smooth([v.numbs_two_seasons_ago for k, v in all_year.items()])

    sum_obs_this_season = _sum_list(obs_this_season)
    sum_obs_prev_season = _sum_list(obs_prev_season)
    sum_obs_two_seasons_ago = _sum_list(obs_two_seasons_ago)

    # Turn off interactive mode
    plt.ioff()

    plt.figure(figsize=(15, 23))
    plt.clf()

    # Make legend
    legend_handles = []
    legend_handles.append(mpatches.Patch(color='0.2', label="2018-19"))
    legend_handles.append(mpatches.Patch(color='blue', label="2017-18"))
    legend_handles.append(mpatches.Patch(color='red', label="2016-17"))

    # x-axis labels
    axis_dates, axis_positions = [], []
    i = -1
    for k, v in all_year.items():
        i += 1
        if v.day == 1:
            axis_dates.append(v.date_as_string)
            axis_positions.append(i)

    # Make plots
    plt.subplot2grid((4, 1), (0, 0), rowspan=1)
    plt.title("Antall skjema daglig")
    plt.plot(obs_this_season, color='0.1', linewidth=0.2)
    plt.plot(obs_this_season_smooth, color='0.1')
    plt.plot(obs_prev_season, color='blue', linewidth=0.2)
    plt.plot(obs_prev_season_smooth, color='blue')
    plt.plot(obs_two_seasons_ago, color='red', linewidth=0.2)
    plt.plot(obs_two_seasons_ago_smooth, color='red')
    plt.legend(handles=legend_handles)
    plt.xticks(axis_positions, axis_dates)

    plt.subplot2grid((4, 1), (1, 0), rowspan=1)
    plt.title("Antall observasjoner daglig")
    plt.plot(regs_this_season, color='0.1', linewidth=0.2)
    plt.plot(regs_this_season_smooth, color='0.1')
    plt.plot(regs_prev_season, color='blue', linewidth=0.2)
    plt.plot(regs_prev_season_smooth, color='blue')
    plt.plot(regs_two_seasons_ago, color='red', linewidth=0.2)
    plt.plot(regs_two_seasons_ago_smooth, color='red')
    plt.legend(handles=legend_handles)
    plt.xticks(axis_positions, axis_dates)

    plt.subplot2grid((4, 1), (2, 0), rowspan=1)
    plt.title("Antall skjema pr observasjon daglig")
    plt.plot(numbs_this_season, color='0.1', linewidth=0.2)
    plt.plot(numbs_this_season_smooth, color='0.1')
    plt.plot(numbs_prev_season, color='blue', linewidth=0.2)
    plt.plot(numbs_prev_season_smooth, color='blue')
    plt.plot(numbs_two_seasons_ago, color='red', linewidth=0.2)
    plt.plot(numbs_two_seasons_ago_smooth, color='red')
    plt.legend(handles=legend_handles)
    plt.xticks(axis_positions, axis_dates)

    plt.subplot2grid((4, 1), (3, 0), rowspan=1)
    plt.title("Sesong sum av leverte skjema")
    plt.plot(sum_obs_this_season, color='0.1')
    plt.plot(sum_obs_prev_season, color='blue')
    plt.plot(sum_obs_two_seasons_ago, color='red')
    plt.legend(handles=legend_handles)
    plt.xticks(axis_positions, axis_dates)

    plt.gcf().text(0.78, 0.06, 'Figur laget {0:%Y-%m-%d %H:%M}'.format(dt.datetime.now()), color='0.5')
    # plt.grid(color='0.6', linestyle='--', linewidth=0.7, zorder=0)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.savefig('{}numbersof3seasons.png'.format(output_folder))
    plt.close()


def _region_by_region_type(all_forecasts):
    """Pick out all regions represented in all_forecasts.
    Order by region_type (A regions first) and descending region_id."""

    regions_and_type_dict = {}
    for f in all_forecasts:
        if f.region_type_name not in regions_and_type_dict.keys():
            regions_and_type_dict[f.region_type_name] = [f.region_id]
        else:
            if f.region_id not in regions_and_type_dict[f.region_type_name]:
                regions_and_type_dict[f.region_type_name].append(f.region_id)

    regions_sorted_list = []
    for region_type_name in ['A', 'B', 'C']:
        if region_type_name in regions_and_type_dict.keys():
            regions_sorted_list += sorted(regions_and_type_dict[region_type_name])

    return regions_sorted_list


def _axis_date_labels_from_year(year):
    """For a season (year) get lables for the first day in the month and positions on x axis."""
    axis_dates = []
    axis_positions = []
    from_date, to_date = gm.get_forecast_dates(year)

    for i in range(0, (to_date - from_date).days + 1, 1):
        date = from_date + dt.timedelta(days=i)
        if date.day == 1:
            axis_dates.append(date.strftime("%b %Y"))
            axis_positions.append(i)

    return axis_dates, axis_positions


class DangerLevelPixel:

    def __init__(self, f, regions_sorted_list):

        self.region_name = f.region_name
        self.region_id = f.region_id
        self.date = f.date_valid
        self.danger_level = f.danger_level

        self.colour = self.set_colour_from_danger_level()
        self.x = self.set_x_from_date()
        self.y = self.set_y_from_region(regions_sorted_list)

    def set_colour_from_danger_level(self):
        if self.danger_level == 1:
            return '#ccff66'
        if self.danger_level == 2:
            return '#ffff00'
        if self.danger_level == 3:
            return '#ff9900'
        if self.danger_level == 4:
            return '#ff0000'
        if self.danger_level == 5:
            return 'k'
        if self.danger_level == 0:
            return '0.5'

    def set_x_from_date(self):
        current_season = gm.get_season_from_date(self.date)
        from_date, to_date = gm.get_forecast_dates(current_season)
        x = (self.date - from_date).days
        return x

    def set_y_from_region(self, regions_sorted_list):
        y = regions_sorted_list.index(self.region_id)
        return y


def plot_seasons_forecasted_danger_level(year='2018-19', output_folder=env.plot_folder+'regobsplots/'):
    """All forecasted danger levels for all regions are plotted in one figure.

    :param year:                [string]    Season as eg '2018-19'
    :param output_folder:       [string]    Full path.
    :return:
    """

    file_name = 'All danger levels {0}'.format(year)
    all_forecasts = gvp.get_all_forecasts(year=year)
    regions_sorted_list = _region_by_region_type(all_forecasts)

    # dlp is for DangerLevelPixel. This list contains positions and colours of all pixels in the plot.
    list_of_dlp = [DangerLevelPixel(f, regions_sorted_list) for f in all_forecasts]

    # Start plotting
    fsize = (16, 7)
    fig, ax = plt.subplots(1, 1, figsize=fsize)

    # Left y-axis labels
    region_names_sorted_list = [gm.get_forecast_region_name(i) for i in regions_sorted_list]
    plt.ylim(len(regions_sorted_list)-1, -1)
    plt.yticks(range(len(regions_sorted_list)+1), region_names_sorted_list)

    # x-axis labels
    axis_dates, axis_positions = _axis_date_labels_from_year(year)
    plt.xticks(axis_positions, axis_dates)

    # plot lines and left and bottom ticks
    for dlp in list_of_dlp:
        plt.hlines(dlp.y, dlp.x, dlp.x + 1.2, lw=15, color=dlp.colour)

    plt.grid(True, ls='--', lw=.5, c='k', alpha=.3)             # add grid lines
    ax.tick_params(axis=u'both', which=u'both', length=0)       # turn off ticks
    ax.spines['top'].set_visible(False)                         # turn off black frame in plot
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    title = 'Alle faregrader varslet sesongen {0}'.format(year)
    plt.title(title)

    plt.gcf().text(0.77, 0.02, 'Figur laget {0:%Y-%m-%d %H:%M}'.format(dt.datetime.now()), color='0.5')

    # This saves the figure to file
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.savefig(u'{0}{1}'.format(output_folder, file_name))
    plt.close(fig)

    pass


class AvalancheProblemPixel:

    def __init__(self, f, regions_sorted_list, sort_by_avalanche_problem_type_id):

        self.region_name = f.region_name
        self.region_id = f.region_id
        self.date = f.date_valid
        self.avalanche_problems = f.avalanche_problems
        self.sort_by_avalanche_problem_type_id = sort_by_avalanche_problem_type_id

        self.colour, self.alpha = None, None
        self.set_colour_from_avalanche_problem()
        self.x = self.set_x_from_date()
        self.y = self.set_y_from_region(regions_sorted_list)

    def set_colour_from_avalanche_problem(self):
        """All colors in the avalanche problem plots are controlled by the class. Opacity (alpha) is
        defined according to the ranking of the avalanche problem (main, second or third)."""

        _alpha_no_problem = 0
        _alpha_main_problem = 1
        _alpha_second_problem = 0.6
        _alpha_third_problem = 0.4

        self.colour, self.alpha = 'white', _alpha_no_problem

        # If no problems in forecast, emphasize with orange colour
        # if len(self.avalanche_problems) == 0:
        #     self.colour, self.alpha = 'orange', _alpha_main_problem

        for ap in self.avalanche_problems:
            if ap.avalanche_problem_type_id in self.sort_by_avalanche_problem_type_id:

                if ap.avalanche_problem_type_id == 30:              # persistent weak layer
                    if ap.avalanche_problem_id == 1:
                        self.colour, self.alpha = 'k', _alpha_main_problem
                    if ap.avalanche_problem_id == 2 and self.alpha < _alpha_second_problem:
                        self.colour, self.alpha = 'k', _alpha_second_problem  # only add if no problem or lesser problem in pixel
                    if ap.avalanche_problem_id == 3 and self.alpha < _alpha_third_problem:
                        self.colour, self.alpha = 'k', _alpha_third_problem

                elif ap.avalanche_problem_type_id in [3, 7]:        # New snow problems (loose and soft slabs)
                    if ap.avalanche_problem_id == 1:
                        self.colour, self.alpha = 'blue', _alpha_main_problem
                    if ap.avalanche_problem_id == 2 and self.alpha < _alpha_second_problem:
                        self.colour, self.alpha = 'blue', _alpha_second_problem
                    if ap.avalanche_problem_id == 3 and self.alpha < _alpha_third_problem:
                        self.colour, self.alpha = 'blue', _alpha_third_problem

                elif ap.avalanche_problem_type_id in [5, 45]:       # wet snow problems (loose and slabs)
                    if ap.avalanche_problem_id == 1:
                        self.colour, self.alpha = 'red', _alpha_main_problem
                    if ap.avalanche_problem_id == 2 and self.alpha < _alpha_second_problem:
                        self.colour, self.alpha = 'red', _alpha_second_problem
                    if ap.avalanche_problem_id == 3 and self.alpha < _alpha_third_problem:
                        self.colour, self.alpha = 'red', _alpha_third_problem

                elif ap.avalanche_problem_type_id in [10]:          # wind slabs
                    if ap.avalanche_problem_id == 1:
                        self.colour, self.alpha = 'green', _alpha_main_problem
                    if ap.avalanche_problem_id == 2 and self.alpha < _alpha_second_problem:
                        self.colour, self.alpha = 'green', _alpha_second_problem
                    if ap.avalanche_problem_id == 3 and self.alpha < _alpha_third_problem:
                        self.colour, self.alpha = 'green', _alpha_third_problem

                else:
                    if ap.avalanche_problem_id == 1:
                        self.colour, self.alpha = 'pink', _alpha_main_problem
                    if ap.avalanche_problem_id == 2 and self.alpha < _alpha_second_problem:
                        self.colour, self.alpha = 'pink', _alpha_second_problem
                    if ap.avalanche_problem_id == 3 and self.alpha < _alpha_third_problem:
                        self.colour, self.alpha = 'pink', _alpha_third_problem

    def set_x_from_date(self):
        current_season = gm.get_season_from_date(self.date)
        from_date, to_date = gm.get_forecast_dates(current_season)
        x = (self.date - from_date).days
        return x

    def set_y_from_region(self, regions_sorted_list):
        y = regions_sorted_list.index(self.region_id)
        return y


def plot_seasons_avalanche_problems(year='2018-19', output_folder=env.plot_folder+'regobsplots/'):
    """All forecasted avalanche problems for alle regions are plotted in one figure. This method
    makes 5 separate plots for each of the general types of avalanche problems.

    :param year:                [string]    Season as eg '2018-19'
    :param output_folder:       [string]    Full path.
    :return:
    """

    file_name_prefix = 'All new snow problems'
    title_prefix = 'Nysnø problemer (løse og flak) varslet sesongen'
    problem_ids = [3, 7]
    _plot_seasons_avalanche_problems(year, file_name_prefix, problem_ids, title_prefix, output_folder)

    file_name_prefix = 'All persistent weak layers'
    title_prefix = 'Alle vedvarende svake lag varslet sesongen'
    problem_ids = [30]
    _plot_seasons_avalanche_problems(year, file_name_prefix, problem_ids, title_prefix, output_folder)

    file_name_prefix = 'All wet snow problems'
    title_prefix = 'Våte skredproblemer (løse og flak) varslet sesongen'
    problem_ids = [5, 45]
    _plot_seasons_avalanche_problems(year, file_name_prefix, problem_ids, title_prefix, output_folder)

    file_name_prefix = 'All wind slab problems'
    title_prefix = 'Fokksnø problemer varslet sesongen'
    problem_ids = [10]
    _plot_seasons_avalanche_problems(year, file_name_prefix, problem_ids, title_prefix, output_folder)

    file_name_prefix = 'All glide avalanche problems'
    title_prefix = 'Glideskred varslet sesongen'
    problem_ids = [50]
    _plot_seasons_avalanche_problems(year, file_name_prefix, problem_ids, title_prefix, output_folder)


def _plot_seasons_avalanche_problems(year, file_name_prefix, problem_ids, title_prefix, output_folder):
    """Supporting method for plotting one or more avalanche problems for all regions for one season.

    :param year:                [string]    Season as eg '2018-19'
    :param file_name_prefix:    [string]    File name. Year is added to string.
    :param problem_ids:         [list of int] One or more avalanche problem type id's as list.
    :param title_prefix:        [string]    title in figure. Year is added to the string.
    :param output_folder:       [string]    Full path.
    :return:
    """

    file_name = '{0} {1}'.format(file_name_prefix, year)
    all_forecasts = gvp.get_all_forecasts(year=year)

    regions_sorted_list = _region_by_region_type(all_forecasts)

    # app is for avalanche problem pixel. This list contains positions and colours of all pixels in the plot.
    list_of_app = [AvalancheProblemPixel(f, regions_sorted_list, problem_ids) for f in all_forecasts]

    # Start plotting
    fsize = (16, 7)
    fig, ax = plt.subplots(1, 1, figsize=fsize)

    # Left y-axis labels
    region_names_sorted_list = [gm.get_forecast_region_name(i) for i in regions_sorted_list]
    plt.ylim(len(regions_sorted_list)-1, -1)
    plt.yticks(range(len(regions_sorted_list)+1), region_names_sorted_list)

    # x-axis labels
    axis_dates, axis_positions = _axis_date_labels_from_year(year)
    plt.xticks(axis_positions, axis_dates)

    # plot lines and left and bottom ticks
    for app in list_of_app:
        plt.hlines(app.y, app.x, app.x + 1.2, lw=15, color=app.colour, alpha=app.alpha)

    plt.grid(True, ls='--', lw=.5, c='k', alpha=.3)             # add grid lines
    ax.tick_params(axis=u'both', which=u'both', length=0)       # turn off ticks
    ax.spines['top'].set_visible(False)                         # turn off black frame in plot
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    title = '{0} {1}'.format(title_prefix, year)
    plt.title(title)

    # When is the figure made?
    plt.gcf().text(0.77, 0.02, 'Figur laget {0:%Y-%m-%d %H:%M}'.format(dt.datetime.now()), color='0.5')

    # This saves the figure to file
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.savefig(u'{0}{1}'.format(output_folder, file_name))
    plt.close(fig)


class MonthlyNumbers:
    """
    Pr month:
    * list num pr geohazard
    * obskorps
    * svv, vegvesen, met, forsvaret, jbv, nve, naturopsynet,
    * andre
    """

    def __init__(self, year, month):

        self.month = month
        self.year = year
        self.all_obs = []

    def add_to_all_obs(self, o):

        self.all_obs.append(o)


def table_regs_obs_numbs():
    """

    :return:

    pr month:
    list of different forms
    snow: obskorps, svv, elrapp, other_gov, voluntary
    ice: NVE, fjelloppsynet, voluntary, webcam images
    water and dirt: NVE, elrapp, other_gov, voluntary
    *, **, ***, ****, *****

    """

    all_obs_201718_list = gvp.get_all_observations('2017-18', output='FlatList', max_file_age=230)
    all_obs_201718_nest = gvp.get_all_observations('2017-18', output='List', max_file_age=230)

    monthly_numbs = {}

    for o in all_obs_201718_nest:
        month = '{}{}'.format(_str(o.DtObsTime.year), _str(o.DtObsTime.month))
        if month not in monthly_numbs.keys():
            monthly_numbs[month] = MonthlyNumbers(o.DtObsTime.year, o.DtObsTime.month)
        else:
            monthly_numbs[month].add_to_all_obs(o)

    pass


if __name__ == '__main__':

    # plot_regs_obs_numbs()
    # table_regs_obs_numbs()
    # plot_numbers_of_3_seasons()
    # plot_seasons_forecasted_danger_level()
    # plot_seasons_avalanche_problems()
    plot_seasons_forecasted_danger_level(year='2017-18')
    plot_seasons_avalanche_problems(year='2017-18')
    plot_seasons_forecasted_danger_level(year='2016-17')
    plot_seasons_avalanche_problems(year='2016-17')

    pass
