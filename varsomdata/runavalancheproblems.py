# -*- coding: utf-8 -*-
__author__ = 'ragnarekker'

import os.path
import getregobs as GRO

# Two sets of folder references: windows based og unix based.
#data_folder = "datafiles\\"
data_folder = "datafiles/"



def save_problems(problems, file_path):
    '''

    :param problems:
    :param file_path:
    :return:
    '''


    if os.path.exists(file_path) == False:
       l = open(file_path, 'w')
       l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'
               .format('Date', 'RegionID', 'Region', 'Source',
               'Order', 'Cause', 'Size',
               'More on the avalanche problem', 'View in regObs', 'URL'))
    else:
        l = open(file_path, 'a')

    for p in problems:
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'.format(
            p.date,
            p.region_id,
            p.region_name,
            p.source,
            p.order,
            p.cause_name,
            p.aval_size,
            p.problem_combined,
            p.regobs_view,
            p.url))
    l.close()


if __name__ == "__main__":

    # This makes a full report

    data_output_filename = '{0}Alle skredproblemer.csv'.format(data_folder)

    regions = list(range(106, 134))

    for r in regions:
        data = GRO.get_all_problems(r)
        save_problems(data, data_output_filename)

    a = 1

