from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from PythonScripts.base import Base


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
