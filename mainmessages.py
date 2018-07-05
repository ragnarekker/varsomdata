# -*- coding: utf-8 -*-

from varsomdata import getforecastapi as gfa
from varsomdata import makepickle as mp
from varsomdata import getmisc as gm
from varsomdata import fencoding as fe
from varsomdata import setcoreenvironment as cenv
from varsomdata import readfile as rf
import os.path
import operator
import setenvironment as env

__author__ = 'raek'


class MainMessage:
    """Special class for this problem. Thus not a separate file.

    The main message in norwegian and english. Danger levels and a selection of values for the avalanche
    problems where the main message is used are put in lists. Occurrences in the data can also be saved.
    """


    def __init__(self, main_message_no_inn):

        self.main_message_no = main_message_no_inn  # String
        self.main_message_en = None                 # String
        self.danger_levels = {}                     # dictionary of values and count
        self.problems = {}                          # dictionary of values and count
        self.cause_names = {}                       # dictionary of values and count
        self.aval_types = {}                        # dictionary of values and count
        self.aval_triggers = {}                     # dictionary of values and count
        self.occurrences = 1                        # int, on initialization it has occurred once


    def add_main_message_en(self, main_message_en_inn):
        self.main_message_en = main_message_en_inn


    def add_to_danger_levels(self, danger_level_inn):
        danger_level_inn = 'Fg{0}'.format(danger_level_inn)
        if danger_level_inn not in self.danger_levels.keys():
            self.danger_levels[danger_level_inn] = 1
        else:
            self.danger_levels[danger_level_inn] = self.danger_levels[danger_level_inn] + 1


    def add_to_problems(self, problem_inn):
        if problem_inn not in self.problems.keys():
            self.problems[problem_inn] = 1
        else:
            self.problems[problem_inn] = self.problems[problem_inn] + 1


    def add_to_cause_names(self, cause_name_inn):
        cause_name_inn = cause_name_inn.replace(' / ', '/')
        if cause_name_inn not in self.cause_names.keys():
            self.cause_names[cause_name_inn] = 1
        else:
            self.cause_names[cause_name_inn] = self.cause_names[cause_name_inn] + 1


    def add_to_aval_types(self, aval_type_inn):
        if aval_type_inn not in self.aval_types.keys():
            self.aval_types[aval_type_inn] = 1
        else:
            self.aval_types[aval_type_inn] = self.aval_types[aval_type_inn] + 1


    def add_to_aval_triggers(self, aval_trigger_inn):
        if aval_trigger_inn not in self.aval_triggers.keys():
            self.aval_triggers[aval_trigger_inn] = 1
        else:
            self.aval_triggers[aval_trigger_inn] = self.aval_triggers[aval_trigger_inn] + 1


    def add_occurrence(self):
        self.occurrences = self.occurrences + 1


class MainMessageInAdmin:

    def __init__(self, row):

        self.AvalancheDangerId = row[0]
        self.AvalancheProblemTypeId1 = row[1]
        self.AvalancheProblemTypeId2 = row[2]
        self.AvalancheProblemTypeId3 = row[3]
        self.AvalancheTriggerId = row[4]
        self.LangKey = int(row[5])
        self.Id = int(row[6])
        self.Text = row[7]


def _messages_found_in_admin(file_name):
    """Loads a list of messages found in admin and returns the norwegian ones as a list.

    :param file_name:   [string] Full path of the file contaning the main messages found in admin
    :return:            [list of strings]
    """

    main_messages_in_admin = rf.read_csv_file(file_name, MainMessageInAdmin)
    main_messages_no = []

    for m in main_messages_in_admin:
        if m.LangKey == 1:
            main_messages_no.append(fe.text_cleanup(m.Text))

    return main_messages_no


def _get_main_message_object(message_no, main_messages):
    """Returns the main message object reference if the main message in Norwegian is in
    the list of main messages.

    :param message_no:
    :param main_messages:
    :return:
    """

    for m in main_messages:
        if message_no == m.main_message_no:
            return m

    return None


def _message_no_is_in_list(message_no, main_messages):
    """Returns True if the main message in Norwegian is in the list of main messages.

    :param message_no:
    :param main_messages:
    :return:
    """

    is_in_list = False

    for m in main_messages:
        if message_no == m.main_message_no:
            is_in_list = True

    return is_in_list


def pickle_warnings(regions, date_from, date_to, pickle_file_name):
    """All warnings and problems are selected from regObs or the avalanche api and neatly pickel'd for later use.
    This method also gets all warnings in english for the english main message.

    :param regions:             [int or list of ints] RegionID as given in the forecast api
    :param date_from:           [date or string as yyyy-mm-dd]
    :param date_to:             [date or string as yyyy-mm-dd]
    :param pickle_file_name:    filename including directory as string

    :return:
    """

    warnings = []

    # get all warning and problems for this region and then loop though them joining them on date
    for r in regions:
        warnings_no = gfa.get_warnings(r, date_from, date_to)
        warnings_en = gfa.get_warnings(r, date_from, date_to, lang_key=2)

        # loop trough all the norwegian forecasts
        for i in range(0, len(warnings_no), 1):

            # add english main message with same dates
            for k in range(0, len(warnings_en), 1):

                if warnings_no[i].date == warnings_en[k].date:
                    warnings_no[i].set_main_message_en(warnings_en[k].main_message_en)
                    continue

        warnings = warnings + warnings_no

    mp.pickle_anything(warnings, pickle_file_name)


def select_messages_with_more(pickle_warnings_file_name):
    """Method selects unique messages and adds the english name to them (english name that appeared on the first
    occurrence), adds the danger levels, main causes, causes, and avalanche types that are used to this main
    message. There is also a count of how many times the main text has occurred.

    :param pickle_warnings_file_name    filename to where the pickle file with the warnings are located
    :return main_messages               list of MainMessage objects ordered by most occurrences first
    """

    warnings = mp.unpickle_anything(pickle_warnings_file_name)
    main_messages_in_admin = _messages_found_in_admin('{}mainmessages.20180704.csv'.format(cenv.input_folder))
    main_messages = []

    for w in warnings:

        message_no = w.main_message_no
        message_no = fe.text_cleanup(message_no)

        # if no content
        if 'Ikke vurdert.' in message_no:
            continue

        if message_no == '':
            continue

        if message_no in main_messages_in_admin:
            continue

        # if message exists in list append changes to it
        if _message_no_is_in_list(message_no, main_messages):
            m = _get_main_message_object(message_no, main_messages)
            m.add_occurrence()
            m.add_to_danger_levels(w.danger_level)

            for p in w.avalanche_problems:
                m.add_to_problems(p.problem)
                m.add_to_cause_names(p.cause_name)
                m.add_to_aval_types(p.aval_type)
                m.add_to_aval_triggers(p.aval_trigger)

        # if not append a new one
        else:
            new_m = MainMessage(message_no)
            new_m.add_main_message_en(w.main_message_en)
            new_m.add_to_danger_levels(w.danger_level)

            for p in w.avalanche_problems:
                new_m.add_to_problems(p.problem)
                new_m.add_to_cause_names(p.cause_name)
                new_m.add_to_aval_types(p.aval_type)
                new_m.add_to_aval_triggers(p.aval_trigger)

            main_messages.append(new_m)

    # sort on main_message_no
    main_messages.sort(key=lambda m: m.main_message_no, reverse=False)

    # sort on occurrences
    # main_messages.sort(key=lambda m: m.occurrences, reverse=True)

    return main_messages


def save_main_messages_to_file(main_messages, file_path):
    """Saves a list of main message objects to file.

    :param main_messages:
    :param file_path:
    :return:
    """

    if os.path.exists(file_path) == False:
        l = open(file_path, 'w', encoding='utf-8')
        l.write('{0};{1};{2};{3};{4};{5};{6}\n'
               .format('Antall', 'Faregrad', 'Skredproblem', 'Skredutløser','Svakt lag', 'Skredtype',
               'Hovedbudskap norsk', 'Hovedbudskap engelsk'))
    else:
        l = open(file_path, 'a', encoding='utf-8')

    for m in main_messages:

        # sort the keys according to which is used most
        danger_levels = sorted(m.danger_levels.items(), key=operator.itemgetter(1), reverse=True)
        problems = sorted(m.problems.items(), key=operator.itemgetter(1), reverse=True)
        cause_names = sorted(m.cause_names.items(), key=operator.itemgetter(1), reverse=True)
        aval_types = sorted(m.aval_types.items(), key=operator.itemgetter(1), reverse=True)
        aval_triggers = sorted(m.aval_triggers.items(), key=operator.itemgetter(1), reverse=True)

        # join (the now after sorting, lists) to strings
        danger_levels = ', '.join("{!s} ({!r})".format(key,val) for (key,val) in danger_levels)
        problems = ', '.join("{!s} ({!r})".format(key,val) for (key,val) in problems)
        cause_names = ', '.join("{!s} ({!r})".format(key,val) for (key,val) in cause_names)
        aval_types = ', '.join("{!s} ({!r})".format(key,val) for (key,val) in aval_types)
        aval_triggers = ', '.join("{!s} ({!r})".format(key,val) for (key,val) in aval_triggers)

        s = u'{0};{1};{2};{3};{4};{5};{6};{7}\n'.format(
            m.occurrences,
            danger_levels,
            problems,
            aval_triggers,
            cause_names,
            aval_types,
            m.main_message_no,
            m.main_message_en)

        l.write(s)
    l.close()


if __name__ == "__main__":

    year = '2017-18'
    regions = gm.get_forecast_regions(year=year)
    date_from, date_to = gm.get_dates_from_season(year=year)

    # file names
    file_name_for_warnings_pickle = '{0}{1}'.format(env.local_storage, 'runmainmessage warnings.pickle')
    file_name_for_main_messages_pickle = '{0}{1}'.format(env.local_storage, 'runmainmessage main messages.pickle')
    file_name_for_main_messages_csv = '{0}{1}'.format(env.output_folder, 'Alle hovedbudskap {}.csv'.format(year))

    ##### pickle the warnings and dataset with main messages
    # pickle_warnings(regions, date_from, date_to, file_name_for_warnings_pickle)
    main_messages = select_messages_with_more(file_name_for_warnings_pickle)
    mp.pickle_anything(main_messages, file_name_for_main_messages_pickle)
    main_messages = mp.unpickle_anything(file_name_for_main_messages_pickle)

    # write to file
    save_main_messages_to_file(main_messages, file_name_for_main_messages_csv)

    pass
