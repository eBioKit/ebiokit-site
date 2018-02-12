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

def main(options):
    read_conf()

    if len(options) < 2 or not(options[1] in ["log", "start", "stop", "status", "restart"]):
        show_help()

    # STEP 0. FETCH ALL INSTALLED SERVICES
    INSTALLED_SERVICES = get_installed_services()

    # STEP 1. CHECK IF SELECTED SERVICE IS AVAILABLE
    params = []
    if options[0] == "all":
        params.append("-a")
    else:
        params.append("-s")
        for service in INSTALLED_SERVICES:
            if service.instance_name == options[0]:
                params.append(service.instance_name)
                break
        if len(params) < 2:
            show_help("Service \"" + options[0] + "\" is not installed.")

    if options[1] == "start":
        import service_start as _dispacher
    elif options[1] == "stop":
        import service_stop as _dispacher
    elif options[1] == "restart":
        import service_restart as _dispacher
    elif options[1] == "log":
        if len(options) > 2:
            params.append("--lines")
            params.append(str(options[2]).replace("-",""))
        import service_log as _dispacher
    else: #status
        if len(options) > 2 and options[2] == "--no-cmd":
            params.append("--no-cmd")
        import service_status as _dispacher

    _dispacher.main(params)

    exit(0)


def show_help(message=""):
    # STEP 0. FETCH ALL INSTALLED SERVICES
    INSTALLED_SERVICES = get_installed_services()
    services = []
    for service in INSTALLED_SERVICES:
        services.append(service.instance_name)

    print "Usage: service [SERVICE NAME] [OPTION]"
    print "where SERVICE NAME includes:"
    print "   all               if you want to run OPTION for all eBioKit Services."
    print "   service_name      if you want to run OPTION for a selected eBioKit service."
    print "                      where service_name must be one of the following options: "
    print "                      [" + ", ".join(services) + "]"
    print ""
    print "where OPTION includes:"
    print "   log               Print the log for the selected eBioKit service"
    print "   start             Start the selected services"
    print "   status            Show the current status for the selected services (RUNNING, STOPPED,...)"
    print "   stop              Stop the selected services"
    print ""
    exit(1)

if __name__ == "__main__":
   main(sys.argv[1:])
