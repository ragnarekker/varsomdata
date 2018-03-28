# -*- coding: utf-8 -*-
from varsomdata import getobservations as go
from varsomdata import getforecastapi as gfa
from varsomdata import getmisc as gm
from varsomdata import makepickle as mp
from varsomdata import makelogs as ml
import setenvironment as env
import collections as cols
import os as os
import datetime as dt

__author__ = 'ragnarekker'


def _get_all(get_new=False, from_date='2012-10-01', to_date='2018-01-01'):
    """Get all observations (only the meta data) for all time. Useful for statistics."""

    file_name = '{}all observations.pickle'.format(env.local_storage)

    if not os.path.exists(file_name):
        get_new = True
        ml.log_and_print('observations.py -> _get_all: pickle missing, getting new data.', print_it=True)

    if get_new:
        all_observations = go.get_all_registrations(from_date, to_date)
        mp.pickle_anything(all_observations, file_name)
    else:
        all_observations = mp.unpickle_anything(file_name)

    return all_observations


def _get_all_snow(get_new=False):

    file_name = '{}observations and forecasts 2012-17.pickle'.format(env.local_storage)

    if get_new:
        all_observations = go.get_all_registrations('2012-12-01', '2017-07-01', geohazard_tids=10)

        years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17']
        all_forecasts = []
        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            region_ids = gm.get_forecast_regions(y)
            all_forecasts += gfa.get_warnings(region_ids, from_date, to_date)

        mp.pickle_anything([all_observations, all_forecasts], file_name)

    else:
        [all_observations, all_forecasts] = mp.unpickle_anything(file_name)

    return all_observations, all_forecasts


def _make_date_list_dict(start_date=dt.date(2012, 10, 1), end_date=dt.date.today()):

    num_days = (end_date-start_date).days
    date_list = [start_date + dt.timedelta(days=x) for x in range(0, num_days)]

    date_dict = cols.OrderedDict()
    for d in date_list:
        date_dict[d] = []

    return date_dict


def _make_date_int_dict(start_date=dt.date(2012, 10, 1), end_date=dt.date.today()):

    num_days = (end_date-start_date).days
    date_list = [start_date + dt.timedelta(days=x) for x in range(0, num_days)]

    date_dict = cols.OrderedDict()
    for d in date_list:
        date_dict[d] = 0

    return date_dict


def find_fun_facts():
    """
    Antall observasjoner totalt
    Andre spm: kva region hadde(prosentvis?) flest obs av vedvarande svakt lag?
    Antall observasjoner i Trollheimen?
    Hvilket svakt lag ble mest observert i 2016-17 (i Hallingfjella)?

    Andel observasjoner med *** eller mer?
    Antall bilder total?
    Antall skredhendelser observert?

    Antall observasjoner på fg 4?
    Antall observasjoner på fg 1?

    :return:
    """

    obs, fore = _get_all_snow(get_new=False)

    num_regtypes = {}
    num_competance = {}

    num_pr_date = _make_date_int_dict()          # antall obs pr dag
    obs_pr_date = _make_date_list_dict()         # alle obs gruppert på dato
    num_pr_region = {}
    obs_pr_region = {}
    num_persweek_pr_region = {}
    obs_persweek_pr_region = {}

    num_serious_incidents = 0

    for o in obs:

        registration_name = o.RegistrationName
        if registration_name in num_regtypes.keys():
            num_regtypes[registration_name] += 1
        else:
            num_regtypes[registration_name] = 0

        competance_level = o.CompetenceLevelName
        if competance_level in num_competance.keys():
            num_competance[competance_level] += 1
        else:
            num_competance[competance_level] = 0

        if 'Ulykke' in registration_name:
            if o.FullObject['DamageExtentTID'] in [29, 30, 40]:
                num_serious_incidents += 1

        date = o.DtObsTime.date()
        num_pr_date[date] += 1
        obs_pr_date[date].append(o)

        # observations pr region
        region_id = o.ForecastRegionTID
        if region_id in num_pr_region.keys():
            num_pr_region[region_id] += 1
            obs_pr_region[region_id].append(o)
        else:
            num_pr_region[region_id] = 1
            obs_pr_region[region_id] = [o]

        # persistent weak layers in regions
        if 'Skredproblem' in o.RegistrationName:
            if o.FullObject['AvalCauseTID'] in [11, 13, 16, 17, 18, 19]:
                if region_id in num_persweek_pr_region.keys():
                    num_persweek_pr_region[region_id] += 1
                    obs_persweek_pr_region[region_id].append(o)
                else:
                    num_persweek_pr_region[region_id] = 1
                    obs_persweek_pr_region[region_id] = [o]

    aval_cause_halling = {}
    for o in obs_pr_region[3032]:
        if 'Skredproblem' in o.RegistrationName:
            aval_cause = o.FullObject['AvalCauseTName']
            if aval_cause in aval_cause_halling.keys():
                aval_cause_halling[aval_cause] += 1
            else:
                aval_cause_halling[aval_cause] = 1

    region_id_name = {}
    for k, v in obs_pr_region.items():
        region_id_name[k] = v[0].ForecastRegionName

    print('Antall snø observasjoner fra tidenes morgen: {}'.format(len(obs)))
    print('Antall snø observasjoner i Trollheimen fra tidenes morgen: {}'.format(num_pr_region[3022]))
    print('Antal hendelser med nestenulykke, personskade eller dødsfall registrert: {}'.format(num_serious_incidents))
    print('Antall bilder registrert: {}'.format(num_regtypes['Bilde']))
    print('Mest observerte svake laget i Hallingdal er Nedføyka lag av nysnø med 157 av totalt {} skredproblemer observert.'.format(sum(aval_cause_halling.values())))
    print('Nest mest observerte svake laget i Hallingdal er Dårlig binding mellom lag i fokksnøen med 145 observasjoner.')
    print('Regionen med flest observerte vedvarende svake lag er Jotunheimen med 236 av totalt {} observasjoner med vedvarende svake lag.'.format(sum(num_persweek_pr_region.values())))
    print('Regionen med nest flest observerte vedvarende svake lag er Hallingdal med 204 observerte problemer.')
    print('Antall observasjoner levert med *** eller høyere kompetanse: {}'.format(num_competance['***']+ num_competance['****']+num_competance['*****']))

    #obs_old_coords = _map_obs_to_old_regions(obs, make_new=False)

    # num_dl4_pr_region = {}
    # for_dl4_pr_region = {}
    # num_dl1_pr_region = {}
    # for_dl1_pr_region = {}
    # for f in fore:
    #     region_id = f.region_regobs_id
    #     if region_id > 2999:
    #         # danger level 4 pr region
    #         if f.danger_level == 4:
    #             if region_id in num_dl4_pr_region.keys():
    #                 num_dl4_pr_region[region_id] += 1
    #                 for_dl4_pr_region[region_id].append(f)
    #             else:
    #                 num_dl4_pr_region[region_id] = 1
    #                 for_dl4_pr_region[region_id] = [f]
    #
    #         if f.danger_level == 1:
    #             if region_id in num_dl1_pr_region.keys():
    #                 num_dl1_pr_region[region_id] += 1
    #                 for_dl1_pr_region[region_id].append(f)
    #             else:
    #                 num_dl1_pr_region[region_id] = 1
    #                 for_dl1_pr_region[region_id] = [f]

    dl_count = {}
    for f in fore:
        dl = f.danger_level
        if dl in dl_count.keys():
            dl_count[dl] += 1
        else:
            dl_count[dl] = 1

    print('Antall varsel siden vi startet: {}'.format(dl_count[1] + dl_count[2] + dl_count[3] + dl_count[4]))
    print('Antall dager med fg 5: 0')
    print('Antall dager med fg 4: {}'.format(dl_count[4]))
    print('Antall dager med fg 3: {}'.format(dl_count[3]))
    print('Antall dager med fg 2: {}'.format(dl_count[2]))
    print('Antall dager med fg 1: {}'.format(dl_count[1]))


    return

    # obs_by_date = cols.OrderedDict(sorted(obs_by_date.items(), key=lambda d: d[0]))
    # num_at_date_most = cols.OrderedDict(sorted(num_at_date.items(), key=lambda d: d[1], reverse=True))

    # c = []
    # d = []
    # for k,v in num_pr_date.items():
    #     c.append(k)
    #     d.append(v)
    #
    # # Write observed snow obs to file
    # with open('all_obs_plot.txt', 'w', encoding='utf-8') as f:
    #     for k, v in num_pr_date.items():
    #         f.write('{}{};{}\n'.format(cenv.output_folder, k, v))


def _map_obs_to_old_regions(obs, make_new=True):

    picle_file_name = '{}all observations with old coords.pickle'.format(env.local_storage)

    if make_new:

        for o in obs:
            utm_n = o.UTMNorth
            utm_e = o.UTMEast
            date = o.DtObsTime
            year = gm.get_season_from_date(date)
            region_id, region_name = gm.get_forecast_region_for_coordinate(utm_e, utm_n, year)
            o.ForecastRegionName = region_name
            o.ForecastRegionTID = region_id

        mp.pickle_anything(obs, picle_file_name)
        return obs

    else:
        obs_old_coords = mp.unpickle_anything(picle_file_name)
        return obs_old_coords


def pick_winners_at_conference():
    import random as rand
    romsdalen_konf_obs = go.get_all_registrations('2017-11-02', '2017-11-05', region_ids=3023, geohazard_tids=10)
    romsdalen_konf_regs = go.get_data('2017-11-02', '2017-11-05', region_ids=3023, geohazard_tids=10, output='Nest')
    rauma_konf_obs = []
    rauma_konf_regs = []
    for o in romsdalen_konf_obs:
        if o.MunicipalName == 'RAUMA':
            rauma_konf_obs.append(o)
    for r in romsdalen_konf_regs:
        if r['MunicipalName'] == 'RAUMA':
            rauma_konf_regs.append(r)
    print('Antall obs: {}'.format(len(rauma_konf_regs)))
    print('Antall enkelt obs: {}'.format(len(rauma_konf_obs)))
    print('1 : {}'.format(rauma_konf_obs[rand.randint(0, len(rauma_konf_obs))].NickName))
    print('2 : {}'.format(rauma_konf_obs[rand.randint(0, len(rauma_konf_obs))].NickName))
    print('3 : {}'.format(rauma_konf_obs[rand.randint(0, len(rauma_konf_obs))].NickName))
    print('4 : {}'.format(rauma_konf_obs[rand.randint(0, len(rauma_konf_obs))].NickName))
    print('5 : {}'.format(rauma_konf_obs[rand.randint(0, len(rauma_konf_obs))].NickName))


def write_to_file_all_obs():

    obs = _get_all(get_new=False)

    num_at_date = _make_date_int_dict()          # antall obs pr dag
    for o in obs:
        date = o.DtObsTime.date()
        num_at_date[date] += 1

    # Write observed dangers to file
    with open('{}number_off_obs_pr_date.txt'.format(env.output_folder), 'w', encoding='utf-8') as f:
        for k, v in num_at_date.items():
            f.write('{};{}\n'.format(k, v))


if __name__ == '__main__':

    # find_fun_facts()
    # pick_winners_at_conference()
    write_to_file_all_obs()

    a = 1
