# -*- coding: utf-8 -*-
"""
Module contains methods for picking through Regobs and Varsom data.It might be to randomly pick
out winners of a competition or count numbers for a report benchmark.
"""

from varsomdata import getobservations as go
from varsomdata import getmisc as gm
from varsomdata import getvarsompickles as gvp
from utilities import makepickle as mp
import setenvironment as env
import collections as cols
import datetime as dt

__author__ = 'ragnarekker'


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


def pick_winners_at_conference():
    """Pick winers at regObs competition at nordic avalanche conference at Åndalsnes."""
    import random as rand
    romsdalen_konf_obs = go.get_all_observations('2017-11-02', '2017-11-05', region_ids=3023, geohazard_tids=10)
    romsdalen_konf_regs = go.get_data('2017-11-02', '2017-11-05', region_ids=3023, geohazard_tids=10)
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


def pick_winners_varsom_friflyt_konk_2019():
    """Method for picking winners of the varsom/friflyt competition.

    Utvalgskriterier:
        • Premie for flest observasjoner av snøoverflate og faretegn
        • Premie til den som sender inn den grundigste observasjonen
        • Uttrekkspremier blant de som leverer flere enn 10 observasjoner
        • Uttrekkspremier blant de som leverer flere enn 5 isobservasjoner

    """

    year = '2018-19'
    all_snow_obs = gvp.get_all_observations(year, geohazard_tids=10, max_file_age=23)
    all_ice_obs = gvp.get_all_observations(year, geohazard_tids=70, max_file_age=23)

    voluntary_snow_obs = []
    users_and_numbers_snow = {}

    voluntary_snowcover_dangersign_obs = []
    users_and_numbers_sc_ds = {}

    voluntary_manyforms_obs = []
    users_and_numbers_manyforms = {}

    for o in all_snow_obs:

        competence_level = o.CompetenceLevelName
        nick_name = o.NickName.lower()
        observer_id_and_nick = '{};{}'.format(o.ObserverID, nick_name)

        if '****' not in competence_level:   # dont include obs with **** or more competance
            if 'obskorps' not in nick_name:
                if 'svv' not in nick_name and 'vegvesen' not in nick_name:
                    if 'nve' not in nick_name and 'met' not in nick_name:
                        if 'wyssen' not in nick_name and 'forsvaret' not in nick_name:
                            if 'kjus@nortind' not in nick_name:

                                voluntary_snow_obs.append(o)
                                if observer_id_and_nick in users_and_numbers_snow.keys():
                                    users_and_numbers_snow[observer_id_and_nick] += 1
                                else:
                                    users_and_numbers_snow[observer_id_and_nick] = 1

                                for oo in o.Observations:
                                    if isinstance(oo, go.SnowSurfaceObservation):
                                        voluntary_snowcover_dangersign_obs.append(o)
                                        if observer_id_and_nick in users_and_numbers_sc_ds.keys():
                                            users_and_numbers_sc_ds[observer_id_and_nick] += 1
                                        else:
                                            users_and_numbers_sc_ds[observer_id_and_nick] = 1
                                    elif isinstance(oo, go.DangerSign):
                                        voluntary_snowcover_dangersign_obs.append(o)
                                        if observer_id_and_nick in users_and_numbers_sc_ds.keys():
                                            users_and_numbers_sc_ds[observer_id_and_nick] += 1
                                        else:
                                            users_and_numbers_sc_ds[observer_id_and_nick] = 1

                                if len(o.Observations) > 7:
                                    voluntary_manyforms_obs.append(o)
                                    if observer_id_and_nick in users_and_numbers_manyforms.keys():
                                        users_and_numbers_manyforms[observer_id_and_nick] += 1
                                    else:
                                        users_and_numbers_manyforms[observer_id_and_nick] = 1

    voluntary_ice_obs = []
    users_and_numbers_ice = {}

    for o in all_ice_obs:
        competence_level = o.CompetenceLevelName
        nick_name = o.NickName.lower()
        observer_id_and_nick = '{};{}'.format(o.ObserverID, nick_name)

        if '*****' not in competence_level:   # dont include obs with **** or more competance
            voluntary_ice_obs.append(o)
            if observer_id_and_nick in users_and_numbers_ice.keys():
                users_and_numbers_ice[observer_id_and_nick] += 1
            else:
                users_and_numbers_ice[observer_id_and_nick] = 1

    import operator
    from random import shuffle

    sorted_users_and_numbers_snow = sorted(users_and_numbers_snow.items(), key=operator.itemgetter(1), reverse=True)
    sorted_users_and_numbers_ice = sorted(users_and_numbers_ice.items(), key=operator.itemgetter(1), reverse=True)

    # Write lists of users and numbers to file. List can be sorted in excel.Need to lookup email and full name.
    # all snow obseravtions
    with open('{}snow_observations_pr_user {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for k, v in users_and_numbers_snow.items():
            f.write('{};{}\n'.format(k, v))

    # all users with 10 or more snowobs with danger signs and/or snow cover obs.
    with open('{}snow_cover_or_danger_sign_pr_user {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for k, v in users_and_numbers_sc_ds.items():
            if v > 9:       # only users with 10 or more obs
                f.write('{};{}\n'.format(k, v))

    # Comprehensive snow observations (many forms)
    with open('{}many_forms_pr_users {}.txt'.format(env.output_folder, year), 'w',
              encoding='utf-8') as f:
        for k, v in users_and_numbers_snow.items():
            f.write('{};{}\n'.format(k, v))

    # Write list of users and numbers to file. List can be sorted in excel. Need to lookup email and full name.
    with open('{}ice_observations_pr_user {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for k, v in users_and_numbers_ice.items():
            if v > 4:       # only users with 5 or more obs
                f.write('{};{}\n'.format(k, v))

    # Shuffle the list of observations
    shuffle(voluntary_snow_obs)
    shuffle(voluntary_snowcover_dangersign_obs)
    shuffle(voluntary_manyforms_obs)
    shuffle(voluntary_ice_obs)

    # Write the random list of users and regid to file
    with open('{}random_snowobs {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for o in voluntary_snow_obs:
            f.write('{};{};{}\n'.format(o.ObserverID, o.NickName, o.RegID))
    with open('{}random_snowcover_dangersign {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for o in voluntary_snowcover_dangersign_obs:
            f.write('{};{};{}\n'.format(o.ObserverID, o.NickName, o.RegID))
    with open('{}random_manyforms {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for o in voluntary_manyforms_obs:
            f.write('{};{};{}\n'.format(o.ObserverID, o.NickName, o.RegID))
    with open('{}random_ice_obs {}.txt'.format(env.output_folder, year), 'w', encoding='utf-8') as f:
        for o in voluntary_ice_obs:
            f.write('{};{};{}\n'.format(o.ObserverID, o.NickName, o.RegID))

    pass


def count_of_water_forms_used():
    """Which forms are use for observing water. Which users submit how much."""

    year = '2018'
    all_water_obs_list = gvp.get_all_observations(year, output='FlatList', geohazard_tids=60, max_file_age=230)
    all_water_obs_nest = gvp.get_all_observations(year, output='List', geohazard_tids=60, max_file_age=230)

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


def total_obs_and_users(year='2018-19'):

    all_snow_obs = gvp.get_all_observations(year, geohazard_tids=10, max_file_age=23)
    all_ice_obs = gvp.get_all_observations(year, geohazard_tids=70, max_file_age=23)
    all_obs = gvp.get_all_observations(year, max_file_age=23)

    snow_observers = {}
    ice_observers = {}
    observers = {}

    for o in all_snow_obs:
        if o.NickName in snow_observers.keys():
            snow_observers[o.NickName] += 1
        else:
            snow_observers[o.NickName] = 1

    for o in all_ice_obs:
        if o.NickName in ice_observers.keys():
            ice_observers[o.NickName] += 1
        else:
            ice_observers[o.NickName] = 1

    for o in all_obs:
        if o.NickName in observers.keys():
            observers[o.NickName] += 1
        else:
            observers[o.NickName] = 1

    print("For sesongen {} (1. sept til 31. aug)\n".format(year))
    print("Totalt snøobservasjoner: {}".format(len(all_snow_obs)))
    print("Antall snøobservatører: {}\n".format(len(snow_observers)))
    print("Totalt isobservasjoner: {}".format(len(all_ice_obs)))
    print("Antall isobservatører: {}\n".format(len(ice_observers)))
    print("Totalt observasjoner: {}".format(len(all_obs)))
    print("Antall observatører: {}".format(len(observers)))

    pass


if __name__ == '__main__':

    # pick_winners_at_conference()
    # write_to_file_all_obs()
    # pick_winners_varsom_friflyt_konk_2019()
    # count_of_water_forms_used()
    # count_all_avalanches()
    # total_2018_and_part_water()
    total_obs_and_users()
