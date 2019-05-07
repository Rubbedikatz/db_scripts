from base import engine, Base
from sqlalchemy_objects import Station, Weather, Trip, Area
from time import sleep
from api_keys import dbapi
import requests
import pandas as pd
import json


def create_database(con):
    Base.metadata.drop_all(con)
    Base.metadata.create_all(con)
    for i in Base.metadata.sorted_tables:
        print("Created table %s" % i.name)


def populate_areas(con):
    try:
        df = pd.read_csv("areas.csv")
        df.to_sql("areas", con, if_exists="append", index=False)
        print("areas populated")
    except FileNotFoundError as e:
        print("%s\n areas table not populated" % e)


def fetch_station_data(station_number):
    headers = {"Authorization": "Bearer %s" % dbapi}
    r = requests.get("https://api.deutschebahn.com/stada/v2/stations/%s" % station_number, headers=headers)
    results = json.loads(r.text)["result"]
    return results


def process_row(json_file):
    """
    take json data from the api and convert into a pandas dataframe
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
    Deutsche Bahn provides this information in an annually updated csv file.

    This function filters out stations of category 1, because they have supposedly the most traffic
    passing through.
    """
    filename = "http://download-data.deutschebahn.com/static/datasets/stationsdaten/DBSuS-Uebersicht_Bahnhoefe-Stand2019-03.csv"
    all_stations = pd.read_csv(filename, sep=";")

    biggest_stations = all_stations.loc[all_stations["Kat. Vst"] <= 1, "Bf. Nr."]
    insert_df = pd.DataFrame()
    for number in biggest_stations[0:5]:
        sleep(2)  # delay api calls to avoid hitting the rate limit
        raw_station = fetch_station_data(number)
        ins_station = process_row(raw_station)
        insert_df = insert_df.append(ins_station)
        print("%s ready to be added to database" % ins_station['name'][0])
    insert_df.to_sql("stations", con, if_exists="replace", index=True, index_label="eva_number")
    print("All stations added to database")


if __name__ == "__main__":
    if engine is not None:
        create_database(engine)
        populate_stations(engine)
        populate_areas(engine)
    else:
        print("Error! cannot create the database connection.")
