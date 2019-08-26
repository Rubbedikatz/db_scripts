import json
import numpy as np
from sqlalchemy import create_engine
import pandas as pd
import os

engine = create_engine("sqlite:////data/deutschebahn.db", echo=False)

df = pd.read_sql_query("SELECT id, ar, dp, car, cdp, name FROM trips\
                           JOIN stations ON trips.eva_number = stations.eva_number \
                           WHERE train_type IN ('IC', 'ICE')", engine)


# Convert columns with time data into datetime
df.loc[:,["ar", "dp", "car", "cdp"]] = df[["ar", "dp", "car", "cdp"]] \ 
                                        .apply(pd.to_datetime, format="%y%m%d%H%M", errors="coerce")

# Add a delays columns which shows the actual delay in minutes
df["dp_delay"] = df["cdp"] - df["dp"]
df["ar_delay"] = df["car"] - df["ar"]
df["delay"] = df["dp_delay"].fillna(df["ar_delay"])
df["delay"] = df["delay"].dt.total_seconds().div(60).fillna(0).astype(int)

trips_per_station = df.loc[:,["id", "name"]].groupby("name").count().sort_values(by="id")
delay_per_station = df.loc[:,["delay", "name"]].groupby("name").mean().sort_values(by="delay")
stations = pd.read_sql_query("SELECT * FROM stations", engine)

stations_summary = delay_per_station.join(trips_per_station).join(stations.set_index("name")).reset_index()
stations_summary = stations_summary.rename(columns={"delay": "mean_delay", "id":"trips"})

# https://geoffboeing.com/2015/10/exporting-python-data-geojson/
def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [row[lat],row[lon]] # switched lat/long for d3
        for prop in properties:
            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson

props = ["trips", "mean_delay", "name"]
geojson = df_to_geojson(stations_summary, props)
output_filename = 'cities.json'
with open(os.join('data' + output_filename), 'w') as output_file:
    json.dump(geojson, output_file) 