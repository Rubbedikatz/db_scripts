import pandas as pd
import requests
import json

from time import sleep
from PythonScripts.base import engine
from filesncodes import dbapi, areasfile


def populate_areas(con, file):
    try:
        df = pd.read_csv(file)
        df.to_sql("areas", con, if_exists="append", index=False)
    except FileNotFoundError as e:
        print("%s\n areas table not populated" % e)
        
        
def fetch_station_data(station_number):
    headers = {"Authorization": "Bearer %s" % dbapi}
    r = requests.get("https://api.deutschebahn.com/stada/v2/stations/%s" % station_number, headers=headers)
    results = json.loads(r.text)["result"]
    return results
     
     
def process_row(json_file):
    """
    this function takes json data from the api and converts
    it into a dataframe
    """
    df = pd.DataFrame(json_file)
    eva_numbers = df["evaNumbers"][0][0]
    df["eva_number"] = pd.Series(eva_numbers["number"])
    df["latitude"] = pd.Series([eva_numbers["geographicCoordinates"]["coordinates"][0]])
    df["longitude"] = pd.Series([eva_numbers["geographicCoordinates"]["coordinates"][1]])
    df["zip_code"] = pd.Series(df["mailingAddress"][0]["zipcode"])
    df = df[["name", "number", "eva_number", "latitude", "longitude", "category", "zip_code"]]
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    df.set_index("eva_number", inplace=True)
    return df
    
        
def populate_stations(con):
    """
    Train stations are uniquely identified by their EVA number.
    Every train station is assigned a category from 1-5. Read more about what the categories represent here:
    https://de.wikipedia.org/wiki/Bahnhofskategorie
    Deutsche Bahn provides this information in a yearly updated csv file.

    This function filters out stations of category 1, because they have supposedly the most traffic
    passing through.
    """
    filename = "http://download-data.deutschebahn.com/static/\
                datasets/stationsdaten/DBSuS-Uebersicht_Bahnhoefe-Stand2019-03.csv"
    all_stations = pd.read_csv(filename, sep=";")

    biggest_stations = all_stations.loc[all_stations["Kat. Vst"] <= 1, "Bf. Nr."]
    df = pd.DataFrame()
    for number in biggest_stations:
        sleep(2)  # delay api calls to avoid hitting the rate limit
        raw_station = fetch_station_data(number)
        ins_station = process_row(raw_station)
        df = df.append(ins_station)
        print("%s added to database" % ins_station['name'])
    df.to_sql("stations", con, if_exists="replace", index=True, index_label="eva_number")
    # df["name"].to_csv(stations_to_scan_file)


def main():
    if engine is not None:
        populate_stations(engine)
        populate_areas(engine, areasfile)
    else:
        print("Error! cannot create the database connection.")     
    
    
if __name__ == '__main__':
    main()
