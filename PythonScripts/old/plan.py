from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from base import Base


class Plan(Base):
    __tablename__ = "plans"
    id = Column(String, primary_key=True)
    hour_retrieved = Column(Integer)
    train_type = Column(String)
    train_number = Column(Integer)
    route_before = Column(String)
    route_after = Column(String)
    ar = Column(Integer)
    dp = Column(Integer)
    eva_number = Column(Integer, ForeignKey("stations.eva_number"))
    station = relationship("Station")

    def set_var(self, var):
        self.__dict__.update(var)
