#!/usr/bin/env python3

import encodings.idna
import argparse
from datetime import datetime, timedelta
import json
import os.path
import urllib.request
import time
import socket
import sys
import re
import ssl
import select
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Submit find3 passive scan results")
    parser.add_argument("-u", dest="url", required=False, help="The find3 REST endpoint url", default="https://cloud.internalpositioning.com")
    parser.add_argument("-f", dest="family", required=True, help="The find3 family identifier")
    parser.add_argument("-i", dest="iface", required=True, help="The monitor mode interface")
    args = parser.parse_args()
    ssl._create_default_https_context = ssl._create_unverified_context
    parser = SignalParser(args.family, args.url, args.iface)
    parser.read()

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

class SignalParser():

    def __init__(self, family, url, iface):
        self.family = family
        self.url = url
        self.iface = iface

    def send_payload(self, stations, last_seen):
        payload = self.build_payload(stations, last_seen)
        clen = len(payload)
        headers = {'Content-Type': 'application/json', 'Content-Length': clen}
        req = urllib.request.Request(self.url + '/passive', payload, headers, method='POST')
        f = urllib.request.urlopen(req)
        response = f.read()
        print("response: %s" % response)
        f.close()

    def build_payload(self, stations, last_seen):
        body = {'f': self.family}
        body['t'] = int(last_seen.timestamp())
        body['d'] = socket.gethostname()
        body['s']  = {'wifi': stations}
        return str(json.dumps(body)).encode('utf8')

    def read(self):
        proc = subprocess.Popen(['tcpdump', '-l', '-i', self.iface, '-e', '-s', str(256), 'type', 'mgt', 'subtype', 'probe-req'], stdout=subprocess.PIPE)
        stations = {}
        start = datetime.now()
        for bb in iter(proc.stdout.readline, ''):
            try:
                row = str(bb, 'utf8')
                if (row is None or "Probe" not in row):
                    time.sleep(0.1)
                    continue
                rows = row.split(' ')

                last_seen = datetime.strptime(rows[0].strip(), "%H:%M:%S.%f")
                last_seen = datetime.combine(datetime.today(), last_seen.time())
                power = re.match(r".*(-\d+|0)dBm", row).group(1)
                station = re.match(r".*SA:(.*?)\s", row).group(1)
                stations[station] = int(power)
                print("Found %s with signal power of %d dBm at %s" % (station, int(power), last_seen))
                elapsed = datetime.now() - start
                if (len(stations) > 0 and int(power) != 0):
                    self.send_payload(stations, last_seen)
                    stations = {}

            except Exception as e :
                time.sleep(0.02)
                sys.stdout.flush()
                print("Failed to read from tcpdump: %s" % (str(e)))
                pass

if __name__ == "__main__":
    main()
