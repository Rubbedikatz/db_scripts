from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from base import Base


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