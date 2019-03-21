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

import copy
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


def get_datastore_stats(session_id, stats):
    get_datastore_stats_base_url = "/v310/datastore/default/"
    stats_url = get_datastore_stats_base_url + stats
    # Invoke the API
    r = tintri.api_get(server_name, stats_url, session_id)
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
    return vmstore_result


# Copyright Ferry Boender, released under the MIT license.
def deepupdate(target, src):
    """Deep update target dict with src
    For each k,v in src: if k doesn't exist in target, it is deep copied from
    src to target. Otherwise, if v is a list, target[k] is extended with
    src[k]. If v is a set, target[k] is updated with v, If v is a dict,
    recursively deep-update it.
    Examples:
    >>> t = {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi']}
    >>> deepupdate(t, {'hobbies': ['gaming']})
    >>> print t
    {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi', 'gaming']}
    """
    for k, v in src.items():
        if type(v) == list:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                target[k].extend(v)
        elif type(v) == dict:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                deepupdate(target[k], v)
        elif type(v) == set:
            if not k in target:
                target[k] = v.copy()
            else:
                target[k].update(v.copy())
        else:
            target[k] = copy.copy(v)


def get_vmstore(session_id):
    # Dictionary of VMstore objects
    vmstore_stats = {}
    # URLs for VMstore stats
    stats_summary = "statsSummary"
    stats_realtime = "statsRealtime"
    vmstore_stats = get_datastore_stats(session_id, stats_summary)
    realtime_stats_obj = get_datastore_stats(session_id, stats_realtime)
    realtime_stats = realtime_stats_obj["items"][0]["sortedStats"][0]
    deepupdate(vmstore_stats,realtime_stats)
    return vmstore_stats


def graphite_message(prefix, stat, value, epochtime):
    message = '%s.%s %f %d\n' % (prefix, stat, float(value), epochtime)
    return message


def send_graphite_metric(server, port, message):
    # Send stat to graphite
    graphite_socket = socket.socket()
    graphite_socket.connect((server, port))
    graphite_socket.sendall(message)
    graphite_socket.close()


def parse_stat(prefix, parent, stat, epochtime):
    if type(parent[stat]) is dict:
        for substat in parent[stat]:
            new_prefix = '%s.%s' % (prefix, stat)
            parse_stat(new_prefix, parent[stat], substat, epochtime)
    elif (type(parent[stat]) is float) or (type(parent[stat]) is int) or (type(parent[stat]) is bool):
        message = graphite_message(prefix, stat, parent[stat], epochtime)
        print_debug(message)
        send_graphite_metric(graphite_server, graphite_port, message)
    else:
        # Skip stat if it's a non-number.  Probably need to add a nested loop above to handle type dict
        print_debug("%s: %s is a %s instead of a float\n" % (stat, parent[stat], type(parent[stat])))


def print_graphite_connection_info():
    print_info("VMstore: %s" % (server_name))
    print_info("API Version: " + json_info['preferredVersion'])
    print_info("Update Frequency: %s seconds" % (interval))
    print_info("Graphite Server: %s" % (graphite_server))
    print_info("Graphite Port: %s" % (graphite_port))
    print_info("Graphite storage schema: tintri.%s." % (graphite_formatted_server_name))


# main
if os.environ.get('vmstore_fqdn') is not None and os.environ.get('vmstore_username') is not None and os.environ.get('vmstore_password') is not None and os.environ.get('graphite_fqdn') is not None and os.environ.get('graphite_port') is not None:
    server_name = os.environ.get('vmstore_fqdn')
    user_name = os.environ.get('vmstore_username')
    password = os.environ.get('vmstore_password')
    graphite_server = os.environ.get('graphite_fqdn')
    graphite_port = int(os.environ.get('graphite_port'))
    print("Using parameters found in your environment\n")
elif len(sys.argv) == 6:
    server_name = sys.argv[1]
    user_name = sys.argv[2]
    password = sys.argv[3]
    graphite_server = sys.argv[4]
    graphite_port = int(sys.argv[5])
    print("Using paramerts passed in on the command line\n")
else:
    print("\nPrints VMstore information\n")
    print("Usage: " + sys.argv[0] + " vmstore_fqdn vmstore_username vmstore_password graphite_fqdn graphite_port\n")
    sys.exit(-1)

graphite_formatted_server_name = server_name.replace(".", "_")

# Get the preferred version
r = tintri.api_version(server_name)
json_info = r.json()

print_graphite_connection_info

while True:
    print_debug("Starting VMstore collection...")

    # Login to VMstore
    session_id = tintri.api_login(server_name, user_name, password)

    # Gather stats
    vmstore_stats = get_vmstore(session_id)

    # Get epoch time
    epochtime = int(time.time())

    # All done, log out
    tintri.api_logout(server_name, session_id)

    for stat in vmstore_stats:
        prefix = 'tintri.' + graphite_formatted_server_name + '.vmstore'
        parse_stat(prefix, vmstore_stats, stat, epochtime)

    print_debug("Collection finished")

    # Wait for x seconds
    print_debug("Sleeping for %s seconds..." % (interval))
    time.sleep(interval)

#end
