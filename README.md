# check ttn gateway status
Icinga check command to check status of a LoraWAN TTN (The Things Network)-Gateway

Heavily influenced by the great work of the [Monitoring Plugin Collection](https://git.linuxfabrik.ch/linuxfabrik/monitoring-plugins)

# installation

- copy script to /usr/lib/nagios/plugins/
- define command in icinga

# help
    usage: check_ttn_gateway.py [-h] [-V] [--always-ok] [--server SERVER_ADDRESS] --gatewayID GATEWAY_ID --apiKey API_KEY [-c CRIT] [-w WARN]

    This plugin lets you track if a TTN-Gateway is connected

    options:
    -h, --help            show this help message and exit
    -V, --version         show program's version number and exit
    --always-ok           Always returns OK.
    --server SERVER_ADDRESS
                            Server address of your gateway. Default: https://eu1.cloud.thethings.network
    --gatewayID GATEWAY_ID
                            ID your gateway.
    --apiKey API_KEY      Gateway apiKey. Can be generated in TTN Console
    -c CRIT, --critical CRIT
                            Set the critical threshold CPU Usage Percentage. Default: 3600
    -w WARN, --warning WARN
                            Set the warning threshold CPU Usage Percentage. Default: 600

# usage example

# Reference
- [Monitoring Plugins Collection](https://git.linuxfabrik.ch/linuxfabrik/monitoring-plugins)
- [TTN API Docs](https://www.thethingsindustries.com/docs/reference/api/gateway_server/)