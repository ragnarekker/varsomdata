# -*- coding: utf-8 -*-
"""All classes of varsomdata. Well, not all. regObs classes are found in getobservations.py and some very special
custom fits are found un getmisc.py.

todo: MountainWeather
"""

import datetime as dt
from utilities import makelogs as ml
from varsomdata import getobservations as go

__author__ = 'raek'


class AvalancheDanger:
    """
    TODO: Split forecast and now-cast into to different classes with the same base-class they inherit from.

    """

    def __init__(self, region_id_inn, region_name_inn, data_table_inn, date_inn, danger_level_inn,
                 danger_level_name_inn):
        """AvalancheDanger object tries to be common ground for three different tables in regObs and
        one from the forecast.

        Parameters part of the constructor:
        :param region_id_inn:           [int]       Region ID is as given in ForecastRegionKDV.
        :param region_name_inn:         [String]    Region name as given in ForecastRegionKDV.
        :param data_table_inn:          [String]    Which table/View in regObs-database is the data from
        :param date_inn:                [Date]      Date. If DateTime given it is parsed.
        :param danger_level_inn:        [int]       Danger level id (0-5)
        :param danger_level_name_inn:   [String]    Danger level written.
        :return:

        Other variables:
        metadata:                       [{key:value}, ..]
        avalanche_problems:             [list of gp.AvalanchProblems] There are allways problems in forecasts.
        """

        # In nov 2016 we updated all regions to have ids in th 3000´s. GIS and regObs equal.
        # Before that GIS har numbers 0-99 and regObs 100-199. Messy..
        # Convetion is regObs ids always
        if region_id_inn < 100:
            region_id_inn += 100

        self.metadata = {}  # [dictionary] {key:value, key:value, ..}
        self.region_regobs_id = region_id_inn  # [int]
        self.region_name = region_name_inn  # [String]
        self.data_table = data_table_inn  # [String]
        self.set_date(date_inn)  # [date]
        self.danger_level = danger_level_inn  # [Int]
        self.danger_level_name = danger_level_name_inn  # [String]

        #### Values declared when needed.
        # self.nick = None                                # [String] regObs NickName of observer or forecaster who issued the avalanche danger
        # self.source = None                              # [String] Usually 'Observasjon' or 'Varsel'
        # self.avalanche_forecast = None                  # [String] Written forecast.
        # self.avalanche_nowcast = None                   # [String] The summery of the snowcover now
        # self.municipal_name = None

        #### forecast stuff
        self.avalanche_problems = []  # [list of gp.AvalanchProblems] In forecasts there are always problems
        self.main_message_no = None  # [String] The main message in norwegian
        self.main_message_en = None  # [String] The main message in english
        self.mountain_weather = None  # contains a MountainWeather object if available

        ##### obs eval 3 stuff
        # self.forecast_correct = None                    # [String] Drop down value if the forecast is correct or no
        # self.forecast_correct_id = None                 # [int]
        # self.forecast_comment = None                    # [String] Comment from observer

    def set_regid(self, regid_inn):
        self.regid = regid_inn

    def set_date(self, date_inn):

        # makes sure we only have the date, but we keep the datetime as metadata
        if isinstance(date_inn, dt.datetime):
            self.add_metadata("Original DtObsTime", date_inn)
            date_inn = date_inn.date()

        self.date = date_inn

    def set_registration_time(self, registration_time_inn):
        # DtRegTime is when the evaluation was registered in regObs.
        self.registration_time = registration_time_inn

    def set_municipal(self, municipal_inn):
        try:
            self.municipal_name = municipal_inn
        except ValueError:
            print("Got ValueError on setting municipal name on {0} for {1}.") \
                .format(self.date, self.region_name)
        except:
            print("Got un expected error on setting municipal name on {0} for {1}.") \
                .format(self.date, self.region_name)

    def set_url(self, url_inn):
        self.url = url_inn

    def add_problem(self, problem_inn):
        self.avalanche_problems.append(problem_inn)
        # make sure lowest index (main problem) is first
        self.avalanche_problems.sort(key=lambda problems: problems.order)

    def set_mountain_weather(self, json_obj):
        _mw = MountainWeather()
        _mw.from_json(json_obj)
        self.mountain_weather = _mw

    def set_main_message_no(self, main_message_no_inn):
        # Remove double spaces, tabs, newlines etc
        self.main_message_no = ' '.join(main_message_no_inn.split())

    def set_main_message_en(self, main_message_en_inn):
        # Remove double spaces, tabs, newlines etc
        self.main_message_en = ' '.join(main_message_en_inn.split())

    def set_nick(self, nick_inn):
        self.nick = nick_inn

    def set_competence_level(self, competence_level_inn):
        self.competence_level = competence_level_inn

    def set_source(self, source_inn):
        self.source = source_inn

    def set_avalanche_nowcast(self, avalanche_nowcast_inn):
        self.avalanche_nowcast = avalanche_nowcast_inn

    def set_avalanche_forecast(self, avalanche_forecast_inn):
        self.avalanche_forecast = avalanche_forecast_inn

    def set_forecast_correct(self, forecast_correct_inn, forecast_correct_id_inn=None):

        if forecast_correct_id_inn is not None:
            forecast_correct_id_inn = int(forecast_correct_id_inn)

        self.forecast_correct_id = forecast_correct_id_inn
        self.forecast_correct = forecast_correct_inn

    def set_forecast_comment(self, forecast_comment_inn):
        self.forecast_comment = forecast_comment_inn

    def add_metadata(self, key, value):
        self.metadata[key] = value

    def to_dict(self):
        """
        Convert the object to a dictionary
        :return: dictionary representation of the AvalancheDanger class
        """
        _dict = {'metadata': self.metadata,  # [dictionary] {key:value, key:value, ..}
                 'region_regobs_id': self.region_regobs_id,  # [int]
                 'region_name': self.region_name,  # [String]
                 'date': self.date,
                 'data_table': self.data_table,  # [String]
                 'danger_level': self.danger_level,  # [Int]
                 'danger_level_name': self.danger_level_name,  # [String]
                 'nick': self.nick,
                 # [String] regObs NickName of observer or forecaster who issued the avalanche danger
                 'source': self.source,  # [String] Usually 'Observasjon' or 'Varsel'
                 'avalanche_forecast': self.avalanche_forecast,  # [String] Written forecast.
                 'avalanche_nowcast': self.avalanche_nowcast,  # [String] The summery of the snowcover now
                 'main_message_no': self.main_message_no,  # [String] The main message in norwegian
                 'main_message_en': self.main_message_en,  # [String] The main message in english

                 # mountain weather stuff
                 "mw_precip_most_exposed": self.mountain_weather.precip_most_exposed,
                 "mw_precip_region": self.mountain_weather.precip_region,
                 "mw_wind_speed": self.mountain_weather.wind_speed,
                 "mw_wind_direction": self.mountain_weather.wind_direction,
                 "mw_change_wind_speed": self.mountain_weather.change_wind_speed,
                 "mw_change_wind_direction": self.mountain_weather.change_wind_direction,
                 "mw_change_hour_of_day_start": self.mountain_weather.change_hour_of_day_start,
                 "mw_change_hour_of_day_stop": self.mountain_weather.change_hour_of_day_stop,
                 "mw_temperature_min": self.mountain_weather.temperature_min,
                 "mw_temperature_max": self.mountain_weather.temperature_max,
                 "mw_temperature_elevation": self.mountain_weather.temperature_elevation,
                 "mw_freezing_level": self.mountain_weather.freezing_level,
                 "mw_fl_hour_of_day_start": self.mountain_weather.fl_hour_of_day_start,
                 "mw_fl_hour_of_day_stop": self.mountain_weather.fl_hour_of_day_stop

                 ##### obs eval 3 stuff
                 # fix: 'forecast_correct': self.forecast_correct                    # [String] Drop down value if the forecast is correct or no
                 # fix: 'forecast_correct_id': self.forecast_correct_id                 # [int]
                 # fix: 'forecast_comment': self.forecast_comment
                 }
        #### add avalanche problems
        for _problem in self.avalanche_problems:
            problem_prefix = f"avalanche_problem_{_problem.order}_"
            _ap_dict = {f'{problem_prefix}cause_tid': _problem.cause_tid, # [int] Avalanche cause ID(TID in regObs). Only used in avalanche problems from dec 2014 and newer.
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


class AvalancheProblem:

    def __init__(self, region_regobs_id_inn, region_name_inn, date_inn, order_inn, cause_name_inn, source_inn,
                 problem_inn=None):
        """The AvalancheProblem object is useful since there are 3 different tables to get regObs-data from and 2 tables
        from forecasts. Thus avalanche problems are saved in 5 ways. The structure of this object is based on the
        "latest" model and the other/older ways to save avalanche problems on may be mapped to these.

        Parameters part of the constructor:
        :param region_regobs_id_inn:       [int]       Region ID is as given in ForecastRegionKDV.
        :param region_name_inn:     [String]    Region name as given in ForecastRegionKDV.
        :param date_inn:            [Date]      Date for avalanche problem.
        :param order_inn:           [int]       The index* of the avalanche problem.
        :param cause_name_inn:      [String]    Avalanche cause/weak layer. For newer problems this as given in AvalCauseKDV.
        :param source_inn:          [String]    The source of the data. Normally 'Observation' or 'Forecast'.
        :param problem_inn          [String]    The avalanche problem. Not given in observations (only forecasts) pr nov 2016.

        * Index doensnt allways start on 0 and count +1. A rule is that the higher the index the higher the priority.

        Other variables declared with initiation:
        metadata = []       [list with dictionaries [{},{},..] ]
        """

        # In nov 2016 we updated all regions to have ids in th 3000´s. GIS and regObs equal.
        # Before that GIS had numbers 0-99 and regObs 100-199. Messy..
        # Convention is regObs ids always
        if region_regobs_id_inn < 100:
            region_regobs_id_inn += 100

        self.metadata = {}  # dictionary {key:value, key:value, ..}
        self.region_regobs_id = region_regobs_id_inn
        self.region_name = region_name_inn
        self.date = None
        self.set_date(date_inn)
        self.order = order_inn
        self.cause_tid = None  # [int] Avalanche cause ID(TID in regObs). Only used in avalanche problems from dec 2014 and newer.
        self.cause_name = cause_name_inn
        self.source = source_inn
        self.problem = problem_inn
        self.problem_tid = None  # [int]       ID used in regObs
        self.main_cause = None  # [String] Problems/weaklayers are grouped into main problems the season 2014/15

        # The following variables are declared on a needed basis.

        # self.regid = None               # [int]       Registration ID in regObs.
        # self.municipal_name = None      # [String]
        self.aval_type = None  # [String]    Avalanche Type
        self.aval_type_tid = None  # [int]       ID used in regObs
        self.aval_size = None  # [String]    Avalanche Size
        self.aval_size_tid = None  # [int]       ID used in regObs
        # self.aval_trigger = None        # [String]    Avalanche Trigger
        # self.aval_trigger_tid = None    # [int]       ID used in regObs
        # self.aval_probability = None    # [String]    Probability for an avalanche to release
        # self.aval_distribution = None   # [String]    Avalanche distribution in the terrain. Named AvalPropagation in regObs.
        # self.registration_time = None   # [datetime]  DtRegTime is when problem was registrered by the regobs database.
        # self.regobs_table = None        # [String]    Table in regObs database.
        # self.url = None                 # [String]    Url to forecast or observation
        # self.nick_name = None           # [String]
        # self.competence_level = None    # [String]
        # self.danger_level = None        # [Int]       In some cases it is conveniant to add the forecasted danger level to the object.
        # self.danger_level_name = None   # [String]
        # self.eaws_problem = None        # [String]  in english
        # self.cause_attribute_crystal_tid = None   # [Int]
        # self.cause_attribute_light_tid = None     # [Int]
        # self.cause_attribute_soft_tid = None      # [Int]
        # self.cause_attribute_thin_tid = None      # [Int]
        # self.cause_attribute_crystal = None       # [String]
        # self.cause_attribute_light = None         # [String]
        # self.cause_attribute_soft = None          # [String]
        # self.cause_attribute_thin = None          # [String]

    def set_date(self, date_inn):

        # makes sure we only have the dat, but we keep the datetime as metadata
        if isinstance(date_inn, dt.datetime):
            self.add_metadata("Original DtObsTime", date_inn)
            date_inn = date_inn.date()

        self.date = date_inn

    def set_registration_time(self, registration_time_inn):
        # DtRegTime is when the problem was registered in regObs.
        self.registration_time = registration_time_inn

    def set_cause_tid(self, cause_tid_inn):
        self.cause_tid = cause_tid_inn

    def set_municipal(self, municipal_inn):
        try:
            self.municipal_name = municipal_inn
        except ValueError:
            print("Got ValueError on setting municipal name on {0} for {1}.") \
                .format(self.date, self.region_name)
        except:
            print("Got un expected error on setting municipal name on {0} for {1}.") \
                .format(self.date, self.region_name)

    def set_regid(self, regid_inn):
        self.regid = regid_inn

    def set_url(self, url_inn):
        self.url = url_inn

    def set_aval_type(self, aval_type_inn, aval_type_tid_inn=None):
        self.aval_type = aval_type_inn
        self.aval_type_tid = aval_type_tid_inn

    def set_aval_size(self, aval_size_inn, aval_size_tid_inn=None):
        self.aval_size = aval_size_inn
        self.aval_size_tid = aval_size_tid_inn

    def set_aval_trigger(self, aval_trigger_inn, aval_trigger_tid_inn=None):
        self.aval_trigger = aval_trigger_inn
        self.aval_trigger_tid = aval_trigger_tid_inn

    def set_aval_probability(self, aval_probability_inn):
        self.aval_probability = aval_probability_inn

    def set_aval_distribution(self, aval_distribution_inn):
        self.aval_distribution = aval_distribution_inn

    def set_aval_cause_attributes(self, problem_object):

        if isinstance(problem_object, go.AvalancheEvalProblem2):
            self.cause_attribute_crystal_tid = problem_object.AvalCauseAttributeCrystalTID
            self.cause_attribute_light_tid = problem_object.AvalCauseAttributeLightTID
            self.cause_attribute_soft_tid = problem_object.AvalCauseAttributeSoftTID
            self.cause_attribute_thin_tid = problem_object.AvalCauseAttributeThinTID

            self.cause_attribute_crystal = problem_object.AvalCauseAttributeCrystalName
            self.cause_attribute_light = problem_object.AvalCauseAttributeLightName
            self.cause_attribute_soft = problem_object.AvalCauseAttributeSoftName
            self.cause_attribute_thin = problem_object.AvalCauseAttributeThinName

            # This was fixed on api in nov 2017.
            # if self.lang_key == 2 and self.cause_attribute_crystal_tid > 0:
            #     self.cause_attribute_crystal = 'A big and identifiable crystal in the weak layer.'
            # if self.lang_key == 2 and self.cause_attribute_light_tid > 0:
            #     self.cause_attribute_light = 'The weak layer collapses easily and clean (easy propagation).'
            # if self.lang_key == 2 and self.cause_attribute_soft_tid > 0:
            #     self.cause_attribute_soft = 'The overlying slab is soft.'
            # if self.lang_key == 2 and self.cause_attribute_thin_tid > 0:
            #     self.cause_attribute_thin = 'The collapsing weak layer is thin < 3 cm.'

        else:
            ml.log_and_print(
                'getproblems -> AvalancheProblem.set_aval_cause_attributes: Avalanche problem class wrong for cause attributes.')

    def set_problem(self, problem_inn, problem_tid_inn=None):
        self.problem = problem_inn
        self.problem_tid = problem_tid_inn

    def set_regobs_table(self, table_inn):
        self.regobs_table = table_inn

    def set_nick_name(self, nick_name_inn):
        self.nick_name = nick_name_inn

    def set_competence_level(self, competence_level_inn):
        self.competence_level = competence_level_inn

    def set_danger_level(self, danger_level_name_inn, danger_level_inn):
        self.danger_level = danger_level_inn
        self.danger_level_name = danger_level_name_inn

    def set_lang_key(self, lang_key_inn):
        self.lang_key = lang_key_inn

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

    def add_metadata(self, key, value):
        self.metadata[key] = value


class MountainWeather:

    def __init__(self):
        """
        The MountainWeather is published with each avalanche bulletin.

        Requires forecast_api_version = 4.0.1 or higher in /config/api.json


        mw = w['MountainWeather']
        """
        self.precip_most_exposed = None
        self.precip_region = None
        self.wind_speed = None
        self.wind_direction = None
        self.change_wind_speed = None
        self.change_wind_direction = None
        self.change_hour_of_day_start = None
        self.change_hour_of_day_stop = None
        self.temperature_min = None
        self.temperature_max = None
        self.temperature_elevation = None
        self.freezing_level = None
        self.fl_hour_of_day_start = None
        self.fl_hour_of_day_stop = None

    def from_json(self, json_obj):
        """

        :param json_obj: the content of the "MountainWeather" tag in the return from get_warnings_as_json
                         in getforecastapi.py (e.g. w['MountainWeather'])
        :return: A MountainWeather object
        """

        for _mt in json_obj['MeasurementTypes']:
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


class KDVelement:
    """Class holds the KDV-element and has some methods used when printing."""

    def __init__(self, id_inn, sort_order_inn, is_active_inn, name_inn, description_inn, lang_key_inn):

        self.ID = id_inn
        self.Langkey = lang_key_inn
        self.Name = name_inn
        if description_inn is None:
            self.Description = ''
        else:
            self.Description = description_inn
        self.IsActive = is_active_inn
        self.SortOrder = sort_order_inn

    def file_output(self, get_header=False):

        if get_header is True:
            return '{0: <5}{1: <7}{2: <10}{3: <10}{4: <50}{5: <50}'.format(
                'ID', 'Order', 'IsActive', 'Langkey', 'Name', 'Description')
        else:
            # in case sort order None (not given) make it an empty string
            sort_order = self.SortOrder
            if not self.SortOrder:
                sort_order = ''

            return '{0: <5}{1: <7}{2: <10}{3: <10}{4: <50}{5: <50}'.format(
                self.ID, sort_order, self.IsActive, self.Langkey, self.Name, self.Description)
