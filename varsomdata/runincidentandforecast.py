# -*- coding: utf-8 -*-
__author__ = 'raek'


import getdangers as gd
import datetime as dt
import getkdvelements as gkdv
import getobservations as go
import makepickle as mp
import setenvironment as env
import fencoding as fe


class IncidentAndForecasts():
    """Contains an incident with the relevant forecast with problems added."""

    def __init__(self, incident, all_forecasts):

        self.incident = incident
        self.forecast = self.add_relevant_forecast(incident, all_forecasts)


    def add_relevant_forecast(self, incident, all_forecasts):

        date = incident.DtObsTime.date()
        forecast_region = incident.ForecastRegionName
        return_value = None

        for forecast in all_forecasts:
            if forecast.date == date and forecast.region_name in forecast_region:
                return_value = forecast
                # break

        return return_value




class NodesAndValues():

    def __init__(self, node_name_inn, node_id_inn, target_name_inn, target_id_inn):

        self.node_name = node_name_inn
        self.node_id = node_id_inn     # labeled scource in datafile
        self.target_name = target_name_inn
        self.target_id = target_id_inn
        self.value = 0

    def add_one(self):
        self.value += 1


    def update_ids(self, nodes_dict):
        self.node_id = nodes_dict[self.node_name]
        self.target_id = nodes_dict[self.target_name]


if __name__ == "__main__":

    ## Get new or load from pickle.
    get_new = False
    ## Use already made data set. Remember to make get_new = False
    make_new_incident_list = True
    make_new_node_list = True

    ## Set dates
    from_date = dt.date(2015, 11, 30)
    to_date = dt.date(2016, 6, 1)
    #to_date = dt.date.today()

    ## Get regions
    # region_id = [112, 117, 116, 128]
    region_ids = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
        if 99 < k < 150 and v.IsActive is True:
            region_ids.append(v.ID)

    ## The output
    incident_ap_dl_json = '{0}incident_and_forecast.json'.format(env.output_folder)

    ##################################### End of configuration, get data ###########################

    pickle_file_name_1 = '{0}runincidentandforecast part 1.pickle'.format(env.local_storage)
    pickle_file_name_2 = '{0}runincidentandforecast part 2.pickle'.format(env.local_storage)
    pickle_file_name_3 = '{0}runincidentandforecast part 3.pickle'.format(env.local_storage)

    if get_new:
        # get all data and save to pickle
        all_incidents = go.get_incident(from_date, to_date, region_ids=region_ids, geohazard_tid=10)
        all_forecasts = []
        for region_id in region_ids:
            all_forecasts += gd.get_forecasted_dangers(region_id, from_date, to_date, include_problems=True)
        mp.pickle_anything([all_forecasts, all_incidents], pickle_file_name_1)
    else:
        # load data from pickle
        all_forecasts, all_incidents = mp.unpickle_anything(pickle_file_name_1)

    ################################## Make incident list ##################################################

    desired_damage_extent_kdv = {#15: 'Trafikk hindret',
                                 #20: 'Kun materielle skader',
                                 #25: 'Evakuering',
                                 29: 'Nestenulykke',
                                 30: 'Personer skadet',
                                 40: 'Personer omkommet'}

    if make_new_incident_list:
        incident_list = []
        for incident in all_incidents:
            if incident.DamageExtentTID in desired_damage_extent_kdv.keys():
                incident_list.append(IncidentAndForecasts(incident, all_forecasts))

        mp.pickle_anything(incident_list, pickle_file_name_2)
    else:
        incident_list = mp.unpickle_anything(pickle_file_name_2)

    #################################### Make node list ###############################################

    if make_new_node_list:
        problem_kdv = {   0: 'Ikke gitt',
                          3: 'Toerre loessnoeskred',
                          5: 'Vaate loessnoeskred',
                          7: 'Nysnoeflak',
                          10 : 'Fokksnoe',
                          20 : 'Nysnoe',
                          30 : 'Vedvarende svakt lag',
                          37 : 'Dypt vedvarende svakt lag',
                          40 : 'Vaat snoe',
                          45 : 'Vaate flakskred',
                          50 : 'Glideskred'}

        cause_kdv = gkdv.get_kdv('AvalCauseKDV')
        danger_kdv = gkdv.get_kdv('AvalancheDangerKDV')
        activity_influenced_kdv = gkdv.get_kdv('ActivityInfluencedKDV')

        nodes_dict = {}
        id_counter = -1

        for cause_tid, cause_kdve in cause_kdv.iteritems():
            cause_name = cause_kdve.Name
            if 'kke gitt' in cause_name:
                cause_name = 'Svakt lag {0}'.format(cause_name)
            if cause_kdve.IsActive:
                id_counter += 1
                nodes_dict[cause_name] = id_counter

        for problem_tid, problem_name in problem_kdv.iteritems():
            if 'kke gitt' in problem_name:
                problem_name = 'Skredproblem {0}'.format(problem_name)
            id_counter += 1
            nodes_dict[problem_name] = id_counter

        for desired_damage_extent_tid, desired_damage_extent_name in desired_damage_extent_kdv.iteritems():
            if 'kke gitt' in desired_damage_extent_name:
                desired_damage_extent_name = 'Skadeomfang {0}'.format(desired_damage_extent_name)
            id_counter += 1
            nodes_dict[desired_damage_extent_name] = id_counter

        for activity_influenced_tid, activity_influenced_kdve in activity_influenced_kdv.iteritems():
            if activity_influenced_tid < 200:  # only snow
                activity_influenced_name = activity_influenced_kdve.Name
                if 'kke gitt' in activity_influenced_name:
                    activity_influenced_name = 'Aktivitet {0}'.format(activity_influenced_name)
                if activity_influenced_kdve.IsActive:
                    id_counter += 1
                    nodes_dict[activity_influenced_name] = id_counter

        for danger_tid, danger_kdve in danger_kdv.iteritems():
            danger_name = danger_kdve.Name
            if 'kke gitt' in danger_name:
                'Faregrad {0}'.format(danger_name)
            if danger_kdve.IsActive:
                id_counter += 1
                nodes_dict[danger_name] = id_counter

        make_nodes = True
        nodes_and_values = []
        print_counter = 0

        for i in incident_list:

            print 'Index {0} of 192 in incidentlist'.format(print_counter)
            print_counter += 1

            if i.forecast:
                cause = i.forecast.avalanche_problems[0].cause_name
                if 'kke gitt' in cause: cause = 'Svakt lag {0}'.format(cause)
                problem = i.forecast.avalanche_problems[0].main_cause
                if 'kke gitt' in problem: problem = 'Skredproblem {0}'.format(problem)

                # Loop through the cause and problem list.
                # If it is the first run make the nodes.
                # If the causes in the lists match what is in the list of acutal incidents, add one to the node.
                for cause_tid, cause_kdve in cause_kdv.iteritems():
                    if cause_kdve.IsActive:
                        cause_name = cause_kdve.Name
                        if 'kke gitt' in cause_name: cause_name = 'Svakt lag {0}'.format(cause_name)
                        for problem_tid, problem_name in problem_kdv.iteritems():
                            if 'kke gitt' in problem_name: problem_name = 'Skredproblem {0}'.format(problem_name)
                            if make_nodes:  # the run of the first item of incident_list covers all nodes
                                nodes_and_values.append(NodesAndValues(cause_name, nodes_dict[cause_name], problem_name, nodes_dict[problem_name]))
                            if cause in cause_name and problem in problem_name:
                                for nv in nodes_and_values:
                                    if cause in nv.node_name and problem in nv.target_name:
                                        nv.add_one()

                damage_extent = i.incident.DamageExtentName
                if 'kke gitt' in damage_extent: damage_extent = 'Skadeomfang {0}'.format(damage_extent)

                for problem_tid, problem_name in problem_kdv.iteritems():
                    if 'kke gitt' in problem_name:
                        problem_name = 'Skredproblem {0}'.format(problem_name)
                    for desired_damage_extent_tid, desired_damage_extent_name in desired_damage_extent_kdv.iteritems():
                        if 'kke gitt' in desired_damage_extent_name:
                            desired_damage_extent_name = 'Skadeomfang {0}'.format(desired_damage_extent_name)
                        if make_nodes:
                            nodes_and_values.append(NodesAndValues(problem_name, nodes_dict[problem_name], desired_damage_extent_name, nodes_dict[desired_damage_extent_name]))
                        if problem in problem_name and damage_extent in desired_damage_extent_name:
                            for nv in nodes_and_values:
                                if problem in nv.node_name and damage_extent in nv.target_name:
                                    nv.add_one()

                activity_influenced = i.incident.ActivityInfluencedName
                if 'kke gitt' in activity_influenced: activity_influenced = 'Aktivitet {0}'.format(activity_influenced)

                for desired_damage_extent_tid, desired_damage_extent_name in desired_damage_extent_kdv.iteritems():
                    if 'kke gitt' in desired_damage_extent_name:
                        desired_damage_extent_name = 'Skadeomfang {0}'.format(desired_damage_extent_name)
                    for activity_influenced_tid, activity_influenced_kdve in activity_influenced_kdv.iteritems():
                        if activity_influenced_tid < 200:  # only snow
                            activity_influenced_name = activity_influenced_kdve.Name
                            if 'kke gitt' in activity_influenced_name:
                                activity_influenced_name = 'Aktivitet {0}'.format(activity_influenced_name)
                            if activity_influenced_kdve.IsActive:
                                if make_nodes:
                                    nodes_and_values.append(NodesAndValues(desired_damage_extent_name, nodes_dict[desired_damage_extent_name], activity_influenced_name, nodes_dict[activity_influenced_name]))
                                if desired_damage_extent_name in damage_extent and activity_influenced_name in activity_influenced:
                                    for nv in nodes_and_values:
                                        if desired_damage_extent_name in nv.node_name and activity_influenced_name in nv.target_name:
                                            nv.add_one()

                danger = i.forecast.danger_level_name
                if 'kke gitt' in danger: danger = 'Faregrad {0}'.format(danger)

                for activity_influenced_tid, activity_influenced_kdve in activity_influenced_kdv.iteritems():
                    if activity_influenced_tid < 200:
                        activity_influenced_name = activity_influenced_kdve.Name
                        if 'kke gitt' in activity_influenced_name:
                            activity_influenced_name = 'Aktivitet {0}'.format(activity_influenced_name)
                        if activity_influenced_kdve.IsActive:
                            for danger_tid, danger_kdve in danger_kdv.iteritems():
                                danger_name = danger_kdve.Name
                                if 'kke gitt' in danger_name:
                                    'Faregrad {0}'.format(danger_name)
                                if danger_kdve.IsActive:
                                    if make_nodes:
                                        nodes_and_values.append(
                                            NodesAndValues(activity_influenced_name, nodes_dict[activity_influenced_name],
                                                           danger_name, nodes_dict[danger_name]))
                                    if activity_influenced_name in activity_influenced and danger_name in danger:
                                        for nv in nodes_and_values:
                                            if activity_influenced_name in nv.node_name and danger_name in nv.target_name:
                                                nv.add_one()

            make_nodes = False

        mp.pickle_anything(nodes_and_values, pickle_file_name_3)
    else:
        nodes_and_values = mp.unpickle_anything(pickle_file_name_3)

    #################################### Clean node list and make file###########################################

    new_nodes_and_values = []       # with values > 0

    for nv in nodes_and_values:
        if nv.value > 0:
            new_nodes_and_values.append(nv)

    new_nodes_dict = {}
    id_counter = -1
    for nv in new_nodes_and_values:
        if nv.node_name not in new_nodes_dict.keys():
            id_counter += 1
            new_nodes_dict[nv.node_name] = id_counter
    for nv in new_nodes_and_values:
        if nv.target_name not in new_nodes_dict.keys():
            id_counter += 1
            new_nodes_dict[nv.target_name] = id_counter

    for nv in new_nodes_and_values:
        nv.update_ids(new_nodes_dict)

    '''
    Output example

    {"nodes":[
    {"name": "Agricultural 'waste'"},
    ],
    "links": [
    {"source": 0, "target": 1, "value": 1240.729},
    ]
    }
    '''

    import operator
    sorted_new_nodes_dict = sorted(new_nodes_dict.items(), key=operator.itemgetter(1))

    first_nodes = True
    first_links = True

    with open(incident_ap_dl_json, "w") as myfile:
        myfile.write('{"nodes":[\n')

        for nd in sorted_new_nodes_dict:
            if first_nodes:
                myfile.write('{{"name":"{0}"}}'.format(nd[0]))
                first_nodes = False
            else:
                myfile.write(',\n{{"name":"{0}"}}'.format(nd[0]))
        myfile.write('\n],\n"links":[\n')

        for nv in new_nodes_and_values:
            if first_links:
                myfile.write('{{"source":{0},"target":{1},"value":{2}}}'.format(nv.node_id, nv.target_id, nv.value))
                first_links = False
            else:
                myfile.write(',\n{{"source":{0},"target":{1},"value":{2}}}'.format(nv.node_id, nv.target_id, nv.value))
        myfile.write('\n]}')

    a = 1
