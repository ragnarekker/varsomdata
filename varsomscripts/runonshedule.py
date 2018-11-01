# -*- coding: utf-8 -*-
from utilities import makelogs as ml
from varsomscripts import plotcalendardata as pcd
from varsomscripts import regobsstatistics as rs
from varsomscripts import plotdangerandproblem as pdap
from varsomdata import getvarsompickles as vp
from varsomdata import getmisc as gm
from utilities import makepickle as mp
import setenvironment as env
import subprocess as sp
import sys as sys
import collections as col
import datetime as dt

__author__ = 'raek'
log_reference = 'runonshedule.py -> '

"""    if operational:
        web_root_folder = '/Users/ragnarekker/Dropbox/Kode/Python/BottleSite/'
        web_pickle_folder = web_root_folder
        web_images_folder = web_root_folder + 'images/'
        web_images_regiondata_folder = web_images_folder + 'regionplots/'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots/'
        web_images_observerdata_folder = web_images_folder + 'observerplots/'
        web_images_svvdata_folder = web_images_folder + 'svvplots/'
        web_view_folder = web_root_folder + 'views/'
    else:
        web_root_folder = root_folder
        web_pickle_folder = output_folder
        web_images_folder = plot_folder
        web_images_regiondata_folder = web_images_folder + 'regionplots/'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots/'
        web_images_observerdata_folder = web_images_folder + 'observerplots/'
        web_images_svvdata_folder = web_images_folder + 'svvplots/'
        web_view_folder = output_folder + 'views/'

elif sys.platform == 'win32':
    root_folder = 'C:\\Users\\raek\\Dropbox\\Kode\\Python\\varsomdata\\'
    local_storage = root_folder + 'localstorage\\'
    output_folder = root_folder + 'output\\'
    plot_folder = output_folder + 'plots\\'

    if operational:
        web_root_folder = 'C:\\Users\\raek\\Dropbox\\Kode\\Python\\BottleSite\\'
        web_pickle_folder = web_root_folder
        web_images_folder = web_root_folder + 'images\\'
        web_images_regiondata_folder = web_images_folder + 'regionplots\\'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots\\'
        web_images_observerdata_folder = web_images_folder + 'observerplots\\'
        web_images_svvdata_folder = web_images_folder + 'svvplots\\'
        web_view_folder = web_root_folder + 'views\\'
    else:
        web_root_folder = root_folder
        web_pickle_folder = output_folder
        web_images_folder = plot_folder
        web_images_regiondata_folder = web_images_folder + 'regionplots\\'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots\\'
        web_images_observerdata_folder = web_images_folder + 'observerplots\\'
        web_images_svvdata_folder = web_images_folder + 'svvplots\\'
        web_view_folder = output_folder + 'views\\'


"""


def make_2017_18_plots():
    """Plots both observations pr observer and pr region for display on web page for the season 2015-16.
    Method includes a request for list of relevant observers."""

    # list of months to be plotted
    months = []
    month = dt.date(2017, 11, 1)
    while month < dt.date.today():
        months.append(month)
        almost_next = month + dt.timedelta(days=35)
        month = dt.date(almost_next.year, almost_next.month, 1)

    # Get all regions
    region_ids = gm.get_forecast_regions('2017-18')

    # get a list of relevant observers to plot and make pickle for adding to the web-folder
    all_observations_nest = vp.get_all_observations('2017-18', output='Nest', geohazard_tids=10)
    all_observations_list = vp.get_all_observations('2017-18', output='List', geohazard_tids=10)

    observer_dict = {}
    for o in all_observations_nest:
        if o.ObserverId in observer_dict.keys():
            observer_dict[o.ObserverId].add_one_observation_count()
        else:
            observer_dict[o.ObserverId] = pcd.ObserverData(o.ObserverId, o.NickName, observation_count_inn=1)

    observer_list = []
    ordered_observer_dict = col.OrderedDict(sorted(observer_dict.items(), key=lambda t: t[1].observation_count, reverse=True))
    for k, v in ordered_observer_dict.items():
        if v.observation_count > 4:
            observer_list.append([v.observer_id, v.observer_nick, v.observation_count])

    mp.pickle_anything(observer_list, '{0}observerlist.pickle'.format(env.web_pickle_folder))

    # run the stuff
    pcd.make_observer_plots(all_observations_list, observer_list, months)
    pcd.make_region_plots(all_observations_list, region_ids, months)
    pcd.make_svv_plots(all_observations_list, observer_dict, region_ids, months)



if __name__ == "__main__":

    # try:
    #     make_2017_18_plots()
    # except Exception:
    #     error_msg = sys.exc_info()[0]
    #     ml.log_and_print("[error] {0}__main__: Full crash on making 2017-18 danger and problem plots. {1}".format(log_reference, error_msg))
    #
    # try:
    #     pcd.make_2017_18_plots()
    # except:
    #     error_msg = sys.exc_info()[0]
    #     ml.log_and_print("[error] {0}__main__: Full crash on making 2017-18 observer and region calender plots. {1}".format(log_reference, error_msg))
    #
    # try:
    #     rs.plot_regs_obs_numbs()
    # except:
    #     error_msg = sys.exc_info()[0]
    #     ml.log_and_print("[error] {0}__main__: Full crash on making regobs statistics plots. {1}".format(log_reference, error_msg))

    try:
        # This requires version 3 of rsync and command is set up to handle utf-8 file names from mac to linux server
        # This command deletes at destination if not at source.
        # More on installing version 3 of rsync: http://clubmate.fi/update-rsync-on-osx-with-homebrew/
        # It also requires x code developer tools: https://apple.stackexchange.com/questions/254380/macos-sierra-invalid-active-developer-path
        # And that you can du passwordless logont unix server with ssh: https://www.jacobtomlinson.co.uk/2013/01/24/ssh-copy-id-os-x/
        rsync_cmd = '/usr/local/Cellar/rsync/3.1.3_1/bin/rsync -rzP --iconv=utf-8-mac,utf-8 ' \
                    '--exclude \'.*\' ' \
                    '--exclude \'/BottleSite/images/httplogplots/\' ' \
                    '--log-file=\'{0}rsync.log\' ' \
                    '~/Dropbox/Kode/Python/BottleSite/ ragnar@ssh.pythonanywhere.com:~/BottleSite ' \
                    '--delete'.format(env.log_folder)
        sp.Popen(rsync_cmd, shell=True).wait()
        ml.log_and_print("[info] {0}__main__: rsync complete. See separate logfile for details.".format(log_reference))
    except:
        error_msg = sys.exc_info()[0]
        ml.log_and_print("[error] {0}__main__: Full crash on rsync. {1}".format(log_reference, error_msg))
