#! /usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4 -*-
#
# Author:  Andreas Bucher
# Contact: icinga (at) buchermail (dot) de
#          
# License: The Unlicense, see LICENSE file.

# https://github.com/anbucher/check_ttn_gateway.git

"""Have a look at the check's README for further details.
"""
import argparse
from difflib import diff_bytes
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

DEFAULT_WARN = 600 # seconds
DEFAULT_CRIT = 3600 # seconds


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
# __author__ = 'Andreas Bucher'
# __version__ = '2022021501'


STATE_OK = 0
STATE_WARN = 1
STATE_CRIT = 2
STATE_UNKNOWN = 3
#STATE_DEPENDENT = 4

########### common functions ###########
# useful functions - Copyright by https://git.linuxfabrik.ch/linuxfabrik/lib/-/blob/master/base3.py

def get_perfdata(label, value, uom, warn, crit, min, max):
    """Returns 'label'=value[UOM];[warn];[crit];[min];[max]
    """
    msg = "'{}'={}".format(label, value)
    if uom is not None:
        msg += uom
    msg += ';'
    if warn is not None:
        msg += str(warn)
    msg += ';'
    if crit is not None:
        msg += str(crit)
    msg += ';'
    if min is not None:
        msg += str(min)
    msg += ';'
    if max is not None:
        msg += str(max)
    msg += ' '
    return msg


def oao(msg, state=STATE_OK, perfdata='', always_ok=False):
    """Over and Out (OaO)

    Print the stripped plugin message. If perfdata is given, attach it
    by `|` and print it stripped. Exit with `state`, or with STATE_OK (0) if
    `always_ok` is set to `True`.
    """
    if perfdata:
        print(msg.strip() + '|' + perfdata.strip())
    else:
        print(msg.strip())
    if always_ok:
        sys.exit(0)
    sys.exit(state)



def coe(result, state=STATE_UNKNOWN):
    """Continue or Exit (CoE)

    This is useful if calling complex library functions in your checks
    `main()` function. Don't use this in functions.

    If a more complex library function, for example `lib.url3.fetch()` fails, it
    returns `(False, 'the reason why I failed')`, otherwise `(True,
    'this is my result'). This forces you to do some error handling.
    To keep things simple, use `result = lib.base3.coe(lib.url.fetch(...))`.
    If `fetch()` fails, your plugin will exit with STATE_UNKNOWN (default) and
    print the original error message. Otherwise your script just goes on.

    The use case in `main()` - without `coe`:

    >>> success, html = lib.url3.fetch(URL)
    >>> if not success:
    >>>     print(html)             # contains the error message here
    >>>>    exit(STATE_UNKNOWN)

    Or simply:

    >>> html = lib.base3.coe(lib.url.fetch(URL))

    Parameters
    ----------
    result : tuple
        The result from a function call.
        result[0] = expects the function return code (True on success)
        result[1] = expects the function result (could be of any type)
    state : int
        If result[0] is False, exit with this state.
        Default: 3 (which is STATE_UNKNOWN)

    Returns
    -------
    any type
        The result of the inner function call (result[1]).
"""

    if result[0]:
        # success
        return result[1]
    print(result[1])
    sys.exit(state)


########### specific check functions ###########

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
        '-c', '--critical',
        help='Set the critical threshold seconds since last connection update. Default: %(default)s',
        dest='CRIT',
        type=int,
        default=DEFAULT_CRIT,
    )

    parser.add_argument(
        '-w', '--warning',
        help='Set the warning threshold  seconds since last connection update. Default: %(default)s',
        dest='WARN',
        type=int,
        default=DEFAULT_WARN,
    )

    parser.add_argument(
        '--gatewayID',
        help='ID of your gateway.',
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
    try:
        j = requests.get(path, headers=headers)
        json_str = j.json()

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        msg = template.format(type(ex).__name__, ex.args)
        return(False, msg)

    # FAKE request
    # f = open("sample_data/response.json")
    # json_str = json.load(f)

    try:
        return (True, json_str)
    except:
        return(False, 'ValueError: No JSON object could be decoded')

def get_sec_last_status(data):
    """Read out seconds since last status update.
    """
    # Get current datetime
    now = datetime.datetime.utcnow()

    # Check date difference
    try:
        ### timeFormat: 2022-02-14T13:33:06.488545731Z
        # dirty fix: remove timezone info, tz is UTC
        datetimestring = str(data['last_status']['time']).replace('Z','')
        # parse GatewayStatus datetime
        lastGatewayStatus = datetime.datetime.strptime(datetimestring, '%Y-%m-%dT%H:%M:%S')
        # calculate time difference
        diffInSecs = (abs(now - lastGatewayStatus ).days * 24 * 60 * 60) + abs(now - lastGatewayStatus ).seconds

        return (True, diffInSecs)
    except:
        return (False, 'ValueError: Last Status could not be parsed') 

def get_metrics(data):

    # field uplink_count in v3.19.1 not available
    # workaround: try to get value, set to -1 if not possible
    try:
        uplink_count = data['uplink_count']
    except:
        uplink_count = -1

    try:
        metrics = {
            'version': data['last_status']['versions']['ttn-lw-gateway-server'],
            'uplink_count': uplink_count,
            'rxok': data['last_status']['metrics']['rxok'],
            'rxfw': data['last_status']['metrics']['rxfw'],
            'ackr': data['last_status']['metrics']['ackr'],
            'txin': data['last_status']['metrics']['txin'],
            'txok': data['last_status']['metrics']['txok'],
            'rxin': data['last_status']['metrics']['rxin']
        }

        return (True, metrics)
    except:
        return (False, 'ValueError: Metrics could not be parsed') 

def main():
    """The main function. Hier spielt die Musik.
    """

    # parse the command line, exit with UNKNOWN if it fails
    try:
        args = parse_args()
    except SystemExit:
        sys.exit(STATE_UNKNOWN)

    # init output vars
    msg = ''
    state = STATE_OK
    perfdata = ''

    # Build API path
    path = args.SERVER_ADDRESS + DEFAULT_API_PATH1 + args.GATEWAY_ID + DEFAULT_API_PATH2

    response = coe(run_api_request(path, args.API_KEY))
    diffSecs = coe(get_sec_last_status(response))
    metrics = coe(get_metrics(response))

    # Add metrics to perfdata
    perfdata += get_perfdata('uplink_count', metrics['uplink_count'], None, None, None, 0, None)
    perfdata += get_perfdata('rxok', metrics['rxok'], None, None, None, 0, 100)
    perfdata += get_perfdata('rxfw', metrics['rxfw'], None, None, None, 0, 100)
    perfdata += get_perfdata('ackr', metrics['ackr'], None, None, None, 0, 100)
    perfdata += get_perfdata('txin', metrics['txin'], None, None, None, 0, 100)
    perfdata += get_perfdata('txok', metrics['txok'], None, None, None, 0, 100)
    perfdata += get_perfdata('rxin', metrics['rxin'], None, None, None, 0, 100)


    # check warn and crit thresholds
    try:
        if diffSecs > args.CRIT:
            msg += 'CRIT threshold reached: ' + str(diffSecs)
            state = STATE_CRIT
        else:    
            if diffSecs > args.WARN:
                msg += 'WARN threshold reached: ' + str(diffSecs)
                state = STATE_WARN
            else:
                msg = 'Gateway: OK - ' + str(diffSecs) + 's since last status update'
                msg += '\nVersion {}'.format(metrics['version']
                )

                state = STATE_OK

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        msg = template.format(type(ex).__name__, ex.args)
        state = STATE_UNKNOWN
        
    # 
    # TODO: get perf values  from metrics (rxfw, ackr)

    oao(msg, state, perfdata)

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
