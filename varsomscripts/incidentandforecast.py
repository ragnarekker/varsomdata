# -*- coding: utf-8 -*-
"""At request we make data for people needing information on incidents in regions over a period, on incidents
in regions mapped to danger levels og avalanche problems forecasted or observed. Sometimes incidents raw from
regObs (untouched by human hands) or sometimes from the data sett on varsom; the select data sett of incidents
that are quality checked to some degree. All the scripts to make data is in this module."""

from varsomdata import getdangers as gd
from varsomdata import getobservations as go
from utilities import makepickle as mp
from varsomdata import getmisc as gm
from utilities import fencoding as fe
from utilities import makemisc as mm
import setenvironment as env
import datetime as dt


__author__ = 'raek'

def make_forecasts_at_incidents_for_mala(get_new=False):
    """Lager csv med alle varsomhendelser sammen med faregrad og de aktuelle skredproblemene
    (svakt lag, skredtype og skredproblemnavnert). Der det er gjort en regObs observasjon
    med «hendelse/ulykke» skjema fylt ut har jeg også lagt på skadeomfangsvurderingen.
    """

    pickle_file_name = '{0}dl_inci_mala.pickle'.format(env.local_storage)
    output_incident_and_dl = '{0}incidents_mala.csv'.format(env.output_folder)


    if get_new:
        varsom_incidents = gm.get_varsom_incidents(add_forecast_regions=True, add_forecasts=True, add_observations=False)
        mp.pickle_anything(varsom_incidents, pickle_file_name)
    else:
        varsom_incidents = mp.unpickle_anything(pickle_file_name)

    incident_and_dl = []

    for i in varsom_incidents:

        incident_date = i.date
        danger_level = None

        problem_1 = None
        problem_2 = None
        problem_3 = None

        avalanche_type_1 = None
        avalanche_type_2 = None
        avalanche_type_3 = None

        weak_layer_1 = None
        weak_layer_2 = None
        weak_layer_3 = None

        dato_regobs = None
        damage_extent = None

        if i.forecast:
            danger_level = i.forecast.danger_level
            for p in i.forecast.avalanche_problems:
                if p.order == 1:
                    problem_1 = p.problem
                    weak_layer_1 = p.cause_name
                    avalanche_type_1 = p.aval_type
                if p.order == 2:
                    problem_2 = p.problem
                    weak_layer_2 = p.cause_name
                    avalanche_type_2 = p.aval_type
                if p.order == 3:
                    problem_3 = p.problem
                    weak_layer_3 = p.cause_name
                    avalanche_type_3 = p.aval_type

            if i.observations:
                dato_regobs = i.observations[0].DtObsTime.date()
                for obs in i.observations:
                    for o in obs.Observations:
                        if isinstance(o, go.Incident):
                            damage_extent = o.DamageExtentName

        incident_and_dl.append({'Date': incident_date,
                                # 'Dato (regObs)': dato_regobs,
                                'Region_id': i.region_id,
                                'Region': i.region_name,
                                'Fatalities': i.fatalities,
                                'Damage_extent': damage_extent,
                                'People_involved': i.people_involved,
                                'Activity': i.activity,
                                'Danger_level': danger_level,
                                'Avalanche_problem_1': problem_1,
                                'Avalanche_type_1': avalanche_type_1,
                                'Weak_layer_1': weak_layer_1,
                                'Avalanche_problem_2': problem_2,
                                'Avalanche_type_2': avalanche_type_2,
                                'Weak_layer_2': weak_layer_2,
                                'Avalanche_problem_3': problem_3,
                                'Avalanche_type_3': avalanche_type_3,
                                'Weak_layer_3': weak_layer_3,
                                'Comment': i.comment,
                                'regObs_id': '{}'.format(i.regid)})

    # Write observed problems to file
    with open(output_incident_and_dl, 'w', encoding='utf-8') as f:
        make_header = True
        for i in incident_and_dl:
            if make_header:
                f.write(';'.join([fe.make_str(d) for d in i.keys()]) + '\n')
                make_header = False
            f.write(';'.join([fe.make_str(d) for d in i.values()]).replace('[', '').replace(']', '') + '\n')


def make_forecasts_at_incidents_for_sander():
    """Lager csv med alle varsomhendelser sammen med faregrad og de aktuelle skredproblemene 
    (svakt lag, skredtype og skredproblemnavnert). Der det er gjort en regObs observasjon 
    med «hendelse/ulykke» skjema fylt ut har jeg også lagt på skadeomfangsvurderingen.

    August 2018: Hei Jostein.

    Som du veit skal eg skriva om: Skredulykker knytt til skredproblem
    Du snakka om at det var muleg å få ut data for dette frå NVE sin database. Kan du hjelpa meg med det?

    Mvh
    Sander
    """

    pickle_file_name = '{0}dl_inci_sander.pickle'.format(env.local_storage)
    output_incident_and_dl = '{0}Hendelse og faregrad til Sander.csv'.format(env.output_folder)
    get_new = False

    if get_new:
        varsom_incidents = gm.get_varsom_incidents(add_forecast_regions=True, add_forecasts=True, add_observations=True)
        mp.pickle_anything(varsom_incidents, pickle_file_name)
    else:
        varsom_incidents = mp.unpickle_anything(pickle_file_name)

    incident_and_dl = []

    for i in varsom_incidents:

        incident_date = i.date
        danger_level = None

        problem_1 = None
        problem_2 = None
        problem_3 = None

        avalanche_type_1 = None
        avalanche_type_2 = None
        avalanche_type_3 = None

        weak_layer_1 = None
        weak_layer_2 = None
        weak_layer_3 = None

        dato_regobs = None
        damage_extent = None

        if i.forecast:
            danger_level = i.forecast.danger_level
            for p in i.forecast.avalanche_problems:
                if p.order == 1:
                    problem_1 = p.problem
                    weak_layer_1 = p.cause_name
                    avalanche_type_1 = p.aval_type
                if p.order == 2:
                    problem_2 = p.problem
                    weak_layer_2 = p.cause_name
                    avalanche_type_2 = p.aval_type
                if p.order == 3:
                    problem_3 = p.problem
                    weak_layer_3 = p.cause_name
                    avalanche_type_3 = p.aval_type

            if i.observations:
                dato_regobs = i.observations[0].DtObsTime.date()
                for obs in i.observations:
                    for o in obs.Observations:
                        if isinstance(o, go.Incident):
                            damage_extent = o.DamageExtentName

        incident_and_dl.append({'Dato': incident_date,
                                # 'Dato (regObs)': dato_regobs,
                                'Region': i.region_name,
                                'Kommune': i.municipality,
                                'Dødsfall': i.fatalities,
                                'Alvorsgrad': damage_extent,
                                'Involverte': i.people_involved,
                                'Aktivitet': i.activity,
                                'Faregrad': danger_level,
                                'Skredproblem 1': problem_1,
                                'Skredtype 1': avalanche_type_1,
                                'Svaktlag 1': weak_layer_1,
                                'Skredproblem 2': problem_2,
                                'Skredtype 2': avalanche_type_2,
                                'Svaktlag 2': weak_layer_2,
                                'Skredproblem 3': problem_3,
                                'Skredtype 3': avalanche_type_3,
                                'Svaktlag 3': weak_layer_3,
                                'Kommentar': i.comment,
                                'regObs': '{}'.format(i.regid)})

    # Write observed problems to file
    with open(output_incident_and_dl, 'w', encoding='utf-8') as f:
        make_header = True
        for i in incident_and_dl:
            if make_header:
                f.write(' ;'.join([fe.make_str(d) for d in i.keys()]) + '\n')
                make_header = False
            f.write(' ;'.join([fe.make_str(d) for d in i.values()]).replace('[', '').replace(']', '') + '\n')


def make_dl_incident_markus(get_new=False):
    """
    From the beginning of time:

    get all forecasts.
    and then get how many on dl 3.

    get all incidents,
    excpt elrapp, and all in back country

    all these, get all on days in regions of dl 3.
    get all with serious caracter on days and in regions on dl 3

    :return:
    """

    pickle_file_name = '{0}incident_on_dl3_for_markus.pickle'.format(env.local_storage)
    years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-2018', '2018-2019']


    all_dangers = []
    all_incidents = []

    if get_new:
        for y in years:

            # get forecast regions used this year
            from_date, to_date = gm.get_forecast_dates(y)

            # get incidents for this year and map to this years forecast regions
            this_year_incidents = go.get_incident(from_date, to_date, geohazard_tids=10)
            for i in this_year_incidents:
                utm33x = i.UTMEast
                utm33y = i.UTMNorth
                region_id, region_name = gm.get_forecast_region_for_coordinate(utm33x, utm33y, y)
                i.region_regobs_id = region_id
                i.region_name = region_name
            all_incidents += this_year_incidents

            # get regions and the forecasts used this year
            region_ids = gm.get_forecast_regions(y)
            all_dangers += gd.get_forecasted_dangers(region_ids, from_date, to_date)

        # in the end, pickle it all
        mp.pickle_anything([all_dangers, all_incidents], pickle_file_name)

    else:
        [all_dangers, all_incidents] = mp.unpickle_anything(pickle_file_name)

    all_dl3 = []
    for d in all_dangers:
        if d.danger_level == 3:
            all_dl3.append(d)

    all_back_country_incidents = []
    for i in all_incidents:
        if 'drift@svv' not in i.NickName:
            # if activity influenced is backcounty og scooter
            # should probably include 100 which is non specified incidents
            # giving this dataset the observations not specified
            if i.ActivityInfluencedTID in [100, 110, 111, 112, 113, 114, 115, 116, 117, 130]:
                all_back_country_incidents.append(i)

    all_back_country_incidents_with_consequence = []
    for i in all_back_country_incidents:
        # If damageextent is nestenulykke, personer skadet eller personer omkommet
        if i.DamageExtentTID > 28:
            all_back_country_incidents_with_consequence.append(i)

    # find incidents in regions on days with danger level 3
    # find incidetns in region on day with dl3
    all_back_country_incidents_on_region_dl3 = []
    all_back_country_incidents_with_consequence_on_region_dl3 = []

    for d in all_dl3:
        danger_date = d.date
        danger_region_id = d.region_regobs_id

        for i in all_back_country_incidents:
            incident_date = i.DtObsTime.date()
            incident_region_id = i.ForecastRegionTID
            if incident_date == danger_date and incident_region_id == danger_region_id:
                all_back_country_incidents_on_region_dl3.append(i)

        for i in all_back_country_incidents_with_consequence:
            incident_date = i.DtObsTime.date()
            incident_region_id = i.ForecastRegionTID
            if incident_date == danger_date and incident_region_id == danger_region_id:
                all_back_country_incidents_with_consequence_on_region_dl3.append(i)

    print('Totalt varsler laget siden tidenes morgen: {}'.format(len(all_dangers)))
    print('Totalt varsler på fg 3: {}'.format(len(all_dl3)))
    print('Totalt antall hendelser i baklandet: {}'.format(len(all_back_country_incidents)))
    print('Totalt antall hendelser i baklandet med konsekvens: {}'.format(len(all_back_country_incidents_with_consequence)))
    print('Totalt antall hendelser i baklandet i regioner på dager med fg3: {}'.format(len(all_back_country_incidents_on_region_dl3)))
    print('Totalt antall hendelser i baklandet i regioner på dager med fg3 med konsekvens: {}'.format(len(all_back_country_incidents_with_consequence_on_region_dl3)))

    return


def incident_troms_winter_2018_for_markus():
    """Communication dated 2018-11-29

    Hei Ragnar og Jostein

    Kan en av dere hjelpe meg å ta ut et plott som viser antall registrerte ulykker og hendelser i
    varslingsregionene Tromsø, Lyngen, Sør-Troms og Indre-Troms for
    perioden 15.02 – 15.05.

    ...

    Er du interessert i det som ligger i registrert i
    regObs eller det som er kvalitetssikkert data  og ligger på varsom?

    Skal du ha hendelser som har hatt konsekvens?

    Skal hendelsene plottes i tid eller vises i kart?

    ...

    Varsom
    Ikke nødvendigvis konsekvens
    Tid

    :return:
    """

    pickle_file_name = '{0}incident_troms_winter_2018_for_markus.pickle'.format(env.local_storage)
    from_date = dt.date(2018, 2, 15)   # '2018-02-15'
    to_date = dt.date(2018, 5, 15)    # '2018-05-15'

    # Tromsø, Lyngen, Sør-Troms og Indre-Troms
    regions = [3011, 3010, 3012, 3013]

    get_new = False

    if get_new:
        all_varsom_incidents = gm.get_varsom_incidents(add_forecast_regions=True, add_observations=True)
        all_regobs_avalobs_and_incidents = go.get_all_observations(from_date, to_date, registration_types=[11, 26], region_ids=regions, output='List')

        mp.pickle_anything([all_varsom_incidents, all_regobs_avalobs_and_incidents], pickle_file_name)

    else:
        [all_varsom_incidents, all_regobs_avalobs_and_incidents] = mp.unpickle_anything(pickle_file_name)

    varsom_incidents = mm.make_date_int_dict(start_date=from_date, end_date=to_date)
    regobs_avalobs_and_incidents = mm.make_date_int_dict(start_date=from_date, end_date=to_date)

    for i in all_varsom_incidents:
        if from_date <= i.date <= to_date:
            if i.region_id in regions:
                if i.date in varsom_incidents.keys():
                    varsom_incidents[i.date] += 1

    for i in all_regobs_avalobs_and_incidents:
        if from_date <= i.DtObsTime.date() <= to_date:
            if i.ForecastRegionTID in regions:
                if i.DtObsTime.date() in regobs_avalobs_and_incidents.keys():
                    regobs_avalobs_and_incidents[i.DtObsTime.date()] += 1

    sum_varsom = sum(varsom_incidents.values())
    sum_regobs = sum(regobs_avalobs_and_incidents.values())

    varsom_incident_troms_winter_2018_for_markus = '{0}varsom_incident_troms_winter_2018_for_markus.csv'.format(env.output_folder)
    regobs_incident_troms_winter_2018_for_markus = '{0}regobs_incident_troms_winter_2018_for_markus.csv'.format(env.output_folder)

    with open(varsom_incident_troms_winter_2018_for_markus, 'w', encoding='utf-8') as f:
        make_header = True
        for k, v in varsom_incidents.items():
            if make_header:
                f.write('date; number\n')
                make_header = False
            f.write('{}; {}\n'.format(k, v))

    with open(regobs_incident_troms_winter_2018_for_markus, 'w', encoding='utf-8') as f:
        make_header = True
        for k, v in regobs_avalobs_and_incidents.items():
            if make_header:
                f.write('date; number\n')
                make_header = False
            f.write('{}; {}\n'.format(k, v))

    pass


if __name__ == "__main__":

    # make_dl_incident_markus(True)
    make_forecasts_at_incidents_for_mala(True)
    # make_forecasts_at_incidents_for_sander()
    #incident_troms_winter_2018_for_markus()
