#!/usr/bin/env python3

import json
import argparse
from datetime import datetime
import os.path
import csv
import urllib.request
import time
import socket
import sched
import ssl

def main():
    parser = argparse.ArgumentParser(description="Submit find3 passive scan results")
    parser.add_argument("-p", dest="interval", type=int, help="The polling interval in seconds", default=5)
    parser.add_argument("-u", dest="url", required=True, help="The find3 REST endpoint url", default="https://cloud.internalpositioning.com")
    parser.add_argument("-f", dest="family", required=True, help="The find3 family identifier")
    parser.add_argument("-i", dest="inputfile", required=True, type=lambda file: is_valid_file(parser, file), help="The csv file in which airodump writes the scan results")
    args = parser.parse_args()
    ssl._create_default_https_context = ssl._create_unverified_context
    s = sched.scheduler(time.time, time.sleep)
    parser = SignalParser(args.inputfile, args.family, args.url, args.interval, s)
    parser.poll()

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

class SignalParser():

    def __init__(self, inputfile, family, url, interval, scheduler):
        self.family = family
        self.url = url
        self.inputfile = inputfile
        self.interval = interval
        self.scheduler = scheduler
        self.last_request = datetime.now()

    def poll(self):
        payload = self.build_payload()
        if payload is not None:
            clen = len(payload)
            headers = {'Content-Type': 'application/json', 'Content-Length': clen}
            req = urllib.request.Request(self.url + '/passive', payload, headers, method='POST')
            f = urllib.request.urlopen(req)
            response = f.read()
            print("respons: %s" % response)
            f.close()
        else:
            print("No probe requests found. Waiting for next interval")
        self.scheduler.enter(self.interval, 1, self.poll)
        self.scheduler.run()

    def build_payload(self):
        stations = self.read_scanfile()
        if len(stations) == 0:
            return None
        body = {'f': self.family}
        body['t'] = int(time.time())
        body['d'] = socket.gethostname()
        body['s']  = {'wifi': stations}
        return str(json.dumps(body)).encode('utf8')

    def read_scanfile(self):
        stations = {}
        start_read = False
        try:
            with open(self.inputfile) as scan_file:
                csv_reader = csv.reader(scan_file, delimiter=',')
                for row in csv_reader:
                    if len(row) == 0:
                        continue
                    if start_read:
                        last_seen = datetime.strptime(row[2].strip(), "%Y-%m-%d %H:%M:%S")
                        if last_seen > self.last_request:
                            power = row[3].strip()
                            station = row[0].strip().lower()
                            stations[station] = power
                            print("Found %s with signal power of %s dBm at %s" % (station, power, last_seen))
                        self.last_request = datetime.now()
                    if row[0] == "Station MAC":
                        start_read = True
        except Exception as e :
            print("Failed to read %s: %s" % (self.inputfile, str(e)))

        return stations

if __name__ == "__main__":
    main()
