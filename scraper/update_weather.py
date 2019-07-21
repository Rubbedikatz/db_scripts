import requests
import json
from datetime import datetime

from scraper.api_keys import weatherapi
from scraper.base import Session
from scraper.sqlalchemy_objects import Weather, Area, Station


def update_weather(session, by_station=True):
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
            location = row.name
        else:
            latitude = row.center_lat
            longitude = row.center_long
            location = row.id
        r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&APPID={weatherapi}")
        raw_weather = json.loads(r.text)
        weather = process_weather(raw_data=raw_weather, time=this_hour, location=location)
        insert_weather = Weather()
        insert_weather.set_var(weather)
        session.merge(insert_weather)
        print("Weather added for %s" % insert_weather.area_id_or_city)


def process_weather(raw_data, time, location):
    weather_dict = {"description": raw_data["weather"][0]["description"],
                    "temperature": raw_data["main"]["temp"],
                    "wind_speed": raw_data["wind"]["speed"],
                    "time_retrieved": int(time),
                    "area_id_or_city": location}
    return weather_dict


if __name__ == '__main__':
    session = Session()
    if session is not None:
        this_hour = datetime.now().strftime("%y%m%d%H")
        update_weather(session, by_station=False)
        session.commit()
        session.close()
    else:
        print("Error! cannot create database connection.")

