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
import fencoding as fe

# I/O and environmental stuff
import readfile as rf
import makepickle as mp
import setenvironment as env


class DayData():

    def __init__(self, date, observer_id):

        self.observer_id = observer_id

        self.box_size_x = None
        self.box_size_y = None
        self.cell_colour = None
        self.set_properties()

        self.date = date
        self.week_no = date.isocalendar()[1]
        self.week_day = date.isocalendar()[2]
        self.observations = col.Counter()
        self.number_obs = None
        self.reg_ids = col.Counter()

        self.x = None
        self.y = None
        self.set_x()
        self.set_y()


    def set_properties(self):
        self.box_size_x = 100
        self.box_size_y = 100
        self.cell_colour = 'white'


    def add_observations(self, observations):
        self.observations = col.Counter(observations)
        self.number_obs = sum(self.observations.values())
        if self.number_obs > 0:
            self.cell_colour = 'gray'


    def add_regids(self, reg_ids):
        self.reg_ids = col.Counter(reg_ids)


    def set_x(self):
        self.x = self.week_day * 100


    def set_y(self):
        year = self.date.year
        month = self.date.month
        first, last  = cal.monthrange(year, month)
        first_week = dt.date(year, month, first).isocalendar()[1]
        last_week = dt.date(year, month, last).isocalendar()[1]

        self.y = 100 * (1 + last_week - self.week_no)


    def get_obs_pos(self, obs_type):

        if obs_type == 'Faretegn':
            return 35, 80, 'red', 'k'
        elif obs_type == 'Observert skredaktivitet':
            return 55, 80, 'red', 'k'
        elif obs_type == 'Observert skred':
            return 85, 80, 'orange', 'k'
        elif obs_type == 'Hendelse':
            return 85, 60, 'orange', 'k'
        elif obs_type == 'Snoedekke':
            return 85, 40, 'blue', 'k'
        elif obs_type == 'Observert vaer':
            return 85, 20, 'blue', 'k'
        elif obs_type == 'Snoeprofil':
            return 55, 20, 'white', 'k'
        elif obs_type == 'Stabilitetstest':
            return 35, 20, 'white', 'k'
        elif obs_type == 'Skredproblem (2014)':
            return 15, 20, 'pink', 'k'
        elif obs_type == 'Skredfarevurdering (2014)':
            return 15, 40, 'pink', 'k'
        elif obs_type == 'Bilde':
            return 15, 60, 'yellow', 'k'
        elif obs_type == 'Fritekstfelt':
            return 35, 60, 'yellow', 'k'
        else:
            return 0, 0, 'k', 'k'


def _get_dates(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta


def step1_get_data(observer_id, year, month, get_new=True):
    """Gets data for one month and prepares for plotting

    :param observer_id:     [int]
    :param year:            [int]
    :param month:           [int]
    :param get_new:         [bool]
    :return:
    """

    pickle_file_name = "{0}runPlotObserverData_{1}_{2}{3}.pickle".format(env.local_storage, observer_id, year, month)

    first, last  = cal.monthrange(year, month)
    from_date = dt.date(year, month, first)
    to_date = dt.date(year, month, last) + dt.timedelta(days=1)

    if get_new:
        all_observations = go.get_all_registrations(from_date, to_date, output='DataFrame', geohazard_tid=10, observer_ids=observer_id)
        dates = []

        # for all dates
        for d in _get_dates(from_date, to_date, dt.timedelta(days=1)):

            dd = DayData(d, observer_id)
            obstyp = []
            regids = []

            # loop through all observations
            for i in all_observations.index:
                this_date = all_observations.iloc[i].DtObsTime.date()

                # append all observations where dates match
                if this_date == d:
                    if all_observations.iloc[i].RegistrationName == 'Bilde':
                        if all_observations.iloc[i].TypicalValue1 == 'Bilde av: Snoeprofil':
                            obstyp.append('Snoeprofil')
                        else:
                            obstyp.append(all_observations.iloc[i].RegistrationName)
                    else:
                        obstyp.append(all_observations.iloc[i].RegistrationName)

                    regids.append(all_observations.iloc[i].RegID)

            # add to object for plotting
            dd.add_observations(obstyp)
            dd.add_regids(regids)
            dates.append(dd)

        mp.pickle_anything(dates, pickle_file_name)

    else:
        dates = mp.unpickle_anything(pickle_file_name)

    return dates


def step2_plot(dates, file_ext=".png"):

    plot_file_name = '{0}observerdata_{1}_{2}{3}'.format(env.plot_folder, dates[0].observer_id, dates[0].date.year, dates[0].date.month)

    # Figure dimensions
    fsize = (20, 13)
    fig = plb.figure(figsize=fsize)
    #plb.clf()
    ax = fig.add_subplot(111)
    plb.subplots_adjust(top=0.95, bottom=0.15, left=0.02, right=0.98)


    for d in dates:
        x = int(d.x)-d.box_size_x
        y = int(d.y)-d.box_size_y
        rect = mpl.patches.Rectangle((x, y), d.box_size_x , d.box_size_y, facecolor=d.cell_colour)
        ax.add_patch(rect)

        plb.text(x+5, y+80, '{0}'.format(d.date.day), fontsize=15)

        for k,v in d.observations.iteritems():
            relative_x, relative_y, obs_colour, obs_edge = d.get_obs_pos(k)
            circ = mpl.patches.Circle((x+relative_x, y+relative_y), d.box_size_x/11, facecolor=obs_colour, edgecolor=obs_edge)
            ax.add_patch(circ)
            plb.text(x+relative_x, y+relative_y, '{0}'.format(v))

        reg_id_string = ''
        for k,v in d.reg_ids.iteritems():
            reg_id_string += '{0}: {1}\n'.format(k, v)
        plb.text(x+60, y+60, reg_id_string)

        if d.number_obs > 0:
            plb.text(x+30, y+25, '{0}'.format(d.number_obs), fontsize=20)

    plb.xlim(-50, 700)
    plb.ylim(0, 550)
    plb.axis('off')
    fig.tight_layout()

    plb.savefig(plot_file_name+file_ext)
    plb.close()

    return





def step3_make_html(dates):
    """

    :param dates:
    :return:

    <div class="container">
      <h2>Observasjoner tabulert</h2>
      <p>Plottet over tabulert. Merk også lenker til hver registrering.</p>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Date</th>
            <th>Registration</th>
            <th>Observations</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John</td>
            <td><a href='http://www.varsom.no'>Doe</a></td>
            <td>john@example.com</td>
          </tr>
          <tr>
            <td>Mary</td>
            <td>Moe</td>
            <td>mary@example.com</td>
          </tr>
          <tr>
            <td>July</td>
            <td>Dooley</td>
            <td>july@example.com</td>
          </tr>
        </tbody>
      </table>
    </div>

    """

    html_file_name = '{0}observerdata_{1}_{2}{3}.html'.format(env.output_folder, dates[0].observer_id, dates[0].date.year, dates[0].date.month)

    f = open(html_file_name, 'w')

    f.write('<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#tbl{0}{1}">Tabell</button>\n'
            '<div id="tbl{0}{1}" class="collapse">\n'.format(dates[0].date.year, dates[0].date.month))
    f.write('</br>\n'
            ''
            '<table class="table table-hover">\n')
    f.write('    <thead>\n'
            '        <tr>\n'
            '            <th>Date</th>\n'
            '            <th>Registration</th>\n'
            '            <th>Observations</th>\n'
            '        </tr>\n'
            '    </thead>\n'
            '    <tbody>\n')

    for d in dates:
        d_one_time = d.date
        for id in d.reg_ids.keys():
            f.write('        <tr>\n'
                    '            <td>{0}</td>\n'
                    '            <td><a href="http://www.regobs.no/registration/{1}">{1}</a></td>\n'
                    '            <td>{2}</td>\n'
                    '        </tr>\n'.format(d_one_time, id, d.observations))
            if d_one_time is not '':
                d_one_time = ''         # date show only once in column 1


    f.write('     </tbody>\n'
            '</table>'
            '</div>')

    f.close()

    return



if __name__ == "__main__":


    observer_list={111:'Jonas@ObsKorps', 282:'Martin?', 325:'Siggen@Obskorps'}

    months = [dt.date(2015,11,1), dt.date(2015,12,1)]

    for k,v in observer_list.iteritems():
        for m in months:

            dates = step1_get_data(k, m.year, m.month, get_new=False)
            step2_plot(dates)
            step3_make_html(dates)

    a = 1