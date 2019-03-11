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
import sqlite3
import sys
from os import path as osPath
import subprocess

global DB_LOCATION
DB_LOCATION = None
global INSTALLED_SERVICES
INSTALLED_SERVICES = None
global DATA_LOCATION
DATA_LOCATION = None


def read_conf():
    import os
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'services.conf')
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.readfp(open(file))
    global DB_LOCATION
    DB_LOCATION = os.path.join(os.path.dirname(os.path.realpath(__file__)), config.get('Database settings', 'DB_LOCATION'))


def get_installed_services():
    global INSTALLED_SERVICES

    if INSTALLED_SERVICES == None:
        connection = sqlite3.connect(DB_LOCATION)
        cursor = connection.cursor()
        cursor.execute('SELECT instance_name, title, enabled FROM applications_application')
        INSTALLED_SERVICES = [
            Service().parse(["ebiokit-web", "eBioKit website", 1]),
            Service().parse(["ebiokit-queue", "eBioKit queue", 1]),
            Service().parse(["docker-engine", "Docker engine", 1])
        ]
        for service_data in cursor:
            INSTALLED_SERVICES.append(Service().parse(service_data))
        cursor.close()
    return INSTALLED_SERVICES


def get_data_location():
    global DATA_LOCATION

    if DATA_LOCATION == None:
        connection = sqlite3.connect(DB_LOCATION)
        cursor = connection.cursor()
        cursor.execute('SELECT value from applications_settings WHERE name="ebiokit_data_location"');
        DATA_LOCATION = cursor.fetchone()[0]
        cursor.close()
    return DATA_LOCATION.rstrip("/")


def printServiceMessage(message, length=30):
    while len(message) < length:
        message += "."
    sys.stdout.write(message)
    sys.stdout.flush()


def ebiokit_remote_launcher(command, instance_name, ignore=False):
    settings = read_settings()
    data_location = get_data_location()
    command = osPath.join(osPath.dirname(osPath.realpath(__file__)), 'ebiokit_launcher.sh') + ' "' + settings.get("platform") + '" "' + command.replace(" ", "_") + '" "' + instance_name + '" "' + data_location + '"'
    error = ""
    try:
        p = subprocess.Popen(['bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, err) = p.communicate()
    except Exception as ex:
        if ignore == True:
            pass
        else:
            raise ex
    return output, err


def read_settings():
    connection = sqlite3.connect(DB_LOCATION)
    cursor = connection.cursor()
    cursor.execute('SELECT name, value FROM applications_settings')
    settings = {}
    for settings_data in cursor:
        settings[settings_data[0]] = settings_data[1]
    return settings

class Service:
    """ High-level application model"""
    service = ""
    title = ""
    enabled = ""

    def parse(self, service_data):
        self.instance_name = service_data[0]
        self.title= service_data[1]
        self.enabled = (service_data[2] == 1)
        return self
