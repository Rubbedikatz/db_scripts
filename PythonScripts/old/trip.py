from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from PythonScripts.base import Base


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
