# -*- coding: utf-8 -*-
__author__ = 'raek'

import setenvironment as env


def read_configuration_file(file_name, element_class):

    print "readfile.py -> read_configuration_file: Reading {0}".format(file_name)

    inn_file = open(file_name)
    inn_data = inn_file.read().replace('\r', '\n')
    inn_data = inn_data.replace('\n\n', '\n')
    inn_file.close()

    # setarate the rows
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



if __name__ == "__main__":


    import runmatrix as rfm

    config_file_name = '{0}{1}'.format(env.input_folder, 'matrixconfiguration.v2.csv')
    m3_elements = read_configuration_file(config_file_name, rfm.M3Element)

    a = 1