import requests
from datetime import datetime
from xml.etree import ElementTree
from time import sleep

from api_keys import dbapi
from base import Session
from sqlalchemy_objects import Station, Trip


def get_plans(station, time):
    headers = {"Authorization": "Bearer %s" % dbapi}
    r = requests.get("https://api.deutschebahn.com/timetables/v1/plan/%s/%s" % (station, time), headers=headers)
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


def update_plan(sess):
    """
    reads list of stations to scan from csv file created when the database
    was populated with station data
    checks before if plan for this hour was already downloaded to avoid unnecessary api calls
    """
    this_hour = datetime.now().strftime("%y%m%d/%H")
    with open("log.txt", "r") as f:
        last_updated = f.readlines()
    if last_updated[0] != this_hour:

        stations_to_scan = get_stations_from_db(sess)
        for eva_number in set(stations_to_scan):
            raw_plans = get_plans(eva_number, this_hour)
            for plan in raw_plans:
                clean_plan = process_plan(eva_number, plan)
                insert_plan = Trip()
                insert_plan.set_var(clean_plan)
                sess.merge(insert_plan)
            print("New plan data fetched for %s" % insert_plan.eva_number)
            sleep(2)
        sess.commit()
        with open("log.txt", "w") as f:
            f.write(this_hour)


def main():
    session = Session()
    if session is not None:
        update_plan(session)
        session.close()
    else:
        print("Error! cannot create database connection.")


if __name__ == '__main__':
    main()
