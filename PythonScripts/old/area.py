from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship

from PythonScripts.base import Base


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
