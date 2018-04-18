#!/bin/bash

# INSTALL DEPENDECIES
sudo apt-get update
sudo apt-get install python-pip python-virtualenv build-essential nginx uwsgi
sudo pip install --upgrade pip


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# Only for developing
# echo "Enabling virtualenv at $DIR"
# virtualenv .env
# source .env/bin/activate

echo "Installing requirements"
pip install -r requirements.txt

echo "Creating SECRET_KEY file at /etc/ebiokit_secretkey.txt"
python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])' | sudo tee /etc/ebiokit_secretkey.txt

echo "Preparing database"
cd server/
python manage.py migrate
python manage.py loaddata config/default/*.json

echo "Creating superuser for Django server"
python manage.py createsuperuser

echo "Creating required directories"
mkdir -p /data/ebiokit-data/nginx/sites-enabled/conf/
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-data
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-logs
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-services/init-scripts
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-services/launchers
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-services/uninstallers
cp config/default/uwsgi_params /data/ebiokit-data/nginx/uwsgi_params
cp config/default/uwsgi.ini /data/ebiokit-data/nginx/uwsgi.ini

echo "Please download the eBioKit virtual machine from ftp://ftpuser@77.235.253.230/ebiokit-original.tar.gz"
echo "and import the machine in VirtualBox"
echo "You will need also to configure Nginx to run as a reverse proxy. Please use the provided site settings "
echo "located at config/default/settings and place it at /etc/nginx/sites-enabled/default:"
echo " $ sudo cp config/default/nginx-default-server /etc/nginx/sites-enabled/default "
echo " $ sudo service nginx restart"
echo ""
