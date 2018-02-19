#!/usr/bin/python
#**************************************************************************
#  This file is part of eBioKit 2017 Admin tools.
#  Copyright Erik Bongcam-Rudloff Group, SLU, Sweden 2017
#
#  This tool updates the configuration for the eBioKit services.
#
#  Version: 0.1
#
#  Changelog:
#    - 2017/04/13:  First version
#
#  Enjoy the eBioKit and please contact us for any question or suggestion!
#  --
#  The eBioKit development team
#  More info http://ebiokit.eu/
#  Technical contact ebiokit@gmail.com
#**************************************************************************

from common import *
from sys import  stderr

def main(options):
    read_conf()

    if len(options) < 1 or not(options[0] in ["-s", "--service"]):
        show_help()

    # STEP 0. FETCH ALL INSTALLED SERVICES
    INSTALLED_SERVICES = get_installed_services()

    # STEP 1. CHECK IF SELECTED SERVICE IS AVAILABLE
    target_services = None
    if options[0] in ["-s", "--service"]:
        if len(options) < 2:
            show_help("Lost parameter 'service_name'.")
        for service in INSTALLED_SERVICES:
            if service.instance_name == options[1]:
                target_services = [service]
                break
        if target_services == None:
            show_help("Service \"" + options[1] + "\" is not installed.")
    else:
        show_help("\"" + options[0] + "\" is not a valid option.")

    n_lines = 25
    if len(options) > 2 and options[2] in ["-n", "--lines"]:
        if len(options) < 4:
            show_help("Lost parameter 'NUM'.")
        else:
            n_lines = options[3]
            try:
                n_lines = int(n_lines)
            except Exception:
                show_help("Invalid number of lines 'NUM'.")

    # STEP 2. CHECK ALL SELECTED SERVICES
    for service in target_services:
        check_service(service, n_lines)
    exit(0)


def show_help(message=""):
    # STEP 0. FETCH ALL INSTALLED SERVICES
    INSTALLED_SERVICES = get_installed_services()

    print message
    print "Usage: service_log -s service_name -n NUM"
    print "       where"
    print "   -s, --service : Print the last 25 lines of the log for the selected eBioKit service "
    print "   -n, --lines : Print the last NUM lines instead of the last 25"
    services = []
    for service in INSTALLED_SERVICES:
        services.append(service.instance_name)
    print "         Available services: [" + ", ".join(services) + "]"
    print ""
    exit(1)

def check_service(service, lines):
    if not service.enabled:
        print "SERVICE IS NOT ENABLED"
        return

    try:
        output, error = ebiokit_remote_launcher("service log", str(lines) + "\" \"" + service.instance_name)
        print output
        print >> sys.stderr, error
    except Exception as ex:
        print ex.message
        print "UNKNOWN"

    return

if __name__ == "__main__":
   main(sys.argv[1:])
