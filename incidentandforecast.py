import datetime as dt
from runvarsomdata import allforecasteddangerlevels as afdl
from varsomdata import getdangers as gd
from varsomdata import getobservations as go
from varsomdata import makepickle as mp
from runvarsomdata import setthisenvironment as env
from varsomdata import getmisc as gm

# -*- coding: utf-8 -*-
__author__ = 'raek'


def get_data(from_date, to_date, region_ids, pickle_file_name_1, get_new):
    """Timeconsuming and inefficient. Not proud..

    :param from_date:
    :param to_date:
    :param region_ids:
    :param pickle_file_name_1:
    :param get_new:
    :return:
    """

    if get_new:
        # get all data and save to pickle
        all_incidents = go.get_incident(from_date, to_date, region_ids=region_ids, geohazard_tids=10)
        all_forecasts = gd.get_forecasted_dangers(region_ids, from_date, to_date)
        mp.pickle_anything([all_forecasts, all_incidents], pickle_file_name_1)
    else:
        # load data from pickle
        all_forecasts, all_incidents = mp.unpickle_anything(pickle_file_name_1)

    return all_forecasts, all_incidents


def write_incidents_to_csv(incidents, file_path):

    # Write to .csv
    with open(file_path, "w", encoding='utf-8') as myfile:
        myfile.write('Dato;Varslingsregion;RegID;Skadeomfang;Aktivitet;URL\n')

        for i in incidents:

            registration = 'http://www.regobs.no/Registration/{0}'.format(i.RegID)

            table_row = '{0};{1};{2};{3};{4};\n'.format(
                i.DtObsTime,
                i.ForecastRegionName,
                i.DamageExtentName,
                i.ActivityInfluencedName,
                registration)

            myfile.write(table_row)


def make_incident_and_forecast_csvs(from_date, to_date, region_ids, region_name, get_new=True):

    # The output
    incident_csv = '{0}incident_{1}_{2}-{3}.csv'.format(env.output_folder, region_name, from_date.strftime('%Y'), to_date.strftime('%y'))
    dl_and_problem_csv = '{0}forecast_{1}_{2}-{3}.csv'.format(env.output_folder, region_name, from_date.strftime('%Y'), to_date.strftime('%y'))

    # The inn between
    pickle_file_name = '{0}incident_and_forecast_{1}_{2}-{3}.pickle'.format(env.output_folder, region_name, from_date.strftime('%Y'), to_date.strftime('%y'))
    all_forecasts, all_incidents = get_data(from_date, to_date, region_ids, pickle_file_name, get_new)

    # Write to file
    write_incidents_to_csv(all_incidents, incident_csv)
    afdl.save_danger_and_problem_to_file(all_forecasts, dl_and_problem_csv)


def make_sunnmoere():

    # Get new or load from pickle.
    get_new = True
    region_name = "Sunnmøre"

    from_date = dt.date(2012, 11, 30)
    to_date = dt.date(2016, 6, 1)
    region_ids = 119

    make_incident_and_forecast_csvs(from_date, to_date, region_ids, region_name, get_new=get_new)

    # Set dates
    from_date = dt.date(2016, 11, 30)
    to_date = dt.date(2017, 6, 1)
    region_ids = 3024

    make_incident_and_forecast_csvs(from_date, to_date, region_ids, region_name, get_new=get_new)


def make_dl_incident_markus():
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
    years = ['2012-13', '2013-14', '2014-15', '2015-16', '2016-17']
    get_new = False

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


if __name__ == "__main__":

    make_sunnmoere()
    # make_dl_incident_markus()
