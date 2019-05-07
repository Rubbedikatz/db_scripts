import requests
import json
from datetime import datetime

from api_keys import weatherapi
from base import Session
from sqlalchemy_objects import Weather, Area


def get_weather(area):
    r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={area.center_lat}&lon={area.center_long}&APPID={weatherapi}")
    results = json.loads(r.text)
    return results


def process_weather(area_id, raw_data, time):
    weather_dict = {"description": raw_data["weather"][0]["description"],
                    "temperature": raw_data["main"]["temp"],
                    "wind_speed": raw_data["wind"]["speed"],
                    "time_retrieved": int(time),
                    "area_id": area_id}
    return weather_dict

    
if __name__ == '__main__':
    session = Session()
    if session is not None:
        this_hour = datetime.now().strftime("%y%m%d%H")
        areas = session.query(Area).all()
        for area in areas:
            raw_weather = get_weather(area)
            weather = process_weather(area.id, raw_weather, this_hour)
            insert_weather = Weather()
            insert_weather.set_var(weather)
            session.merge(insert_weather)
            print("Weather added for area %s" % insert_weather.area_id)
        session.commit()
        session.close()
    else:
        print("Error! cannot create database connection.")
