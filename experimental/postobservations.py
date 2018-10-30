# -*- coding: utf-8 -*-
import json
import uuid
import requests
import base64

__author__ = 'raek'


def wyssent_testing():
    # Fra item
    url = "http://tst-h-web03.nve.no/regobswebapi/registration/insert"
    # url = "https://api.nve.no/hydrology/regobs/webapi_v3.2.0/registration/insert"

    Guid = uuid.uuid4()
    Guid = Guid.urn
    Guid = Guid[9:]

    string1 = '{"Id": "'
    string2 = '","GeoHazardTID": 10,"DtObsTime":"2017-11-22T10:00:00Z","DangerObs": [ {"DangerSignTID": 2,"Comment": "Ett skred detektert vha. infralyd 2017-11-12, UTC 04:54:34",} ],"Picture": [ {"RegistrationTID": "13","PictureImageBase64": "data:image/png;base64,'
    string4 = '","PictureComment": "Plott av infralydsignal siste 6 timer."}],"ObserverGuid":"72E255E2-B44A-44BC-A8EA-58DF3C186E4F","ObserverGroupID":145,"SourceTID": 24,"Email": false,"ObsLocation": {"ObsLocationId": 53109}}'
    string3 = 'http://148.251.122.130/item_drumplot/NO2_RealTime1.png'
    string3 = requests.get(string3).content
    string3 = base64.b64encode(string3)
    string3 = str(string3, "utf-8")

    data = '{0}{1}{2}{3}{4}'.format(string1, Guid, string2, string3, string4)

    data_json = json.dumps(data)
    data_json = json.loads(data_json)
    data_json = data_json.encode('utf-8')
    headers = {
        "Content-type" : "application/json",
        "regObs_apptoken" : '00000000-0000-0000-0000-000000000000'}
    # auth = HTTPBasicAuth('my@email.no', 'pwd')
    response = requests.post(url, data=data_json, headers=headers) #, auth=auth)

    print(response.text, response.reason)


if __name__ == "__main__":

    wyssent_testing()
