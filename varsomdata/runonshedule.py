# -*- coding: utf-8 -*-
__author__ = 'raek'

import runplotdangerandproblem as dap
import runplotobserversdata as od
import subprocess

if __name__ == "__main__":

    #dap.make_2015_16_plots()
    #od.make_2015_16_plots(run_all=True)
    #od.make_svv_plots(run_all=True)

    rsync_cmd = 'rsync -rzP ~/Dropbox/Kode/Python/BottleSite/ ragnar@ssh.pythonanywhere.com:~/BottleSite'
    subprocess.Popen(rsync_cmd, shell=True).wait()

