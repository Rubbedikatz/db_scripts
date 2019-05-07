from PythonScripts.base import Session, engine
from trip import Trip
# from area import Area
# from weather import Weather

session = Session()

# REFLECTED WITH AUTOMAP BASE AND ENGINE
from sqlalchemy.ext.automap import automap_base
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.stations
for station in session.query(Station):
    print("\"%s\": %s, " % (station.name, station.eva_number))

from sqlalchemy import inspect
mapper = inspect(Trip)
for i in mapper.attrs:
    print(i)



session.close()