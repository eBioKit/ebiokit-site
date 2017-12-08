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

echo "Creating superuser for Django server"
python manage.py createsuperuser


