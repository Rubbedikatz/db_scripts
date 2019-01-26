import requests
from datetime import datetime
from xml.etree import ElementTree

from base import Session
from station import Station
from trip import Trip
from filesncodes import dbapi, stations_to_scan_file
from pandas import DataFrame, read_csv
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


if __name__ == "__main__":
    stations_to_scan = read_csv(stations_to_scan_file, header=None)
    for eva_number in stations_to_scan.iloc[:,0]:
        trips_this_hour = session.query(Trip).filter(Trip.eva_number == eva_number)\
            .filter(Trip.hour_retrieved == this_hour)
        if trips_this_hour.first() is not None:
            sleep(3)
            raw_delays = get_delays(eva_number)
            for row in raw_delays:
                delayed = process_delays(row)
                update_trips_with_delay(delayed, trips_this_hour.all())
        else:
            print("No trips found for % this hour. Abort updating delays." % station)
    session.commit()
    session.close()
