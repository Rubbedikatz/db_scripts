import requests
from datetime import datetime
from xml.etree import ElementTree

from base import Session
from station import Station
from trip import Trip
from filesncodes import dbapi

session = Session()
eva_numbers = [8010101]  # eva for Erfurt Hbf
this_hour = datetime.now().strftime("%y%m%d%H")


def get_delays(eva_number):
    """
    this function takes the number of a train station and retrieves delay data
    from the timetable API on deutschebahn.com and
    returns an XML object
    """
    headers = {"Authorization": f"Bearer {dbapi}"}
    r = requests.get(f"https://api.deutschebahn.com/timetables/v1/fchg/{eva_number}", headers=headers)
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
            print(f"Delay data added for trip at {t.eva_number}")


if __name__ == "__main__":
    for station in eva_numbers:
        trips_this_hour = session.query(Trip).filter(Trip.eva_number == station)\
            .filter(Trip.hour_retrieved == this_hour)
        if trips_this_hour.first() is not None:
            raw_delays = get_delays(station)
            for row in raw_delays:
                delayed = process_delays(row)
                update_trips_with_delay(delayed, trips_this_hour.all())
        else:
            print(f"No trips found for {station} this hour. Abort updating delays.")
    session.commit()
    session.close()
