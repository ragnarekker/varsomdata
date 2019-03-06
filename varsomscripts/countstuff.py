# -*- coding: utf-8 -*-
"""

"""

from varsomdata import getobservations as go
from varsomdata import getforecastapi as gfa
from varsomdata import getmisc as gm
from varsomdata import getvarsompickles as gvp
from utilities import makepickle as mp, makemisc as mm
import setenvironment as env
import collections as cols
import datetime as dt

__author__ = 'ragnarekker'


def _get_all_snow(get_new=False):

    file_name = '{}observations and forecasts 2012-17.pickle'.format(env.local_storage)

    if get_new:
        all_observations = go.get_all_registrations('2012-12-01', '2017-07-01', geohazard_tids=10)

        years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17']
        all_forecasts = []
        for y in years:
            from_date, to_date = gm.get_forecast_dates(y)
            region_ids = gm.get_forecast_regions(y)
            all_forecasts += gfa.get_avalanche_warnings(region_ids, from_date, to_date)

        mp.pickle_anything([all_observations, all_forecasts], file_name)

    else:
        [all_observations, all_forecasts] = mp.unpickle_anything(file_name)

    return all_observations, all_forecasts


class ObsCount:

    def __init__(self):
        self.total = 0
        self.snow = 0
        self.landslide = 0
        self.water = 0
        self.ice = 0

    def add_one_to_total(self):
        self.total += 1

    def add_one_to_snow(self):
        self.snow += 1

    def add_one_to_landslide(self):
        self.landslide += 1

    def add_one_to_water(self):
        self.water += 1

    def add_one_to_ice(self):
        self.ice += 1


def _make_date_obscount_dict(start_date=dt.date(2012, 10, 1), end_date=dt.date.today()):
    """Makes dictionary with all dates in a period as keys and values set to empty ObsCount objects."""

    num_days = (end_date-start_date).days
    date_list = [start_date + dt.timedelta(days=x) for x in range(0, num_days)]

    date_dict = cols.OrderedDict()
    for d in date_list:
        date_dict[d] = ObsCount()

    return date_dict


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


def write_to_file_all_obs():
    """Writes to file all dates and the number of observations on the dates.
    Both the total and the numbers pr geohazard."""

    years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19']
    all_observations = []
    for y in years:
        all_observations += gvp.get_all_observations(y)

    num_at_date = _make_date_obscount_dict()          # number of obs pr day pr geohazard

    for o in all_observations:
        date = o.DtObsTime.date()
        try:
            num_at_date[date].add_one_to_total()

            if o.GeoHazardTID == 10:
                num_at_date[date].add_one_to_snow()
            if o.GeoHazardTID in [20, 30, 40]:
                num_at_date[date].add_one_to_landslide()
            if o.GeoHazardTID == 60:
                num_at_date[date].add_one_to_water()
            if o.GeoHazardTID == 70:
                num_at_date[date].add_one_to_ice()

        except:
            pass

    # Write observed dangers to file
    with open('{}number_off_obs_pr_date.txt'.format(env.output_folder), 'w', encoding='utf-8') as f:
        f.write('Date;Water;Landslide;Ice;Snow;Total\n')
        for k, v in num_at_date.items():
            f.write('{};{};{};{};{};{}\n'.format(k, v.water, v.landslide, v.ice, v.snow, v.total))


def find_fun_facts():
    """Til regObs quiz på oppstartsamling nov2017
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

    num_pr_date = mm.make_date_int_dict()          # antall obs pr dag
    obs_pr_date = mm.make_date_list_dict()         # alle obs gruppert på dato
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
    #         f.write('{}{};{}\n'.format(env.output_folder, k, v))


def pick_winners_at_conference():
    """Pick winers at regObs competition at nordic avalanche conference at Åndalsnes."""
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


def pick_winners_varsom_friflyt_konk_2018():
    """Method for picking winners of the varsom/friflyt competition.
    Winter 2017-18 we encouraged voluntary observations.
    We pick som winners among snow obs.
    1st, 2nd and 3rd to those who observed most.
    The rest on random pick in relevant obs.

    :return:
    """

    year = '2017-18'
    all_snow_obs = gvp.get_all_observations(year, output='Nest', geohazard_tids=10, max_file_age=23)

    voluntary_obs = []
    users_and_numbers = {}

    for o in all_snow_obs:

        competence_level = o.CompetenceLevelName
        nick_name = o.NickName.lower()
        observer_id_and_nick = '{};{}'.format(o.ObserverId, nick_name)

        if '****' not in competence_level:   # dont include obs with *** or more cometance
            if 'obskorps' not in nick_name:
                if 'svv' not in nick_name and 'vegvesen' not in nick_name:
                    if 'nve' not in nick_name and 'met' not in nick_name:
                        if 'wyssen' not in nick_name and 'forsvaret' not in nick_name:
                            if 'kjus@nortind' not in nick_name:

                                voluntary_obs.append(o)
                                if observer_id_and_nick in users_and_numbers.keys():
                                    users_and_numbers[observer_id_and_nick] += 1
                                else:
                                    users_and_numbers[observer_id_and_nick] = 1

    import operator
    from random import shuffle
    sorted_users_and_numbers = sorted(users_and_numbers.items(), key=operator.itemgetter(1), reverse=True)

    # Write list of users and numbers to file. List can be sorted in excel. Need to lookup email and full name.
    with open('{}users_and_numbers {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for k, v in users_and_numbers.items():
            f.write('{};{}\n'.format(k, v))

    # Shuffle the list of observations
    shuffle(voluntary_obs)

    # Write the random list of users and regid to file
    with open('{}random_users_and_obs {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for o in voluntary_obs:
            f.write('{};{};{}\n'.format(o.ObserverId, o.NickName, o.RegID))

    pass


def count_of_water_forms_used():
    """Which forms are use for observing water. Which users submit how much."""

    year = '2018'
    all_water_obs_list = gvp.get_all_observations(year, output='List', geohazard_tids=60, max_file_age=230)
    all_water_obs_nest = gvp.get_all_observations(year, output='Nest', geohazard_tids=60, max_file_age=230)

    form_count = {}
    for o in all_water_obs_list:
        form_name = o.__class__.__name__
        if form_name in form_count.keys():
            form_count[form_name] += 1
        else:
            form_count[form_name] = 1

        if 'Picture' in form_name:
            form_name = 'Picture_{}'.format(o.RegistrationName)
            if form_name in form_count.keys():
                form_count[form_name] += 1
            else:
                form_count[form_name] = 1

    observation_count = len(all_water_obs_nest)
    user_count = {}
    for o in all_water_obs_nest:
        nick_name = o.NickName
        if nick_name in user_count.keys():
            user_count[nick_name] += 1
        else:
            user_count[nick_name] = 1

    with open('{}water_users_and_numbers {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        f.write('Totalt antall observasjoner; {}\n'.format(observation_count))
        f.write('Totalt antall skjema; {}\n'.format(len(all_water_obs_list)))
        f.write('\n')
        for k, v in form_count.items():
            f.write('{};{}\n'.format(k, v))
        f.write('\n')
        for k, v in user_count.items():
            f.write('{};{}\n'.format(k, v))

    pass


def count_all_avalanches(year='2017-18'):
    """How many avalanches?

    jaas [30-10-2018 6:14 PM]
    sit og driv med ein presentasjon til IKAR ettermøte. Er det lett å ta ut talet på kor mange skred
    det er innrapportert på regObs sist vinter? viss mogeleg delt på farteikn-skred, ulykke/hending,
    og skredaktivitet. (er klar over at dette vert veldig ca, men interessant om det er 100, 1000,
    eller 10000)"""

    all_observations = gvp.get_all_observations(year=year, output='List')

    danger_signs_all = []
    danger_signs_count_activity = 0
    danger_signs_count_no_danger = 0
    avalanches_all = []
    avalanche_activities_all = []
    avalanche_activities_count_activity = 0
    avalanche_activities_count_no_activity = 0

    # I thought nobody used this form - it turned out it was used 2 times in 2017-18.
    old_avalanche_activity_forms = 0

    for o in all_observations:

        if isinstance(o, go.AvalancheActivityObs2) or isinstance(o, go.AvalancheActivityObs):
            avalanche_activities_all.append(o)

            if isinstance(o, go.AvalancheActivityObs):
                old_avalanche_activity_forms += 1

            if o.EstimatedNumTID == 1:   # no activity
                avalanche_activities_count_no_activity += 1
            else:
                avalanche_activities_count_activity += 1

        if isinstance(o, go.AvalancheObs):
            avalanches_all.append(o)

        if isinstance(o, go.DangerSign):
            danger_signs_all.append(o)
            if o.DangerSignTID == 1:    # no dangers
                danger_signs_count_no_danger += 1
            if o.DangerSignTID == 2:    # avalanche activity
                danger_signs_count_activity += 1

    print("SKRED OBSERVERT VINTERN 2017-18")
    print("")
    print("Skredaktivitet som faretegn: {}".format(danger_signs_count_activity))
    print("Ingen faretegn observert: {}".format(danger_signs_count_no_danger))
    print("")
    print("Observert skredaktivitet: {}".format(avalanche_activities_count_activity))
    print("Ingen skredaktivitet observert: {}".format(avalanche_activities_count_no_activity))
    print("")
    print("Antall skredhendelser observert: {}".format(len(avalanches_all)))


def total_2018_and_part_water():

    # from_date = dt.date(2018, 1, 1)
    # to_date = dt.date(2018, 12, 31)
    # all_observations = go.get_data(from_date, to_date, output='Count nest')
    # all_water_observ = go.get_data(from_date, to_date, geohazard_tids=60, output='Count nest')
    # all_snow_observ = go.get_data(from_date, to_date, geohazard_tids=10, output='Count nest')
    # all_dirt_observ = go.get_data(from_date, to_date, geohazard_tids=[20,30,40], output='Count nest')
    # all_ice_observ = go.get_data(from_date, to_date, geohazard_tids=70, output='Count nest')

    # all_observations_2016 = gvp.get_all_observations('2016')
    # all_forms_2016 = gvp.get_all_observations('2016', output='List')

    years = ['2013', '2014', '2015', '2016', '2017', '2018']
    
    for y in years:
        
        all_observations = gvp.get_all_observations(y)
        all_forms = gvp.get_all_observations(y, output='List')

        all_water_forms = [f for f in all_forms if f.GeoHazardTID == 60 and not isinstance(f, go.PictureObservation)]
        all_water_pictures = [f for f in all_forms if f.GeoHazardTID == 60 and isinstance(f, go.PictureObservation)]

        all_snow_forms = [f for f in all_forms if f.GeoHazardTID == 10 and not isinstance(f, go.PictureObservation)]
        all_snow_pictures = [f for f in all_forms if f.GeoHazardTID == 10 and isinstance(f, go.PictureObservation)]

        all_dirt_forms = [f for f in all_forms if f.GeoHazardTID in [20,30,40] and not isinstance(f, go.PictureObservation)]
        all_dirt_pictures = [f for f in all_forms if f.GeoHazardTID in [20,30,40] and isinstance(f, go.PictureObservation)]

        all_ice_forms = [f for f in all_forms if f.GeoHazardTID == 70 and not isinstance(f, go.PictureObservation)]
        all_ice_pictures = [f for f in all_forms if f.GeoHazardTID == 70 and isinstance(f, go.PictureObservation)]

        print(y)

        print("All observations:\t{0}".format(len(all_observations)))
        print("All forms:\t{0}".format(len(all_forms)))

        print("Snow forms:\t{0}".format(len(all_snow_forms)))
        print("Snow pictures:\t{0}".format(len(all_snow_pictures)))

        print("Water forms:\t{0}".format(len(all_water_forms)))
        print("Water pictures:\t{0}".format(len(all_water_pictures)))

        print("Dirt forms:\t{0}".format(len(all_dirt_forms)))
        print("Dirt pictures:\t{0}".format(len(all_dirt_pictures)))

        print("Ice forms:\t{0}".format(len(all_ice_forms)))
        print("Ice pictures:\t{0}".format(len(all_ice_pictures)))

        print()


    # all_observations_2015_16 = gvp.get_all_observations('2015-16')
    # all_forms_2015_16 = gvp.get_all_observations('2015-16', output='List')
    #
    # all_observations_2016_17 = gvp.get_all_observations('2016-17')
    # all_forms_2016_17 = gvp.get_all_observations('2016-17', output='List')
    #
    # all_observations_2017_18 = gvp.get_all_observations('2017-18')
    # all_forms_2017_18 = gvp.get_all_observations('2017-18', output='List')


    pass


if __name__ == '__main__':

    # find_fun_facts()
    # pick_winners_at_conference()
    write_to_file_all_obs()
    # pick_winners_varsom_friflyt_konk_2018()
    # count_of_water_forms_used()
    # count_all_avalanches()
    # total_2018_and_part_water()

