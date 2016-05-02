# -*- coding: utf-8 -*-
__author__ = 'raek'


import getdangers as gd
import datetime as dt
import getmisc as gm
import makepickle as mp
import setenvironment as env
import os as os
import fencoding as fe


def pickle_201516_warnings(file_name):

    from_date = dt.date(2015, 11, 30)
    to_date = dt.date.today()

    region_ids = [117, 128]  # Trollheimen
    region_ids = gm.get_active_forecast_regions()

    all_warnings = []
    for region_id in region_ids:
        all_warnings += gd.get_forecasted_dangers(region_id, from_date, to_date, include_problems=True, include_ikke_vurdert=False)

    # Sort by date
    all_warnings = sorted(all_warnings, key=lambda AvalancheDanger: AvalancheDanger.date)

    mp.pickle_anything(all_warnings, file_name)

    return


def make_plots(warnings, nick, forecaster_dict, path=''):

    import matplotlib.pyplot as plt
    import numpy

    observer_id = forecaster_dict[nick].observer_id

    nowcast_lengths = []
    forecast_lengths = []
    danger_level = []
    problems_pr_warning = []

    nowcast_lengths_nick = []
    forecast_lengths_nick = []
    danger_level_nick = []
    problems_pr_warning_nick = []

    for w in warnings:
        nowcast_lengths.append(len(w.avalanche_nowcast))
        forecast_lengths.append(len(w.avalanche_forecast))
        danger_level.append(w.danger_level)
        problems_pr_warning.append(len(w.avalanche_problems))

        if nick in w.nick:
            nowcast_lengths_nick.append(len(w.avalanche_nowcast))
            forecast_lengths_nick.append(len(w.avalanche_forecast))
            danger_level_nick.append(w.danger_level)
            problems_pr_warning_nick.append(len(w.avalanche_problems))


    plt.clf()
    bins = numpy.linspace(0, 1024, 20)
    plt.hist(nowcast_lengths, bins, alpha=0.5, label='Alle varsel')
    plt.hist(nowcast_lengths_nick, bins, label='{0}'.format(nick))
    plt.title("Tegn brukt paa naasituasjonen")
    plt.xlabel("Antall")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_nowcast.png'.format(path, observer_id))


    plt.clf()
    bins = numpy.linspace(0, 1024, 20)
    plt.hist(forecast_lengths, bins, alpha=0.5, label='Alle varsel')
    plt.hist(forecast_lengths_nick, bins, color='pink', label='{0}'.format(nick))
    plt.title("Tegn brukt paa varsel")
    plt.xlabel("Antall")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_forecast.png'.format(path, observer_id))


    plt.clf()
    bins = numpy.linspace(0, 5, 6)
    plt.hist(danger_level, bins, align='left', rwidth=0.5, alpha=0.5, label='Alle varsel')
    plt.hist(danger_level_nick, bins, align='left', rwidth=0.5, color='k', label='{0}'.format(nick))
    plt.title("Fordeling paa faregrader")
    plt.xlabel("Faregrad")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_danger.png'.format(path, observer_id))


    plt.clf()
    bins = numpy.linspace(0, 4, 5)
    plt.hist(problems_pr_warning, bins, align='left', rwidth=0.5, alpha=0.5, label='Alle varsel')
    plt.hist(problems_pr_warning_nick, bins, align='left', rwidth=0.5, color='pink', label='{0}'.format(nick))
    plt.title("Skredproblemer pr varsel")
    plt.xlabel("Antall")
    plt.ylabel("Frequency")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_problems_pr_warning.png'.format(path, observer_id))


    plt.clf()
    plt.bar(forecaster_dict[nick].dates.keys(), forecaster_dict[nick].dates.values(), color='g')
    ymax = max(forecaster_dict[nick].dates.values()) + 1
    plt.title("Antall varsler paa datoer")
    plt.ylim(0, ymax)
    plt.xlim(dt.date(2015, 12, 01), dt.date(2016, 06, 01))
    plt.xticks( rotation=17 )
    plt.savefig('{0}{1}_dates.png'.format(path, observer_id))

    return


def make_html(forecaster_dict, nick, observer_id, path='', type='Simple'):
    '''Makes a html with dates and links to the forecasts made by a given forecaster.

    :param forecaster_dict:
    :param nick:
    :param observer_id:
    :param path:
    :return:
    '''

    if 'Simple' in type:

        html_file_name = '{0}{1}_forecasts_simple.html'.format(path, observer_id)
        f = open(html_file_name, 'w')

        f.write('<table class="table table-hover"><tbody><tr><td>')
        d_one_time = None
        for w in forecaster_dict[nick].warnings:
            region_name_varsom = w.region_name.replace('aa','a').replace('oe', 'o').replace('ae', 'a')
            if d_one_time != w.date:
                f.write('</td>\n</tr>\n<tr>\n')
                d_one_time = w.date
                f.write('   <td>{0}</td>\n'.format(d_one_time))
                f.write('   <td><a href="http://varsom.no/Snoskred/{1}/?date={2}">{0}</a>'.format(w.region_name, region_name_varsom, w.date.strftime('%d.%m.%Y')))
            else:
                f.write(', <a href="http://varsom.no/Snoskred/{1}/?date={2}">{0}</a>'.format(w.region_name, region_name_varsom, w.date.strftime('%d.%m.%Y')))
        f.write('</tr></tbody></table>')

    elif 'Advanced' in type:

        html_file_name = '{0}{1}_forecasts_advanced.html'.format(path, observer_id)
        f = open(html_file_name, 'w')

        f.write('<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#advanced">Tabell med info om faregrad og skredproblemer</button>\n'
            '<div id="advanced" class="collapse">\n')
        f.write('</br>\n')
        f.write('<table class="table table-hover"><tbody>')

        d_one_time = forecaster_dict[nick].warnings[0]
        for w in forecaster_dict[nick].warnings:
            region_name_varsom =  w.region_name.replace('aa','a').replace('oe', 'o').replace('ae', 'a')
            problem_highlights = ''
            for p in w.avalanche_problems:
                problem_highlights += '<br>P{6}[{5}, {0}, {1}, {2}, {3}, {4}]'.format(p.cause_name, p.aval_size, p.aval_probability, p.aval_distribution, p.aval_trigger, p.aval_type, p.order+1 )
            forecast_highlights = 'Faregrad {0}'.format(w.danger_level) + problem_highlights
            f.write('<tr>\n')
            if d_one_time != w.date:
                d_one_time = w.date
                f.write('   <td>{0}</td>\n'.format(d_one_time))
            else:
                f.write('   <td></td>\n')
            f.write('   <td><a href="http://varsom.no/Snoskred/{1}/?date={2}">{0}</a></td>'.format(w.region_name, region_name_varsom, w.date.strftime('%d.%m.%Y')))
            f.write('   <td>{0}</td>'.format(forecast_highlights))
            f.write('</tr>\n')
        f.write('</tbody></table></div>')


    else:
        html_file_name = '{0}{1}_forecasts.html'.format(path, observer_id)
        f = open(html_file_name, 'w')
        f.write('<table class="table table-hover"><tbody><tr><td>Ble ikke spurt om  å lage noe data..')
        f.write('</td></tr></tbody></table>')

    f.close()

    return


def make_m3_figs(warnings, nick, observer_id, path=''):
    '''Makes m3 tables for each forecaster. Uses methods from the runmatrix module.

    :param warnings:        all warings
    :param nick:            is how I can select relevant warnings for this forecaster
    :param observer_id:     use id for making filenames
    :param product_folder:  location where plots (endproduct) is saved
    :param project_folder:  many files generated; make project folder in product folder
    :return:
    '''

    import runmatrix as rm

    # select only warnings for this forecaster
    one_forecaster_warnings = []
    for w in warnings:
        if w.nick == nick:
            one_forecaster_warnings.append(w)

    # prepare dataset
    pickle_data_set_file_name = '{0}runforefollow data set {1}.pickle'.format(env.local_storage, observer_id)
    rm.pickle_data_set(one_forecaster_warnings, pickle_data_set_file_name, use_ikke_gitt=False)
    forecaster_data_set = mp.unpickle_anything(pickle_data_set_file_name)

    # prepare the m3 elementes (cell contents)
    pickle_m3_v2_file_name = '{0}runforefollow m3 {1}.pickle'.format(env.local_storage, observer_id)
    rm.pickle_M3(forecaster_data_set, 'matrixconfiguration.v2.csv', pickle_m3_v2_file_name)
    m3_v2_elements = mp.unpickle_anything(pickle_m3_v2_file_name)

    # plot
    plot_m3_v2_file_name = '{0}{1}_m3'.format(path, observer_id)
    rm.plot_m3_v2(m3_v2_elements, plot_m3_v2_file_name)

    return


class Forecaster():


    def __init__(self, nick_inn):

        self.nick = nick_inn

        self.warnings = []
        self.warning_count = None
        self.dates = {}
        self.observer_id = None

        # not used
        self.work_days = None
        self.warnings_avg_pr_day = None
        self.problems_avg_pr_warning = None


    def add_warning(self, warning_inn):
        self.warnings.append(warning_inn)


    def add_warnings_count(self, warning_count_inn):
        self.warning_count = warning_count_inn


    def add_dates(self, dates_inn):
        self.dates = dates_inn


    def add_observer_id(self, observer_id_inn):
        self.observer_id = observer_id_inn


if __name__ == "__main__":

    # Some controls for debuging and developing
    plot_one = False         # make one plot. If False it makes all plots.
    save_for_web = True     # save for web. If false it saves to plot folder.
    get_new = True          # get new data from forecast api and regobs

    # Manny files. Use a project folder.
    project_folder = 'forecasterfollowup/'
    product_image_folder='plots/'+ project_folder
    if save_for_web: product_image_folder=env.web_images_folder + project_folder
    # Make folder if it doesnt exist
    if not os.path.exists('{0}'.format(product_image_folder)):
        os.makedirs('{0}'.format(product_image_folder))
    product_html_folder=product_image_folder
    if save_for_web: product_html_folder=env.web_view_folder

    # Get and pickle all the warnings this season.
    pickle_warnings_file_name = '{0}{1}'.format(env.local_storage, 'runforecasterfollowup warnings.pickle')
    if get_new: pickle_201516_warnings(pickle_warnings_file_name)
    warnings = mp.unpickle_anything(pickle_warnings_file_name)

    # Make dataset with dict {nick: Forecaster}. Add warnings to forecarster objecst.
    # Note: A list of all forecasters is all the keys in this dictionary
    forecaster_dict = {}
    for w in warnings:
        if w.nick not in forecaster_dict:
            forecaster_dict[w.nick] = Forecaster(w.nick)
            forecaster_dict[w.nick].add_warning(w)
        else:
            forecaster_dict[w.nick].add_warning(w)

    # get nicknames and ids to all regObs users. Get {id:nick} to all forecasters.
    observer_nicks = gm.get_observer_v()

    # Add more data for forecaster object
    for n,f in forecaster_dict.iteritems():
        # add no warnings made
        forecaster_dict[f.nick].add_warnings_count(len(f.warnings))
        for o_i, o_n in observer_nicks.iteritems():
            if o_n == f.nick:
                forecaster_dict[f.nick].add_observer_id(o_i)
        # find how many pr date
        dates = {}
        for w in f.warnings:
            if w.date not in dates:
                dates[w.date] = 1
            else:
                dates[w.date] += 1
        forecaster_dict[f.nick].add_dates(dates)

    # Save dict of forecasters for webview. Find where nick match forecasters.
    forecaster_nicknid_dict = {}
    for o_i,o_n in observer_nicks.iteritems():
        for f_n, f_F in forecaster_dict.iteritems():
            if o_n == f_n:
                forecaster_nicknid_dict[o_i] = o_n
    mp.pickle_anything(forecaster_nicknid_dict, '{0}forecasterlist.pickle'.format(env.web_root_folder))

    # make output
    if plot_one:
        # plot for singe user
        make_m3_figs(warnings, 'Ragnar@NVE', 6, path=product_image_folder)
        make_plots(warnings, 'Ragnar@NVE', forecaster_dict, path=product_image_folder)
        make_html(forecaster_dict, 'Ragnar@NVE', 6, path=product_html_folder, type='Advanced')
        make_html(forecaster_dict, 'Ragnar@NVE', 6, path=product_html_folder, type='Simple')
    else:
        # plot for all forecasters
        for n,f in forecaster_dict.iteritems():
            nick = fe.remove_norwegian_letters(n)
            make_m3_figs(warnings, nick, f.observer_id, path=product_image_folder)
            make_plots(warnings, nick, forecaster_dict, path=product_image_folder)
            make_html(forecaster_dict, nick, f.observer_id, path=product_html_folder, type='Advanced')
            make_html(forecaster_dict, nick, f.observer_id, path=product_html_folder, type='Simple')


