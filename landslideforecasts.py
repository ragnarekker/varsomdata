# -*- coding: utf-8 -*-

import datetime as dt
import csv as csv
from varsomdata import getforecastapi as gfa
from varsomdata import fencoding as fe
import setenvironment as env

__author__ = 'raek'


def get_landslide_warnings_for_Heidi_Bjordal():
    """June 2018: Method finds all landslide warnings for Heidi Bjordal at SVV for a given list of municipalities.
    All warnings are written directly to file without appending much logic."""

    municipality = [1201,   # Bergen
                    1234,   # Granvin
                    1235,   # Voss
                    1238,   # Kvam
                    1242,   # Samnanger
                    1251,   # Vaksdal
                    1252,   # Modalen
                    1263,   # Lindås
                    1804,   # Bodø
                    1833,   # Rana
                    1834,   # Lurøy
                    1836,   # Rødøy
                    1837,   # Meløy
                    1838,   # Gildeskål
                    1840,   # Saltdal
                    1841]   # Fauske

    from_date = dt.date(2013, 1, 1)
    to_date = dt.date(2018, 7, 1)

    landslide_warnings = gfa.get_landslide_warnings_as_json(municipality, from_date, to_date)
    output_file_name = '{0}201807 Jordskredvarsler for Heidi.txt'.format(env.output_folder)

    with open(output_file_name, 'w', encoding='utf-8') as f:
        w = csv.DictWriter(f, landslide_warnings[0].keys(), delimiter=";")
        w.writeheader()
        for lw in landslide_warnings:
            lw['MainText'] = fe.text_cleanup(lw['MainText'])
            lw['WarningText'] = fe.text_cleanup(lw['WarningText'])
            lw['ConsequenceText'] = fe.text_cleanup(lw['ConsequenceText'])
            lw['AdviceText'] = fe.text_cleanup(lw['AdviceText'])
            w.writerow(lw)

    pass


if __name__ == "__main__":

    get_landslide_warnings_for_Heidi_Bjordal()
