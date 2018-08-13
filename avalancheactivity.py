# -*- coding: utf-8 -*-
from varsomdata import getdangers as gd
from varsomdata import getobservations as go
from varsomdata import getkdvelements as gkdv
from varsomdata import readfile as rf
from varsomdata import makepickle as mp
import setenvironment as env
import datetime as dt
import matplotlib as mpl
import pylab as plb

__author__ = 'raek'


class ActivityAndDanger:

    def __init__(self):

        self.danger_level = None        # in current region at current date

        self.avalanche_trigger = []
        self.destructive_size = None
        self.estimated_number = None

        self.observation_count = 0

        self.x = None
        self.y = None

        self.cell_colour = None

    def add_configuration_row(self, row):

        self.danger_level = row[0]
        self.destructive_size = row[2]
        self.estimated_number = row[1]

        self.x = row[5]
        self.y = row[6]

        self.cell_colour = row[7]
        # self.update_cell_colour()

        return


    def update_cell_colour(self):
        if self.danger_level is not None and self.cell_colour in 'white':
            if '1' in self.danger_level:
                self.cell_colour = '#ccff66'
            elif '2' in  self.danger_level:
                self.cell_colour = '#ffff00'
            elif '3' in self.danger_level:
                self.cell_colour = '#ff9900'
            elif '4' in self.danger_level:
                self.cell_colour = '#ff0000'
            elif '5' in self.danger_level:
                self.cell_colour = 'k'
            else:
                self.colour = 'pink'        # pink means something whent wrong


class DataOnDateInRegion:

    def __init__(self, date, region_name):

        self.date = date
        self.region_name = region_name

        self.forecast = []
        self.danger_sign = []
        self.avalanche = []
        self.avalanche_activity = []

        self.most_valued_observation = None
        self.highest_value = -1


class IndexOfSizeAndNumber:

    def __init__(self):
        self.estimated_num = None
        self.destructive_size = None
        self.index = None

    def add_configuration_row(self, row):
        self.estimated_num = row[0]
        self.destructive_size = row[1]
        self.index = row[2]
        return


def step_1_make_data_set(region_ids, from_date, to_date):
    """Makes the dataset of all observed avalanche activity (inl signs and isingle avalanches obs) and maps
    to forecasts for those days.

    :param region_ids:   [int or list of ints]
    :param from_date:   [date]
    :param to_date:     [date]
    :return:
    """

    # get all data
    dangers = gd.get_all_dangers(region_ids, from_date, to_date)
    avalanches = go.get_avalanche_activity(from_date, to_date, region_ids)
    single_avalanches = go.get_avalanche(from_date, to_date, region_ids)
    danger_signs = go.get_danger_sign(from_date, to_date, region_ids)

    # List of only forecasts
    forecasted_dangers = []
    for d in dangers:
        if 'Forecast' in d.data_table and d.danger_level != 0:
            forecasted_dangers.append(d)

    # List of only valid activity observations
    observed_activity = []
    for a in avalanches:
        if not 'Ikke gitt' in a.EstimatedNumName:
            observed_activity.append(a)

    # list of relevant danger observations
    danger_sign_avalanches = []
    for ds in danger_signs:
        if 'Ferske skred' in ds.DangerSignName or 'Ingen faretegn observert' in ds.DangerSignName:
            danger_sign_avalanches.append(ds)

    # list of relevant singel avalanches
    observed_avalanche = []
    for sa in single_avalanches:
        if not 'Ikke gitt' in sa.DestructiveSizeName:
            observed_avalanche.append(sa)

    # Make list of all regions pr date and append forecasts and observations.
    data_date_region = []
    for d in forecasted_dangers:
        danger_date = d.date
        print('{0}'.format(danger_date))
        danger_region_name = d.region_name

        data = DataOnDateInRegion(danger_date, danger_region_name)
        data.forecast.append(d)

        for a in observed_activity:
            aval_date = a.DtAvalancheTime.date()
            aval_region_name = a.ForecastRegionName
            if aval_date == danger_date and aval_region_name == danger_region_name:
                data.avalanche_activity.append(a)

        for da in danger_sign_avalanches:
            aval_date = da.DtObsTime.date()
            aval_region_name = da.ForecastRegionName
            if aval_date == danger_date and aval_region_name == danger_region_name:
                data.danger_sign.append(da)

        for oa in observed_avalanche:
            aval_date = oa.DtAvalancheTime.date()
            aval_region_name = oa.ForecastRegionName
            if aval_date == danger_date and aval_region_name == danger_region_name:
                data.avalanche.append(oa)

        data_date_region.append(data)

    # discard days and regions where no observations present
    date_region = []
    for d in data_date_region:
        if not len(d.avalanche_activity) == 0 or not len(d.danger_sign) == 0 or not len(d.avalanche) == 0:
            date_region.append(d)

    return date_region, forecasted_dangers


def step_2_find_most_valued(date_region):

    # most valued obs could change name to observation with highest index

    index = rf.read_configuration_file('{0}aval_dl_order_of_size_and_num.csv'.format(env.input_folder), IndexOfSizeAndNumber)
    for d in date_region:

        for aa in d.avalanche_activity:
            max_index = 0
            for i in index:
                if i.estimated_num in aa.EstimatedNumName and i.destructive_size in aa.DestructiveSizeName:
                    max_index = i.index
            if d.highest_value < max_index:
                d.highest_value = max_index
                d.most_valued_observation = aa

        for a in d.avalanche:
            max_index = 0
            for i in index:
                if i.estimated_num in 'Ett (1)' and i.destructive_size in a.DestructiveSizeName:
                    max_index = i.index
            if d.highest_value < max_index:
                d.highest_value = max_index
                d.most_valued_observation = a

        for ds in d.danger_sign:
            if 'Ferske skred' in ds.DangerSignName:
                if d.highest_value < 2:
                    d.highest_value = 2
                    d.most_valued_observation = ds
            if 'Ingen faretegn observert' in ds.DangerSignName:
                if d.highest_value < 1:
                    d.highest_value = 1
                    d.most_valued_observation = ds

    return date_region


def step_3_count_occurances(date_region, elements):

    for d in date_region:
        for e in elements:
            if str(d.forecast[0].danger_level) in e.danger_level:

                # if danger sign
                if isinstance(d.most_valued_observation, go.DangerObs):
                    danger_sign_name = d.most_valued_observation.DangerSignName
                    if e.estimated_number == "Fra faretegn" and 'Ikke gitt' in e.destructive_size and 'Ferske skred' in danger_sign_name:
                        e.observation_count += 1
                    if e.estimated_number == 'Ingen' and 'Ikke gitt' in e.destructive_size and 'Ingen faretegn observert' in danger_sign_name:
                        e.observation_count += 1

                # if one avalanche
                if isinstance(d.most_valued_observation, go.AvalancheObs):
                    num = "Ett (1)"
                    size = d.most_valued_observation.DestructiveSizeName
                    trigger = d.most_valued_observation.AvalancheTriggerName
                    if size in e.destructive_size and num in e.estimated_number:
                        e.observation_count += 1
                        e.avalanche_trigger.append(trigger)

                # if activity
                # Note that in the elements no activity i "Ingen" whereas no activity in EstimatedNumKDV is
                # "Ingen skredaktivitet"
                if isinstance(d.most_valued_observation, go.AvalancheActivityObs):
                    num = d.most_valued_observation.EstimatedNumName
                    size = d.most_valued_observation.DestructiveSizeName
                    trigger = d.most_valued_observation.AvalancheTriggerName
                    if size in e.destructive_size and e.estimated_number in num:
                        e.observation_count += 1
                        e.avalanche_trigger.append(trigger)

    return elements


def step_4_plot(date_region, forecasted_dangers, elements, file_name, file_ext=".png"):

   # Figure dimensions
    fsize = (24, 13)
    fig = plb.figure(figsize=fsize)
    #plb.clf()
    ax = fig.add_subplot(111)
    plb.subplots_adjust(top=0.95, bottom=0.15, left=0.02, right=0.98)

    unused_elements = []
    box_size = 100

    font_bold = mpl.font_manager.FontProperties()
    font_bold.set_weight('bold')

    for e in elements:
        if not e.x == '0' and not e.y == '0' and '5' not in e.danger_level:
            x = int(e.x)-box_size
            y = int(e.y)-box_size
            rect = mpl.patches.Rectangle((x, y), box_size , box_size, facecolor=e.cell_colour)
            ax.add_patch(rect)

            if e.observation_count is not 0 and '#BABDB6' not in e.cell_colour and 'Ikke gitt' not in e.destructive_size:
                plb.text(x+10, y+60, 'N = {0}'.format(e.observation_count), fontproperties=font_bold)
                if e.avalanche_trigger.count('Naturlig utloest') is not 0:
                    plb.text(x+10, y+40, 'NT = {0}'.format(e.avalanche_trigger.count('Naturlig utloest')))
                if e.observation_count-e.avalanche_trigger.count('Naturlig utloest')-e.avalanche_trigger.count('Ikke gitt') is not 0:
                    plb.text(x+10, y+20, 'HT = {0}'.format(e.observation_count-e.avalanche_trigger.count('Naturlig utloest')-e.avalanche_trigger.count('Ikke gitt')))
            elif e.observation_count is not 0 and '#BABDB6' not in e.cell_colour:
                plb.text(x+10, y+60, 'N = {0}'.format(e.observation_count), fontproperties=font_bold)

        else:
            # if elements are given coordinates 0 they are an illegal combination. Append them to this list for debug purposes
            unused_elements.append(e)

    # Figure header
    plb.text(0, 790, 'Hoeyest observerte skredaktivitet i regionen sett sammen mot faregraden - vinter 2015/16', fontsize=30)

    # Label Avalanche size
    plb.text(-100, 430, 'Skredstoerelse', fontsize=20, rotation=90)
    for i in range(1,6,1):
        plb.text(-40, i*100+50, '{0}'.format(i), fontsize=15)
        plb.hlines(i*100, -50, 2400, lw=1, color='0.8')

    for i in range(0, 2400, 100):
        plb.vlines(i, 0, 600, lw=1, color='0.8')

    for i in range(1, 5, 1):

        # Label x axis estimated number
        x_labels = {10:'Ingen*\n',
                    120:'Ferske\nskred**',
                    220:'Ett***\n',
                    320:'Noen\n(2-5)',
                    420:'Flere\n(6-10)',
                    520:'Mange\n(>10)'}
        for k,v in x_labels.iteritems():
            plb.text( (i-1)*600+k , -50, '{0}'.format(v), fontsize=15)

        plb.vlines((i-1)*600, -250, 630, lw=1, color='0.8')

        # plot distributions
        step_4_1_plot_numbers_and_distribution(i, ax, (i - 1) * 600, elements, date_region, forecasted_dangers)

    plb.xlim(-100, 2410)
    plb.ylim(-300, 800)
    plb.axis('off')
    plb.savefig(file_name+file_ext)
    plb.close()

    return


def step_4_1_plot_numbers_and_distribution(danger_level, ax, x, elements, date_region, forecasted_dangers):


    total_dl = sum(d.danger_level == danger_level for d in forecasted_dangers)
    obs_dl = sum(d.forecast[0].danger_level == danger_level for d in date_region)
    total_obs = len(date_region)

    # Label header with covered days
    if total_dl > 0:
        frac_dl= float(obs_dl)/total_dl*100
        plb.text(x+20, 680, 'Faregrad {3} ble varslet {0} dager. I {2:.0f}% av tilfellene\n'
                            'var det en eller flere observasjoner til aa steotte varslet.'.format(total_dl, obs_dl, frac_dl, danger_level))

        obs_trigger = 0
        aval_obs_total = 0

        for e in elements:
            if e.estimated_number not in ['Fra faretegn', 'Ingen'] and str(danger_level) in e.danger_level:
                obs_trigger += sum(t not in 'Ikke gitt' for t in e.avalanche_trigger)
                aval_obs_total += e.observation_count

        if aval_obs_total == 0:
            frac_trigger = 0
        else:
            frac_trigger = float(obs_trigger)/aval_obs_total*100

        plb.text(x+20, 620, 'I {0:.0f}% av tilfellene hvor skred eller skredaktivitet var\n'
                            'observert var tilleggsbelastning observert.'.format(frac_trigger))

    if obs_dl > 0:

        # histogrammer
        size_1 = 0
        size_2 = 0
        size_3 = 0
        size_4 = 0
        size_5 = 0
        no_act = 0
        danger_sign = 0
        est_num_1 = 0
        est_num_2 = 0
        est_num_3 = 0
        est_num_4 = 0

        for e in elements:
            if str(danger_level) in e.danger_level and '1' in e.destructive_size: size_1 += e.observation_count
            if str(danger_level) in e.danger_level and '2' in e.destructive_size: size_2 += e.observation_count
            if str(danger_level) in e.danger_level and '3' in e.destructive_size: size_3 += e.observation_count
            if str(danger_level) in e.danger_level and '4' in e.destructive_size: size_4 += e.observation_count
            if str(danger_level) in e.danger_level and '5' in e.destructive_size: size_5 += e.observation_count
            if str(danger_level) in e.danger_level and 'Ingen' in e.estimated_number: no_act += e.observation_count
            if str(danger_level) in e.danger_level and 'Fra faretegn' in e.estimated_number: danger_sign += e.observation_count
            if str(danger_level) in e.danger_level and 'Ett' in e.estimated_number: est_num_1 += e.observation_count
            if str(danger_level) in e.danger_level and 'Noen' in e.estimated_number: est_num_2 += e.observation_count
            if str(danger_level) in e.danger_level and 'Flere' in e.estimated_number: est_num_3 += e.observation_count
            if str(danger_level) in e.danger_level and 'Mange' in e.estimated_number: est_num_4 += e.observation_count

        activity_tot = size_1 + size_2 + size_3 + size_4 + size_5 + no_act + danger_sign
        scale = 75

        # activity_tot = total_obs
        # scale = 200

        size_1_bar = float(size_1)/activity_tot*scale
        size_2_bar = float(size_2)/activity_tot*scale
        size_3_bar = float(size_3)/activity_tot*scale
        size_4_bar = float(size_4)/activity_tot*scale
        size_5_bar = float(size_5)/activity_tot*scale

        no_act_bar = float(no_act)/activity_tot*scale
        danger_sign_bar = float(danger_sign)/activity_tot*scale

        est_num_1_bar = float(est_num_1)/activity_tot*scale
        est_num_2_bar = float(est_num_2)/activity_tot*scale
        est_num_3_bar = float(est_num_3)/activity_tot*scale
        est_num_4_bar = float(est_num_4)/activity_tot*scale

        rect_size_1 = mpl.patches.Rectangle((x+200-size_1_bar, 100), size_1_bar, 100, facecolor='k', edgecolor="none")
        rect_size_2 = mpl.patches.Rectangle((x+200-size_2_bar, 200), size_2_bar, 100, facecolor='k', edgecolor="none")
        rect_size_3 = mpl.patches.Rectangle((x+200-size_3_bar, 300), size_3_bar, 100, facecolor='k', edgecolor="none")
        rect_size_4 = mpl.patches.Rectangle((x+200-size_4_bar, 400), size_4_bar, 100, facecolor='k', edgecolor="none")
        rect_size_5 = mpl.patches.Rectangle((x+200-size_5_bar, 500), size_5_bar, 100, facecolor='k', edgecolor="none")

        rect_no_act = mpl.patches.Rectangle((x+000, 0), 100, no_act_bar, facecolor='k', edgecolor="none")
        rect_danger_obs = mpl.patches.Rectangle((x+100, 0), 100, danger_sign_bar, facecolor='k', edgecolor="none")

        rect_est_num_1 = mpl.patches.Rectangle((x+200, 100-est_num_1_bar), 100, est_num_1_bar, facecolor='k', edgecolor="none")
        rect_est_num_2 = mpl.patches.Rectangle((x+300, 100-est_num_2_bar), 100, est_num_2_bar, facecolor='k', edgecolor="none")
        rect_est_num_3 = mpl.patches.Rectangle((x+400, 100-est_num_3_bar), 100, est_num_3_bar, facecolor='k', edgecolor="none")
        rect_est_num_4 = mpl.patches.Rectangle((x+500, 100-est_num_4_bar), 100, est_num_4_bar, facecolor='k', edgecolor="none")

        ax.add_patch(rect_size_1)
        ax.add_patch(rect_size_2)
        ax.add_patch(rect_size_3)
        ax.add_patch(rect_size_4)
        ax.add_patch(rect_size_5)

        ax.add_patch(rect_no_act)
        ax.add_patch(rect_danger_obs)

        ax.add_patch(rect_est_num_1)
        ax.add_patch(rect_est_num_2)
        ax.add_patch(rect_est_num_3)
        ax.add_patch(rect_est_num_4)

        # Bottom text
        no_act_danger_sign = 0
        no_act_aval_activity = 0

        est_num_1_aval_act = 0
        est_num_1_aval = 0

        for d in date_region:
            if d.forecast[0].danger_level == danger_level:

                if int(d.highest_value) == 1:
                    for ds in d.danger_sign:
                        if 'Ingen faretegn observert' in ds.DangerSignName:
                            no_act_danger_sign += 1
                    for aa in d.avalanche_activity:
                        if 'Ingen' in aa.EstimatedNumName and 'Ikke gitt' in aa.DestructiveSizeName:
                            no_act_aval_activity += 1

                elif int(d.highest_value) in [3,4,6,8,14]:
                    for aa in d.avalanche_activity:
                        if 'Ett (1)' in aa.EstimatedNumName and not "Ikke gitt" in aa.DestructiveSizeName:
                            est_num_1_aval_act += 1
                    for a in d.avalanche:
                        if not "Ikke gitt" in a.DestructiveSizeName:
                            est_num_1_aval += 1

        plb.text(x+20, -170, '*   {0} ganger var ingen skredaktivitet hoeyeste index. Totalt\n'
                             '    var det da {1} observasjoner fra ingen skredaktivitet og\n'
                             '    {2} fra ingen faretegn.'.format(no_act, no_act_danger_sign, no_act_aval_activity))

        plb.text(x+20, -200, '**  Ferske skred som faretegn ble observert {0} ganger.'.format(danger_sign))

        plb.text(x+20, -270, '*** {0} ganger er ett snoeskred med hoeysete index. \n'
                             '    {1} som skredaktivitet og {2} med skjema for \n'
                             '    enkeltskred.'.format(est_num_1, est_num_1_aval_act, est_num_1_aval))

    return


if __name__ == "__main__":

    ### Get all regions
    #region_id = [112, 117, 116, 128]

    region_id = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
       if 99 < k < 150 and v.IsActive is True:
           region_id.append(v.ID)

    from_date = dt.date(2015, 11, 30)
    to_date = dt.date(2016, 6, 1)
    #to_date = dt.date.today()

    # ## get and make the data set
    # date_region, forecasted_dangers = step_1_make_data_set(region_id, from_date, to_date)
    # mp.pickle_anything([date_region, forecasted_dangers], '{0}runforavalancheactivity_step_1.pickle'.format(cenv.local_storage))
    #
    # ## Find the observaton of highest value pr region pr date
    # date_region, forecasted_dangers = mp.unpickle_anything('{0}runforavalancheactivity_step_1.pickle'.format(cenv.local_storage))
    # date_region = step_2_find_most_valued(date_region)
    # mp.pickle_anything([date_region, forecasted_dangers], '{0}runforavalancheactivity_step_2.pickle'.format(cenv.local_storage))
    #
    # ## ready to add to count elements
    # date_region, forecasted_dangers = mp.unpickle_anything('{0}runforavalancheactivity_step_2.pickle'.format(cenv.local_storage))
    # elements = rf.read_configuration_file('{0}aval_dl_configuration.csv'.format(cenv.input_folder), ActivityAndDanger)
    # elements = step_3_count_occurances(date_region, elements)
    # mp.pickle_anything([date_region, forecasted_dangers, elements], '{0}runforavalancheactivity_step_3.pickle'.format(cenv.local_storage))

    ### ready to plot?
    date_region, forecasted_dangers, elements = mp.unpickle_anything('{0}runforavalancheactivity_step_3.pickle'.format(env.local_storage))
    step_4_plot(date_region, forecasted_dangers, elements, '{0}Avalanches and dangers {1} to {2}'.format(env.plot_folder, from_date, to_date))

    # Do a count on observations..
    total_a = 0
    total_aa = 0
    total_ds = 0
    for d in date_region:
        total_a += len(d.avalanche)
        total_aa += len(d.avalanche_activity)
        total_ds += len(d.danger_sign)
    total_obs = total_a + total_aa + total_ds

    # ..and used elements. Useful for debugging.
    used_elements = []
    for e in elements:
        if e.observation_count is not 0:
            used_elements.append(e)

    a = 1