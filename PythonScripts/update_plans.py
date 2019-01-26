import requests
from datetime import datetime
from xml.etree import ElementTree

from filesncodes import dbapi, stations_to_scan_file
from base import Session
from station import Station
from trip import Trip
from pandas import DataFrame, read_csv
from time import sleep

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
    
    
def main():
    session = Session()
    if session is not None:
        this_hour = datetime.now().strftime("%y%m%d/%H")
        # read list of stations to scan from csv file created when the database 
        # was populated with station data
        stations_to_scan = read_csv(stations_to_scan_file, header=None)
        # loop through all eva_numbers in stations_to_scan file and fetch plan data
        for eva_number in stations_to_scan.iloc[:,0]:         
            raw_plans = get_plans(eva_number, this_hour)
            for plan in raw_plans:
                clean_plan = process_plan(eva_number, plan)
                insert_plan = Trip()
                insert_plan.set_var(clean_plan)
                session.merge(insert_plan)
            print("New plan data fetched for %s" % insert_plan.eva_number)
            sleep(3)
        session.commit()
        session.close()
    else:
        print("Error! cannot create the database connection.") 


if __name__ == '__main__':
    main()
