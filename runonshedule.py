# -*- coding: utf-8 -*-
import plotdangerandproblem as pdap
import plotcalendardata as pcd
import regobsstatistics as rs
from varsomdata import makelogs as ml
from varsomdata import setcoreenvironment as cenv
import subprocess as sp
import sys as sys

__author__ = 'raek'
log_reference = 'runonshedule.py -> '

if __name__ == "__main__":

    # try:
    #     pdap.make_2017_18_plots()
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
                    '--delete'.format(cenv.log_folder)
        sp.Popen(rsync_cmd, shell=True).wait()
        ml.log_and_print("[info] {0}__main__: rsync complete. See separate logfile for details.".format(log_reference))
    except:
        error_msg = sys.exc_info()[0]
        ml.log_and_print("[error] {0}__main__: Full crash on rsync. {1}".format(log_reference, error_msg))
