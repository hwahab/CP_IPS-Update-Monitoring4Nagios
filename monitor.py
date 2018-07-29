#
# monitor.py
# version 1.0
#
# written by Daniel Meier (github.com/leinadred)
# July 2018
#### Handle with care ####
#### 
#### Changed in SDK (to unsecure - no warnings)
#### mgmt_api.py - line 35 to unsafe_auto_accept=True<---

from __future__ import print_function
# A package for reading passwords without displaying them on the console.
import getpass
import sys, os
import datetime
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--api_server', help='Target Host (CP Management Server)')
parser.add_argument('-U', '--api_user', help='API User')
parser.add_argument('-P', '--api_pwd', help='API Users Password')

args = parser.parse_args()

# CONSTANTS FOR RETURN CODES UNDERSTOOD BY NAGIOS
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

# Checkpoint SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# lib is a library that handles the communication with the Check Point management server.
from lib import APIClient, APIClientArgs


def main():
    client_args = APIClientArgs(server=args.api_server)
    with APIClient(client_args) as client:
        #
        #### This i
        if client.check_fingerprint() is False:
            print("Could not get the server's fingerprint - Check connectivity with the server.")
            raise SystemExit, UNKNOWN

        # login to server:
        login_res = client.login(args.api_user, args.api_pwd)

        if login_res.success is False:
            print("Login failed: {}".format(login_res.error_message))
            raise SystemExit, UNKNOWN
        monitor_ips_version = client.api_call("show-ips-status")
        if monitor_ips_version.success:
            #Editing around Vars
            ips_info=monitor_ips_version.data
            #version numbers
            ips_current_ver_info=ips_info["installed-version"]
            ips_update_ver_info=ips_info["latest-version"]
            #bool update available - yes/no
            ips_bool_update=ips_info["update-available"]
            #install dates
            ips_date_last_install=ips_info["last-updated"]
            ips_date_last_install_iso=ips_date_last_install["iso-8601"]
            ips_date_last_install_posix=ips_date_last_install["posix"]
            #release date of last update
            ips_date_update=ips_info["latest-version-creation-time"]
            ips_date_update_iso=ips_date_update["iso-8601"]
            ips_date_update_posix=ips_date_update["posix"]
            #
            #
            ips_update_date_delta=datetime.date.fromtimestamp(ips_date_update_posix/1000) - datetime.date.fromtimestamp(ips_date_last_install_posix/1000)            
            #work with it
            if not ips_bool_update:
                if ips_update_date_delta.days < 0:
                    print("OK! No Update available - Last installed update: {0} - Installed Version {1}" .format(ips_date_last_install_iso, ips_current_ver_info))
                    raise SystemExit, OK
                else:
                    print("OK! No Update available - Last installed update: {0} - Installed Version {1} - Update Date Delta: {2}" .format(ips_date_last_install_iso, ips_current_ver_info, ips_update_date_delta))
                    raise SystemExit, OK
            elif ips_update_date_delta.days > 3:
                print("CRITICAL! Updates available -  Last installed update: {0} - last Installed {1}; available {2} - Update Date Delta: {3} Days!" .format(ips_date_last_install_iso, ips_current_ver_info, ips_update_ver_info,ips_update_date_delta.days))
                raise SystemExit, CRITICAL
            else:
                if ips_update_date_delta.days < 0:
                    print("WARNING! Updates available -  Last installed update: {0} - last Installed {1}; available {2}" .format(ips_date_last_install_iso, ips_current_ver_info, ips_update_ver_info))
                    raise SystemExit, WARNING
                else:
                    print("WARNING! Updates available -  Last installed update: {0} - last Installed {1}; available {2} - Update Date Delta: {3} Days" .format(ips_date_last_install_iso, ips_current_ver_info, ips_update_ver_info,ips_update_date_delta.days))
                    raise SystemExit, WARNING    
        else:
            print("meh - something went wrong")
            
if __name__ == "__main__":
    main()