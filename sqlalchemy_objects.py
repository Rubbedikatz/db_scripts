from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from base import Base


class Area(Base):
    __tablename__ = "areas"
    id = Column(String, primary_key=True)
    north_long = Column(Float)
    west_lat = Column(Float)
    south_long = Column(Float)
    east_lat = Column(Float)
    center_lat = Column(Float)
    center_long = Column(Float)
    weather = relationship("Weather", back_populates="area")

    def set_var(self, var):
        self.__dict__.update(var)


class Trip(Base):
    __tablename__ = "trips"
    id = Column(String, primary_key=True)
    train_type = Column(String)
    train_number = Column(Integer)
    route_before = Column(String)
    route_after = Column(String)
    ar = Column(Integer)
    dp = Column(Integer)
    car = Column(Integer)
    cdp = Column(Integer)
    hour_retrieved = Column(Integer)
    eva_number = Column(Integer, ForeignKey("stations.eva_number"))
    station = relationship("Station", back_populates="trips")

    def set_var(self, var):
        self.__dict__.update(var)


class Weather(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True)
    time_retrieved = Column(Integer)
    description = Column(String)
    temperature = Column(Float)
    wind_speed = Column(Float)
    area_id = Column(Integer, ForeignKey("areas.id"))
    area = relationship("Area", back_populates="weather")

    def set_var(self, var):
        self.__dict__.update(var)


class Station(Base):
    __tablename__ = "stations"
    eva_number = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    zip_code = Column(Integer)
    category = Column(Integer)
    trips = relationship("Trip", back_populates="station")

    def set_var(self, var):
        self.__dict__.update(var)