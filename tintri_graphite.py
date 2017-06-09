#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Tintri, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import os
import socket
import sys
import time
import tintri_1_1 as tintri

"""
 This Python script gets vmstore stats and feeds them graphite

 Command usage: tintri_graphite <server_name> <userName> <password>

"""

# For exhaustive messages on console, make it to True; otherwise keep it False
debug_mode = False

# Polling interval in seconds
interval = int(5)

def print_with_prefix(prefix, out):
    print(prefix + out)
    return


def print_debug(out):
    if debug_mode:
        print_with_prefix("[DEBUG] : ", out)
    return


def print_info(out):
    print_with_prefix("[INFO] : ", out)
    return


def print_error(out):
    print_with_prefix("[ERROR] : ", out)
    return


def get_vmstore(session_id):

    # Dictionary of VMstore objects
    vmstore_stats = {}

    # URL for VMstore stats
    get_vmstore_url = "/v310/datastore/default/statsRealtime"
    count = 1

    # Invoke the API
    r = tintri.api_get(server_name, get_vmstore_url, session_id)
    print_debug("The JSON response of the get invoke to the server " +
                server_name + " is: " + r.text)

    # if HTTP Response is not 200 then raise an error
    if r.status_code != 200:
        print_error("The HTTP response for the get invoke to the server " +
              server_name + " is not 200, but is: " + str(r.status_code))
        print_error("url = " + url)
        print_error("response: " + r.text)
        tintri.api_logout(server_name, session_id)
        sys.exit(-10)

    # Get and store the VM items and save in a vmstore object.
    vmstore_result = r.json()

    vmstore_stats = vmstore_result["items"][0]["sortedStats"]

    return vmstore_stats


# main
if os.environ.get('vmstore_fqdn') is not None and os.environ.get('vmstore_username') is not None and os.environ.get('vmstore_password') is not None and os.environ.get('graphite_fqdn') is not None and os.environ.get('graphite_port') is not None:
    server_name = os.environ.get('vmstore_fqdn')
    user_name = os.environ.get('vmstore_username')
    password = os.environ.get('vmstore_password')
    graphite_server = os.environ.get('graphite_fqdn')
    graphite_port = os.environ.get('graphite_port')
    print("Using parameters found in your environment\n")
elif len(sys.argv) == 6:
    server_name = sys.argv[1]
    user_name = sys.argv[2]
    password = sys.argv[3]
    graphite_server = sys.argv[4]
    graphite_port = sys.argv[5]
    print("Using paramerts passed in on the command line\n")
else:
    print("\nPrints VMstore information\n")
    print("Usage: " + sys.argv[0] + " vmstore_fqdn vmstore_username vmstore_password graphite_fqdn graphite_port\n")
    sys.exit(-1)

server_name_formatted = server_name.replace(".", "_")

# Get the preferred version
r = tintri.api_version(server_name)
json_info = r.json()

print_info("VMstore: %s" % (server_name))
print_info("API Version: " + json_info['preferredVersion'])
print_info("Update Frequency: %s seconds" % (interval))
print_info("Graphite Server: %s" % (graphite_server))
print_info("Graphite Port: %s" % (graphite_port)) 
print_info("Graphite storage schema: tintri.%s." % (server_name_formatted))

while True:
    print_debug("Starting VMstore collection...")

    # Login to VMstore
    session_id = tintri.api_login(server_name, user_name, password)

    vmstore_stats = get_vmstore(session_id)

    # Get epoch time
    epochtime = int(time.time())

    # All pau, log out
    tintri.api_logout(server_name, session_id)

    for stat in vmstore_stats[0]:
        # Make sure each stat is a number (float or int)
        if (type(vmstore_stats[0][stat]) is float) or (type(vmstore_stats[0][stat]) is int):
            message = 'tintri.%s.vmstore.%s %f %d\n' % (server_name_formatted, stat, float(vmstore_stats[0][stat]), epochtime)
            print_debug(message)

            # Send stat to graphite
            sock = socket.socket()
            sock.connect((graphite_server, graphite_port))
            sock.sendall(message)

	else:
            # Skip stat if it's a non-number.  Probably need to add a nested loop above to handle type dict
            print_debug("%s: %s is a %s instead of a float\n" % (stat, vmstore_stats[0][stat], type(vmstore_stats[0][stat])))

    print_debug("Collection finished")

    # Close graphite socket
    sock.close()

    # Wait for x seconds
    print_debug("Sleeping for %s seconds..." % (interval))
    time.sleep(interval)

#end
