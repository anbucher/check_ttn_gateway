# check ttn gateway status
Icinga check command to check status of a LoraWAN TTN (The Things Network)-Gateway

Heavily influenced by the great work of the [Monitoring Plugin Collection](https://git.linuxfabrik.ch/linuxfabrik/monitoring-plugins)

# installation

- copy script to /usr/lib/nagios/plugins/
- make script executable `chmod a+x ./check_ttn_gateway.py`
- define command in icinga

# help

```
usage: check_ttn_gateway.py [-h] [-V] [--always-ok] [--server SERVER_ADDRESS] [-c CRIT] [-w WARN] --gatewayID GATEWAY_ID --apiKey API_KEY

This plugin lets you track if a TTN-Gateway is connected

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --always-ok           Always returns OK.
  --server SERVER_ADDRESS
                        Server address of your gateway. Default: https://eu1.cloud.thethings.network
  -c CRIT, --critical CRIT
                        Set the critical threshold seconds since last connection update. Default: 3600
  -w WARN, --warning WARN
                        Set the warning threshold seconds since last connection update. Default: 600
  --gatewayID GATEWAY_ID
                        ID of your gateway.
  --apiKey API_KEY      Gateway apiKey. Can be generated in TTN Console
```
# usage example

```
./check_ttn_gateway.py --gatewayID mygatewayid --apiKey 'NNSXS.XXXXXXXXX'
```

# output

```
Gateway: OK - 21s since last status update
Version 3.17.2|'uplink_count'=302;;;0; 'rxok'=0;;;0;100 'rxfw'=0;;;0;100 'ackr'=100;;;0;100 'txin'=0;;;0;100 'txok'=0;;;0;100 'rxin'=0;;;0;100
```

# Reference
- [Monitoring Plugins Collection](https://git.linuxfabrik.ch/linuxfabrik/monitoring-plugins)
- [TTN API Docs](https://www.thethingsindustries.com/docs/reference/api/gateway_server/)