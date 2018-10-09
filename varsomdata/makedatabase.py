# -*- coding: utf-8 -*-
import datetime as dt
import setcoreenvironment as cenv
from varsomdata import getobservations as go
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__author__ = 'raek'

engine = create_engine('sqlite:///' + cenv.root_folder + '/tester.sqlite', echo=True)
Base = declarative_base(bind=engine)


def _unix_time_2_normal(unix_date_time):
    """
    Takes in a date in unix datetime and returns a "normal date"

    :param unix_date_time:    Unix date time in milliseconds from 1.1.1970
    :return:                The date as datetime object

    Ex: date = unix_time_2_normal(int(p['DtObsTime'][6:-2]))
    """

    unix_datetime_in_seconds = unix_date_time/1000      # For some reason they are given in milliseconds
    date = dt.datetime.fromtimestamp(int(unix_datetime_in_seconds))
    return date


class AllRegistrations(Base):

    __tablename__ = 'AllRegistrations'

    RegID = Column(Integer)
    DtObsTime = Column(DateTime)
    DtRegTime = Column(DateTime)
    DtChangeTime = Column(DateTime, nullable=True)

    LocationName = Column(String(128), nullable=True)
    UTMZone = Column(Integer)
    UTMEast = Column(Integer)
    UTMNorth = Column(Integer)
    ForecastRegionName = Column(String(128))
    MunicipalName = Column(String(128))

    NickName = Column(String(128))
    CompetenceLevelName = Column(String(128))

    ForecastRegionTID = Column(Integer)
    ObserverId = Column(Integer)
    RowNumber = Column(Integer, primary_key=True)
    GeoHazardName = Column(String(128))
    RegistrationName = Column(String(128))
    TypicalValue1 = Column(String(128))
    TypicalValue2 = Column(String(128))
    LangKey = Column(Integer)
    Picture = Column(Integer)

    def __init__(self, d):

        self.RegID = d.RegID
        self.DtObsTime = d.DtObsTime
        self.DtRegTime = d.DtRegTime
        self.DtChangeTime = d.DtChangeTime

        self.LocationName = d.LocationName
        self.UTMZone = d.UTMZone
        self.UTMEast = d.UTMEast
        self.UTMNorth = d.UTMNorth
        self.ForecastRegionName = d.ForecastRegionName
        self.MunicipalName = d.MunicipalName

        self.NickName = d.NickName
        self.CompetenceLevelName = d.CompetenceLevelName

        self.ForecastRegionTID = d.ForecastRegionTID
        self.ObserverId = d.ObserverId
        self.RowNumber = d.RowNumber
        self.GeoHazardName = d.GeoHazardName
        self.RegistrationName = d.RegistrationName
        self.TypicalValue1 = d.TypicalValue1
        self.TypicalValue2 = d.TypicalValue2
        self.LangKey = d.LangKey
        self.Picture = d.Picture


if __name__ == "__main__":

    from_date = dt.date(2016, 4, 1)
    to_date = dt.date(2016, 5, 1)
    region_ids = 116

    all_data = go.get_all_registrations(from_date, to_date, region_ids)

    Base.metadata.create_all()
    Session = sessionmaker(bind=engine)
    s = Session()

    all_data_ny_mapping = []
    for d in all_data:
        all_data_ny_mapping.append(AllRegistrations(d))

    s.add_all(all_data_ny_mapping)
    s.commit()

    a = 1

