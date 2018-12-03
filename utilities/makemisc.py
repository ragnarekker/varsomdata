# -*- coding: utf-8 -*-
"""General methods for making life easier."""

import datetime as dt
import collections as cols


def make_date_int_dict(start_date=dt.date(2012, 10, 1), end_date=dt.date.today()):
    """Makes dictionary with all dates in a period as keys and values set to 0."""

    num_days = (end_date-start_date).days
    date_list = [start_date + dt.timedelta(days=x) for x in range(0, num_days)]

    date_dict = cols.OrderedDict()
    for d in date_list:
        date_dict[d] = 0

    return date_dict


def make_date_list_dict(start_date=dt.date(2012, 10, 1), end_date=dt.date.today()):
    """Makes dictionary with all dates in a period as keys and values set to []."""

    num_days = (end_date-start_date).days
    date_list = [start_date + dt.timedelta(days=x) for x in range(0, num_days)]

    date_dict = cols.OrderedDict()
    for d in date_list:
        date_dict[d] = []

    return date_dict
