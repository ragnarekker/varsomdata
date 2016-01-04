# -*- coding: utf-8 -*-
__author__ = 'raek'


import requests
import os.path
import makepickle as mp
import fencoding as fe
import setenvironment as env
import datetime as dt
import collections


def get_kdv(view):
    '''Imports a view view from regObs and returns a dictionary with <key, value> = <ID, Name>
    An view is requested from the regObs api if the pickle file is older thatn 3 days.

    :param view:    [string]    kdv view
    :return dict:   {}          view as a dictionary

    Ex of use: aval_cause_kdv = get_kdv('AvalCauseKDV')
    Ex of url for returning values for IceCoverKDV in norwegian:
    http://api.nve.no/hydrology/regobs/v0.9.4/OData.svc/ForecastRegionKDV?$filter=Langkey%20eq%201%20&$format=json
    '''

    kdv_file_name = '{0}{1}.pickle'.format(env.local_storage, view)
    dict = {}

    if os.path.exists(kdv_file_name):

        max_file_age = 3
        file_date_seconds = os.path.getctime(kdv_file_name)
        file_date_datetime = dt.datetime.fromtimestamp(file_date_seconds)
        file_date_limit = dt.datetime.now() - dt.timedelta(days=max_file_age)

        if file_date_datetime < file_date_limit:
            print "getkdvelements.py -> get_kdv: Removing KDV from local storage: {0}".format(kdv_file_name)
            os.remove(kdv_file_name)
            ordered_dict = get_kdv(view)
        else:
            # print "getkdvelements.py -> get_kdv: Getting KDV from local storage: {0}".format(kdv_file_name)
            ordered_dict = mp.unpickle_anything(kdv_file_name, print_message=False)

    else:

        filter = 'filter=Langkey%20eq%201'

        if 'TripTypeKDV' in view:
            filter = 'filter=LangKey%20eq%201'

        url = 'http://api.nve.no/hydrology/regobs/{0}/OData.svc/{1}?${2}&$format=json'\
            .format(env.api_version, view, filter)

        lang_key = 1

        print "getkdvelements.py -> get_kdv: Getting KDV from URL: {0}".format(url)
        kdv = requests.get(url).json()

        for a in kdv['d']['results']:
            try:
                sort_order = a["SortOrder"]
                is_active = a["IsActive"]

                if 'AvalCauseKDV' in url and 9 < int(a['ID']) < 26:      # this table gets special treatment
                    id = int(a["ID"])
                    name = fe.remove_norwegian_letters(a["Description"])
                    description = fe.remove_norwegian_letters(a["Name"])
                elif 'TripTypeKDV' in view:
                    id = int(a["TripTypeTID"])
                    name = fe.remove_norwegian_letters(a["Name"])
                    description = fe.remove_norwegian_letters(a["Descr"])
                else:
                    id = int(a["ID"])
                    name = fe.remove_norwegian_letters(a["Name"])
                    description = fe.remove_norwegian_letters(a["Description"])

                dict[id] = KDVelement(id, sort_order, is_active, name, description, lang_key)

            except (RuntimeError, TypeError, NameError):
                pass

        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        mp.pickle_anything(ordered_dict, kdv_file_name)

    return ordered_dict


def get_name(view, tid):

    kdv = get_kdv(view)
    name = kdv[tid].Name

    return name


class KDVelement():


    def __init__(self, id_inn, sort_order_inn, is_active_inn, name_inn, description_inn, lang_key_inn):

        self.ID = id_inn
        self.Langkey = lang_key_inn
        self.Name = name_inn
        self.Description = description_inn
        self.IsActive = is_active_inn
        self.SortOrder = sort_order_inn


    def file_output(self, get_header = False):

        if get_header is True:
            return "{0: <5}{1: <7}{2: <10}{3: <10}{4: <50}{5: <50}".format(
                "ID", "Order", "IsActive", "Langkey", "Name", "Description")

        else:
            return "{0: <5}{1: <7}{2: <10}{3: <10}{4: <50}{5: <50}".format(
                self.ID, self.SortOrder, self.IsActive, self.Langkey, self.Name, self.Description)


def write_kdv_dictionary(data, file_name, get_is_active=True, extension='.txt'):
    """Writes a directory to file.

    :param data:        [dictionary of KDVelement()]
    :param file_name:
    :param extension:

    """

    file_name += extension

    with open(file_name, "w") as myfile:
        myfile.write("{0}\n".format( data[0].file_output(get_header=True)) )

        for key, value in data.iteritems():
            if get_is_active is True:
                if value.IsActive is True:
                    myfile.write("{0}\n".format(value.file_output()))
            else:
                myfile.write("{0}\n".format(value.file_output()))


if __name__ == "__main__":

    trigger = get_kdv('AvalancheDangerKDV')
    write_kdv_dictionary(trigger, '{0}AvalancheDangerKDV'.format(env.output_folder))

    danger_sign_kdv = get_kdv('DangerSignKDV')
    write_kdv_dictionary(danger_sign_kdv, '{0}DangerSignKDV'.format(env.output_folder))

    registration_kdv = get_kdv('RegistrationKDV')
    forecast_region_KDV = get_kdv('ForecastRegionKDV')

    write_kdv_dictionary(registration_kdv, "{0}RegistrationKDV".format(env.output_folder))
    write_kdv_dictionary(forecast_region_KDV, "{0}ForecastRegionKDV".format(env.output_folder))

    a = 1