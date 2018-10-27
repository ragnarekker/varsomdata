# -*- coding: utf-8 -*-
"""Throughout the project this module is used for creating log files."""

import datetime as dt
import os as os
import setenvironment as env
from utilities import fencoding as fe

__author__ = 'raek'


def log_and_print(message, print_it=False, log_it=True):
    """For logging and printing this method does both.

    :param message:     [string] what to print and/or log
    :param print_it:    [bool] default True
    :param log_it:      [bool] default True
    """

    time_and_message = '{:%H:%M}: '.format(dt.datetime.now().time()) + message
    time_and_message.encode('utf-8')

    if print_it:
        # When run with os x Launchd, printing to screen caused unicode error with non ascii characters. Remove the characters.
        print(fe.remove_norwegian_letters(time_and_message))

    if log_it:

        # If log folder doesnt exist, make it.
        if not os.path.exists(env.log_folder):
            os.makedirs(env.log_folder)

        file_name = '{0}get_obs_{1}.log'.format(env.log_folder, dt.date.today())
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(time_and_message + '\n')
