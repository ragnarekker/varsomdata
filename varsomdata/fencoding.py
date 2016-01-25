# -*- coding: utf-8 -*-
__author__ = 'ragnarekker'

import datetime as dt


def unix_time_2_normal(unix_date_time):
    """
    Takes in a date in unix datetime and returns a "normal date"

    :param unix_date_time:    Unix date time in milliseconds from 1.1.1970
    :return:                The date as datetime object

    Ex: date = unix_time_2_normal(int(p['DtObsTime'][6:-2]))
    """

    # odata returns a string with prefix "Date". Cropp and cast.
    if "Date" in unix_date_time:
        unix_date_time = int(unix_date_time[6:-2])

    unix_datetime_in_seconds = unix_date_time/1000 # For some reason they are given in miliseconds
    date = dt.datetime.fromtimestamp(int(unix_datetime_in_seconds))
    return date


def remove_norwegian_letters(name_inn):
    """

    :param name_inn:
    :return:
    """

    if name_inn is None:
        return None

    name = name_inn

    if u'å' in name:
        name = name.replace(u'å', 'aa')
    if u'ø' in name:
        name = name.replace(u'ø', 'oe')
    if u'æ' in name:
        name = name.replace(u'æ', 'ae')
    if u'Å' in name:
        name = name.replace(u'Å', 'AA')
    if u'Ø' in name:
        name = name.replace(u'Ø', 'OE')
    if u'Æ' in name:
        name = name.replace(u'Æ', 'AE')


    name = name.encode('ascii', 'ignore')
    name = name.strip()                 # removes whitespace to left and right
    name = name.replace('\n', '')
    name = name.replace('\t', '')

    return name


def add_norwegian_letters(name_inn, use_encoding='utf8'):
    """

    :param name_inn:
    :return:
    """

    if name_inn is None:
        return None

    name = name_inn.decode(use_encoding, 'ignore')

    if u'ae' in name:
        name = name.replace(u'ae', 'æ'.decode(use_encoding, 'ignore'))
    if u'oe' in name:
        name = name.replace(u'oe', 'ø'.decode(use_encoding, 'ignore'))
    if u'aa' in name:
        name = name.replace(u'aa', 'å'.decode(use_encoding, 'ignore'))
    if u'AE' in name:
        name = name.replace(u'AE', 'Æ'.decode(use_encoding, 'ignore'))
    if u'OE' in name:
        name = name.replace(u'OE', 'Ø'.decode(use_encoding, 'ignore'))
    if u'AA' in name:
        name = name.replace(u'AA', 'Å'.decode(use_encoding, 'ignore'))

    return name


if __name__ == "__main__":

    a = u'æøå'.encode('utf8')
    c = add_norwegian_letters('Proeve.')
    b = 1
