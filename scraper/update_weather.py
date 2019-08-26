import requests
import json
from datetime import datetime
from time import sleep

from scraper.api_keys import weatherapi
from scraper.base import Session
from scraper.sqlalchemy_objects import Weather, Area, Station


def update_weather(session, time, by_station=True):
    """
    Fetch weather data from openweathermap.org for a list of coordinates
    and writes it to the Weather table in the database.
    Uses coordinates of all stations in the database by default. 
    If "by_station=False" is passed, it instead updates weather data
    for a 3x4 grid of areas that cover all of Germany.
    """
    if by_station:
        data = session.query(Station).all()
    else:
        data = session.query(Area).all()
    for row in data:
        if by_station:
            latitude = row.latitude
            longitude = row.longitude
            location = row.eva_number
        else:
            latitude = row.center_lat
            longitude = row.center_long
            location = row.id
        for i in range(5):
            r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&APPID={weatherapi}")
            if r.status_code != 500: 
                break
            elif i < 5:
                sleep(i*2)
                print(f"Error for {location}. Trying again ({i+1})")
        if r.status_code == 500:
            print(f"Internal server error: 500. Could not fetch data for {location} after several tries.")
            with open("errors.txt", "a+") as f:
                f.write(f"Error {r.status_code} getting delays for {location} at {time}.")
            return 
        raw_weather = json.loads(r.text)
        weather = process_weather(raw_data=raw_weather, time=time, location=location)
        insert_weather = Weather()
        insert_weather.set_var(weather)
        session.merge(insert_weather)
        print("Weather added for %s" % location)


def process_weather(raw_data, time, location):
    weather_dict = {"description": raw_data["weather"][0]["description"],
                    "temperature": raw_data["main"]["temp"],
                    "wind_speed": raw_data["wind"]["speed"],
                    "time_retrieved": int(time)}
    # test if location is based on eva_number or area_id
    if len(str(location)) > 2:
        weather_dict["eva_number"] = location
    else:
        weather_dict["area_id"] = location
    return weather_dict


if __name__ == '__main__':
    session = Session()
    if session is not None:
        this_hour = datetime.now().strftime("%y%m%d%H")
        update_weather(session, this_hour, by_station=True)
        session.commit()
        session.close()
    else:
        print("Error! cannot create database connection.")

