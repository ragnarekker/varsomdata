# -*- coding: utf-8 -*-
__author__ = 'raek'

import makepickle as mp
import fencoding as fe
import os.path
import setenvironment as se


def save_danger_levels_to_file(warnings, file_path):
    """
    Saves a list of warning objects to file.

    :param warnings:
    :param file_path:
    :return:
    """

    if os.path.exists(file_path) == False:
        l = open(file_path, 'w')
        l.write('{0}\t{1}\t{2}\t{3}\n'
               .format('Dato', 'Region', 'Faregrad', 'Faregrad'))
    else:
        l = open(file_path, 'a')

    for w in warnings:

        use_encoding = 'utf8'
        #use_encoding = 'latin-1'

        date = w.date
        region = w.region_name
        region = fe.add_norwegian_letters(region, use_encoding=use_encoding)
        danger_level = w.danger_level
        danger_level_name = w.danger_level_name

        if (region != "") and (region != "Hemsedal Skisenter"):
            # add norwegian letters
            s = u'{0}\t{1}\t{2}\t{3}\n'.format(
                date,
                region,
                danger_level,
                danger_level_name)

            l.write(s.encode(use_encoding))
    l.close()


def save_danger_and_problem_to_file(warnings, file_path):
    """
    Saves a list of warning and problems to file.

    :param warnings:
    :param file_path:
    :return:
    """

    if os.path.exists(file_path) == False:
        l = open(file_path, 'w')
        l.write('{0}\t{1}\t{2}\t{3}\t{4}\n'
               .format('Dato', 'Region', 'Faregrad', 'Faregrad', "Svakt lag"))
    else:
        l = open(file_path, 'a')

    for w in warnings:
        use_encoding = 'utf8'
        #use_encoding = 'latin-1'

        date = w.date
        region = w.region_name
        region = fe.add_norwegian_letters(region, use_encoding=use_encoding)
        danger_level = w.danger_level
        danger_level_name = w.danger_level_name

        for p in w.avalanche_problems:
            problem_combined = p.problem_combined
            problem_combined = fe.add_norwegian_letters(problem_combined)

            if (region != "") and (region != "Hemsedal Skisenter"):
                # add norwegian letters
                s = u'{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                    date,
                    region,
                    danger_level,
                    danger_level_name,
                    problem_combined)

                l.write(s.encode(use_encoding))
    l.close()


if __name__ == "__main__":

    # file names
    file_name_for_warnings_pickle = '{0}{1}'.format(se.local_storage, 'runForMainMessage warnings.pickle')
    file_name_for_all_danger_levels_csv = '{0}{1}'.format(se.output_folder, 'Alle varslede faregrader.csv')
    file_name_for_all_danger_and_problems_csv = '{0}{1}'.format(se.output_folder, 'Alle varslede faregrader og problemer.csv')

    # NOTE!! Warnings with problems found in pickle file for main messages. If update needed, use pickle_warnings
    # method in runmainmessage.py
    warnings = mp.unpickle_anything(file_name_for_warnings_pickle)

    # write to files
    save_danger_levels_to_file(warnings, file_name_for_all_danger_levels_csv)
    save_danger_and_problem_to_file(warnings, file_name_for_all_danger_and_problems_csv)

    a = 1