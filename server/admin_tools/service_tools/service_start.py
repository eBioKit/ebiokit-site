#!/usr/bin/python
#**************************************************************************
#  This file is part of eBioKit 2017 Admin tools.
#  Copyright Erik Bongcam-Rudloff Group, SLU, Sweden 2017
#
#  This tool starts the eBioKit services.
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
from time import sleep


def main(options):
    read_conf()

    if len(options) < 1 or not(options[0] in ["-a", "--all", "-s", "--service"]):
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
        target_services = INSTALLED_SERVICES

    # STEP 2. START ALL SELECTED SERVICES
    for service in target_services:
        start_service(service)
    exit(0)


def show_help(message=""):
    # STEP 0. FETCH ALL INSTALLED SERVICES
    INSTALLED_SERVICES = get_installed_services()

    print message
    print "Usage: service_start [-s service_name | -a]"
    print "       where"
    print "   -a, --all     : Start all eBioKit services"
    print "   -s, --service : Start the selected eBioKit service "
    services = []
    for service in INSTALLED_SERVICES:
        services.append(service.instance_name)
    print "         Available services: [" + ", ".join(services) + "]"
    print ""
    exit(1)


def start_service(service):
    printServiceMessage("STARTING " + service.title)
    if not service.enabled:
        print "SERVICE IS NOT ENABLED"
        return

    try:
        ebiokit_remote_launcher("service start", service.instance_name)
        sleep(5)
        print "DONE"
    except Exception as ex:
        print "FAIL"

    return


if __name__ == "__main__":
   main(sys.argv[1:])
