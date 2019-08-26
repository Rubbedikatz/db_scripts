import requests
from datetime import datetime
from xml.etree import ElementTree
from time import sleep

from scraper.api_keys import dbapi
from scraper.base import Session
from scraper.sqlalchemy_objects import Station, Trip


def get_plans(station, time):
    headers = {"Authorization": "Bearer %s" % dbapi}
    for i in range(5):
        r = requests.get("https://api.deutschebahn.com/timetables/v1/plan/%s/%s" % (station, time), headers=headers)
        if r.status_code != 500: 
            break
        elif i < 5:
            sleep(i*2)
            print(f"Error for {station}. Trying again ({i+1})")
    if r.status_code == 500:
        print(f"Internal server error: 500. Could not fetch data for {station} after several tries.")
        with open("errors.txt", "a+") as f:
            f.write(f"Error {r.status_code} getting plans for {station} at {time}.")
        return 
    results = ElementTree.fromstring(r.content)
    return results


def get_delays(eva_number, time):
    """
    this function takes the number of a train station and retrieves delay data
    from the timetable API on deutschebahn.com and
    returns an XML object
    """
    headers = {"Authorization": "Bearer %s" % dbapi}
    for i in range(5):
        r = requests.get("https://api.deutschebahn.com/timetables/v1/fchg/%s" % eva_number, headers=headers)
        if r.status_code != 500: 
            break
        elif i < 5:
            sleep(i*2)
            print(f"Error for {eva_number}. Trying again ({i+1})")
    if r.status_code == 500:
        print(f"Internal server error: 500. Could not fetch data for {eva_number} after several tries.")
        with open("errors.txt", "a+") as f:
            f.write(f"Error {r.status_code} getting weather data for {eva_number} at {time}.")
        return 
    results = ElementTree.fromstring(r.content)
    return results


def process_plan(eva_number, plan):
    trip = {"id": plan.attrib["id"],
            "eva_number": eva_number,
            "hour_retrieved": int(datetime.now().strftime("%y%m%d%H"))}
    try:
        trip["train_type"] = plan.find("tl").attrib["c"]
    except (AttributeError, KeyError):
        trip["train_type"] = None
    try:
        trip["train_number"] = int(plan.find("tl").attrib["n"])
    except (AttributeError, KeyError):
        trip["train_number"] = None
    try:
        trip["route_before"] = plan.find("ar").attrib["ppth"]
    except (AttributeError, KeyError):
        trip["route_before"] = None
    try:
        trip["route_after"] = plan.find("dp").attrib["ppth"]
    except (AttributeError, KeyError):
        trip["route_after"] = None
    try:
        trip["ar"] = int(plan.find("ar").attrib["pt"])
    except (AttributeError, KeyError):
        trip["ar"] = None
    try:
        trip["dp"] = int(plan.find("dp").attrib["pt"])
    except (AttributeError, KeyError):
        trip["dp"] = None
    return trip


def get_stations_from_db(sess):
    stations = []
    for instance in sess.query(Station):
        stations.append(instance.eva_number)
    return stations


def update_plans(sess, stations, hour):
    """
    reads list of stations to scan from station data in database
    checks before if plan for this hour was already downloaded to avoid unnecessary api calls
    """
    try:
        with open("log.txt", "r") as f:
            last_updated = f.readlines()
    except FileNotFoundError:
        last_updated = 0
    if last_updated != [hour]:
        for eva_number in set(stations):
            raw_plans = get_plans(eva_number, hour)
            for plan in raw_plans:
                clean_plan = process_plan(eva_number, plan)
                insert_plan = Trip()
                insert_plan.set_var(clean_plan)
                sess.merge(insert_plan)
            print("New plan data fetched for %s" % eva_number)
            sleep(3.5)
        sess.commit()
        with open("log.txt", "w") as f:
            f.write(this_hour)


def process_delays(xml):
    trip = {"id": xml.attrib["id"]}
    try:
        trip["car"] = int(xml.find("ar").attrib["ct"])
    except (AttributeError, KeyError):
        trip["car"] = None
    try:
        trip["cdp"] = int(xml.find("dp").attrib["ct"])
    except (AttributeError, KeyError):
        trip["cdp"] = None
    return trip


def update_trips_with_delay(delay, trips, sess):
    for t in trips:
        if t.id == delay["id"]:
            sess.query(Trip).filter(Trip.id == t.id).update({"car": delay["car"], "cdp": delay["cdp"]})


def update_delays(sess, stations, hour):
    for eva_number in set(stations):
        print(f"looking for delays for {eva_number}")        
        hour = hour.replace("/", "")
        trips_this_hour = sess.query(Trip).filter(Trip.eva_number == eva_number)\
            .filter(Trip.hour_retrieved == hour)
        if trips_this_hour.first() is not None:
            sleep(2)
            raw_delays = get_delays(eva_number, hour)
            for row in raw_delays:
                delayed = process_delays(row)
                update_trips_with_delay(delayed, trips_this_hour.all(), sess)
            print(f"Delays added for station {eva_number}.")
        else:
            print(f"No trips found for {eva_number} at {hour}.")
    sess.commit()


if __name__ == '__main__':
    session = Session()
    if session is not None:
        this_hour = datetime.now().strftime("%y%m%d/%H")
        stations_to_scan = get_stations_from_db(session)
        update_plans(session, stations_to_scan, this_hour)
        update_delays(session, stations_to_scan, this_hour)
        session.close()
    else:
        print("Cannot create database connection.")
