# -*- coding: utf-8 -*-
__author__ = 'ragnarekker'

import os.path
import setenvironment as env
import makepickle as mp
import getproblems as gp
import getkdvelements as gkdv
import datetime as dt


def save_problems(problems, file_path):
    '''

    :param problems:
    :param file_path:
    :return:
    '''


    if os.path.exists(file_path) == False:
        l = open(file_path, 'w')
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'
                .format('Dato', 'RegionID', 'RegionNavn', 'fgTall', 'Faregrad', 'ProblemOprinnelse',
                'Rekkefoelge', 'Aarsak', 'Stoerrelse',
                'MerOmProblemet', 'ViewIregObs', 'URLtilOrginal'))
    else:
        l = open(file_path, 'a')

    for p in problems:
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\{11}\n'.format(
            p.date,
            p.region_id,
            p.region_name,
            p.danger_level,
            p.danger_level_name,
            p.source,
            p.order,
            p.cause_name,
            p.aval_size,
            p.problem_combined,
            p.regobs_view,
            p.url))
    l.close()


def save_problems_simple(problems, file_path):
    '''

    :param problems:
    :param file_path:
    :return:
    '''

    l = open(file_path, 'w')
    l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'
            .format('Dato', 'RegionNavn', 'Faregrad', 'ProblemOprinnelse',
            'Rekkefoelge', 'Aarsak'))

    for p in problems:
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(
            p.date,
            p.region_name,
            p.danger_level_name,
            p.source,
            p.order,
            p.cause_name))

    l.close()


if __name__ == "__main__":

    # This makes a full report

    data_output_filename = '{0}Alle skredproblemer.csv'.format(env.output_folder)
    pickle_file_name = '{0}runavalancheproblems.pickle'.format(env.local_storage)

    region_ids = [118, 128, 117]

    # Get all regions
    region_ids = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
       if 99 < k < 150 and v.IsActive is True:
           region_ids.append(v.ID)

    from_date = dt.date(2012, 12, 31)
    to_date = dt.date(2015, 7, 1)

    data = gp.get_all_problems(region_ids, from_date, to_date)
    mp.pickle_anything(data, pickle_file_name)

    data = mp.unpickle_anything(pickle_file_name)
    save_problems_simple(data, data_output_filename)

    a = 1

