#! /usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4 -*-
#
# Author:  Andreas Bucher
# Contact: icinga (at) buchermail (dot) de
#          
# TODO License: The Unlicense, see LICENSE file.

# TODO <git-url>

"""Have a look at the check's README for further details.
"""
import argparse
import sys
import json
import datetime
import requests
from requests.structures import CaseInsensitiveDict
from traceback import format_exc

__author__ = 'Andreas Bucher'
__version__ = '2022021501'


DESCRIPTION = """This plugin lets you track if a TTN-Gateway is connected"""

# Sample URL: https://eu1.cloud.thethings.network/api/v3/gs/gateways/{gateway_id}/connection/stats
DEFAULT_SERVER = 'https://eu1.cloud.thethings.network'
DEFAULT_API_PATH1 = '/api/v3/gs/gateways/'
DEFAULT_API_PATH2 = '/connection/stats'

## Define states

# STATE_OK = 0: The plugin was able to check the service and it appeared
# to be functioning properly.

# STATE_WARN = 1: The plugin was able to check the service, but it
# appeared to be above some "warning" threshold or did not appear to be
# working properly.

# STATE_CRIT = 2: The plugin detected that either the service was not
# running or it was above some "critical" threshold.

# STATE_UNKNOWN = 3: Invalid command line arguments were supplied to the
# plugin or low-level failures internal to the plugin (such as unable to
# fork, or open a tcp socket) that prevent it from performing the
# specified operation. Higher-level errors (such as name resolution
# errors, socket timeouts, etc) are outside of the control of plugins and
# should generally NOT be reported as UNKNOWN states.

# Author of state definition
# __author__ = 'Linuxfabrik GmbH, Zurich/Switzerland'
# __version__ = '2020043001'


STATE_OK = 0
STATE_WARN = 1
STATE_CRIT = 2
STATE_UNKNOWN = 3
#STATE_DEPENDENT = 4




def parse_args():
    """Parse command line arguments using argparse.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s: v{} by {}'.format(__version__, __author__)
    )

    parser.add_argument(
        '--always-ok',
        help='Always returns OK.',
        dest='ALWAYS_OK',
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '--server',
        help='Server address of your gateway. Default: %(default)s',
        dest='SERVER_ADDRESS',
        default=DEFAULT_SERVER,
    )

    parser.add_argument(
        '--gatewayID',
        help='ID your gateway.',
        dest='GATEWAY_ID',
        default='',
        required=True,
    )

    parser.add_argument(
        '--apiKey',
        help='Gateway apiKey. Can be generated in TTN Console',
        dest='API_KEY',
        default='',
        required=True,
    )

    return parser.parse_args()


def run_api_request(path, apiKey):
    """Check TTN API.
    """
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + apiKey


    # Get Status from Gateway Server API
    # Method: Gs.GetGatewayConnectionStats
    # stdout, stderr, resp = requests.get(path, headers=headers)

    # FAKE request
    f = open("response.json")

    try:
        return json.load(f)
    except:
        print('ValueError: No JSON object could be decoded'.strip())
        sys.exit(STATE_UNKNOWN)

def get_sec_last_status(data):

    # Get current datetime
    now = datetime.datetime.now()

    # Check date difference
    try:
        ### timeFormat: 2022-02-14T13:33:06.488545731Z
        lastGatewayStatus = datetime.datetime.strptime(data['last_status']['time'], '%Y-%m-%dT%H:%M:%SZ')
    
        diffInSecs = (abs(now - lastGatewayStatus ).days * 24 * 60 * 60) + abs(now - lastGatewayStatus ).seconds

        return diffInSecs
    except:
        print('ValueError: Last Status could not be parsed'.strip())
        sys.exit(STATE_UNKNOWN)       

def main():
    """The main function. Hier spielt die Musik.
    """

    # parse the command line, exit with UNKNOWN if it fails
    try:
        args = parse_args()
    except SystemExit:
        sys.exit(STATE_UNKNOWN)

    # Build API path
    path = args.SERVER_ADDRESS + DEFAULT_API_PATH1 + args.GATEWAY_ID + DEFAULT_API_PATH2

    response = run_api_request(path, args.API_KEY)
    diffSecs = get_sec_last_status(response)

    print(diffSecs)
    sys.exit(STATE_OK)

    # 
    # TODO: get perf values  from metrics (rxfw, ackr)
    # interprete secs with warning and critical

if __name__ == '__main__':
    try:
        main()
    except Exception:   # pylint: disable=W0703
        """See you (cu)

        Prints a Stacktrace (replacing "<" and ">" to be printable in Web-GUIs), and exits with
        STATE_UNKNOWN.
        """
        print(format_exc().replace("<", "'").replace(">", "'"))
        sys.exit(STATE_UNKNOWN)
