# -*- coding: utf-8 -*-
__author__ = 'raek'


import datetime as dt
import setenvironment as se


def log_and_print(message, print_it=False, log_it=True):
    '''For logging and printing this method does both.

    :param message:     [string] what to print and/or log
    :param print_it:    [bool] default True
    :param log_it:      [bool] default True

    :return:
    '''

    time_and_message = '{:%H:%M}: '.format(dt.datetime.now().time()) + message

    if print_it:
        print time_and_message

    if log_it:
        file_name = '{0}get_obs_{1}.log'.format(se.output_folder, dt.date.today())
        with open(file_name, 'a') as f:
            f.write(time_and_message + '\n')