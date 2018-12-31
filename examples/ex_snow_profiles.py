# -*- coding: utf-8 -*-
"""This is an example of how varsomdata/getobservations.py may be used to get observations
from regObs webapi - http://api.nve.no/doc/regobs-webapi/

It takes time to make requests. Progress can be followed in the log files.
"""

from varsomdata import getobservations as go

__author__ = 'raek'

# get snow profiles during a period
snow_profiles = go.get_snow_profile('2018-12-13', '2018-12-26')

# look for profiles with persistent weak layers. Loop through all.
profiles_with_prec_weak_layers = []
for p in snow_profiles:

    # look at the stratigraphic profiles
    strat_profile = p.StratProfile

    # if layers have buried (sort order > 0) grain type of persistent weak layer, add it.
    for l in strat_profile:

        grain_form_name = l.GrainFormPrimaryName

        # surface hoar (SH) and depth hoar (DH) qualifies.
        if 'SH' in grain_form_name or 'DH' in grain_form_name:
            if l.SortOrder > 0:
                profiles_with_prec_weak_layers.append(p)

        # Large facets (FC > 3mm) qualifies.
        elif 'FC' in grain_form_name:
            if l.SortOrder > 0:
                if l.GrainSizeAvg >= 0.003:
                    profiles_with_prec_weak_layers.append(p)

print("Profiles hinting of persistent weak layers: \n")
for pwl in profiles_with_prec_weak_layers:
    print("{}, \t{}, \t{}, \thttps://www.regobs.no/Registration/{}".format(pwl.ForecastRegionName, pwl.DtObsTime, pwl.NickName, pwl.RegID))
