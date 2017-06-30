#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2017 Charles Fourneau
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import json
from argparse import ArgumentParser
from configparser import ConfigParser
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import logging
import socket

# TODO: move to config file
URL_IP_EXTERNAL = [
    "http://ifconfig.me/ip",
    "http://ipecho.net/plain",
    "http://myexternalip.com/raw"]

def get_external_ip(url_list, index=0):
    """ get the external IP address by querying web providers """
    try:
        response = urlopen(url_list[index], None, 3)
    except (URLError, socket.timeout) as e:
        #on error, try the next url
        ip = get_external_ip(url_list, index + 1)
    else:
        data = response.read().decode('utf-8')
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', data)[0]
    return ip


class RecordManager(object):
    """ manage (create/update) DNS records from config_file """
    
    def __init__(self):
        self.config = None

    def load_config(self, config_file):
        self.config = ConfigParser()
        self.config.default_section = "general"
        if os.path.isfile(config_file) and os.access(config_file, os.R_OK):
            self.config.read(config_file)

    def _get_record(self, url, headers):
        try:
            response = urlopen(Request(url, headers=headers))
        except HTTPError as e:
            # we have to handle http return codes in the 400-599 range (errors)
            return None
        if (response.getcode() != 200):
            return None
        encoding = response.info().get_content_charset('utf-8')
        return json.loads(response.read().decode(encoding))

    def update_records(self):
        ip = get_external_ip(URL_IP_EXTERNAL)
        for r in self.config.sections():
            headers = { 'Content-Type': 'application/json',
                        'X-Api-Key': self.config[r]["api_key"]}
            logging.info("Record {} ({}) for domain {}".format(self.config[r]["name"],
                                                               self.config[r]["type"],
                                                               self.config[r]["domain"]))
            url = '{}domains/{}/records/{}/{}'.format(self.config[r]["api"],
                                                      self.config[r]["domain"],
                                                      self.config[r]["name"],
                                                      self.config[r]["type"])
            data = {'rrset_ttl': self.config[r]["ttl"],
                    'rrset_values': [ip]}
            current_record = self._get_record(url, headers)
            if current_record is None:
                logging.info(" Record does not exist. Let's create it...")
                method = 'POST'
            else:
                if current_record['rrset_values'][0] == ip:
                    logging.info(" No IP change. Nothing to do...")
                    continue
                logging.info(" IP change detected. Updating...")
                method = 'PUT'
            json_data = json.dumps(data).encode('utf-8')
            req = Request(url, data=json_data, headers=headers, method=method)
            try:
                response = urlopen(req)
            except HTTPError as e:
                # something has gone wrong
                logging.info(" Record update failed with error code: {}".format(e.code))
                continue
            if response.getcode() != 201:
                logging.info(" Record update failed with status code: {}".format(response.getcode()))
                continue
            logging.info(" Zone record updated succesfuly")


if __name__ == "__main__":
    parser = ArgumentParser(description='Update Gandi DNS records.')
    parser.add_argument('-c', '--config-file', help="configuration file", dest='config_file', required=True)
    parser.add_argument('-v', '--verbose', help="increase output verbosity", action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    rm = RecordManager()
    rm.load_config(args.config_file)
    rm.update_records()
