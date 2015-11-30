# -*- coding: utf-8 -*-
__author__ = 'raek'

import pickle


def pickle_anything(something_to_pickle, file_name_and_path, print_message=True):
    '''Pickles anything.

    :param something_to_pickle:
    :param file_name_and_path:
    :return:
    '''

    with open(file_name_and_path, 'w') as f:
        pickle.dump(something_to_pickle, f)

    if print_message is True:
        print 'makepickle.py -> pickle_anything: {0} pickled.'.format(file_name_and_path)


def unpickle_anything(file_name_and_path, print_message=True):
    '''Unpickles anything.

    :param file_name_and_path:
    :return:
    '''

    with open(file_name_and_path) as f:
        something_to_unpickle = pickle.load(f)

    if print_message is True:
        print 'makepickle.py -> unpickle_anything: {0} unpickled.'.format(file_name_and_path)

    return something_to_unpickle

