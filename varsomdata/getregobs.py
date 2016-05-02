# -*- coding: utf-8 -*-
__author__ = 'raek'

import datetime
import requests
import getforecastapi as fa
import fencoding as fe
import setenvironment as env
import getkdvelements as gkdv
import getdangers as gd
import getproblems as gp
import getobservations as go


# Some global variables
api_version = env.api_version
registration_basestring = env.registration_basestring
kdv_elements_folder = env.kdv_elements_folder


log = []


def unix_time_2_normal(unixDatetime):
    """
    Takes in a date in unix datetime and returns a "normal date"

    :param unixDatetime:    Unix date time in milliseconds from 1.1.1970
    :return:                The date as datetime object

    Ex: date = unix_time_2_normal(int(p['DtObsTime'][6:-2]))
    """

    unix_datetime_in_seconds = unixDatetime/1000 # For some reason they are given in miliseconds
    date = datetime.datetime.fromtimestamp(int(unix_datetime_in_seconds))
    return date


def get_forecast_region_name(region_id):
    """
    Method takes in the region id (same as ForecastRegionTID in regObs). It looks up the name in ForecastRegionKDV
    and returns the region name.

    :param region_id:    Region ID is an int as given i ForecastRegionKDV
    :return:             Region Name string is returned
    """

    forecast_region_kdv = gkdv.get_kdv("ForecastRegionKDV")
    forecast_region_kdvelement = forecast_region_kdv[region_id]
    forecast_region_name = fe.remove_norwegian_letters(forecast_region_kdvelement.Name)

    return forecast_region_name


def get_problems_from_AvalancheProblemV(region_id, start_date, end_date):
    '''
    Used for observations from 2012-01-01 upp until 2012-12-02
    Elrapp used the view longer but added only "Ikke gitt"

    :param region_name:
    :param region_id:
    :param start_date:
    :param end_date:
    :return:


    Example of data:
    {
        __metadata: {
            id: "http://api.nve.no/hydrology/RegObs/v0.9.9/OData.svc/AvalancheProblemV(DtObsTime=datetime'2012-04-23T14:00:00',LangKey=1,NickName='H%C3%A5vardT%40met',RegID=2681,UTMEast=655106,UTMNorth=7763208,UTMZone=33)",
            uri: "http://api.nve.no/hydrology/RegObs/v0.9.9/OData.svc/AvalancheProblemV(DtObsTime=datetime'2012-04-23T14:00:00',LangKey=1,NickName='H%C3%A5vardT%40met',RegID=2681,UTMEast=655106,UTMNorth=7763208,UTMZone=33)",
            type: "RegObsModel.AvalancheProblemV"
        },
        RegID: 2681,
        DtObsTime: "/Date(1335189600000)/",
        DtRegTime: "/Date(1335186705637)/",
        LocationName: "Tromsø",
        UTMZone: 33,
        UTMEast: 655106,
        UTMNorth: 7763208,
        ForecastRegionName: "Tromsø",
        MunicipalName: "INGEN KOMMUNE",
        NickName: "HåvardT@met",
        CompetenceLevelName: "Ukjent",
        AvalancheProblemTID1: 2,
        AvalancheProblemTID2: 10,
        AvalancheProblemTID3: 0,
        AvalancheProblemName1: "Fokksnø",
        AvalancheProblemName2: "Solpåvirkning",
        AvalancheProblemName3: "Ikke gitt",
        LangKey: 1
    }
    '''

    region_name = get_forecast_region_name(region_id)
    view = "AvalancheProblemV"
    odata_query = "DtObsTime gt datetime'{1}' and " \
                 "DtObsTime lt datetime'{2}' and " \
                 "ForecastRegionName eq '{0}' and " \
                 "LangKey eq 1".format(region_name, start_date, end_date)
    odata_query = fe.add_norwegian_letters(odata_query)

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}?$filter={2}&$format=json".decode('utf8').format(
        api_version, view, odata_query)

    result = requests.get(url).json()
    result = result['d']['results']

    print 'getregobs.py -> get_problems_from_AvalancheProblemV: {0} observations for {1} in from {2} to {3}.'\
        .format(len(result), region_id, start_date, end_date)

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(result) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        problems = get_problems_from_AvalancheProblemV(region_id, start_date, date_in_middle) \
               + get_problems_from_AvalancheProblemV(region_id, date_in_middle, end_date)
    else:
        problems = []
        if len(result) != 0:
            for p in result:

                date = unix_time_2_normal(int(p['DtObsTime'][6:-2])).date()   # DtObsTime and data on Day0 gives best data
                cause_name1 = p["AvalancheProblemName1"]
                cause_name2 = p["AvalancheProblemName2"]
                cause_name3 = p["AvalancheProblemName3"]
                source = "Observasjon"

                if cause_name1 != "Ikke gitt":
                    prob = gp.AvalancheProblem(region_id, region_name, date, 0, cause_name1, source)
                    prob.set_regobs_view(view)
                    prob.set_regid(p['RegID'])
                    prob.set_url("{0}{1}".format(registration_basestring, prob.regid))
                    problems.append(prob)

                if cause_name2 != "Ikke gitt":
                    prob = gp.AvalancheProblem(region_id, region_name, date, 1, cause_name2, source)
                    prob.set_regobs_view(view)
                    prob.set_regid(p['RegID'])
                    prob.set_url("{0}{1}".format(registration_basestring, prob.regid))
                    problems.append(prob)

                if cause_name3 != "Ikke gitt":
                    prob = gp.AvalancheProblem(region_id, region_name, date, 2, cause_name3, source)
                    prob.set_regobs_view(view)
                    prob.set_regid(p['RegID'])
                    prob.set_url("{0}{1}".format(registration_basestring, prob.regid))
                    problems.append(prob)

    return problems


def get_problems_from_AvalancheEvalProblemV(region_id, start_date, end_date):
    '''Used for observations from 2012-11-29 up until 2014-05-13
    (elrapp used the view but added only "Ikke gitt")

    Eg url:
    http://api.nve.no/hydrology/regobs/v0.9.8/Odata.svc/AvalancheEvalProblemV?$filter=DtObsTime%20gt%20datetime%272012-01-10%27%20and%20DtObsTime%20lt%20datetime%272013-01-15%27%20and%20ForecastRegionName%20eq%20%27Senja%27%20and%20LangKey%20eq%201&$format=json

    :param region_name:
    :param region_id:
    :param start_date:
    :param end_date:
    :return:
    '''

    region_name = get_forecast_region_name(region_id)
    view = "AvalancheEvalProblemV"
    odata_query = "DtObsTime gt datetime'{1}' and " \
                 "DtObsTime lt datetime'{2}' and " \
                 "ForecastRegionName eq '{0}' and " \
                 "LangKey eq 1".format(region_name, start_date, end_date)
    odata_query = fe.add_norwegian_letters(odata_query)

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}?$filter={2}&$format=json".decode('utf8').format(
        api_version, view, odata_query)

    result = requests.get(url).json()
    result = result['d']['results']

    print 'getregobs.py -> get_problems_from_AvalancheEvalProblemV: {0} observations for {1} in from {2} to {3}.'\
        .format(len(result), region_id, start_date, end_date)

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(result) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        problems = get_problems_from_AvalancheEvalProblemV(region_id, start_date, date_in_middle) \
               + get_problems_from_AvalancheEvalProblemV(region_id, date_in_middle, end_date)
    else:
        problems = []

        if len(result) != 0:
            for p in result:

                cause = int(p['AvalCauseTID'])
                cause_ext = int(p["AvalCauseExtTID"])

                if cause != 0 and cause_ext != 0:

                    date = unix_time_2_normal(int(p['DtObsTime'][6:-2])).date()
                    order = int(p["AvalancheEvalProblemID"])
                    cause_name = fe.remove_norwegian_letters(p['AvalCauseName'])
                    cause_ext_name = fe.remove_norwegian_letters(p['AvalCauseExtName'])
                    cause_name = "{0}, {1}".format(cause_name, cause_ext_name)
                    source = "Observasjon"

                    prob = gp.AvalancheProblem(region_id, region_name, date, order, cause_name, source)

                    prob.set_municipal(p['MunicipalName'])
                    prob.set_regid(p['RegID'])
                    prob.set_url("{0}{1}".format(registration_basestring, prob.regid))
                    prob.set_aval_size(p["DestructiveSizeExtName"])
                    prob.set_problem_combined(p['AvalancheProblemCombined'])
                    prob.set_regobs_view(view)
                    prob.set_nick_name(p['NickName'])

                    problems.append(prob)

    return problems


def get_problems_from_AvalancheEvalProblem2V(region_id, start_date, end_date):
    '''Used from 2014-02-10 up to today

    http://api.nve.no/hydrology/regobs/v0.9.8/Odata.svc/AvalancheEvalProblem2V?$filter=DtObsTime%20gt%20datetime%272012-01-10%27%20and%20DtObsTime%20lt%20datetime%272015-01-15%27%20and%20ForecastRegionName%20eq%20%27Senja%27%20and%20LangKey%20eq%201&$format=json
    :param region_name:
    :param region_id:
    :param start_date:
    :param end_date:
    :return:

    Datasample:
    {
        __metadata: {
            id: "http://api.nve.no/hydrology/RegObs/v0.9.9/OData.svc/AvalancheEvalProblem2V(AvalancheEvalProblemID=0,AvalProbabilityName='Mulig%20',DtObsTime=datetime'2014-04-27T19%3A00%3A00',LangKey=1,NickName='MagnusH%40obskorps',ObsLocationID=11031,RegID=34540,UTMEast=639918,UTMNorth=7731868,UTMZone=33)",
            uri: "http://api.nve.no/hydrology/RegObs/v0.9.9/OData.svc/AvalancheEvalProblem2V(AvalancheEvalProblemID=0,AvalProbabilityName='Mulig%20',DtObsTime=datetime'2014-04-27T19%3A00%3A00',LangKey=1,NickName='MagnusH%40obskorps',ObsLocationID=11031,RegID=34540,UTMEast=639918,UTMNorth=7731868,UTMZone=33)",
            type: "RegObsModel.AvalancheEvalProblem2V"
        },
        RegID: 34540,
        AvalancheEvalProblemID: 0,
        DtObsTime: "/Date(1398625200000)/",
        DtRegTime: "/Date(1398633678170)/",
        ObsLocationID: 11031,
        LocationName: "Steinskardtind",
        UTMZone: 33,
        UTMEast: 639918,
        UTMNorth: 7731868,
        ForecastRegionName: "Tromsø",
        MunicipalName: "TROMSØ",
        NickName: "MagnusH@obskorps",
        CompetenceLevelName: "****",
        AvalancheExtTID: 0,
        AvalancheExtName: "Ikke gitt ",
        AvalCauseTID: 22,
        AvalCauseName: "Opphopning av vann over skarelag",
        AvalCauseDepthTID: 2,
        AvalCauseDepthName: "Innen en meter",
        AvalCauseAttributes: 4,
        AvalCauseAttributeName: "Det overliggende laget er mykt.  ",
        DestructiveSizeTID: 2,
        DestructiveSizeName: "2 - Små",
        AvalTriggerSimpleTID: 10,
        AvalTriggerSimpleName: "Stor tilleggsbelastning ",
        AvalProbabilityTID: 3,
        AvalProbabilityName: "Mulig ",
        ValidExposition: "00000000",
        ExposedHeight1: 600,
        ExposedHeight2: 300,
        Comment: "Gammelt skarelag i ferd med å gå i oppløsning. Laget over og under er omvandlet til fuktig/våt grovkornet snø. Skarelaget bærer ikke lenger og kan kollapse. Ser ut til å ha liten evne til propagering, men glir ut som lite flak.",
        LangKey: 1
}

    '''

    region_name = get_forecast_region_name(region_id)
    aval_cause_kdv = gkdv.get_kdv('AvalCauseKDV')
    view = "AvalancheEvalProblem2V"

    odata_query = "DtObsTime gt datetime'{1}' and " \
                 "DtObsTime lt datetime'{2}' and " \
                 "ForecastRegionName eq '{0}' and " \
                 "LangKey eq 1".format(region_name, start_date, end_date)
    odata_query = fe.add_norwegian_letters(odata_query)

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}?$filter={2}&$format=json".decode('utf8').format(
        api_version, view, odata_query)

    result = requests.get(url).json()
    result = result['d']['results']

    print 'getregobs.py -> get_problems_from_AvalancheEvalProblem2V: {0} observations for {1} in from {2} to {3}.'\
        .format(len(result), region_id, start_date, end_date)


    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(result) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        problems = get_problems_from_AvalancheEvalProblem2V(region_id, start_date, date_in_middle) \
               + get_problems_from_AvalancheEvalProblem2V(region_id, date_in_middle, end_date)
    else:

        problems = []

        if len(result) != 0:
            for p in result:
                cause = int(p['AvalCauseTID'])
                if cause != 0:

                    date = unix_time_2_normal(int(p['DtObsTime'][6:-2])).date()
                    order = int(p["AvalancheEvalProblemID"])
                    cause_tid = p['AvalCauseTID']
                    cause_name = aval_cause_kdv[cause_tid].Name
                    source = "Observasjon"

                    prob = gp.AvalancheProblem(region_id, region_name, date, order, cause_name, source)

                    prob.set_cause_tid(cause_tid)
                    prob.set_municipal(p['MunicipalName'])
                    prob.set_regid(p['RegID'])
                    prob.set_url("{0}{1}".format(registration_basestring, prob.regid))
                    prob.set_aval_size(p["DestructiveSizeName"])
                    prob.set_problem_combined(p['AvalCauseName'])
                    prob.set_regobs_view(view)
                    prob.set_nick_name(p['NickName'])

                    problems.append(prob)

    return problems


def get_problems_from_AvalancheWarningV(region_id, start_date, end_date):
    '''

    :param region_name:
    :param region_id:
    :param start_date:
    :param end_date:
    :return:

    Used for warnings 2012-01 to 2012-07

    results: [
        {
        __metadata: {
        id: "http://api.nve.no/hydrology/RegObs/v0.9.8/OData.svc/AvalancheWarningV(AvalancheEvaluation='Det%20har%20bl%C3%A5st%20nordlig%20stiv%20kuling%20i%20fjellet%20siste%20d%C3%B8gn.%205-10%20cm%20nysn%C3%B8%20siste%20to%20d%C3%B8gn.%0D%0AI%20begynnelsen%20av%20uken%20ble%20det%20observert%20mindre%20skred%20p%C3%A5%20grunn%20av%20solinnstr%C3%A5ling.%20Observasjoner%20viser%20at%20nysn%C3%B8en%20fra%20siste%20nedb%C3%B8rperiode%20n%C3%A5%20har%20festet%20seg%20bra%20til%20det%20gamle%20sn%C3%B8dekket%2C%20spesielt%20i%20S%C3%98-vendte%20fjellsider.%20Flakene%20krever%20dog%20fortsatt%20oppmerksomhet.%20Det%20er%20observert%20rimkrystaller%20i%20h%C3%B8yden%20i%20fjellsider%20med%20skygge%2C%20men%20det%20er%20usikkert%20hvorvidt%20disse%20fortsatt%20er%20intakte.%20',AvalancheWarning='Det%20ventes%20%C3%A5%20dannes%20et%20polart%20lavtrykk%20i%20havet%20utenfor%20Troms%20natt%20til%20fredag.%20Plasseringen%20av%20dette%20er%20enn%C3%A5%20usikker%2C%20men%20der%20det%20treffer%20land%20vil%20det%20bli%20kortvarig%20mye%20vind%20fra%20nord%20og%20kraftige%20sn%C3%B8-%20og%20haglbyger.%20Vinden%20ventes%20%C3%A5%20komme%20opp%20i%20stiv%20kuling.%0D%0ANedb%C3%B8r%20som%20torsdag%20og%20fredag%20kommer%20med%20vind%20fra%20N%20og%20NV%20kan%20danne%20flak%20i%20leheng.%20Disse%20vil%20trolig%20kunne%20l%C3%B8ses%20ut%20med%20liten%20tilleggsbelastning%20i%20bratt%20terreng.%20I%20fjellsider%20der%20rimkrystaller%20var%20intakte%20f%C3%B8r%20de%20sn%C3%B8dde%20ned%2C%20typiske%20i%20sider%20med%20skygge%2C%20vil%20det%20v%C3%A6re%20ustabile%20forhold%20dersom%20det%20legger%20seg%20flak%20av%20betydning.%20L%C3%B8rdag%20minking%20til%20skiftende%20bris%20og%20mye%20pent%20v%C3%A6r.%20L%C3%B8rdag%20vil%20det%20kunne%20l%C3%B8ses%20ut%20l%C3%B8ssn%C3%B8skred%20i%20bratte%20soleksponerte%20fjellsider%20p%C3%A5%20grunn%20av%20solinnstr%C3%A5ling.%20Nedb%C3%B8rvarslet%20for%20fredag%20er%20usikkert%20og%20dersom%20det%20ikke%20kommer%20varslet%20nedb%C3%B8rmengde%20vil%20faregraden%20fredag%20og%20l%C3%B8rdag%20v%C3%A6re%202-moderat.%20',Day0AvalDangerTID=2,DtNextWarningTime=datetime'2012-04-16T16:00:00',DtValidToTime=datetime'2012-04-14T00:00:00',LangKey=1,NickName='Kalle%40NGI',ObserverGroupName='Sn%C3%B8skredvarslingen',ObsLocationID=39,RegID=2472,UTMEast=655106,UTMNorth=7763208,UTMZone=33)",
        uri: "http://api.nve.no/hydrology/RegObs/v0.9.8/OData.svc/AvalancheWarningV(AvalancheEvaluation='Det%20har%20bl%C3%A5st%20nordlig%20stiv%20kuling%20i%20fjellet%20siste%20d%C3%B8gn.%205-10%20cm%20nysn%C3%B8%20siste%20to%20d%C3%B8gn.%0D%0AI%20begynnelsen%20av%20uken%20ble%20det%20observert%20mindre%20skred%20p%C3%A5%20grunn%20av%20solinnstr%C3%A5ling.%20Observasjoner%20viser%20at%20nysn%C3%B8en%20fra%20siste%20nedb%C3%B8rperiode%20n%C3%A5%20har%20festet%20seg%20bra%20til%20det%20gamle%20sn%C3%B8dekket%2C%20spesielt%20i%20S%C3%98-vendte%20fjellsider.%20Flakene%20krever%20dog%20fortsatt%20oppmerksomhet.%20Det%20er%20observert%20rimkrystaller%20i%20h%C3%B8yden%20i%20fjellsider%20med%20skygge%2C%20men%20det%20er%20usikkert%20hvorvidt%20disse%20fortsatt%20er%20intakte.%20',AvalancheWarning='Det%20ventes%20%C3%A5%20dannes%20et%20polart%20lavtrykk%20i%20havet%20utenfor%20Troms%20natt%20til%20fredag.%20Plasseringen%20av%20dette%20er%20enn%C3%A5%20usikker%2C%20men%20der%20det%20treffer%20land%20vil%20det%20bli%20kortvarig%20mye%20vind%20fra%20nord%20og%20kraftige%20sn%C3%B8-%20og%20haglbyger.%20Vinden%20ventes%20%C3%A5%20komme%20opp%20i%20stiv%20kuling.%0D%0ANedb%C3%B8r%20som%20torsdag%20og%20fredag%20kommer%20med%20vind%20fra%20N%20og%20NV%20kan%20danne%20flak%20i%20leheng.%20Disse%20vil%20trolig%20kunne%20l%C3%B8ses%20ut%20med%20liten%20tilleggsbelastning%20i%20bratt%20terreng.%20I%20fjellsider%20der%20rimkrystaller%20var%20intakte%20f%C3%B8r%20de%20sn%C3%B8dde%20ned%2C%20typiske%20i%20sider%20med%20skygge%2C%20vil%20det%20v%C3%A6re%20ustabile%20forhold%20dersom%20det%20legger%20seg%20flak%20av%20betydning.%20L%C3%B8rdag%20minking%20til%20skiftende%20bris%20og%20mye%20pent%20v%C3%A6r.%20L%C3%B8rdag%20vil%20det%20kunne%20l%C3%B8ses%20ut%20l%C3%B8ssn%C3%B8skred%20i%20bratte%20soleksponerte%20fjellsider%20p%C3%A5%20grunn%20av%20solinnstr%C3%A5ling.%20Nedb%C3%B8rvarslet%20for%20fredag%20er%20usikkert%20og%20dersom%20det%20ikke%20kommer%20varslet%20nedb%C3%B8rmengde%20vil%20faregraden%20fredag%20og%20l%C3%B8rdag%20v%C3%A6re%202-moderat.%20',Day0AvalDangerTID=2,DtNextWarningTime=datetime'2012-04-16T16:00:00',DtValidToTime=datetime'2012-04-14T00:00:00',LangKey=1,NickName='Kalle%40NGI',ObserverGroupName='Sn%C3%B8skredvarslingen',ObsLocationID=39,RegID=2472,UTMEast=655106,UTMNorth=7763208,UTMZone=33)",
        type: "RegObsModel.AvalancheWarningV"
        },
        RegID: 2472,
        DtObsTime: "/Date(1334246400000)/",
        DtRegTime: "/Date(1334246249110)/",
        ObsLocationID: 39,
        LocationName: "Tromsø",
        UTMZone: 33,
        UTMEast: 655106,
        UTMNorth: 7763208,
        ForecastRegionName: "Tromsø",
        MunicipalName: "INGEN KOMMUNE",
        NickName: "Kalle@NGI",
        ObserverGroupName: "Snøskredvarslingen",
        ObserverGroupDescription: "Snøskredvarslingen i Norge utgir regionale varsler for snøskredfare. Varslene brukes på eget ansvar og ikke til kritiske avgjørelser alene. Snøskredvarslingen er et samarbeid mellom NVE, met.no, Statens vegvesen og Jernbaneverket.",
        CompetenceLevelName: "Ukjent",
        Day0AvalDangerTID: 2,
        Day0AvalDangerName: "2 Moderat",
        Day0ValidExposition: "11011100",
        Day0ValidHeightRelative: "001",
        Day1ValidExposition: "11011100",
        Day1ValidHeightRelative: "001",
        Day2ValidExposition: "11011100",
        Day2ValidHeightRelative: "001",
        Day0AvalProblemTID1: 2,
        Day0AvalProblemName1: "Fokksnø",
        Day0AvalProblemName2: "Ustabile lag i dekket",
        Day0AvalProblemName3: "Ikke gitt",
        Day1AvalProblemName1: "Fokksnø",
        Day1AvalProblemName2: "Ustabile lag i dekket",
        Day1AvalProblemName3: "Ikke gitt",
        Day2AvalProblemName1: "Fokksnø",
        Day2AvalProblemName2: "Solpåvirkning",
        Day2AvalProblemName3: "Ustabile lag i dekket",
        Day1AvalDangerTID: 3,
        Day1AvalDangerName: "3 Betydelig",
        Day2AvalDangerTID: 3,
        Day2AvalDangerName: "3 Betydelig",
        AvalancheWarning: "Det ventes å dannes et polart lavtrykk i havet utenfor Troms natt til fredag. Plasseringen av dette er ennå usikker, men der det treffer land vil det bli kortvarig mye vind fra nord og kraftige snø- og haglbyger. Vinden ventes å komme opp i stiv kuling.
        Nedbør som torsdag og fredag kommer med vind fra N og NV kan danne flak i leheng. Disse vil trolig kunne løses ut med liten tilleggsbelastning i bratt terreng. I fjellsider der rimkrystaller var intakte før de snødde ned, typiske i sider med skygge, vil det være ustabile forhold dersom det legger seg flak av betydning. Lørdag minking til skiftende bris og mye pent vær. Lørdag vil det kunne løses ut løssnøskred i bratte soleksponerte fjellsider på grunn av solinnstråling. Nedbørvarslet for fredag er usikkert og dersom det ikke kommer varslet nedbørmengde vil faregraden fredag og lørdag være 2-moderat. ",
        AvalancheEvaluation: "Det har blåst nordlig stiv kuling i fjellet siste døgn. 5-10 cm nysnø siste to døgn.
        I begynnelsen av uken ble det observert mindre skred på grunn av solinnstråling. Observasjoner viser at nysnøen fra siste nedbørperiode nå har festet seg bra til det gamle snødekket, spesielt i SØ-vendte fjellsider. Flakene krever dog fortsatt oppmerksomhet. Det er observert rimkrystaller i høyden i fjellsider med skygge, men det er usikkert hvorvidt disse fortsatt er intakte. ",
        Comment: null,
        DtNextWarningTime: "/Date(1334592000000)/",
        DtValidToTime: "/Date(1334361600000)/",
        LangKey: 1
        }
        ]
        '''

    region_name = get_forecast_region_name(region_id)
    view = "AvalancheWarningV"
    odata_query = "DtObsTime gt datetime'{1}' and " \
                 "DtObsTime lt datetime'{2}' and " \
                 "ForecastRegionName eq '{0}' and " \
                 "LangKey eq 1".format(region_name, start_date, end_date)
    odata_query = fe.add_norwegian_letters(odata_query)

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}?$filter={2}&$format=json".decode('utf8').format(
        env.old_api_version, view, odata_query)
    result = requests.get(url).json()
    try:
        result = result['d']['results']
    except:
        result = []

    print 'getregobs.py -> get_problems_from_AvalancheWarningV: {0} observations for {1} in from {2} to {3}.'\
        .format(len(result), region_id, start_date, end_date)

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(result) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        problems = get_problems_from_AvalancheWarningV(region_id, start_date, date_in_middle) \
               + get_problems_from_AvalancheWarningV(region_id, date_in_middle, end_date)
    else:
        problems = []
        if len(result) != 0:
            for p in result:

                date = unix_time_2_normal(int(p['DtObsTime'][6:-2])).date()   # DtObsTime and data on Day0 gives best data
                cause_name1 = p["Day0AvalProblemName1"]
                cause_name2 = p["Day0AvalProblemName2"]
                cause_name3 = p["Day0AvalProblemName3"]
                source = "Varsel"

                # http://api.nve.no/hydrology/regobs/v0.9.8/Odata.svc/AvalancheWarningV?$filter=RegID%20eq%202472%20and%20LangKey%20eq%201&$format=json
                view_url_base = 'http://api.nve.no/hydrology/regobs/v0.9.8/Odata.svc/AvalancheWarningV?$filter=RegID%20eq%20{0}%20and%20LangKey%20eq%201&$format=json'

                if cause_name1 != "Ikke gitt":
                    prob = gp.AvalancheProblem(region_id, region_name, date, 0, cause_name1, source)
                    prob.set_regobs_view(view)
                    prob.set_regid(p['RegID'])
                    prob.set_url(view_url_base.format(p['RegID']))
                    problems.append(prob)

                if cause_name2 != "Ikke gitt":
                    prob = gp.AvalancheProblem(region_id, region_name, date, 1, cause_name2, source)
                    prob.set_regobs_view(view)
                    prob.set_regid(p['RegID'])
                    prob.set_url(view_url_base.format(p['RegID']))
                    problems.append(prob)

                if cause_name3 != "Ikke gitt":
                    prob = gp.AvalancheProblem(region_id, region_name, date, 2, cause_name3, source)
                    prob.set_regobs_view(view)
                    prob.set_regid(p['RegID'])
                    prob.set_url(view_url_base.format(p['RegID']))
                    problems.append(prob)

    return problems


def get_problems_from_AvalancheWarnProblemV(region_id, start_date, end_date):
    '''AvalancheWarnProblemV used from 2012-11-15 to today. It selects only problems linked to published
    warnings.

    There was made changes to the view in des 2013 which I think affected destructive size and avalanche cause.
    Changes were made to the data model before startup in december 2014. Changes involve use of cause_name
    and avalanche size.

    Notes to do:
    * aval_type distingushes if aval type is dry or wet. Varsom does not this any more.
    * lots of typos in KDV_names. Inconsistent capitalization, blankspace at end of line.
    * exposed terain not included
    * no mapping to the manin categroies of avalanche problems.

    :param region_name:
    :param region_id:
    :param start_date:
    :param end_date:
    :return:

    {
        __metadata: {
            id: "http://api.nve.no/hydrology/RegObs/v0.9.9/OData.svc/AvalancheWarnProblemV(AvalancheWarnProblemID=1,AvalProbabilityName='Mulig%20',DtObsTime=datetime'2015-01-08T11%3A43%3A24.593',LangKey=1,NickName='Silje%40svv',ObsLocationID=39,RegID=45272,TMNorth=7763208,UTMEast=655106,UTMZone=33)",
            uri: "http://api.nve.no/hydrology/RegObs/v0.9.9/OData.svc/AvalancheWarnProblemV(AvalancheWarnProblemID=1,AvalProbabilityName='Mulig%20',DtObsTime=datetime'2015-01-08T11%3A43%3A24.593',LangKey=1,NickName='Silje%40svv',ObsLocationID=39,RegID=45272,TMNorth=7763208,UTMEast=655106,UTMZone=33)",
            type: "RegObsModel.AvalancheWarnProblemV"
        },
        RegID: 45272,
        AvalancheWarnProblemID: 1,
        DtObsTime: "/Date(1420717404593)/",
        DtRegTime: "/Date(1420717404320)/",
        ObsLocationID: 39,
        LocationName: "Tromsø",
        UTMZone: 33,
        UTMEast: 655106,
        TMNorth: 7763208,
        ForecastRegionTID: 108,
        ForecastRegionName: "Tromsø",
        MunicipalName: "INGEN KOMMUNE",
        NickName: "Silje@svv",
        ObserverGroupID: 1,
        CompetenceLevelTID: 120,
        CompetenceLevelName: "***",
        AvalProbabilityTID: 3,
        AvalProbabilityName: "Mulig ",
        AvalTriggerSimpleTID: 10,
        AvalTriggerSimpleName: "Stor tilleggsbelastning ",
        DestructiveSizeExtTID: 0,
        DestructiveSizeExtName: "Ikke gitt",
        AvalancheExtTID: 20,
        AvalancheExtName: "Tørre flakskred",
        AvalCauseTID: 15,
        AvalCauseName: "Dårlig binding mellom lag i fokksnøen",
        AvalCauseExtTID: 0,
        AvalCauseExtName: "ikke gitt ",
        AvalReleaseHeightTID: 0,
        AvalReleaseHeighName: "Ikke gitt ",
        ProbabilityCombined: null,
        CauseCombined: null,
        ReleaseHeightCombined: "",
        AvalancheProblemCombined: "  ",
        Comment: null,
        LangKey: 1,
        ValidExposistion: "11111111",
        ExposedHeight1: 400,
        ExposedHeight2: 0,
        ExposedHeightComboTID: 1,
        DestructiveSizeTID: 1,
        DestructiveSizeName: "1 - Harmløst",
        SortOrder: 1,
        AvalPropagationTID: 1,
        AvalPropagationName: "Isolerte faresoner",
        AvalWeakLayerId: null,
        AdviceText: "Se etter områder hvor vinden nylig har lagt fra seg fokksnø, typisk bak rygger, i renneformasjoner og søkk. Lokale vindeffekter og skiftende vindretning kan gi stor variasjon i hvor fokksnøen legger seg. Snø som sprekker opp rundt skiene/brettet er et typisk tegn. Unngå områder med fokksnø til den har fått stabilisert seg. Det er størst sannsynlighet for å løse ut skred på kul-formasjoner i terrenget og der fokksnøen er myk."
    }


    '''
    region_name = get_forecast_region_name(region_id)
    aval_cause_kdv = gkdv.get_kdv('AvalCauseKDV')
    view = "AvalancheWarnProblemV"

    # Note this view queries on LocationName and not on ForeCastRegionName as the other views
    odata_query = "DtObsTime gt datetime'{1}' and " \
             "DtObsTime lt datetime'{2}' and " \
             "LocationName eq '{0}' and " \
             "LangKey eq 1".format(region_name, start_date, end_date)
    odata_query = fe.add_norwegian_letters(odata_query)

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}?$filter={2}&$format=json".decode('utf8').format(
        env.old_api_version, view, odata_query)
    result = requests.get(url).json()
    try:
        result = result['d']['results']
    except:
        result = []

    print 'getregobs.py -> get_problems_from_AvalancheWarnProblemV: {0} observations for {1} in from {2} to {3}.'\
        .format(len(result), region_id, start_date, end_date)

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(result) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        problems = get_problems_from_AvalancheWarnProblemV(region_id, start_date, date_in_middle) \
               + get_problems_from_AvalancheWarnProblemV(region_id, date_in_middle, end_date)
    else:
        valid_regids = fa.get_valid_regids(region_id-100, start_date, end_date)
        problems = []
        if len(result) != 0:
            for p in result:
                regid = p["RegID"]

                if regid in valid_regids:

                    date = datetime.datetime.strptime(valid_regids[regid][0:10], '%Y-%m-%d').date()
                    source = "Varsel"

                    aval_cause_tid = int(p['AvalCauseTID']) + int(p['AvalCauseExtTID'])
                    cause_name = p["CauseCombined"]
                    aval_size = fe.remove_norwegian_letters(p['DestructiveSizeExtName'])
                    aval_type = p['AvalancheExtName']
                    aval_trigger = fe.remove_norwegian_letters(p['AvalTriggerSimpleName'])
                    aval_probability = fe.remove_norwegian_letters(p['AvalProbabilityName'])
                    aval_distribution = fe.remove_norwegian_letters(p['AvalPropagationName'])
                    aval_cause_combined = p['AvalancheProblemCombined']
                    problem_url = 'http://api.nve.no/hydrology/regobs/{0}/Odata.svc/{1}?$filter=RegID eq {2} and LangKey eq 1&$format=json'.format(api_version, view, regid)

                    # from late november 2013 there was a change in data model
                    if date > datetime.datetime.strptime('2013-11-15', '%Y-%m-%d').date():
                        aval_cause_tid = int(p['AvalCauseTID'])
                        cause_name = aval_cause_kdv[aval_cause_tid].Name
                        aval_size = fe.remove_norwegian_letters(p['DestructiveSizeName'])
                        aval_probability = fe.remove_norwegian_letters(p['AvalProbabilityName'])
                        aval_distribution = fe.remove_norwegian_letters(p['AvalPropagationName'])
                        aval_cause_combined = p['AvalCauseName']

                        # http://www.varsom.no/Snoskred/Senja/?date=18.03.2015
                        varsom_name = region_name.replace('æ','a').replace('ø','o').replace('å','a')
                        varsom_date = date.strftime("%d.%m.%Y")
                        problem_url = "http://www.varsom.no/Snoskred/{0}/?date={1}".format(varsom_name, varsom_date)

                    if cause_name is not None and aval_cause_tid != 0:
                        order = int(p["AvalancheWarnProblemID"])
                        prob = gp.AvalancheProblem(region_id, region_name, date, order, cause_name, source)
                        prob.set_aval_type(aval_type)
                        prob.set_aval_size(aval_size)
                        prob.set_aval_trigger(aval_trigger)
                        prob.set_aval_distribution(aval_distribution)
                        prob.set_aval_probability(aval_probability)
                        prob.set_problem_combined(aval_cause_combined)
                        prob.set_regobs_view(view)
                        prob.set_url(problem_url)
                        prob.set_cause_tid(aval_cause_tid)
                        prob.set_main_cause(cause_name)
                        problems.append(prob)

    return problems


def get_observed_danger_AvalancheEvaluation3V(region_id, start_date, end_date):
    '''

    :param region_id:
    :param start_date:
    :param end_date:
    :return:
    '''


    region_name = get_forecast_region_name(region_id)
    oDataQuery = "DtObsTime gt datetime'{1}' and " \
                 "DtObsTime lt datetime'{2}' and " \
                 "ForecastRegionName eq '{0}' and " \
                 "LangKey eq 1".format(region_name, start_date, end_date)
    oDataQuery = fe.add_norwegian_letters(oDataQuery)    # Need norwegian letters in the URL

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/AvalancheEvaluation3V?$filter={1}&$format=json".decode('utf8').format(api_version, oDataQuery)
    AvalancheEvaluation3V = requests.get(url).json()
    avalEval3 = AvalancheEvaluation3V['d']['results']

    print 'getregobs.py -> get_observed_danger_AvalancheEvaluation3V: {0} observations for {1} in from {2} to {3}.'\
        .format(len(avalEval3), region_id, start_date, end_date)

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(avalEval3) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        evaluations = get_observed_danger_AvalancheEvaluation3V(region_id, start_date, date_in_middle) \
               + get_observed_danger_AvalancheEvaluation3V(region_id, date_in_middle, end_date)
    else:

        evaluations = []

        if len(avalEval3) != 0:
            for e in avalEval3:
                date = unix_time_2_normal(int(e['DtObsTime'][6:-2]))
                danger_level = e['AvalancheDangerTID']
                danger_level_name = e['AvalancheDangerName']
                nick = e['NickName']
                eval = gd.AvalancheDanger(region_id, region_name, "AvalancheEvaluation3V", date, danger_level, danger_level_name)
                eval.set_nick(nick)
                eval.set_source('Observasjon')
                evaluations.append(eval)

    # sort list by date
    #evaluations = sorted(evaluations, key=lambda AvalancheEvaluation: AvalancheEvaluation.date)

    return evaluations


def get_observed_danger_AvalancheEvaluation2V(region_id, start_date, end_date):
    '''

    :param region_id:
    :param start_date:
    :param end_date:
    :return:
    '''


    region_name = get_forecast_region_name(region_id)
    oDataQuery = "DtObsTime gt datetime'{1}' and " \
                 "DtObsTime lt datetime'{2}' and " \
                 "ForecastRegionName eq '{0}' and " \
                 "LangKey eq 1".format(region_name, start_date, end_date)
    oDataQuery = fe.add_norwegian_letters(oDataQuery)    # Need norwegian letters in the URL

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/AvalancheEvaluation2V?$filter={1}&$format=json".decode('utf8').format(api_version, oDataQuery)
    AvalancheEvaluation2V = requests.get(url).json()
    avalEval2 = AvalancheEvaluation2V['d']['results']

    print 'getregobs.py -> get_observed_danger_AvalancheEvaluation2V: {0} observations for {1} in from {2} to {3}.'\
        .format(len(avalEval2), region_id, start_date, end_date)

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(avalEval2) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        evaluations = get_observed_danger_AvalancheEvaluation2V(region_id, start_date, date_in_middle) \
               + get_observed_danger_AvalancheEvaluation2V(region_id, date_in_middle, end_date)
    else:

        evaluations = []

        if len(avalEval2) != 0:
            for e in avalEval2:
                date = unix_time_2_normal(int(e['DtObsTime'][6:-2]))
                danger_level = e['AvalancheDangerTID']
                danger_level_name = e['AvalancheDangerName']
                nick = e['NickName']
                eval = gd.AvalancheDanger(region_id, region_name, "AvalancheEvaluation2V", date, danger_level, danger_level_name)
                eval.set_nick(nick)
                eval.set_source('Observasjon')
                evaluations.append(eval)

    # sort list by date
    # evaluations = sorted(evaluations, key=lambda AvalancheEvaluation: AvalancheEvaluation.date)

    return evaluations


def get_observed_danger_AvalancheEvaluationV(region_id, start_date, end_date):
    '''

    :param region_id:
    :param start_date:
    :param end_date:
    :return:
    '''

    region_name = get_forecast_region_name(region_id)
    oDataQuery = "DtObsTime gt datetime'{1}' and " \
                 "DtObsTime lt datetime'{2}' and " \
                 "ForecastRegionName eq '{0}' and " \
                 "LangKey eq 1".format(region_name, start_date, end_date)
    oDataQuery = fe.add_norwegian_letters(oDataQuery)    # Need norwegian letters in the URL

    url = "http://api.nve.no/hydrology/regobs/{0}/Odata.svc/AvalancheEvaluationV?$filter={1}&$format=json".decode('utf8').format(api_version, oDataQuery)
    AvalancheEvaluationV = requests.get(url).json()
    avalEval = AvalancheEvaluationV['d']['results']

    print 'getregobs.py -> get_observed_danger_AvalancheEvaluationV: {0} observations for {1} in from {2} to {3}.'\
        .format(len(avalEval), region_id, start_date, end_date)

    # if more than 1000 elements are requested, odata truncates data to 1000. We do more requests
    if len(avalEval) == 1000:
        time_delta = end_date - start_date
        date_in_middle = start_date + time_delta/2
        evaluations = get_observed_danger_AvalancheEvaluationV(region_id, start_date, date_in_middle) \
               + get_observed_danger_AvalancheEvaluationV(region_id, date_in_middle, end_date)
    else:

        evaluations = []

        if len(avalEval) != 0:
            for e in avalEval:
                date = unix_time_2_normal(int(e['DtObsTime'][6:-2]))
                danger_level = e['AvalancheDangerTID']
                danger_level_name = e['AvalancheDangerName']
                nick = e['NickName']
                eval = gd.AvalancheDanger(region_id, region_name, "AvalancheEvaluationV", date, danger_level, danger_level_name)
                eval.set_nick(nick)
                eval.set_source('Observasjon')
                evaluations.append(eval)

    # sort list by date
    # evaluations = sorted(evaluations, key=lambda AvalancheEvaluation: AvalancheEvaluation.date)

    return evaluations


def __get_cause_from_old_cause(old_cause_parameter_name, old_cause_tid):
    '''
    INCOMPLETE

    This method returns the value of a new avalalnche caus given an old one.
    This transformation is going to induce som errors because the old avalanche causes are not exactly
    projectet/compatible with the new ones. That why we made new ones...

    :param old_cause_parameter_name:
    :param old_cause_tid:
    :return:

    aval_cause_kdv{
        0: 'Ikke gitt',
        1: 'Regn',
        2: 'Oppvarming',
        3: 'Ingen gjenfrysing',
        4: 'Paalagring',
        5: 'Svake lag',
        6: 'Regn + oppvarming',
        7: 'Regn + oppvarm + ingen gj.frys',
        8: 'Vind',
        9: 'Oppvarm + ingen gj.frys',
        10: 'Lag med loes nysnoe',
        11: 'Lag med overflaterim',
        12: 'Lag med sproehagl',
        13: 'Lag med kantkornet snoe',
        14: 'Glatt skare',
        15: 'I fokksnoeen',
        16: 'Kantkornet ved bakken',
        17: 'Kantkornet rundt vegetasjon',
        18: 'Kantkornet over skaren',
        19: 'Kantkornet under skaren',
        20: 'Gjennomfuktet fra bakken',
        21: 'Gjennomfuktet fra overflaten',
        22: 'Opphopning over skaren',
        23: 'Snoedekket er overmettet av vann',
        24: 'Ubundet loes snoe',
        25: 'Regn/temperaturstigning',
        26: 'Smelting fra bakken',
        27: 'Vannmettet snoe',
        28: 'Loes toerr snoe',
        29: 'Regn / temperaturstigning / soloppvarming'
    }



    avalanche_problem_kdv{
        0: 'Ikke gitt',
        1: 'Nysnoe',
        2: 'Fokksnoe',
        3: 'Tynt snoedekke',
        4: 'Ustabile lag i dekket',
        5: 'Ustabile lag naer bakken',
        7: 'Regn',
        8: 'Rask temperaturstigning',
        9: 'Mye vann i dekket',
        10: 'Solpaavirkning'
    }
    '''
    aval_cause_kdv = gkdv.get_kdv('AvalCauseKDV')

    if old_cause_parameter_name == 'AvalancheProblem':
        # avalanche_problem_kdv = gkdv.get_kdv('AvalancheProblemKDV')
        if old_cause_tid == 0:
            return aval_cause_kdv[0].Name
        elif old_cause_tid == 1:
            return aval_cause_kdv[28].Name


if __name__ == "__main__":

    import datetime as dt
    # __get_cause_from_old_cause('AvalancheProblem', 3)
    region_list = gkdv.get_kdv("ForecastRegionKDV")
    aval_cause_kdv = gkdv.get_kdv("AvalCauseKDV")


    avalanche_warning = get_problems_from_AvalancheWarningV(108, dt.date(2011,11,30), dt.date(2013,3,15))
    avalache_problems2_v = get_problems_from_AvalancheEvalProblem2V(108, dt.date(2014,11,30), dt.date(2015,3,15))
    # AvalancheWarnProblem = get_problems_from_AvalancheWarnProblemV(108, '2015-01-01','2015-01-15')

    a = 1



