# -*- coding: utf-8 -*-
__author__ = 'raek'


from varsomdata import getdangers as gd
import datetime as dt
from varsomdata import getmisc as gm
from varsomdata import makepickle as mp
from varsomdata import setcoreenvironment as env
import os as os
import numpy as np


def get_2016_17_warnings(how_to_get_data='Get new and dont pickle', pickle_file_name=None):
    '''

    :param hot_to_get_data:     'Get new and dont pickle', 'Get new and save pickle' or 'Load pickle'
    :param file_name:           Not needed if no pickles involved
    :return:
    '''

    if 'Get new' in how_to_get_data:

        from_date = dt.date(2016, 11, 30)
        #to_date = dt.date.today()
        to_date = dt.date(2017, 5, 31)

        #region_ids = [3012, 3013]
        region_ids = gm.get_forecast_regions(year='2016-17')

        all_warnings = []
        for region_id in region_ids:
            all_warnings += gd.get_forecasted_dangers(region_id, from_date, to_date, include_ikke_vurdert=False)

        # Sort by date
        all_warnings = sorted(all_warnings, key=lambda AvalancheDanger: AvalancheDanger.date)

        if 'and save pickle' in how_to_get_data:
            mp.pickle_anything(all_warnings, pickle_file_name)

    elif 'Load pickle' in how_to_get_data:
        all_warnings = mp.unpickle_anything(pickle_warnings_file_name)

    else:
        all_warnings = 'No valid data retrival method given in get_2015_16_warnings.'

    return all_warnings


def make_forecaster_data(warnings, save_for_web=False):
    '''Make the forecaster dictionary with all the neccesary data.
    method also makes the dict needed fore the menu on the pythonanywhre website.

    :param warnings:
    :return:
    '''

    # get nicknames and ids to all regObs users. Get {id:nick} to all forecasters.
    observer_nicks = gm.get_observer_v()

    # Make dataset with dict {nick: Forecaster}. Add warnings to Forecaster object.
    # Note: A list of all forecaster names is all the keys in this dictionary
    forecaster_dict = {}
    for w in warnings:
        if w.nick not in forecaster_dict:
            forecaster_dict[w.nick] = Forecaster(w.nick)
            forecaster_dict[w.nick].add_warning(w)
        else:
            forecaster_dict[w.nick].add_warning(w)

    # need this below for forecasterstatisitics
    nowcast_lengths_all = []
    forecast_lengths_all = []
    danger_levels_all = []
    problems_pr_warning_all = []
    for w in warnings:
        nowcast_lengths_all.append(len(w.avalanche_nowcast))
        forecast_lengths_all.append(len(w.avalanche_forecast))
        danger_levels_all.append(w.danger_level)
        problems_pr_warning_all.append(len(w.avalanche_problems))

    # Add more data for forecaster objects in the dict
    for n, f in forecaster_dict.items():

        # add # warnings made
        forecaster_dict[f.nick].add_warnings_count(len(f.warnings))
        for o_i, o_n in observer_nicks.items():
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

        # Add lists of dangerlevels, nowcastlengths, forecast lengths and problems.
        # for this forecaster and all and avarages.
        nowcast_lengths = []
        forecast_lengths = []
        danger_levels = []
        problems_pr_warning = []

        for w in f.warnings:
            nowcast_lengths.append(len(w.avalanche_nowcast))
            forecast_lengths.append(len(w.avalanche_forecast))
            danger_levels.append(w.danger_level)
            problems_pr_warning.append(len(w.avalanche_problems))

        forecaster_dict[f.nick].add_nowcast_lengths(nowcast_lengths, nowcast_lengths_all)
        forecaster_dict[f.nick].add_forecast_lengths(forecast_lengths, forecast_lengths_all)
        forecaster_dict[f.nick].add_danger_levels(danger_levels, danger_levels_all)
        forecaster_dict[f.nick].add_problems_pr_warning(problems_pr_warning, problems_pr_warning_all)

    # Save dict of forecasters for the website menu. Find where nick match forecasters.
    if save_for_web:
        forecaster_nicknid_dict = {-1:'_OVERSIKT ALLE_'}
        for o_i,o_n in observer_nicks.items():
            for f_n, f_F in forecaster_dict.items():
                if o_n == f_n:
                    forecaster_nicknid_dict[o_i] = o_n
        mp.pickle_anything(forecaster_nicknid_dict, '{0}forecasterlist.pickle'.format(env.web_root_folder))

    return forecaster_dict


def make_plots(forecaster_dict, nick, path=''):

    import matplotlib.pyplot as plt
    import numpy
    import datetime as dt

    f = forecaster_dict[nick]

    plt.clf()
    bins = numpy.linspace(0, 1024, 20)
    plt.hist(f.nowcast_lengths_all, bins, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.nowcast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.nowcast_lengths, bins, alpha=0.5, color='b', label='{0}'.format(nick))
    plt.axvline(f.nowcast_lengths_avg, color='b', linestyle='dashed', linewidth=3, label='Snitt {0}'.format(nick))
    plt.title("Tegn brukt paa naasituasjonen")
    plt.xlabel("Antall")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper left')
    plt.savefig('{0}{1}_nowcast.png'.format(path, f.observer_id))


    plt.clf()
    bins = numpy.linspace(0, 1024, 20)
    plt.hist(f.forecast_lengths_all, bins, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.forecast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.forecast_lengths, bins, alpha=0.5, color='pink', label='{0}'.format(nick))
    plt.axvline(f.forecast_lengths_avg, color='pink', linestyle='dashed', linewidth=3, label='Snitt {0}'.format(nick))
    plt.title("Tegn brukt paa varsel")
    plt.xlabel("Antall")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_forecast.png'.format(path, f.observer_id))


    plt.clf()
    bins = numpy.linspace(0, 5, 6)
    plt.hist(f.danger_levels_all, bins, align='left', rwidth=0.5, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.danger_levels_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.danger_levels, bins, align='left', rwidth=0.5, color='pink', label='{0}'.format(nick))
    plt.axvline(f.danger_levels_avg, color='pink', linestyle='dashed', linewidth=3, label='Snitt {0}'.format(nick))
    plt.title("Fordeling paa faregrader")
    plt.xlabel("Faregrad")
    plt.ylabel("Frekvens")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_danger.png'.format(path, f.observer_id))


    plt.clf()
    bins = numpy.linspace(0, 4, 5)
    plt.hist(f.problems_pr_warning_all, bins, align='left', rwidth=0.5, alpha=0.5, color='k', label='Alle varsel')
    plt.axvline(f.problems_pr_warning_all_avg, color='k', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.hist(f.problems_pr_warning, bins, align='left', rwidth=0.5, color='pink', label='{0}'.format(nick))
    plt.axvline(f.problems_pr_warning_avg, color='pink', linestyle='dashed', linewidth=3, label='Snitt alle')
    plt.title("Skredproblemer pr varsel")
    plt.xlabel("Antall")
    plt.ylabel("Frequency")
    plt.legend(loc='upper right')
    plt.savefig('{0}{1}_problems_pr_warning.png'.format(path, f.observer_id))


    plt.clf()
    antall_pr_dag = f.dates.values()
    if len(antall_pr_dag) != 0:
        snitt = sum(antall_pr_dag)/float(len(antall_pr_dag))
        plt.plot((dt.date(2016, 12, 1), dt.date(2017, 6, 1)), (snitt, snitt), color='g', linestyle='dashed', linewidth=3)
    # barplot needs datetimes not dates
    dates = [dt.datetime.combine(d, dt.datetime.min.time()) for d in f.dates.keys()]
    plt.bar(dates, antall_pr_dag, color='g')
    ymax = max(f.dates.values()) + 1
    plt.title("Antall varsler paa datoer")
    plt.ylim(0, ymax)
    plt.xlim(dt.date(2016, 12, 1), dt.date(2017, 6, 1))
    plt.xticks( rotation=17 )
    plt.savefig('{0}{1}_dates.png'.format(path, f.observer_id))

    return


def make_html(forecaster_dict, nick, path='', type='Simple'):
    '''Makes a html with dates and links to the forecasts made by a given forecaster.

    :param forecaster_dict:
    :param nick:
    :param observer_id:
    :param path:
    :return:
    '''

    fc = forecaster_dict[nick]

    if 'Simple' in type:

        html_file_name = '{0}{1}_forecasts_simple.html'.format(path, fc.observer_id)
        f = open(html_file_name, 'w', encoding='utf-8')

        f.write('<table class="table table-hover"><tbody><tr><td>')
        d_one_time = None
        for w in fc.warnings:
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

        html_file_name = '{0}{1}_forecasts_advanced.html'.format(path, fc.observer_id)
        f = open(html_file_name, 'w', encoding='utf-8')

        f.write('<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#advanced">Tabell med info om faregrad og skredproblemer</button>\n'
            '<div id="advanced" class="collapse">\n')
        f.write('</br>\n')
        f.write('<table class="table table-hover"><tbody>')

        d_one_time = forecaster_dict[nick].warnings[0]
        for w in fc.warnings:
            region_name_varsom =  w.region_name.replace('aa','a').replace('oe', 'o').replace('ae', 'a')
            problem_highlights = ''
            for p in w.avalanche_problems:
                if not hasattr(p, 'aval_size'):
                    p.aval_size = 'Ikke gitt'
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
        html_file_name = '{0}{1}_forecasts.html'.format(path, fc.observer_id)
        f = open(html_file_name, 'w', encoding='utf-8')
        f.write('<table class="table table-hover"><tbody><tr><td>Ble ikke spurt om  å lage noe data..')
        f.write('</td></tr></tbody></table>')

    f.close()

    return


def make_m3_figs(forecaster_dict, nick, path=''):
    '''Makes m3 tables for each forecaster. Uses methods from the runmatrix module.

    :param forecaster_dict:
    :param nick:            is how I can select relevant warnings for this forecaster
    :param product_folder:  location where plots (endproduct) is saved
    :param project_folder:  many files generated; make project folder in product folder
    :return:
    '''

    from runvarsomdata import runmatrix as rm

    f = forecaster_dict[nick]
    # select only warnings for this forecaster
    one_forecaster_warnings = f.warnings

    # prepare dataset
    pickle_data_set_file_name = '{0}runforefollow data set {1}.pickle'.format(env.local_storage, f.observer_id)
    rm.pickle_data_set(one_forecaster_warnings, pickle_data_set_file_name, use_ikke_gitt=False)
    forecaster_data_set = mp.unpickle_anything(pickle_data_set_file_name)

    # prepare the m3 elementes (cell contents)
    pickle_m3_v2_file_name = '{0}runforefollow m3 {1}.pickle'.format(env.local_storage, f.observer_id)
    rm.pickle_M3(forecaster_data_set, 'matrixconfiguration.v2.csv', pickle_m3_v2_file_name)
    m3_v2_elements = mp.unpickle_anything(pickle_m3_v2_file_name)

    # plot
    plot_m3_v2_file_name = '{0}{1}_m3'.format(path, f.observer_id)
    rm.plot_m3_v2(m3_v2_elements, plot_m3_v2_file_name)

    return


def make_comparison_plots(forecaster_dict, path=''):

    import matplotlib.pyplot as plt; plt.rcdefaults()
    import numpy as np

    forecasters = [n for n,f in forecaster_dict.items()]
    y_pos = np.arange(len(forecasters))

    all_danger_levels = [f.danger_levels_avg for n,f in forecaster_dict.items()]
    all_danger_levels_std = [f.danger_levels_std for n,f in forecaster_dict.items()]

    all_problems_pr_warning = [f.problems_pr_warning_avg for n,f in forecaster_dict.items()]
    all_problems_pr_warning_std = [f.problems_pr_warning_std for n,f in forecaster_dict.items()]

    all_nowcast_lengths = [f.nowcast_lengths_avg for n,f in forecaster_dict.items()]
    all_nowcast_lengths_std = [f.nowcast_lengths_std for n,f in forecaster_dict.items()]

    all_forecast_lengths = [f.forecast_lengths_avg for n,f in forecaster_dict.items()]
    all_forecast_lengths_std = [f.forecast_lengths_std for n,f in forecaster_dict.items()]

    # all danger levels
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_danger_levels, align='center', alpha=0.5, color='pink',
             xerr=all_danger_levels_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Gjennomsnittlig faregrad')
    plt.xlim(0., 4.5)
    plt.axvline(forecaster_dict['Ragnar@NVE'].danger_levels_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Sammenlignet varselt faregrad sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_danger_201617.png'.format(path))

    # all problems pr warning
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_problems_pr_warning, align='center', alpha=0.5, color='pink',
             xerr=all_problems_pr_warning_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Snitt antall skredproblemer')
    plt.xlim(0.5, 3.)
    plt.axvline(forecaster_dict['Ragnar@NVE'].problems_pr_warning_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Antall skredproblemer pr varsel sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_problems_pr_warning_201617.png'.format(path))

    # all nowcast lengths
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_nowcast_lengths, align='center', alpha=0.5, color='b',
             xerr=all_nowcast_lengths_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Snitt tegn paa naasituasjon')
    plt.xlim(0., 1024.)
    plt.axvline(forecaster_dict['Ragnar@NVE'].nowcast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Antall tegn brukt i naasituasjonen sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_nowcast_lengths_201617.png'.format(path))

    # all forecast lengths
    plt.clf()
    plt.figure(figsize=(12, 8))
    plt.barh(y_pos, all_forecast_lengths, align='center', alpha=0.5, color='b',
             xerr=all_forecast_lengths_std, error_kw=dict(ecolor='k', lw=0.25, capsize=1.5, capthick=1.5))
    plt.yticks(y_pos, forecasters,  rotation=0)
    plt.xlabel('Snitt tegn paa varselet')
    plt.xlim(0., 1024.)
    plt.axvline(forecaster_dict['Ragnar@NVE'].forecast_lengths_all_avg, color='k', linestyle='dashed', linewidth=3)
    plt.title('Antall tegn brukt i varselet sesongen 2016/17')
    fig = plt.gcf()
    fig.subplots_adjust(left=0.2)
    plt.savefig('{0}all_forecast_lengths_201617.png'.format(path))

    return


class Forecaster():


    def __init__(self, nick_inn):

        self.nick = nick_inn

        self.warnings = []              # all warnings made by this forecaster
        self.warning_count = None       # int number of of warnings
        self.dates = {}                 # dict of {date:#}
        self.observer_id = None         # int observer id in regObs

        self.work_days = None

        self.danger_levels = None
        self.nowcast_lengths = None
        self.forecast_lengths = None
        self.problems_pr_warning = None

        self.danger_levels_all = None
        self.nowcast_lengths_all = None
        self.forecast_lengths_all = None
        self.problems_pr_warning_all = None

        self.danger_levels_avg = None
        self.nowcast_lengths_avg = None
        self.forecast_lengths_avg = None
        self.problems_pr_warning_avg = None

        self.danger_levels_all_avg = None
        self.nowcast_lengths_all_avg = None
        self.forecast_lengths_all_avg = None
        self.problems_pr_warning_all_avg = None

        self.danger_levels_std = None
        self.nowcast_lengths_std = None
        self.forecast_lengths_std = None
        self.problems_pr_warning_std = None

        self.danger_levels_all_std = None
        self.nowcast_lengths_all_std = None
        self.forecast_lengths_all_std = None
        self.problems_pr_warning_all_std = None



    def add_warning(self, warning_inn):
        self.warnings.append(warning_inn)


    def add_warnings_count(self, warning_count_inn):
        self.warning_count = warning_count_inn


    def add_dates(self, dates_inn):
        self.dates = dates_inn
        self.work_days = len(self.dates)


    def add_observer_id(self, observer_id_inn):
        self.observer_id = observer_id_inn


    def add_nowcast_lengths(self, nowcast_lengths_inn, nowcast_lengths_all_inn):

        self.nowcast_lengths = [float(i) for i in nowcast_lengths_inn]
        self.nowcast_lengths_avg = np.mean(np.array(self.nowcast_lengths))
        self.nowcast_lengths_std = np.std(np.array(self.nowcast_lengths))

        self.nowcast_lengths_all = [float(i) for i in nowcast_lengths_all_inn]
        self.nowcast_lengths_all_avg = sum(self.nowcast_lengths_all)/len(self.nowcast_lengths_all)
        self.nowcast_lengths_all_std = np.std(np.array(self.nowcast_lengths_all))


    def add_forecast_lengths(self, forecast_lengths_inn, forecast_lengths_all_inn):

        self.forecast_lengths = [float(i) for i in forecast_lengths_inn]
        self.forecast_lengths_avg = sum(self.forecast_lengths)/len(self.forecast_lengths)
        self.forecast_lengths_std = np.std(np.array(self.forecast_lengths))

        self.forecast_lengths_all = [float(i) for i in forecast_lengths_all_inn]
        self.forecast_lengths_all_avg = sum(self.forecast_lengths_all)/len(self.forecast_lengths_all)
        self.forecast_lengths_all_std = np.std(np.array(self.forecast_lengths_all))


    def add_danger_levels(self, danger_levels_inn, danger_levels_all_inn):

        self.danger_levels = [float(i) for i in danger_levels_inn]
        self.danger_levels_avg = sum(self.danger_levels)/len(self.danger_levels)
        self.danger_levels_std = np.std(np.array(self.danger_levels))

        self.danger_levels_all = [float(i) for i in danger_levels_all_inn]
        self.danger_levels_all_avg = sum(self.danger_levels_all)/len(self.danger_levels_all)
        self.danger_levels_all_std = np.std(np.array(self.danger_levels_all))


    def add_problems_pr_warning(self, problems_pr_warning_inn, problems_pr_warning_all_inn):

        self.problems_pr_warning = [float(i) for i in problems_pr_warning_inn]
        self.problems_pr_warning_avg = sum(self.problems_pr_warning)/len(self.problems_pr_warning)
        self.problems_pr_warning_std = np.std(np.array(self.problems_pr_warning))

        self.problems_pr_warning_all = [float(i) for i in problems_pr_warning_all_inn]
        self.problems_pr_warning_all_avg = sum(self.problems_pr_warning_all)/len(self.problems_pr_warning_all)
        self.problems_pr_warning_all_std = np.std(np.array(self.problems_pr_warning_all))


if __name__ == "__main__":

    # Some controls for debugging and developing
    plot_one = False         # make one plot for user 'Ragnar@NVE'. If False it makes all plots.
    save_for_web = True      # save for web. If false it saves to plot folder.
    get_new = False           # if false it uses a local pickle
    make_pickle = True      # save pickle of what is gotten by get_new if true

    # Many files. Use a project folder.
    project_folder = 'forecasterplots/'

    product_image_folder='plots/'+ project_folder
    if save_for_web:
        product_image_folder=env.web_images_folder + project_folder
    # Make folder if it doesnt exist
    if not os.path.exists('{0}'.format(product_image_folder)):
        os.makedirs('{0}'.format(product_image_folder))

    product_html_folder=product_image_folder
    if save_for_web: product_html_folder=env.web_view_folder

    # Get and pickle all the warnings this season.
    pickle_warnings_file_name = '{0}{1}'.format(env.local_storage, 'runforecasterfollowup warnings.pickle')
    how_to_get_warning_data='Load pickle'
    if get_new:
        if make_pickle:
            how_to_get_warning_data='Get new and save pickle'
        else:
            how_to_get_warning_data='Get new and dont pickle'
    warnings = get_2016_17_warnings(how_to_get_data=how_to_get_warning_data, pickle_file_name=pickle_warnings_file_name)

    # This is the data used from now on
    forecaster_dict = make_forecaster_data(warnings, save_for_web=save_for_web)

    # make plots about all forecasters
    make_comparison_plots(forecaster_dict, path=product_image_folder)

    # make finge forecaster output
    if plot_one:
        # plot for singe user
        make_m3_figs(forecaster_dict, 'Ragnar@NVE', path=product_image_folder)
        make_plots(forecaster_dict, 'Ragnar@NVE', path=product_image_folder)
        make_html(forecaster_dict, 'Ragnar@NVE', path=product_html_folder, type='Advanced')
        make_html(forecaster_dict, 'Ragnar@NVE', path=product_html_folder, type='Simple')
    else:
        # plot for all forecasters
        for n,f in forecaster_dict.items():
            nick = n
            make_m3_figs(forecaster_dict, nick, path=product_image_folder)
            make_plots(forecaster_dict, nick, path=product_image_folder)
            make_html(forecaster_dict, nick, path=product_html_folder, type='Advanced')
            make_html(forecaster_dict, nick, path=product_html_folder, type='Simple')



