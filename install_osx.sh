#!/bin/bash

sudo port selfupdate
sudo port upgrade outdated

sudo port install nginx git
#
# sudo port install py27-pip
# sudo port select --set pip pip27
# which pip

# sudo pip install --upgrade pip

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

echo "Installing requirements"
modules=$(cat requirements.txt )
for m in $modules; do
  sudo easy_install $m;
done

cd /tmp
wget http://projects.unbit.it/downloads/uwsgi-latest.tar.gz
tar xzvf uwsgi-latest.tar.gz
cd uwsgi-*
make
sudo cp uwsgi /usr/local/bin/


cd ~/Downloads/
wget https://github.com/eBioKit/ebiokit-site/archive/v18.02beta.tar.gz
tar xzvf v18.02beta.tar.gz
cd ebioki-site-*
sudo mv server/ /var/www/ebiokit

cd /var/www/ebiokit

echo "Creating SECRET_KEY file at /etc/ebiokit_secretkey.txt"
python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])' | sudo tee /etc/ebiokit_secretkey.txt

echo "Preparing database"
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

sudo mkdir /opt/local/etc/nginx/sites-enabled
sudo mkdir /var/log/nginx/
sudo mkdir /var/log/uwsgi
sudo chown -R ebioadmin:staff /var/log/uwsgi

echo "Please download the eBioKit virtual machine from ftp://ftpuser:KCwtk5UYBgxvU2pP@77.235.253.230/ebiokit-original.tar.gz"
echo "and import the machine in VirtualBox"
echo "You will need also to configure Nginx to run as a reverse proxy. Please use the provided site settings "
echo "located at config/default/settings and place it at /etc/nginx/sites-enabled/default:"
echo " $ sudo cp config/default/nginx-default-server /opt/local/etc/nginx/sites-enabled/default "
echo " $ sudo service nginx restart"
echo ""

#TODO: admin tools command line
#TODO: nginx.conf
#TODO: start services and go to IP/admin
#TODO: Go to settings check if valid data dirs
#TODO: logout and create an account, login again as ebiokit and change admin users
