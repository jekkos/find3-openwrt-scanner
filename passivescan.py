#!/usr/bin/env python3

import encodings.idna
import argparse
from datetime import datetime
import json
import os.path
import urllib.request
import time
import socket
import sys
import re
import ssl
import select

def main():
    parser = argparse.ArgumentParser(description="Submit find3 passive scan results")
    parser.add_argument("-u", dest="url", required=False, help="The find3 REST endpoint url", default="https://cloud.internalpositioning.com")
    parser.add_argument("-i", dest="fifo", required=False, help="Tcpdump output.file location. Point this to OpenWrt logfile if using procd", default="/tmp/logfile")
    parser.add_argument("-f", dest="family", required=False, help="The find3 family identifier")
    args = parser.parse_args()
    ssl._create_default_https_context = ssl._create_unverified_context
    parser = SignalParser(args.family, args.url, args.fifo)
    parser.read()

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

class SignalParser():

    def __init__(self, family, url, fifo):
        self.family = family
        self.url = url
        self.fifo = fifo

    def send_payload(self, stations):
        payload = self.build_payload(stations)
        clen = len(payload)
        headers = {'Content-Type': 'application/json', 'Content-Length': clen}
        req = urllib.request.Request(self.url + '/passive', payload, headers, method='POST')
        f = urllib.request.urlopen(req)
        response = f.read()
        print("response: %s" % response)
        f.close()

    def build_payload(self, stations):
        body = {'f': self.family}
        body['t'] = int(time.time())
        body['d'] = socket.gethostname()
        body['s']  = {'wifi': stations}
        return str(json.dumps(body)).encode('utf8')

    def read(self):
        stations = {}
        start = datetime.now()
        try:
            with open(self.fifo) as fifo:
                while True:
                    select.select([fifo], [], [fifo])
                    row = fifo.readline()
                    if (row is None or "Probe" not in row or "tcpdump" not in row):
                        continue
                    rows = row.split(': ')[1].split(' ')

                    last_seen = datetime.strptime(rows[0].strip(), "%H:%M:%S.%f")
                    last_seen = datetime.combine(datetime.today(), last_seen.time())
                    power = re.match(r".*(-?\d+)dBm", row).group(1)
                    station = re.match(r".*SA:(.*?)\s", row).group(1)
                    stations[station] = power
                    print("Found %s with signal power of %s dBm at %s" % (station, power, last_seen))
                    elapsed = datetime.now() - start
                    if (len(stations) > 0):
                        self.send_payload(stations)
                        stations = {}

        except Exception as e :
            sys.stdout.flush()
            print("Failed to read from stdin: %s" % (str(e)))
            pass

if __name__ == "__main__":
    main()
