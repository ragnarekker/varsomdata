# -*- coding: utf-8 -*-
"""Contains methods for accessing KDV-elements used in regObs.

In regObs, xKDV elements contain the link between an element ID and its name and description.
This is also the contents of drop down choices in regObs. It is useful to have a local copy of
these tables.
"""

import requests
import os.path
import datetime as dt
import collections
from utilities import makepickle as mp
from utilities import makelogs as ml
from varsomdata import varsomclasses as vc
import setenvironment as env

__author__ = 'raek'


def get_kdv(view):
    """Imports a view view from regObs and returns a dictionary with <key, value> = <ID, Name>
    An view is requested from the regObs api if the pickle file is older than 3 days.

    :param view:    [string]    kdv view
    :return dict:   {}          view as a dictionary

    Ex of use: aval_cause_kdv = get_kdv('AvalCauseKDV')
    Ex of url for returning values for IceCoverKDV in norwegian:
    http://api.nve.no/hydrology/regobs/v0.9.4/OData.svc/ForecastRegionKDV?$filter=Langkey%20eq%201%20&$format=json
    """

    kdv_file_name = '{0}{1}.pickle'.format(env.local_storage, view)
    dict = {}

    if os.path.exists(kdv_file_name):

        max_file_age = 3
        # file_date_seconds = os.path.getctime(kdv_file_name)
        file_date_seconds = os.path.getmtime(kdv_file_name)
        file_date_datetime = dt.datetime.fromtimestamp(file_date_seconds)
        file_date_limit = dt.datetime.now() - dt.timedelta(days=max_file_age)

        if file_date_datetime < file_date_limit:
            ml.log_and_print("[info] getkdvelements.py -> get_kdv: Old xKDV. Removing file from local storage: {0}".format(kdv_file_name))
            os.remove(kdv_file_name)
            ordered_dict = get_kdv(view)
            mp.pickle_anything(ordered_dict, kdv_file_name)
        else:
            # ml.log_and_print("[info] getkdvelements.py -> get_kdv: Getting KDV from local storage: {0}".format(kdv_file_name))
            ordered_dict = mp.unpickle_anything(kdv_file_name, print_message=False)

    else:

        filter = 'filter=Langkey%20eq%201'

        if 'TripTypeKDV' in view:
            filter = 'filter=LangKey%20eq%201'

        url = 'https://api.nve.no/hydrology/regobs/{0}/OData.svc/{1}?${2}&$format=json'.format(env.odata_version, view, filter)
        lang_key = 1

        print("getkdvelements.py -> get_kdv: Getting KDV from URL: {0}".format(url))
        kdv = requests.get(url).json()

        for a in kdv['d']['results']:
            try:
                sort_order = a['SortOrder']
                is_active = a['IsActive']

                if 'AvalCauseKDV' in url and 9 < int(a['ID']) < 26:      # this table gets special treatment. Short names are in description and long names are in Name.
                    id = int(a['ID'])
                    name = a['Description']
                    description = a['Name']
                elif 'TripTypeKDV' in view:
                    id = int(a['TripTypeTID'])
                    name = a['Name']
                    description = a['Descr']
                else:
                    id = int(a['ID'])
                    name = a['Name']
                    description = a['Description']

                dict[id] = vc.KDVelement(id, sort_order, is_active, name, description, lang_key)

            except (RuntimeError, TypeError, NameError):
                pass

        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        mp.pickle_anything(ordered_dict, kdv_file_name)

    return ordered_dict


def get_name(view, tid):
    """Gets a Name-value given ist value and the KDV-view it belongs to.

    :param view:    [string]
    :param tid:     [int]
    :return name:   [string]
    """

    kdv = get_kdv(view)
    name = kdv[tid].Name

    return name


def write_kdv_dictionary(data, file_name, get_is_active=True, extension='.txt'):
    """Writes a kdv dictionary to file.

    :param data:        [dictionary of KDVelement()]
    :param file_name:
    :param extension:
    """

    file_name += extension

    with open(file_name, 'w', encoding='utf-8') as my_file:
        my_file.write('{0}\n'.format( data[0].file_output(get_header=True)) )

        for key, value in data.items():
            if get_is_active is True:
                if value.IsActive is True:
                    my_file.write('{0}\n'.format(value.file_output()))
            else:
                my_file.write('{0}\n'.format(value.file_output()))


if __name__ == '__main__':

    # cause_kdv = get_kdv('AvalCauseKDV')
    # write_kdv_dictionary(cause_kdv, '{0}AvalCauseKDV'.format(env.output_folder))
    #
    # cause_ext_kdv = get_kdv('AvalCauseExtKDV')
    # write_kdv_dictionary(cause_ext_kdv, '{0}AvalCauseExtKDV'.format(env.output_folder))
    #
    # snow_surface_kdv = get_kdv('SnowSurfaceKDV')
    # write_kdv_dictionary(snow_surface_kdv, '{0}SnowSurfaceKDV'.format(env.output_folder))
    #
    # danger = get_kdv('AvalancheDangerKDV')
    # write_kdv_dictionary(danger, '{0}AvalancheDangerKDV'.format(env.output_folder))
    #
    # danger_sign_kdv = get_kdv('DangerSignKDV')
    # write_kdv_dictionary(danger_sign_kdv, '{0}DangerSignKDV'.format(env.output_folder))
    #
    # registration_kdv = get_kdv('RegistrationKDV')
    # write_kdv_dictionary(registration_kdv, '{0}RegistrationKDV'.format(env.output_folder))
    #
    # damage_extent_kdv = get_kdv('DamageExtentKDV')
    # write_kdv_dictionary(damage_extent_kdv, '{0}DamageExtentKDV'.format(env.output_folder))
    #
    # avalanche_ext_kdv = get_kdv('AvalancheExtKDV')
    # avalanche_kdv = get_kdv('AvalancheKDV')
    #
    forecast_region_KDV = get_kdv('ForecastRegionKDV')
    write_kdv_dictionary(forecast_region_KDV, '{0}ForecastRegionKDV'.format(env.output_folder))

    a = 1