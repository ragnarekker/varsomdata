# -*- coding: utf-8 -*-
"""When a read method is generic and can be utilized across modules, the method is placed here."""

from utilities import makelogs as ml

__author__ = 'raek'


def read_configuration_file(file_name, element_class):
    """

    :param file_name:
    :param element_class:
    :return:
    """

    ml.log_and_print("[info] readfile.py -> read_configuration_file: Reading {0}".format(file_name))

    with open(file_name, 'rb') as f:
        inn_data = f.read()

    inn_data = inn_data.decode('utf-8')

    inn_data = inn_data.replace('\r', '\n')
    inn_data = inn_data.replace('\n\n', '\n')

    # separate the rows
    inn_data = inn_data.split('\n')

    separator = ';'
    elements = []
    for i in range(1, len(inn_data), 1):

        inn_data[i] = inn_data[i].strip()       # get rid of ' ' and '\n' and such
        if inn_data[i] == '':                   # blank line at end of file
            break

        row = inn_data[i].split(separator)      # splits line into list of elements in the line

        element = element_class()
        element.add_configuration_row(row)

        elements.append(element)

    return elements


def read_csv_file(file_name, element_class):
    """

    :param file_name:
    :param element_class:
    :return:
    """

    ml.log_and_print("[info] readfile.py -> read_csv_file: Reading {0}".format(file_name))

    with open(file_name, 'rb') as f:
        inn_data = f.read()

    inn_data = inn_data.decode('utf-8')

    inn_data = inn_data.replace('\r', '\n')
    inn_data = inn_data.replace('\n\n', '\n')

    # separate the rows
    inn_data = inn_data.split('\n')

    separator = ';'
    elements = []
    for i in range(1, len(inn_data), 1):        # begin range at 1 since 0 is the headers

        inn_data[i] = inn_data[i].strip()       # get rid of ' ' and '\n' and such
        if inn_data[i] == '':                   # blank line at end of file
            break

        row = inn_data[i].split(separator)      # splits line into list of elements in the line
        element = element_class(row)

        elements.append(element)

    return elements
