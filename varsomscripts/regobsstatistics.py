# -*- coding: utf-8 -*-
"""Module for calculating and plotting overall performance of regObs."""

import setenvironment as env
from varsomdata import getvarsompickles as gvp
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

    def none_to_zero(self):
        # method not used

        self.regs_this_season_num = None
        self.obs_this_season_num = None
        # self.numbs_this_season = None

        if self.regs_prev_season_num is None:
            self.regs_prev_season_num = 0
        if self.obs_prev_season_num is None:
            self.obs_prev_season_num = 0
        # self.numbs_prev_season = None

        if self.regs_two_seasons_ago_num is None:
            self.regs_two_seasons_ago_num = 0
        if self.obs_two_seasons_ago_num is None:
            self.obs_two_seasons_ago_num = 0
        # self.numbs_two_seasons_ago = None


def plot_numbers_of_3_seasons(output_folder=env.plot_folder+'regobsplots/'):
    """Plots the last tree seasons of regObs data to 4 subplots the daily total of observations,
    forms, forms pr observation and the seasonal total.

    :param output_folder:
    :return:

    TODO: get the x-axis right
    """

    # Get data
    all_obs_201819_list = gvp.get_all_observations('2018-19', output='List', max_file_age=23)
    all_obs_201819_nest = gvp.get_all_observations('2018-19', output='Nest', max_file_age=23)
    all_obs_201718_list = gvp.get_all_observations('2017-18', output='List')
    all_obs_201718_nest = gvp.get_all_observations('2017-18', output='Nest')
    all_obs_201617_list = gvp.get_all_observations('2016-17', output='List')
    all_obs_201617_nest = gvp.get_all_observations('2016-17', output='Nest')

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

    plt.subplot2grid((4, 1), (1, 0), rowspan=1)
    plt.title("Antall observasjoner daglig")
    plt.plot(regs_this_season, color='0.1', linewidth=0.2)
    plt.plot(regs_this_season_smooth, color='0.1')
    plt.plot(regs_prev_season, color='blue', linewidth=0.2)
    plt.plot(regs_prev_season_smooth, color='blue')
    plt.plot(regs_two_seasons_ago, color='red', linewidth=0.2)
    plt.plot(regs_two_seasons_ago_smooth, color='red')
    plt.legend(handles=legend_handles)

    plt.subplot2grid((4, 1), (2, 0), rowspan=1)
    plt.title("Antall skjema pr observasjon daglig")
    plt.plot(numbs_this_season, color='0.1', linewidth=0.2)
    plt.plot(numbs_this_season_smooth, color='0.1')
    plt.plot(numbs_prev_season, color='blue', linewidth=0.2)
    plt.plot(numbs_prev_season_smooth, color='blue')
    plt.plot(numbs_two_seasons_ago, color='red', linewidth=0.2)
    plt.plot(numbs_two_seasons_ago_smooth, color='red')
    plt.legend(handles=legend_handles)

    plt.subplot2grid((4, 1), (3, 0), rowspan=1)
    plt.title("Sesong sum av leverte skjema")
    plt.plot(sum_obs_this_season, color='0.1')
    plt.plot(sum_obs_prev_season, color='blue')
    plt.plot(sum_obs_two_seasons_ago, color='red')
    plt.legend(handles=legend_handles)

    plt.gcf().text(0.78, 0.06, 'Figur laget {0:%Y-%m-%d %H:%M}'.format(dt.datetime.now()), color='0.5')
    # plt.grid(color='0.6', linestyle='--', linewidth=0.7, zorder=0)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.savefig('{}numbersof3seasons.png'.format(output_folder))
    plt.close()


class MonthlyNumbers:
    """
    pr month
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
    snow: obskorps, svv, elrapp, other_gov, voluntary
    ice: NVE, fjelloppsynet, voluntary, webcam images
    water and dirt: NVE, elrapp, other_gov, voluntary
    *, **, ***, ****, *****

    """

    all_obs_201718_list = gvp.get_all_observations('2017-18', output='List', max_file_age=230)
    all_obs_201718_nest = gvp.get_all_observations('2017-18', output='Nest', max_file_age=230)

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
    plot_numbers_of_3_seasons()
