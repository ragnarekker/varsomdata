# -*- coding: utf-8 -*-
__author__ = 'raek'

import runplotdangerandproblem as dap
import runplotobserversdata as od
import subprocess

if __name__ == "__main__":

    #dap.make_2015_16_plots()
    #od.make_2015_16_plots(run_all=False)
    #od.make_svv_plots(run_all=False)

    rsync_cmd = 'rsync -rzP ~/Documents/github/BottleSite/ ragnar@ssh.pythonanywhere.com:~/BottleSite'
    subprocess.Popen(rsync_cmd, shell=True).wait()

