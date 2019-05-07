import requests
from datetime import datetime
from xml.etree import ElementTree

from PythonScripts.base import Session
from PythonScripts.sqlalchemy_objects import Station, Trip
from PythonScripts.api_keys import dbapi
from time import sleep

session = Session()
this_hour = datetime.now().strftime("%y%m%d%H")


def get_delays(eva_number):
    """
    this function takes the number of a train station and retrieves delay data
    from the timetable API on deutschebahn.com and
    returns an XML object
    """
    headers = {"Authorization": "Bearer %s" % dbapi}
    r = requests.get("https://api.deutschebahn.com/timetables/v1/fchg/%s" % eva_number, headers=headers)
    results = ElementTree.fromstring(r.content)
    return results


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


def update_trips_with_delay(delay, trips):
    for t in trips:
        if t.id == delay["id"]:
            session.query(Trip).filter(Trip.id == t.id).update({"car": delay["car"], "cdp": delay["cdp"]})
            print("Delay data added for trip at %s" % t.eva_number)


def get_stations_from_db(sess):
    stations = []
    for instance in sess.query(Station):
        stations.append(instance.eva_number)
    return stations


if __name__ == "__main__":
    stations_to_scan = get_stations_from_db(session)
    for eva_number in stations_to_scan:
        trips_this_hour = session.query(Trip).filter(Trip.eva_number == eva_number)\
            .filter(Trip.hour_retrieved == this_hour)
        if trips_this_hour.first() is not None:
            sleep(2)
            raw_delays = get_delays(eva_number)
            for row in raw_delays:
                delayed = process_delays(row)
                update_trips_with_delay(delayed, trips_this_hour.all())
        else:
            print("No trips found for %s this hour. Abort updating delays." % eva_number)
    session.commit()
    session.close()
