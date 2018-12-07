# -*- coding: utf-8 -*-
"""
Contains methods for accessing data on the forecast api's. See api.nve.no for more info

Modifications:
- 06.12.2018, kmunve: added class AvalancheWarning, MountainWeather, AvalancheProblem
- 06.12.2018, kmunve: Class AvalancheProblem was moved from varsomclasses.py
"""

import requests
import datetime as dt
from varsomdata import varsomclasses as vc
from utilities import makelogs as ml
import setenvironment as env

__author__ = 'raek'


class AvalancheWarning:
    """
    AvalancheWarning represents the returns from http://api.nve.no/doc/snoeskredvarsel/#avalanchewarningbyregion as a Python object.
    """

    def __init__(self):
        """
        Init class properties
        """
        self.reg_id = None  # [int]
        self.region_id = None  # [int]
        self.region_name = None  # [String]
        self.region_type_id = None  # [int]
        self.region_type_name = None  # [String]
        self.utm_east = None  # [int]
        self.utm_north = None  # [int]
        self.utm_zone = None  # [int]
        self.valid_from = None  # [datetime]
        self.valid_to = None  # [datetime]
        self.date_valid = None  # [datetime]

        self.county_list = []  # [list of county names overlapping with the region]
        self.muncipality_list = []  # [list of muncipalities overlapping with the region]

        self.next_warning_time = None  # [datetime]
        self.publish_time = None  # [datetime]
        self.danger_level = None  # [int]
        self.danger_level_name = None  # [String]
        self.main_text = None  # [String]
        self.author = None  # [String]
        self.avalanche_danger = None  # [String]
        self.emergency_warning = None  # [String]
        self.snow_surface = None  # [String]
        self.current_weak_layers = None  # [String]
        self.latest_avalanche_activity = None  # [String]
        self.latest_observations = None  # [String]
        self.mountain_weather = None  # [MountainWeather object]
        self.avalanche_problems = []  # [List of AvalancheProblem objects]

        self.metadata = {}  # [dictionary] {key:value, key:value, ..}
        self.base_url_no = 'http://www.varsom.no/snoskredvarsling/varsel'  # [String]

    def __repr__(self):
        return f"{self.__class__.__name__}(RegObsID: {self.reg_id}, Region: {self.region_name} ({self.region_id}), " \
               f"Valid from: {self.valid_from})"

    def set_reg_id(self, _):
        if isinstance(_, str):
            self.reg_id = int(_)
        else:
            self.reg_id = _

    def set_region_id(self, _):
        if isinstance(_, str):
            self.region_id = int(_)
        else:
            self.region_id = _

    def set_region_type_id(self, _):
        if isinstance(_, str):
            self.region_type_id = int(_)
        else:
            self.region_type_id = _

    def set_utm_east(self, _):
        if isinstance(_, str):
            self.utm_east = int(_)
        else:
            self.utm_east = _

    def set_utm_north(self, _):
        if isinstance(_, str):
            self.utm_north = int(_)
        else:
            self.utm_north = _

    def set_utm_zone(self, _):
        if isinstance(_, str):
            self.utm_zone = int(_)
        else:
            self.utm_zone = _

    def set_danger_level(self, _):
        if isinstance(_, str):
            self.danger_level = int(_)
        else:
            self.danger_level = _

    def set_valid_from(self, date_in):
        if isinstance(date_in, dt.datetime):
            self.valid_from = date_in
        else:
            self.valid_from = dt.datetime.strptime(date_in, '%Y-%m-%dT%H:%M:%S')
        self.date_valid = self.valid_from.date()

    def set_valid_to(self, date_in):
        if isinstance(date_in, dt.datetime):
            self.valid_to = date_in
        else:
            self.valid_to = dt.datetime.strptime(date_in, '%Y-%m-%dT%H:%M:%S')

    def add_problem(self, problem_in):
        self.avalanche_problems.append(problem_in)
        # make sure lowest index (main problem) is first
        self.avalanche_problems.sort(key=lambda problems: problems.order)

    def set_mountain_weather(self, _d):
        _mw = MountainWeather()
        _mw.from_dict(_d)
        self.mountain_weather = _mw

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def get_url(self):
        return f'{self.base_url_no}/{self.region_name}/{self.date_valid}'

    def from_dict(self, _d):
        """
        Create AvalancheWarning object from JSON string returned by http://api.nve.no/doc/snoeskredvarsel/#avalanchewarningbyregion
        :param _d: the return from get_warnings_as_json
        """

        self.set_reg_id(_d['RegId'])
        self.set_region_id(_d['RegionId'])
        self.region_name = _d['RegionName']
        self.set_region_type_id(_d['RegionTypeId'])
        self.region_type_name = _d['RegionTypeName']
        self.set_utm_east(_d['UtmEast'])
        self.set_utm_north(_d['UtmNorth'])
        self.set_utm_zone(_d['UtmZone'])
        self.set_valid_from(_d['ValidFrom'])  # sets self.date_valid, too
        self.set_valid_to(_d['ValidTo'])

        #self.county_list = []  # [list of county names overlapping with the region]
        #self.muncipality_list = []  # [list of muncipalities overlapping with the region]

        #self.next_warning_time = None  # [datetime]
        #self.publish_time = None  # [datetime]
        self.set_danger_level(_d['DangerLevel'])
        self.danger_level_name = _d['DangerLevelName']
        self.main_text = _d['MainText']
        self.author = _d['Author']
        self.avalanche_danger = _d['AvalancheDanger']
        self.emergency_warning = _d['EmergencyWarning']
        self.snow_surface = _d['SnowSurface']
        self.current_weak_layers = _d['CurrentWeaklayers']
        self.latest_avalanche_activity = _d['LatestAvalancheActivity']
        self.latest_observations = _d['LatestObservations']
        self.set_mountain_weather(_d['MountainWeather'])  # [MountainWeather object]
        #self.set_avalanche_problems()  # [List of AvalancheProblem objects]

    def to_dict(self):
        """
        Convert the object to a dictionary
        :return: dictionary representation of the AvalancheWarning class
        """
        _dict = {'reg_id': self.region_reg_id,
                 'region_name': self.region_name,
                 'danger_level': self.danger_level,
                 'danger_level_name': self.danger_level_name,

                 # mountain weather stuff
                 "mountain_weather_precip_most_exposed": self.mountain_weather.precip_most_exposed,
                 "mountain_weather_precip_region": self.mountain_weather.precip_region,
                 "mountain_weather_wind_speed": self.mountain_weather.wind_speed,
                 "mountain_weather_wind_direction": self.mountain_weather.wind_direction,
                 "mountain_weather_change_wind_speed": self.mountain_weather.change_wind_speed,
                 "mountain_weather_change_wind_direction": self.mountain_weather.change_wind_direction,
                 "mountain_weather_change_hour_of_day_start": self.mountain_weather.change_hour_of_day_start,
                 "mountain_weather_change_hour_of_day_stop": self.mountain_weather.change_hour_of_day_stop,
                 "mountain_weather_temperature_min": self.mountain_weather.temperature_min,
                 "mountain_weather_temperature_max": self.mountain_weather.temperature_max,
                 "mountain_weather_temperature_elevation": self.mountain_weather.temperature_elevation,
                 "mountain_weather_freezing_level": self.mountain_weather.freezing_level,
                 "mountain_weather_fl_hour_of_day_start": self.mountain_weather.fl_hour_of_day_start,
                 "mountain_weather_fl_hour_of_day_stop": self.mountain_weather.fl_hour_of_day_stop

                 ##### obs eval 3 stuff
                 # fix: 'forecast_correct': self.forecast_correct                    # [String] Drop down value if the forecast is correct or no
                 # fix: 'forecast_correct_id': self.forecast_correct_id                 # [int]
                 # fix: 'forecast_comment': self.forecast_comment
                 }
        #### add avalanche problems
        # generate dummy keys for three potential avalanche problems
        for n in range(1, 4):
            problem_prefix = f"avalanche_problem_{n}_"
            _ap_dict = {f'{problem_prefix}cause_tid': 0,
                        # [int] Avalanche cause ID(TID in regObs). Only used in avalanche problems from dec 2014 and newer.
                        f'{problem_prefix}cause_name': 'Not given',
                        f'{problem_prefix}source': '',
                        f'{problem_prefix}problem': 'Not given',
                        f'{problem_prefix}problem_tid': 0,  # [int]       ID used in regObs
                        f'{problem_prefix}main_cause': 'Not given',
                        # [String] Problems/weaklayers are grouped into main problems the season 2014/15
                        f'{problem_prefix}aval_type': 'Not given',  # [String]    Avalanche Type
                        f'{problem_prefix}aval_type_tid': 0,  # [int]       ID used in regObs
                        f'{problem_prefix}aval_size': 'Not given',  # [String]    Avalanche Size
                        f'{problem_prefix}aval_size_tid': 0
                        }

            _dict.update(_ap_dict)

        # insert values for the issued avalanche problem(s)
        for _problem in self.avalanche_problems:
            problem_prefix = f"avalanche_problem_{_problem.order}_"
            _ap_dict = {f'{problem_prefix}cause_tid': _problem.cause_tid,
                        # [int] Avalanche cause ID(TID in regObs). Only used in avalanche problems from dec 2014 and newer.
                        f'{problem_prefix}cause_name': _problem.cause_name,
                        f'{problem_prefix}source': _problem.source,
                        f'{problem_prefix}problem': _problem.problem,
                        f'{problem_prefix}problem_tid': _problem.problem_tid,  # [int]       ID used in regObs
                        f'{problem_prefix}main_cause': _problem.main_cause,
                        # [String] Problems/weaklayers are grouped into main problems the season 2014/15
                        f'{problem_prefix}aval_type': _problem.aval_type,  # [String]    Avalanche Type
                        f'{problem_prefix}aval_type_tid': _problem.aval_type_tid,  # [int]       ID used in regObs
                        f'{problem_prefix}aval_size': _problem.aval_size,  # [String]    Avalanche Size
                        f'{problem_prefix}aval_size_tid': _problem.aval_size_tid
                        }

            _dict.update(_ap_dict)
        return _dict

    def to_df(self):
        """
        Convert the object to a Pandas.DataFrame
        :return: pandas.DataFrame representation of the AvalancheDanger class
        """
        import pandas
        _d = self.to_dict()
        return pandas.DataFrame.from_dict(_d)


class AvalancheWarningProblem:

    def __init__(self):
        """
        The AvalancheWarningProblem object contains the AvalancheProblems published as part of an AvalancheWarning.
        You find the API documentation here: http://api.nve.no/doc/snoeskredvarsel/#avalanchewarningbyregion
        """
        self.avalanche_type_id = 0  # [int]
        self.avalanche_type_name = 'Not given'  # [string]
        self.avalanche_problem_type_id = 0  # [int],
        self.avalanche_problem_type_name = 'Not given'  # [string]
        self.avalanche_ext_id = 0  # [int],
        self.avalanche_ext_name = 'Not given'  # [string]
        self.aval_cause_id = 0  # [int],
        self.aval_cause_name = 'Not given'  # [string]
        self.destructive_size_ext_id = 0  # [int],
        self.destructive_size_ext_name = 'Not given'  # [string]
        self.aval_probability_id = 0  # [int],
        self.aval_probability_name = 'Not given'  # [string]
        self.aval_trigger_simple_id = 0  # [int],
        self.aval_trigger_simple_name = 'Not given'  # [string]
        self.aval_propagation_id = 0  # [int],
        self.aval_propagation_name = 'Not given'  # [string]
        self.exposed_height_fill = 0  # [int],
        self.exposed_height_1 = 0  # [int],
        self.exposed_height_2 = 0  # [int],
        self.valid_expositions = '00000000'  # [string] of digits, one for each of the eight sectors, starting with N and moving clockwise,1=True, 0=False
        self.avalanche_advice = 'Not given'  # [string]

        self.metadata = {}  # dictionary {key:value, key:value, ..}

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def map_to_eaws_problems(self):
        """The EAWS problems are:

        eaws_problems = ['New snow',
                 'Wind-drifted snow',
                 'Persistent waek layers',
                 'Wet snow',
                 'Gliding snow']

        Mapping forecasts to EAWS problems: For the forecasts, we have a classification of avalanche
        problem type. These are mapped to EAWS problems in the following way:

        Loose dry avalanches --> New snow
        Loose wet avalanches --> Wet snow
        Storm slab avalanches --> New snow
        Wind slab avalanches --> Wind-drifted snow
        New snow --> New snow
        Persistent slab avalanches --> Persistent weak layers
        Persistent weak layer --> Persistent weak layers
        Persistent deep slab avalanches --> Persistent weak layers
        Wet snow --> Wet snow
        Wet slab avalanches --> Wet snow
        Glide avalanches --> Gliding snow


        Mapping observations to EAWS problems: For the observations, we don’t have a classification of
        avalanche problems yet. The mapping is therefore somewhat more complex.

        Some avalanche types give the avalanche problem directly:

        Loose dry avalanche --> New snow
        Loose wet avalanche --> Wet snow
        Wet slab avalanche --> Wet snow
        Glide avalanche --> Gliding snow

        The expected avalanche type does not always give the problem. Neither is it mandatory for an observer
        to include avalanche type in the observation. In some cases, weak layers correspond directly to an
        avalanche problem:

        Poor bonding between layers in wind deposited snow --> Wind-drifted snow
        Wet snow / melting near the ground --> Gliding snow
        Wet snow on the surface --> Wet snow
        Water pooling in / above snow layers --> Wet snow

        The cases of dry slabs require some more inspection. First, if the slab over the weak layer is
        soft the avalanche problems are classified as “new snow” problems. Else, if it has a buried weak
        layer of surface hoar or of faceted snow the problem is classified as a persistent weak layer.


        :return:
        """
        pass  # Todo: check out later.
        """
        # problem_tid is available in the forecasts.
        problem_tid_to_eaws_problems = {
            0: 'Not given',
            3: 'New snow',  # Loose dry avalanches
            5: 'Wet snow',  # Loose wet avalanches
            7: 'New snow',  # Storm slab avlanches
            10: 'Wind-drifted snow',  # Wind slab avalanches
            20: 'New snow',  # New snow
            30: 'Persistent weak layers',  # Persistent slab avalanches
            35: 'Persistent weak layers',  # Persistent weak layer
            37: 'Persistent weak layers',  # Persistent deep slab avalanches
            40: 'Wet snow',  # Wet snow
            45: 'Wet snow',  # Wet slab avalanches
            50: 'Gliding snow'}  # Glide avalanches

        # AvalancheExtKDV holds information on avalanche type (self.aval_type)
        # id40:Corice and id30:Slush flow not included
        # id20:Dry slab in not uniquely mapped to an avalanche problem
        avalanche_ext_tid_to_eaws_problems = {
            10: 'New snow',  # Loose dry avalanche
            15: 'Wet snow',  # Loose wet avalanche
            # 20: ,              # Dry slab avalanche
            25: 'Wet snow',  # Wet slab avalanche
            27: 'Gliding snow'}  # Glide avalanche
        # 30: ,              # Slush avalanche
        # 40: ,              # Cornice

        aval_cause_to_eaws_problems = {
            # 10: ,   # Buried weak layer of new snow
            # 11: ,   # Buried weak layer of surface hoar
            # 12: ,   # Buried weak layer of graupel
            # 13: ,   # Buried weak layer of faceted snow near surface
            # 14: ,   # Poor bonding between crust and overlying snow
            15: 'Wind-drifted snow',  # Poor bonding between layers in wind deposited snow
            # 16: ,   # Buried weak layer of faceted snow near the ground
            # 17: ,   # Buried weak layer of faceted snow near vegetation
            # 18: ,   # Buried weak layer of faceted snow above a crust
            # 19: ,   # Buried weak layer of faceted snow beneath a crust
            20: 'Gliding snow',  # Wet snow / melting near the ground
            21: 'Wet snow',  # Wet snow on the surface
            22: 'Wet snow'}  # Water pooling in / above snow layers
        # 23: ,   # Water - saturated snow
        # 24: ,   # Loose snow
        # 25: ,   # Rain / rise in temperature / solar heating

        self.eaws_problem = None

        if self.source == 'Observation':
            # first try some avalanche types that are uniquely connected to eaws problem
            if self.aval_type_tid in avalanche_ext_tid_to_eaws_problems.keys():
                self.eaws_problem = avalanche_ext_tid_to_eaws_problems[self.aval_type_tid]

            # then try some causes that are uniquely linked to eaws problems
            if self.eaws_problem is None:
                if self.cause_tid in aval_cause_to_eaws_problems.keys():
                    self.eaws_problem = aval_cause_to_eaws_problems[self.cause_tid]

            # if eaws problem still none, try some cases of dry slabs
            if self.eaws_problem is None:
                if self.aval_type_tid == 20:
                    if self.cause_tid in [10, 14]:
                        # only the AvalancheEvalProblem2 table has case attributes
                        if self.regobs_table == 'AvalancheEvalProblem2':
                            if self.cause_attribute_soft_tid > 0:
                                self.eaws_problem = 'New snow'
                            else:
                                self.eaws_problem = 'Wind-drifted snow'
                                # self.eaws_problem = None
                    if self.cause_tid in [11, 13, 16, 17, 18, 19]:
                        self.eaws_problem = 'Persistent weak layers'

        elif self.source == 'Forecast':
            if self.problem_tid is not None:
                self.eaws_problem = problem_tid_to_eaws_problems[self.problem_tid]

        else:
            ml.log_and_print('getproblems.py -> AvalancheProblem.map_to_eaws_problems: Unknown source.')
        
        """

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def from_dict(self, _d):

        self.avalanche_type_id = _d["AvalancheTypeId"]  # 10
        self.avalanche_type_name = _d["AvalancheTypeName"]  # "Flakskred",
        self.avalanche_problem_type_id = _d["AvalancheProblemTypeId"]  # 30,
        self.avalanche_problem_type_name = _d["AvalancheProblemTypeName"]  # "Vedvarende svakt lag",
        self.avalanche_ext_id = _d["AvalancheExtId"]  # 15,
        self.avalanche_ext_name = _d["AvalancheExtName"]  # "Våte løssnøskred",
        self.aval_cause_id = _d["AvalCauseId"]  # 21,
        self.aval_cause_name = _d["AvalCauseName"]  # "Snødeket gjennomfuktet og ustabilt fra overflaten",
        self.destructive_size_ext_id = _d["DestructiveSizeExtId"]  # 6,
        self.destructive_size_ext_name = _d["DestructiveSizeExtName"]  # "Store",
        self.aval_probability_id = _d["AvalProbabilityId"]  # 7,
        self.aval_probability_name = _d["AvalProbabilityName"]  # "Meget sannsynlig",
        self.aval_trigger_simple_id = _d["AvalTriggerSimpleId"]  # 21,
        self.aval_trigger_simple_name = _d["AvalTriggerSimpleName"]  # "Liten tilleggsbelastning",
        self.aval_propagation_id = _d["AvalPropagationId"]  # 3,
        self.aval_propagation_name = _d["AvalPropagationName"]  # "Mange bratte heng",
        self.exposed_height_fill = _d["ExposedHeightFill"]  # 1,
        self.exposed_height_1 = _d["ExposedHeight1"]  # 600,
        self.exposed_height_2 = _d["ExposedHeight2"]  # 0,
        self.valid_expositions = _d["ValidExpositions"]  # 10000011,
        self.avalanche_advice = _d["Avalancheadvice"]  # "Det krever mye kunnskap å gjenkjenne hvor det svake laget er gjemt. Drønnelyder, skytende sprekker og ferske skred er tydelige tegn, men fravær av tegn betyr ikke at det er trygt. Gjør svært konservative vegvalg, særlig i ukjent terreng, etter snøfall og perioder med temperaturstigning. Hold god avstand til hverandre og til løsneområdene. NB, fjernutløsning er mulig."


class MountainWeather:
    """
    The MountainWeather is published with each avalanche bulletin.
    The API returns it as ['MountainWeather'] since version 4.
    Requires forecast_api_version = 4.0 or higher in /config/api.json
    """
    def __init__(self):
        # Init properties
        self.precip_most_exposed = -1.
        self.precip_region = -1.
        self.wind_speed = -1.
        self.wind_direction = 'Not given'
        self.change_wind_speed = -1.
        self.change_wind_direction = 'Not given'
        self.change_hour_of_day_start = -1
        self.change_hour_of_day_stop = -1
        self.temperature_min = -999.
        self.temperature_max = -999.
        self.temperature_elevation = -1.
        self.freezing_level = -1.
        self.fl_hour_of_day_start = -1
        self.fl_hour_of_day_stop = -1

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def from_dict(self, _d):
        """

        :param _d: the content of the "MountainWeather" tag in the return from get_warnings_as_json
                         in getforecastapi.py (e.g. w['MountainWeather'])
        :return: A MountainWeather object
        """

        for _mt in _d['MeasurementTypes']:
            if _mt['Id'] == 10:  # precipitation
                for _st in _mt['MeasurementSubTypes']:
                    if _st['Id'] == 60:  # most exposed
                        self.precip_most_exposed = float(_st['Value'])
                    elif _st['Id'] == 70:  # regional average
                        self.precip_region = float(_st['Value'])

            elif _mt['Id'] == 20:  # wind
                for _st in _mt['MeasurementSubTypes']:
                    if _st['Id'] == 20:  # wind_speed
                        self.wind_speed = _st['Value']
                    elif _st['Id'] == 50:  # wind_direction
                        self.wind_direction = _st['Value']

            elif _mt['Id'] == 30:  # changing wind
                for _st in _mt['MeasurementSubTypes']:
                    if _st['Id'] == 20:  # wind_speed
                        self.change_wind_speed = _st['Value']
                    elif _st['Id'] == 50:  # wind_direction
                        self.change_wind_direction = _st['Value']
                    elif _st['Id'] == 100:  # hour_of_day_start
                        try:
                            self.change_hour_of_day_start = int(_st['Value'])
                        except TypeError:
                            self.change_hour_of_day_start = 0
                    elif _st['Id'] == 110:  # hour_of_day_stop
                        try:
                            self.change_hour_of_day_stop = int(_st['Value'])
                        except TypeError:
                            self.change_hour_of_day_stop = 0

            elif _mt['Id'] == 40:  # temperature
                for _st in _mt['MeasurementSubTypes']:
                    if _st['Id'] == 30:  # temperature_min
                        self.temperature_min = float(_st['Value'])
                    elif _st['Id'] == 40:  # temperature_max
                        self.temperature_max = float(_st['Value'])
                    elif _st['Id'] == 90:  # temperature_elevation
                        self.temperature_elevation = float(_st['Value'])

            elif _mt['Id'] == 50:  # freezing level
                for _st in _mt['MeasurementSubTypes']:
                    if _st['Id'] == 90:  # wind_speed
                        self.freezing_level = float(_st['Value'])
                    elif _st['Id'] == 100:  # hour_of_day_start
                        self.fl_hour_of_day_start = int(_st['Value'])
                    elif _st['Id'] == 110:  # hour_of_day_stop
                        self.fl_hour_of_day_stop = int(_st['Value'])


# Todo: rename to get_avalanche_dangers_as_json
def get_avalanche_warnings_as_json(region_ids, from_date, to_date, lang_key=1, recursive_count=5):
    """Selects warnings and returns the json structured as given on the api.

    :param region_ids:      [int or list of ints]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param from_date:       [date or string as yyyy-mm-dd]
    :param to_date:         [date or string as yyyy-mm-dd]
    :param lang_key:        [int]                       Language setting. 1 is norwegian and 2 is english.
    :param recursive_count  [int]                       by default attempt the same request # times before giving up

    :return warnings:       [string]                    String as json

    Eg. http://api01.nve.no/hydrology/forecast/avalanche/v2.0.2/api/AvalancheWarningByRegion/Detail/10/1/2013-01-10/2013-01-20
        http://api01.nve.no/hydrology/forecast/avalanche/v2.0.2/api/AvalancheWarningByRegion/Detail/29/1/2015-12-02/2015-12-02
    """

    # If input isn't a list, make it so
    if not isinstance(region_ids, list):
        region_ids = [region_ids]

    warnings = []
    recursive_count_default = recursive_count   # need the default for later

    for region_id in region_ids:

        if len(region_ids) > 1:
            # if we are looping the initial list make sure each item gets the recursive count default
            recursive_count = recursive_count_default

        # In nov 2016 we updated all regions to have ids in th 3000´s. GIS and regObs equal.
        # Before that GIS har numbers 0-99 and regObs 100-199. Messy..
        if region_id > 100 and region_id < 3000:
            region_id = region_id - 100

        url = "http://api01.nve.no/hydrology/forecast/avalanche/{4}/api/AvalancheWarningByRegion/Detail/{0}/{3}/{1}/{2}"\
            .format(region_id, from_date, to_date, lang_key, env.forecast_api_version)

        # If at first you don't succeed, try and try again.
        try:
            warnings_region = requests.get(url).json()
            ml.log_and_print('[info] getforecastapi.py -> get_avalanche_warnings_as_json: {0} warnings found for {1} in {2} to {3}'
                             .format(len(warnings_region), region_id, from_date, to_date))
            warnings += warnings_region

        except:
            ml.log_and_print('[error] getforecastapi.py -> get_avalanche_warnings_as_json: EXCEPTION. RECURSIVE COUNT {0} for {1} in {2} to {3}'
                             .format(recursive_count, region_id, from_date, to_date))
            if recursive_count > 1:
                recursive_count -= 1        # count down
                warnings += get_avalanche_warnings_as_json(region_id, from_date, to_date, lang_key, recursive_count=recursive_count)

    return warnings


# Todo: rename to get_avalanche_dangers
def get_avalanche_warnings(region_ids, from_date, to_date, lang_key=1, as_dict=False):
    """Selects warnings and returns a list of AvalancheDanger Objects. This method adds the
    avalanche problems to the warning.

    :param region_ids:  [int or list of ints]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param from_date:   [date or string as yyyy-mm-dd]
    :param to_date:     [date or string as yyyy-mm-dd]
    :param lang_key:    [int]                       Language setting. 1 is norwegian and 2 is english.
    :param as_dict:     [bool]                      when True, it returns a list of dictionaries instead of AvalancheDanger objects

    :return avalanche_danger_list: List of AvalancheDanger objects or AvalancheDanger dictionaries (see as_dict)
    """

    warnings_as_json = get_avalanche_warnings_as_json(region_ids, from_date, to_date, lang_key=lang_key)
    avalanche_warning_list = []
    exception_counter = 0

    for w in warnings_as_json:
        #try:
        region_id = int(w['RegionId'])
        region_name = w['RegionName']
        date = dt.datetime.strptime(w['ValidFrom'][0:10], '%Y-%m-%d').date()
        danger_level = int(w['DangerLevel'])
        danger_level_name = w['DangerLevelName']
        author = w['Author']
        avalanche_forecast = w['AvalancheDanger']

        try:
            avalanche_nowcast = w['AvalancheWarning']
        except:
            avalanche_nowcast = ''
            ml.log_and_print('No nowcast available.')


        warning = vc.AvalancheDanger(region_id, region_name, 'Forecast API', date, danger_level, danger_level_name)
        warning.set_source('Forecast')
        warning.set_nick(author)
        warning.set_avalanche_nowcast(avalanche_nowcast)
        warning.set_avalanche_forecast(avalanche_forecast)

        try:
            warning.set_mountain_weather(w['MountainWeather'])
        except:
            ml.log_and_print('No MountainWeather tag found in json-string - set forecast_api_version to 4.0.1 or higher')

        # http://www.varsom.no/Snoskred/Senja/?date=18.03.2015
        # http://www.varsom.no/snoskredvarsling/varsel/Indre%20Sogn/2017-01-19
        varsom_name = region_name  # .replace(u'æ', u'a').replace(u'ø', u'o').replace(u'å', u'a')
        varsom_date = date.strftime("%Y-%m-%d")
        url = "http://www.varsom.no/snoskredvarsling/varsel/{0}/{1}".format(varsom_name, varsom_date)
        warning.set_url(url)

        if lang_key == 1:
            warning.set_main_message_no(w['MainText'])
        if lang_key == 2:
            warning.set_main_message_en(w['MainText'])

        if w['AvalancheProblems'] is not None:
            for p in w['AvalancheProblems']:

                order = p['AvalancheProblemId']              # sort order of the avalanche problems in this forecast
                problem_tid = p['AvalancheProblemTypeId']
                problem_name = p['AvalancheProblemTypeName']
                cause_tid = p['AvalCauseId']                            # weak layer
                cause_name = p['AvalCauseName']

                aval_main_type_tid = p['AvalancheTypeId']               # used on varsom
                aval_main_type_name = p['AvalancheTypeName']
                aval_type_tid = p['AvalancheExtId']                     # used in regObs
                aval_type_name = p['AvalancheExtName']

                destructive_size_tid = p['DestructiveSizeExtId']
                destructive_size_name = p['DestructiveSizeExtName']

                trigger_tid = p['AvalTriggerSimpleId']
                trigger_name = p['AvalTriggerSimpleName']
                distribution_tid = p['AvalPropagationId']
                distribution_name = p['AvalPropagationName']
                probability_tid = p['AvalProbabilityId']
                probability_name = p['AvalProbabilityName']

                exposed_height_1 = p['ExposedHeight1']
                exposed_height_2 = p['ExposedHeight2']
                exposed_height_fill = p['ExposedHeightFill']                # based on values in exp heigt 1 and 2 this colores the mountain
                valid_expositions = p['ValidExpositions']                   # north is first cahr and it goes clockwize

                problem = vc.AvalancheProblem(region_id, region_name, date, order, cause_name, 'Forecast', problem_inn=problem_name)

                problem.set_cause_tid(cause_tid)
                problem.set_problem(problem_name, problem_tid)
                problem.set_aval_type(aval_type_name, aval_type_tid)
                problem.set_aval_size(destructive_size_name, destructive_size_tid)
                problem.set_aval_trigger(trigger_name, trigger_tid)
                problem.set_aval_distribution(distribution_name)
                problem.set_aval_probability(probability_name)

                problem.set_danger_level(danger_level_name, danger_level)
                problem.set_url(url)

                problem.set_regobs_table('AvalancheWarnProblem')
                problem.set_nick_name(author)
                problem.set_lang_key(lang_key)

                warning.add_problem(problem)

        if as_dict:
            avalanche_warning_list.append(warning.to_dict())
            avalanche_danger_list = sorted(avalanche_warning_list, key=lambda AvalancheDanger: AvalancheDanger['date'])
        else:
            avalanche_warning_list.append(warning)
            # Sort by date
            avalanche_danger_list = sorted(avalanche_warning_list, key=lambda AvalancheDanger: AvalancheDanger.date)
        '''
        except:
            ml.log_and_print('[error] getForecastApi -> get_avalanche_warnings: Exception at {0} of {1}'.format(len(avalanche_warning_list) + exception_counter, len(warnings_as_json)))
            exception_counter += 1
        '''


    return avalanche_danger_list


def get_valid_regids(region_id, from_date, to_date):
    """Method looks up all forecasts for a region and selects and returns the RegIDs used in regObs. Thus, the list of
    RegIDs are for published forecasts.

    :param region_id:   [int]       RegionID as given in the forecast api [1-99] or in regObs [101-199]
    :param from_date:   [string]    date as yyyy-mm-dd
    :param to_date:     [string]    date as yyyy-mm-dd
    :return:            {RegID:date, RegID:date, ...}
    """

    warnings = get_avalanche_warnings_as_json(region_id, from_date, to_date)
    valid_regids = {}

    for w in warnings:
        danger_level = int(w["DangerLevel"])
        if danger_level > 0:
            valid_regids[w["RegId"]] = w["ValidFrom"]

    return valid_regids


def get_landslide_warnings_as_json(municipality, from_date, to_date, lang_key=1, recursive_count=5):
    """Selects landslide warnings and returns the json structured as given on the api as dict objects.

    :param municipality:    [int or list of ints]       Municipality numbers
    :param from_date:       [date or string as yyyy-mm-dd]
    :param to_date:         [date or string as yyyy-mm-dd]
    :param lang_key:        [int]                       Language setting. 1 is norwegian and 2 is english.
    :param recursive_count  [int]                       by default attempt the same request # times before giving up

    :return warnings:       [warnings]

    Eg. https://api01.nve.no/hydrology/forecast/landslide/v1.0.5/api/Warning/Municipality/1201/1/2018-06-03/2018-07-03
    """

    # If input isn't a list, make it so
    if not isinstance(municipality, list):
        municipality = [municipality]

    landslide_warnings = []
    recursive_count_default = recursive_count   # need the default for later

    for m in municipality:

        if len(municipality) > 1:
            # if we are looping the initial list make sure each item gets the recursive count default
            recursive_count = recursive_count_default

        landslide_api_base_url = 'https://api01.nve.no/hydrology/forecast/landslide/v1.0.5/api'
        headers = {'Content-Type': 'application/json'}
        url = landslide_api_base_url + '/Warning/Municipality/{0}/{1}/{2}/{3}'.format(m, lang_key, from_date, to_date)

        # If at first you don't succeed, try and try again.
        try:
            landslide_warnings_municipal = requests.get(url, headers=headers).json()
            ml.log_and_print('[info] getforecastapi.py -> get_landslide_warnings_as_json: {0} warnings found for {1} in {2} to {3}'
                             .format(len(landslide_warnings_municipal), m, from_date, to_date))
            landslide_warnings += landslide_warnings_municipal

        except:
            ml.log_and_print('[error] getforecastapi.py -> get_avalanche_warnings_as_json: EXCEPTION. RECURSIVE COUNT {0} for {1} in {2} to {3}'
                             .format(recursive_count, m, from_date, to_date))
            if recursive_count > 1:
                recursive_count -= 1        # count down
                landslide_warnings += get_landslide_warnings_as_json(m, from_date, to_date, lang_key, recursive_count=recursive_count)

    return landslide_warnings


if __name__ == "__main__":

    #land_slide_warnings = get_landslide_warnings_as_json([1201], dt.date(2018, 1, 1), dt.date(2018, 4, 1))
    warnings = get_avalanche_warnings([3022, 3014], dt.date(2016, 12, 1), dt.date(2016, 12, 21))
    # p = get_valid_regids(10, '2013-03-01', '2013-03-09')

    pass
