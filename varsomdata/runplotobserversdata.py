# -*- coding: utf-8 -*-
__author__ = 'raek'


# external library
import datetime as dt
import matplotlib as mpl
import pylab as plb
import collections as col
import calendar as cal

# Core varsom data
import getdangers as gd
import getobservations as go
import getkdvelements as gkdv
import getmisc as gm
import fencoding as fe

# I/O and environmental stuff
import readfile as rf
import makepickle as mp
import setenvironment as env


class DayData():

    def __init__(self, date, observer_id=None, region_id=None):

        self.observer_id = observer_id
        self.region_id = region_id

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

        self.x = None
        self.y = None
        self.set_x()                    # x and y positions in plot set based on date
        self.set_y()


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
        first, last  = cal.monthrange(year, month)
        first_week = dt.date(year, month, 1).isocalendar()[1]
        # make sure to get last week of previous year if needed
        if month == 1 and first != 1:
            first_week = 0
        last_week = dt.date(year, month, last).isocalendar()[1]

        self.y = -100 * (self.week_no - first_week)


    def get_obs_pos(self, obs_type):

        if obs_type == 'Faretegn':
            return 38, 86, 'tomato', 'k'
        elif 'Observert skredaktivitet' in obs_type:
            return 62, 86, 'tomato', 'k'
        elif obs_type == 'Observert skred':
            return 86, 86, 'orange', 'k'
        elif obs_type == 'Hendelse':
            return 86, 62, 'orange', 'k'
        elif obs_type == 'Snoedekke':
            return 86, 38, 'lightskyblue', 'k'
        elif obs_type == 'Observert vaer':
            return 86, 14, 'lightskyblue', 'k'
        elif obs_type == 'Snoeprofil':
            return 62, 14, 'white', 'k'
        elif obs_type == 'Kompresjonstest':
            return 38, 14, 'white', 'k'
        elif obs_type == 'Skredproblem':
            return 14, 14, 'pink', 'k'
        elif obs_type == 'Skredfarevurdering':
            return 14, 38, 'pink', 'k'
        elif obs_type == 'Bilde':
            return 14, 62, 'yellow', 'k'
        elif obs_type == 'Fritekstfelt':
            return 38, 62, 'yellow', 'k'
        else:
            return 0, 0, 'k', 'k'


def _get_dates(start, end, delta):
    '''Yields all dates in an interval from - to.

    :param start:
    :param end:
    :param delta:
    :return:
    '''

    curr = start
    while curr < end:
        yield curr
        curr += delta


def step1_get_data(year, month, observer_id=None, region_id=None, get_new=True, make_pickle=False, data_description="no_description_given"):
    """Gets data for one month and prepares for plotting

    :param year:                [int]
    :param month:               [int]
    :param observer_id:         [int or list of ints]
    :param region_id            [int]
    :param get_new:             [bool] get data with a new request or use local pickle
    :param make_pickle:         [bool] only matters if getting new data, make a pickle in local storage
    :param data_description     [string] Custom description for naming pickle-files
    :return dates:              [list of DayData objects]

    """

    if data_description is not None:
        pickle_file_name = "{0}{1}_{2}{3:02d}.pickle".format(env.local_storage, data_description, year, month)
    else:
        if region_id is not None:
            pickle_file_name = "{0}runPlotRegionData_{1}_{2}{3:02d}.pickle".format(env.local_storage, region_id, year, month)
        else:
            if observer_id is not None:
                pickle_file_name = "{0}runPlotObserverData_{1}_{2}{3:02d}.pickle".format(env.local_storage, observer_id, year, month)
            else:
                print 'Need Observerid and/or forecastRegionTID to make this work.'
                return []

    first, last  = cal.monthrange(year, month)
    from_date = dt.date(year, month, 1)
    to_date = dt.date(year, month, last) + dt.timedelta(days=1)

    if get_new:
        all_observations = go.get_all_registrations(from_date, to_date, output='DataFrame', geohazard_tid=10,
                                                    observer_ids=observer_id, region_ids=region_id)

        # for all dates in the requested from-to interval
        dates = []
        for d in _get_dates(from_date, to_date, dt.timedelta(days=1)):

            if observer_id is not None and region_id is None:   # if only data for one observer
                dd = DayData(d, observer_id=observer_id)
            else:                                               # else whish to have data for some/all observervers in a region
                dd = DayData(d, region_id=region_id)

            obstyp = []
            regids = []
            nicks = []
            loc_pr_regid = {}
            obs_pr_regid = {}
            nic_pr_regid = {}

            # loop through all observations
            for i in all_observations.index:
                this_date = all_observations.iloc[i].DtObsTime.date()

                # append all observations where dates match
                if this_date == d:

                    regid = all_observations.iloc[i].RegID

                    # location on regid (only one location pr RegID)
                    if regid not in loc_pr_regid.keys():
                        loc_pr_regid[regid] = all_observations.iloc[i].ForecastRegionName

                    # get the nicname use on the regid (only one pr RegID)
                    if regid not in nic_pr_regid.keys():
                        nic_pr_regid[regid] = all_observations.iloc[i].NickName

                    # observations pr regid (might be more)
                    if regid not in obs_pr_regid.keys():
                        obs_pr_regid[regid] = [all_observations.iloc[i].RegistrationName]
                    else:
                        obs_pr_regid[regid].append(all_observations.iloc[i].RegistrationName)

                    # list of all observations on this date
                    if all_observations.iloc[i].RegistrationName == 'Bilde':
                        if all_observations.iloc[i].TypicalValue1 == 'Bilde av: Snoeprofil':
                            obstyp.append('Snoeprofil')
                        else:
                            obstyp.append(all_observations.iloc[i].RegistrationName)
                    else:
                        obstyp.append(all_observations.iloc[i].RegistrationName)

                    # list of all regids - this counts occurances
                    regids.append(int(all_observations.iloc[i].RegID))

                    # list of all observers nickanmes - this counts occurances
                    nicks.append(all_observations.iloc[i].NickName)

            # add to object for plotting
            dd.add_loc_pr_regid(loc_pr_regid)
            dd.add_obs_pr_regid(obs_pr_regid)
            dd.add_nic_pr_regid(nic_pr_regid)
            dd.add_observations(obstyp)
            dd.add_regids(regids)
            dd.add_nicks(nicks)
            dates.append(dd)

        if make_pickle:
            mp.pickle_anything(dates, pickle_file_name)

    else:
        dates = mp.unpickle_anything(pickle_file_name)

    return dates


def step2_plot(dates, observer_name=None, region_name=None, file_ext=".png", data_description=None):
    """
    If it is a custom data set ragion_name shold be provided because it wil be plotted by region.
    observer_name and region_name determines the main groupiong of data. They should not be provided both.

    :param dates:
    :param observer_name:
    :param region_name:
    :param file_ext:
    :param data_description:    Custom description for naming plot-files
    :return:
    """

    if data_description is not None:
        plot_file_name = '{0}{1}_{2}{3:02d}'.format(env.web_images_folder, data_description, dates[0].date.year, dates[0].date.month)
    else:
        if region_name is not None:
            plot_file_name = '{0}{1}_regiondata_{2}{3:02d}'.format(env.web_images_folder, region_name, dates[0].date.year, dates[0].date.month)
        else:
            if observer_name is not None:
                plot_file_name = '{0}observerdata_{1}_{2}{3:02d}'.format(env.web_images_folder, dates[0].observer_id, dates[0].date.year, dates[0].date.month)
            else:
                print 'Need ObserverID and/or forecastRegionTID to make this work.'
                plot_file_name = 'no_good_plot'


    # Figure dimensions
    fsize = (18, 13)
    fig = plb.figure(figsize=fsize)
    #plb.clf()
    ax = fig.add_subplot(111)
    plb.subplots_adjust(top=0.95, bottom=0.15, left=0.02, right=0.98)

    # plot all boxes pr date
    for d in dates:
        x = int(d.x)-d.box_size_x
        y = int(d.y)-d.box_size_y
        rect = mpl.patches.Rectangle((x, y), d.box_size_x , d.box_size_y, facecolor=d.cell_colour)
        ax.add_patch(rect)

        # The date in top left corner
        plb.text(x+6, y+84, '{0}'.format(d.date.day), fontsize=20)

        # plot circles with individual observation count
        for k,v in d.observations.iteritems():
            relative_x, relative_y, obs_colour, obs_edge = d.get_obs_pos(k)
            circ = mpl.patches.Circle((x+relative_x, y+relative_y), d.box_size_x/11, facecolor=obs_colour, edgecolor=obs_edge)
            ax.add_patch(circ)
            plb.text(x+relative_x-2, y+relative_y-2, '{0}'.format(v))

        if observer_name is not None:
            # List all regids
            reg_id_string = ''
            for k,v in d.reg_ids.iteritems():
                reg_id_string += '{0}: {1}\n'.format(k, v)
            plb.text(x+45, y+60-len(d.reg_ids)*8, reg_id_string)

        if region_name is not None:
            # List all observer nicks
            nick_string = ''
            for k,v in d.nick_names.iteritems():
                nick_string += '{0}: {1}\n'.format(k, v)
            plb.text(x+35, y+60-len(d.nick_names)*8, nick_string)

        # total obs this day
        if d.number_obs > 0:
            plb.text(x+30, y+35, '{0}'.format(d.number_obs), fontsize=25)

    # add weeknumbers
    year = dates[0].date.year
    month = dates[0].date.month
    first, last  = cal.monthrange(year, month)
    first_week = dt.date(year, month, 1).isocalendar()[1]
    # make sure to get last week of previous year if needed
    if month == 1 and first != 1:
        first_week = 0
    last_week = dt.date(year, month, last).isocalendar()[1]
    week_nos = range(first_week, last_week+1, 1)
    index = -100
    for wn in week_nos:
        plb.text(-15, index+60, 'Uke {0}'.format(wn), fontsize=20, rotation=90)
        index -= 100

    # add weekdays
    week_days = ['Mandag','Tirsdag','Onsdag','Torsdag','Fredag','Loerdag','Soendag']
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
        plb.title('Observasjoner i {0} i {1}, {2}'.format(data_description, month_names[month], year), fontsize=30)
    else:
        if region_name is not None:
            plb.title('Observasjoner i {0} i {1}, {2}'.format(region_name, month_names[month], year), fontsize=30)
        else:
            if observer_name is not None:
                plb.title('Observasjoner av {0} i {1}, {2}'.format(observer_name, month_names[month], year), fontsize=30)
            else:
                plb.title('No title - probably an error', fontsize=30)

    plb.xlim(-20, 700)
    plb.ylim(-1 *(len(week_nos) * 100), 50)
    plb.axis('off')
    #fig.tight_layout()

    plb.savefig(plot_file_name+file_ext)
    plb.close()

    return


def step3_make_html(dates, region_name=None, data_description=None):
    """Method serves both plots for selected obserevars or selected regions.

    :param dates:
    :param region_name:     If doing observers region_name=None else we are doing regions and this is a region name
    :return:

    """
    observer_id = dates[0].observer_id      # if doing regions this is always None

    if data_description is not None:
        html_file_name = '{0}{1}_{2}{3:02d}.html'.format(env.web_view_folder, data_description, dates[0].date.year, dates[0].date.month)
    else:
        if region_name is not None:
            html_file_name = '{0}{1}_regiondata_{2}{3:02d}.html'.format(env.web_view_folder, region_name, dates[0].date.year, dates[0].date.month)
        else:
            if observer_id is not None:
                html_file_name = '{0}observerdata_{1}_{2}{3:02d}.html'.format(env.web_view_folder, observer_id, dates[0].date.year, dates[0].date.month)
            else:
                print 'Got to have region and/or observer to make this work.'
                html_file_name = 'no_good_html'


    f = open(html_file_name, 'w')

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

    f.close()

    return


def make_observer_plots(observer_list, months):

    for k,v in observer_list.iteritems():
        for m in months:

            dates = step1_get_data(m.year, m.month, observer_id=k, get_new=True)
            step2_plot(dates, observer_name=v)
            step3_make_html(dates)


def make_region_plots(region_ids, months):

    for id in region_ids:
        for m in months:

            dates = step1_get_data(m.year, m.month, region_id=id, get_new=True)
            region_name = gkdv.get_name('ForecastRegionKDV', id)
            step2_plot(dates, region_name=region_name)
            step3_make_html(dates, region_name=region_name)


def make_svv_plots(run_all=False):

    months = []
    month = dt.date(2015,11,1)
    while month < dt.date.today():
        months.append(month)
        almost_next = month + dt.timedelta(days=35)
        month = dt.date(almost_next.year, almost_next.month, 1)

    if not run_all:
        if dt.date.today().day < 5 and len(months) > 1:
            months = months[-2:]
        else:
            months = [months[-1]]

    observer_list = [1090, 79, 43, 1084, 33, 119, 67, 101, 952, 41, 34, 125, 126, 8, 384, 955, 14, 841, 50, 175, 1123, 199, 1068, 1598, 1646, 637, 1664, 1307, 135, 307, 1212, 1279, 1310]

    region_ids = [108,109,131,133,117,118,119,121,122,123,124,127,128]

    for id in region_ids:
        region_name = gkdv.get_name('ForecastRegionKDV', id)
        data_description="svv_i_{0}".format(region_name)

        for m in months:
            dates = step1_get_data(m.year, m.month, observer_id=observer_list, region_id=id, make_pickle=False, get_new=True, data_description=data_description)
            step2_plot(dates, region_name=region_name, data_description=data_description)
            step3_make_html(dates, region_name=region_name, data_description=data_description)

    return


def make_2015_16_plots(run_all=False):
    """Plots both observations pr observer and pr region for display on web page for the season 2015-16.
    Method includes a request for list of relevant observers.

    :return:
    """

    # list of months to be plotted
    all_months = []
    month = dt.date(2015,11,1)
    while month < dt.date.today():
        all_months.append(month)
        almost_next = month + dt.timedelta(days=35)
        month = dt.date(almost_next.year, almost_next.month, 1)

    # if not specified run only the last month
    if not run_all:
        if dt.date.today().day < 5 and len(all_months) > 1:
            last_months = all_months[-2:]
        else:
            last_months = [all_months[-1]]
    else:
        last_months = all_months

    # get a list of relevant observerst to plot and make plickle in the web-folder
    previous_observer_list = mp.unpickle_anything('{0}observerlist.pickle'.format(env.web_root_folder))
    observer_list = gm.get_observer_dict_for_2015_16_ploting()
    mp.pickle_anything(observer_list, '{0}observerlist.pickle'.format(env.web_root_folder))

    # if observer not in previous observer list, run all months else only run last months
    new_observers = {}
    for k,v in observer_list.iteritems():
        if k not in previous_observer_list.keys():
            new_observers[k] = v

    # Get all regions
    region_ids = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
        if 100 < k < 150 and v.IsActive is True:
            region_ids.append(v.ID)

    # run the stuff
    make_observer_plots(new_observers, all_months)
    make_observer_plots(previous_observer_list, last_months)
    make_region_plots(region_ids, last_months)

    return


def test_sort_observer_list():

    observer_dict = mp.unpickle_anything('{0}observerlist.pickle'.format(env.web_root_folder))
    observer_list_unsorted = [[k,v] for k,v in observer_dict.iteritems()]
    unknown_user = observer_list_unsorted[0]
    observer_list_unsorted.pop(0)
    observer_list = sorted(observer_list_unsorted, key=lambda nick: nick[1].lower())
    observer_list.insert(0, unknown_user)

    return


if __name__ == "__main__":

    #make_svv_plots(run_all=False)
    test_sort_observer_list()
    make_2015_16_plots()

    # observer_list={111:'JonasD@ObsKorps',
    #                282:'martin@obskorps',
    #                325:'Siggen@Obskorps',
    #                45:'jostein@nve',
    #                580:'SindreH@ObsKorps',
    #                759:'madspaatopp@senjaobs'}
    #
    # observer_list={282:'martin@obskorps', 325:'Siggen@Obskorps'}
    #
    # months = []
    # month = dt.date(2016,1,1)
    # while month < dt.date.today():
    #     months.append(month)
    #     almost_next = month + dt.timedelta(days=35)
    #     month = dt.date(almost_next.year, almost_next.month, 1)
    #
    # # months = [dt.date(2015,11,1)]
    # make_observer_plots(observer_list, months)
    # make_region_plots([119, 121], months)
    #
    #
    #






























