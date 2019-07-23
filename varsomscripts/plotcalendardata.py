# -*- coding: utf-8 -*-
"""
The code for downloading and making the plots on ragnar.pythonanywhere.com/observerdata/ etc.

Modifications:
2019-07-12, Ragnar: Api4 support.
"""

import datetime as dt
import matplotlib as mpl
import pylab as plb
import collections as col
import calendar as cal
from varsomdata import getvarsompickles as gvp
from varsomdata import getkdvelements as gkdv
from varsomdata import getmisc as gm
from utilities import makepickle as mp
import logging as lg
import setenvironment as env
import os as os

__author__ = 'raek'


class DayData:
    """Class handles all data for plotting observations in a certain day in calender plots."""

    def __init__(self, date):

        self.observer_id = None
        self.region_id = None

        self.box_size_x = None
        self.box_size_y = None
        self.cell_colour = None
        self.set_properties()

        self.date = date
        self.week_no = date.isocalendar()[1]
        # if in january use week 0 instead of week 53
        if date.month == 1 and self.week_no > 50:
            self.week_no = 0

        self.week_day = date.isocalendar()[2]
        self.observations = col.Counter()
        self.number_obs = None
        self.reg_ids = col.Counter()
        self.nick_names = col.Counter()

        self.obs_pr_regid = {}          # which registration names (observations) have been used tis day?
        self.loc_pr_regid = {}          # which forecast regions have been used this day?
        self.nic_pr_regid = {}          # which nicknames (observers) have contributed this day?

        self.pictures_count = None      # number of pictures submitted with the observed forms.

        self.x = None
        self.y = None
        self.set_x()                    # x and y positions in plot set based on date
        self.set_y()

    def set_region_id(self, region_id_inn):
        self.region_id = region_id_inn

    def set_observer_id(self, observer_id_inn):
        self.observer_id = observer_id_inn

    def set_properties(self):
        self.box_size_x = 100
        self.box_size_y = 100
        self.cell_colour = 'white'

    def add_observations(self, observations):
        self.observations = col.Counter(observations)
        self.number_obs = sum(self.observations.values())
        if self.number_obs > 0:
            self.cell_colour = 'gainsboro'

    def add_regids(self, reg_ids):
        self.reg_ids = col.Counter(reg_ids)

    def add_nicks(self, nicks):
        self.nick_names = col.Counter(nicks)

    def add_pictures_count(self, pictures_count_inn):
        self.pictures_count = pictures_count_inn

    def add_obs_pr_regid(self, obs_pr_regid):
        self.obs_pr_regid = obs_pr_regid

    def add_loc_pr_regid(self, loc_pr_regid):
        self.loc_pr_regid = loc_pr_regid

    def add_nic_pr_regid(self, nic_pr_regid):
        self.nic_pr_regid = nic_pr_regid

    def set_x(self):
        self.x = self.week_day * 100

    def set_y(self):
        year = self.date.year
        month = self.date.month
        first, last = cal.monthrange(year, month)

        first_week = dt.date(year, month, 1).isocalendar()[1]
        # make sure to get last week of previous year if needed
        if month == 1 and first != 1:
            first_week = 0

        # make sure to get the last week if is is in the new year
        if month == 12 and self.week_no == 1:
            self.week_no = 53

        self.y = -100 * (self.week_no - first_week)

    def get_obs_pos(self, obs_type):
        if obs_type == 'Faretegn':
            return 38, 86, 'tomato', 'k'
        elif 'kredaktivitet' in obs_type:
            return 62, 86, 'tomato', 'k'
        elif obs_type == 'Skredhendelse':
            return 86, 86, 'orange', 'k'
        elif obs_type == 'Ulykke/hendelse':
            return 86, 62, 'orange', 'k'
        elif obs_type == 'Snødekke':
            return 86, 38, 'lightskyblue', 'k'
        elif obs_type == 'Vær':
            return 86, 14, 'lightskyblue', 'k'
        elif 'Snøprofil' in obs_type:
            return 62, 14, 'white', 'k'
        elif obs_type == 'Tester':
            return 38, 14, 'white', 'k'
        elif obs_type == 'Skredproblem':
            return 14, 14, 'pink', 'k'
        elif obs_type == 'Skredfarevurdering':
            return 14, 38, 'pink', 'k'
        elif obs_type == 'Bilde':
            return 6, 54, 'gray', 'k'
        elif obs_type == 'Notater':
            return 38, 62, 'yellow', 'k'
        else:
            lg.warning("plotcalendardata.py -> DayData.get_obs_pos: Unknown obs_type: {}".format(obs_type))
            return 0, 0, 'k', 'k'


class ObserverData:

    def __init__(self, observer_id_inn, observer_nick_inn, observation_count_inn=0):
        self.observer_id = observer_id_inn
        self.observer_nick = observer_nick_inn
        self.observation_count = observation_count_inn
        self.competence_level_tid = None
        self.competence_level_name = None

    def set_competence_level(self, competence_level_tid_inn, competence_level_name_inn):
        self.competence_level_name = competence_level_name_inn
        self.competence_level_tid = competence_level_tid_inn

    def add_one_observation_count(self):
        self.observation_count += 1


def _get_dates(start, end, delta):
    """Yields all dates in a date interval from - to."""

    curr = start
    while curr < end:
        yield curr
        curr += delta


def _make_plot(dates, observer_name=None, region_name=None, file_ext='.png', data_description=None, plot_folder=env.plot_folder):
    """If it is a custom data set region_name should be provided because it will be plotted by region.
    observer_name and region_name determines the main grouping of data. They should not be provided both.

    :param dates:
    :param observer_name:
    :param region_name:
    :param file_ext:
    :param data_description:    Custom description for naming plot-files
    :param plot_folder:         Folder for saving the plots.
    :return:
    """

    if data_description is not None:
        if 'svv_i_' in data_description:
            folder = plot_folder + 'svvplots/'
        else:
            folder = plot_folder

        if not os.path.exists(folder):
            os.makedirs(folder)

        plot_file_name = '{0}{1}_{2}{3:02d}'.format(folder, data_description, dates[0].date.year, dates[0].date.month)

    else:
        if region_name is not None:
            folder = plot_folder + 'regionplots/'
            if not os.path.exists(folder):
                os.makedirs(folder)
            plot_file_name = '{0}{1}_regiondata_{2}{3:02d}'.format(folder, region_name, dates[0].date.year, dates[0].date.month)

        else:
            if observer_name is not None:
                folder = plot_folder + 'observerplots/'
                if not os.path.exists(folder):
                    os.makedirs(folder)
                plot_file_name = '{0}observerdata_{1}_{2}{3:02d}'.format(folder, dates[0].observer_id, dates[0].date.year, dates[0].date.month)

            else:
                lg.warning("plotcalendardata.py -> _make_plot: Need ObserverID and/or forecastRegionTID to make this work.")
                plot_file_name = 'no_good_plot'

    # Figure dimensions
    fsize = (18, 13)
    fig = plb.figure(figsize=fsize)
    # plb.clf()
    ax = fig.add_subplot(111)
    plb.subplots_adjust(top=0.95, bottom=0.15, left=0.02, right=0.98)

    # plot all boxes pr date
    for d in dates:
        x = int(d.x)-d.box_size_x
        y = int(d.y)-d.box_size_y
        rect = mpl.patches.Rectangle((x, y), d.box_size_x, d.box_size_y, facecolor=d.cell_colour)
        ax.add_patch(rect)

        # The date in top left corner
        plb.text(x+6, y+84, '{0}'.format(d.date.day), fontsize=20)

        # plot circles with individual observation count
        for k, v in d.observations.items():
            relative_x, relative_y, obs_colour, obs_edge = d.get_obs_pos(k)
            circ = mpl.patches.Circle((x+relative_x, y+relative_y), d.box_size_x/11, facecolor=obs_colour, edgecolor=obs_edge)
            ax.add_patch(circ)
            plb.text(x+relative_x-2, y+relative_y-2, '{0}'.format(v))

        if d.pictures_count > 0:
            relative_x, relative_y, obs_colour, obs_edge = d.get_obs_pos('Bilde')
            rect = mpl.patches.Rectangle((x+relative_x, y+relative_y), d.box_size_x/6, d.box_size_x/6, facecolor=obs_colour, edgecolor=obs_edge)
            ax.add_patch(rect)
            plb.text(x+relative_x+5, y+relative_y+5, '{0}'.format(d.pictures_count))

        if observer_name is not None:
            # List all regids
            reg_id_string = ''
            for k, v in d.reg_ids.items():
                reg_id_string += '{0}: {1}\n'.format(k, v)
            plb.text(x+45, y+60-len(d.reg_ids)*8, reg_id_string)

        if region_name is not None:
            # List all observer nicks
            nick_string = ''
            for k, v in d.nick_names.items():
                nick_string += '{0}: {1}\n'.format(k, v)
            plb.text(x+35, y+60-len(d.nick_names)*8, nick_string)

        # total obs this day
        if d.number_obs > 0:
            plb.text(x+30, y+35, '{0}'.format(d.number_obs), fontsize=25)

    # add week numbers
    year = dates[0].date.year
    month = dates[0].date.month
    first, last = cal.monthrange(year, month)
    first_week = dt.date(year, month, 1).isocalendar()[1]

    # make sure to get last week of previous year if needed
    if month == 1 and first != 1:
        first_week = 0
    last_week = dt.date(year, month, last).isocalendar()[1]

    # make sure to handle if the last week is in the next year
    if month == 12 and last_week == 1:
        last_week = 53

    week_nos = list(range(first_week, last_week+1, 1))

    # and if the last week is 53, it is in fact week 1 of the next year.
    if month == 12 and last_week == 53:
        week_nos[-1] = 1

    index = -100
    for wn in week_nos:
        plb.text(-15, index+60, 'Uke {0}'.format(wn), fontsize=20, rotation=90)
        index -= 100

    # add weekdays
    week_days = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag']
    index = 0
    for wd in week_days:
        plb.text(index+30, 10, '{0}'.format(wd), fontsize=20)
        index += 100

    month_names = {1:'januar',
                   2:'februar',
                   3:'mars',
                   4:'april',
                   5:'mai',
                   6:'juni',
                   7:'juli',
                   8:'august',
                   9:'september',
                   10:'oktober',
                   11:'november',
                   12:'desember'}

    # add title
    if data_description is not None:
        plb.title("Observasjoner i {0} i {1}, {2}".format(data_description, month_names[month], year), fontsize=30)
    else:
        if region_name is not None:
            plb.title("Observasjoner i {0} i {1}, {2}".format(region_name, month_names[month], year), fontsize=30)
        else:
            if observer_name is not None:
                plb.title("Observasjoner av {0} i {1}, {2}".format(observer_name, month_names[month], year), fontsize=30)
            else:
                plb.title("No title - probably an error", fontsize=30)

    plb.xlim(-20, 700)
    plb.ylim(-1 *(len(week_nos) * 100), 50)
    plb.axis('off')
    #fig.tight_layout()

    plb.savefig(plot_file_name+file_ext)
    plb.close()


def _make_html(dates, observer_id=None, region_name=None, data_description=None, html_folder=env.output_folder + 'views/'):
    """Method serves both plots for selected observers or selected regions.

    :param dates:
    :param observer_id:
    :param region_name:         If doing observers: region_name=None else: we are doing regions and this is a region name.
    :param data_description:
    :param html_folder:         Output folder for the html files generated.
    :return:
    """

    if not os.path.exists(html_folder):
        os.makedirs(html_folder)

    if data_description is not None:
        html_file_name = '{0}{1}_{2}{3:02d}.html'.format(html_folder, data_description, dates[0].date.year, dates[0].date.month)
    else:
        if region_name is not None:
            html_file_name = '{0}{1}_regiondata_{2}{3:02d}.html'.format(html_folder, region_name, dates[0].date.year, dates[0].date.month)
        else:
            if observer_id is not None:
                html_file_name = '{0}observerdata_{1}_{2}{3:02d}.html'.format(html_folder, observer_id, dates[0].date.year, dates[0].date.month)
            else:
                lg.warning("plotcalendardata.py -> _make_html: Got to have region and/or observer to make this work.")
                html_file_name = 'no_good_html'

    with open(html_file_name, 'w', encoding='utf-8') as f:

        f.write('<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#tbl{0}{1}">Tabell med observasjoner og lenker til regObs</button>\n'
                '<div id="tbl{0}{1}" class="collapse">\n'.format(dates[0].date.year, dates[0].date.month))
        f.write('</br>\n'
                ''
                '<table class="table table-hover">\n')
        f.write('    <thead>\n'
                '        <tr>\n'
                '            <th>Dato</th>\n'
                '            <th>Registrering</th>\n')
        if observer_id is not None:
            f.write('            <th>Region</th>\n')
        elif region_name is not None:
            f.write('            <th>Observer</th>\n')
        else:
            f.write('            <th>Noe gikk galt</th>\n')
        f.write('            <th>Observasjon</th>\n'
                '        </tr>\n'
                '    </thead>\n'
                '    <tbody>\n')

        for d in dates:
            d_one_time = d.date
            for regid in d.reg_ids.keys():
                if observer_id is not None:
                    thrd_column = d.loc_pr_regid[regid]
                elif region_name is not None:
                    thrd_column = d.nic_pr_regid[regid]
                else:
                    thrd_column = 'No good'
                f.write('        <tr>\n'
                        '            <td>{0}</td>\n'
                        '            <td><a href="http://www.regobs.no/registration/{1}" target="_blank">{1}</a></td>\n'
                        '            <td>{2}</td>\n'
                        '            <td>{3}</td>\n'
                        '        </tr>\n'.format(d_one_time, regid, thrd_column, ', '.join(d.obs_pr_regid[regid])))
                if d_one_time is not '':
                    d_one_time = ''         # date show only once in column 1

        f.write('     </tbody>\n'
                '</table>'
                '</div>')


def _make_day_data_list(region_observations_list, m, frid=None, o=None):
    """Makes a list of all the dates in a month and adds a observers or regions observations (forms) to it.

    :param region_observations_list:
    :param m:       [date] month in question
    :param frid:    [int] forecast region id
    :param o:       [ObserverData] Observer data
    :return:
    """

    month = m.month
    year = m.year
    first, last = cal.monthrange(year, month)
    from_date = dt.date(year, month, 1)
    to_date = dt.date(year, month, last) + dt.timedelta(days=1)

    # for all dates in the requested from-to interval
    dates = []
    for d in _get_dates(from_date, to_date, dt.timedelta(days=1)):

        dd = DayData(d)

        if frid is not None:
            dd.set_region_id(id)
        if o is not None:
            dd.set_observer_id(o.observer_id)
        if frid is None and o is None:
            lg.warning("plotcalendardata.py -> _make_day_data_list: No region id og observer id provided. Unable to make DayData list.")
            return []

        obstyp = []
        regids = []
        nicks = []
        pictures_count = 0
        loc_pr_regid = {}
        obs_pr_regid = {}
        nic_pr_regid = {}

        for ao in region_observations_list:

            # append all observations where dates match
            if ao.DtObsTime.date() == d:

                # location on regid (only one location pr RegID)
                if ao.RegID not in loc_pr_regid.keys():
                    loc_pr_regid[ao.RegID] = ao.ForecastRegionName

                # get the nickname use on the regid (only one pr RegID)
                if ao.RegID not in nic_pr_regid.keys():
                    nic_pr_regid[ao.RegID] = ao.NickName

                # count pictures submitted
                pictures_count += len(ao.Pictures)

                # observations pr regid (might be more)
                observation_name = ao.RegistrationName

                if ao.RegID not in obs_pr_regid.keys():
                    obs_pr_regid[ao.RegID] = [observation_name]
                else:
                    obs_pr_regid[ao.RegID].append(observation_name)

                # list of all observations on this date
                obstyp.append(observation_name)

                # list of all reg ids - this counts occurrences
                regids.append(ao.RegID)

                # list of all observers nick names - this counts occurrences
                nicks.append(ao.NickName)

        # add to object for plotting
        dd.add_loc_pr_regid(loc_pr_regid)
        dd.add_obs_pr_regid(obs_pr_regid)
        dd.add_nic_pr_regid(nic_pr_regid)
        dd.add_pictures_count(pictures_count)
        dd.add_observations(obstyp)
        dd.add_regids(regids)
        dd.add_nicks(nicks)
        dates.append(dd)

    return dates


def make_observer_plots(all_observations_list, observer_list, months, plot_folder=env.plot_folder, html_folder=env.output_folder + 'views/'):
    """
    Method prepares data for plotting and making the corresponding table for the observations for a list of
    observers.

    :param all_observations_list:
    :param observer_list:           [list of ObserverData]
    :param months:
    :param plot_folder:         Folder for saving the plots.
    :param html_folder:         Output folder for the html files generated.
    :return:
    """

    # if not a list, make it so
    if not isinstance(observer_list, list):
        observer_list = [observer_list]

    for o in observer_list:

        lg.info("plotcalendardata.py -> make_observer_plots: {} {}".format(o.observer_id, o.observer_nick))
        observers_observations_list = [all_obs for all_obs in all_observations_list if all_obs.ObserverID == o.observer_id]

        # plot one month at the time
        for m in months:
            dates = _make_day_data_list(observers_observations_list, m, o=o)

            _make_plot(dates, observer_name=o.observer_nick, plot_folder=plot_folder)
            _make_html(dates, observer_id=o.observer_id, html_folder=html_folder)


def make_region_plots(all_observations_list, region_ids, months, plot_folder=env.plot_folder, html_folder=env.output_folder + 'views/'):
    """
    Method prepares data for plotting and making the corresponding table for the observations for one
    region.

    :param all_observations_list:
    :param region_ids:
    :param months:
    :param plot_folder:         Folder for saving the plots.
    :param html_folder:         Output folder for the html files generated.
    :return:
    """

    for frid in region_ids:

        region_observations_list = [all_obs for all_obs in all_observations_list if all_obs.ForecastRegionTID == frid]
        region_name = gkdv.get_name('ForecastRegionKDV', frid)
        lg.info("plotcalendardata.py -> make_region_plots: {} {}".format(frid, region_name))

        # plot one month at the time
        for m in months:
            dates = _make_day_data_list(region_observations_list, m, frid=frid)

            _make_plot(dates, region_name=region_name, plot_folder=plot_folder)
            _make_html(dates, region_name=region_name, html_folder=html_folder)


def make_svv_plots(all_observations_list, observer_dict, region_ids, months, plot_folder=env.plot_folder, html_folder=env.output_folder + 'views/'):
    """

    :param all_observations_list:
    :param observer_dict:
    :param region_ids:
    :param months:
    :param plot_folder:         Folder for saving the plots.
    :param html_folder:         Output folder for the html files generated.
    :return:
    """

    # Make a list of all svv observers.
    # Look for members of groups with names containing 'svv' or 'vegvesen' or
    # look for user nick containing 'svv' or 'vegvesen'
    groups = gm.get_observer_group_member()

    svv_group_ids_dict = {}
    for g in groups:
        if 'svv' in g.ObserverGroupName.lower() or 'vegvesen' in g.ObserverGroupName.lower():
            if g.ObserverGroupName in svv_group_ids_dict.keys():
                svv_group_ids_dict[g.ObserverGroupName].append(g.ObserverID)
            else:
                svv_group_ids_dict[g.ObserverGroupName] = [g.ObserverID]

    observer_ids_list = []
    for k, v in svv_group_ids_dict.items():
        for id in v:
            observer_ids_list.append(id)
    observer_ids_list = list(set(observer_ids_list))        # remove duplicates

    svv_observer_dict = {}
    for k, v in observer_dict.items():
        if k not in [237, 4075, 6696, 6]:    # not elrapp, wyssen-svv, cautus-svv, ragnar
            if 'svv' in v.observer_nick.lower() or 'vegvesen' in v.observer_nick.lower():
                svv_observer_dict[k] = v
            if k in observer_ids_list:
                if k not in svv_observer_dict.keys():
                    svv_observer_dict[k] = v

    svv_observer_ids = list(svv_observer_dict.keys())

    svv_observations_list = [all_obs for all_obs in all_observations_list if all_obs.ObserverID in svv_observer_ids]

    for frid in region_ids:
        region_observations_list = [all_obs for all_obs in svv_observations_list if all_obs.ForecastRegionTID == frid]
        region_name = gkdv.get_name('ForecastRegionKDV', frid)
        data_description = 'svv_i_{0}'.format(region_name)
        lg.info("plotcalendardata.py -> make_svv_plots: {} {}".format(frid, region_name))

        # plot one month at the time
        for m in months:
            dates = _make_day_data_list(region_observations_list, m, frid=frid)
            _make_plot(dates, region_name=region_name, data_description=data_description, plot_folder=plot_folder)
            _make_html(dates, region_name=region_name, data_description=data_description, html_folder=html_folder)


def make_season_calender_plots(year='2018-19', plot_folder=env.plot_folder, html_folder=env.output_folder + 'views/', web_pickle_folder=env.output_folder + 'webpickles/'):
    """Makes observation calender plots for both observer and region for display on web page for the season 2018-19.
    Method includes a request for list of relevant observers."""

    from_year = int(year[0:4])
    to_year = int('20' + year[-2:])

    from_day = dt.date(from_year, 11, 1)
    to_day = dt.date(to_year, 6, 30)

    # if the seasons expected end is after todays date, set it to today.
    if to_day > dt.date.today():
        to_day = dt.date.today()

    # list of months to be plotted
    months = []
    month = from_day

    while month < to_day:
        months.append(month)
        almost_next = month + dt.timedelta(days=35)
        month = dt.date(almost_next.year, almost_next.month, 1)

    # Get all regions
    region_ids = gm.get_forecast_regions(year)

    # get a list of relevant observers to plot and make pickle for adding to the web-folder
    all_observations_nest = gvp.get_all_observations(year, output='List', geohazard_tids=10)
    all_observations_list = gvp.get_all_observations(year, output='FlatList', geohazard_tids=10)

    observer_dict = {}
    for o in all_observations_nest:
        if o.ObserverID in observer_dict.keys():
            observer_dict[o.ObserverID].add_one_observation_count()
        else:
            observer_dict[o.ObserverID] = ObserverData(o.ObserverID, o.NickName, observation_count_inn=1)

    observer_list = []
    observer_list_web = []
    ordered_observer_dict = col.OrderedDict(sorted(observer_dict.items(), key=lambda t: t[1].observation_count, reverse=True))
    for k, v in ordered_observer_dict.items():
        if v.observation_count > 4:
            observer_list.append(ObserverData(v.observer_id, v.observer_nick, observation_count_inn=v.observation_count))
            observer_list_web.append([v.observer_id, v.observer_nick, v.observation_count])

    if not os.path.exists(web_pickle_folder):
        os.makedirs(web_pickle_folder)
    mp.pickle_anything(observer_list_web, '{0}observerlist.pickle'.format(web_pickle_folder))

    # run the stuff
    make_observer_plots(all_observations_list, observer_list, months, plot_folder=plot_folder, html_folder=html_folder)
    make_region_plots(all_observations_list, region_ids, months, plot_folder=plot_folder, html_folder=html_folder)
    make_svv_plots(all_observations_list, observer_dict, region_ids, months, plot_folder=plot_folder, html_folder=html_folder)


if __name__ == "__main__":

    make_season_calender_plots(year='2018-19')

    observer = [ObserverData(325, 'Siggen@obskorps'), ObserverData(10, 'Andreas@nve')]

    all_observations = gvp.get_all_observations('2018-19', output='FlatList', geohazard_tids=10, max_file_age=1000)
    months = [dt.date(2019, 1, 1), dt.date(2019, 2, 1), dt.date(2019, 3, 1), dt.date(2019, 4, 1)]
    make_observer_plots(all_observations, observer, months)

    pass
