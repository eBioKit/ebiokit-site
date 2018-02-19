#!/bin/bash

sudo apt-get update
sudo apt-get install python-pip python-virtualenv build-essential
sudo pip install --upgrade pip

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

echo "Enabling virtualenv at $DIR"
virtualenv .env
source .env/bin/activate

echo "Installing requirements"
pip install -r requirements.txt

echo "Preparing database"
cd server/
python manage.py migrate
python manage.py loaddata config/default/*

echo "Creating superuser for Django server"
python manage.py createsuperuser

mkdir /data/ebiokit/ebiokit_components
mkdir /data/ebiokit/ebiokit_components/ebiokit-data
mkdir /data/ebiokit/ebiokit_components/ebiokit-logs
mkdir /data/ebiokit/ebiokit_components/ebiokit-services
mkdir /data/ebiokit/ebiokit_components/ebiokit-services/init-scripts
mkdir /data/ebiokit/ebiokit_components/ebiokit-services/launchers
mkdir /data/ebiokit/ebiokit_components/ebiokit-services/uninstallers

echo "Please download the eBioKit virtual machine from ftp://ftpuser@77.235.253.230/ebiokit-original.tar.gz"
echo "and import the machine in VirtualBox"
