import pandas as pd
import requests
import json

from base import engine
from filesncodes import dbapi, stationsfile, areasfile


def populate_areas(con, file):
    try:
        df = pd.read_csv(file)
        df.to_sql("areas", con, if_exists="append", index=False)
        print("All areas added to areas table")
    except FileNotFoundError as e:
        print("%s, areas table not populated" % e)
        
        
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
    
        
def populate_stations(con, filename):
    allstations_df = pd.read_csv(filename, sep=";")
    cat1_df = allstations_df.loc[allstations_df["Kat. Vst"] <= 1, "Bf. Nr."]
    erfurt = allstations_df.loc[allstations_df["Station"] == "Erfurt Hbf", "Bf. Nr."]
    allstations_df = cat1_df.append(erfurt)
    #allstations_df = allstations_df.loc[allstations_df["Station"] == "Erfurt Hbf", ["Bf. Nr."]]  # for testing only fetch Erfurt
    df = pd.DataFrame()
    for number in allstations_df["Bf. Nr."]:
        raw_station = fetch_station_data(number)
        ins_station = process_row(raw_station)
        df = df.append(ins_station)
        print(f"{ins_station['name']} added to stations table")
    df.to_sql("stations", con, if_exists="append", index=True, index_label="eva_number")
     
     
def main():
    if engine is not None:
        populate_stations(engine, stationsfile)
        populate_areas(engine, areasfile)
    else:
        print("Error! cannot create the database connection.")     
    
    
if __name__ == '__main__':
    main()
