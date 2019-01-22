from base import engine, Base
from station import Station
from area import Area
from trip import Trip
from weather import Weather

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
for i in Base.metadata.sorted_tables:
    print(f"Created table {i.name}")