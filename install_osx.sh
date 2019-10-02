#!/bin/bash

# --------------------------------------------------------------------------------
# Step 0. Define const
EBIOKIT_WWW_DIRECTORY="/usr/local/var/www"
EBIOKIT_USER="ebiokit"
EBIOKIT_GROUP="staff"

# --------------------------------------------------------------------------------
# Step 1. Install general dependencies
# Install Homebrew package system
 /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
# Install dependencies
brew install wget nginx uwsgi htop md5sha1sum
# Root for docs is: /usr/local/var/www
# By default the port is set to 8080 at  /usr/local/etc/nginx/nginx.conf.
# We must edit this file and change default port to 80
# Consequently, nginx needs to be run as sudo.
#
# nginx will load all files in /usr/local/etc/nginx/servers/.
#
# To have launchd start nginx now and restart at login:
#   brew services start nginx
# Or, if you don't want/need a background service you can just run:
#   nginx
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
sudo python /tmp/get-pip.py

sudo ln -s  /usr/local/var/www /var/www

# --------------------------------------------------------------------------------
# Step 2. Install Docker CE
# Please install Docker using the DMG image provided at the web.

# --------------------------------------------------------------------------------
# Step 3. Create the user that will launch the dockers and run the uwsgi server
#sudo adduser $EBIOKIT_USER
#sudo usermod -aG docker $EBIOKIT_USER

# --------------------------------------------------------------------------------
# Step 4. Install eBioKit application
# Step 4.1 Get the latest version of the eBioKit application
# sudo mkdir /data
# sudo chown $USER:staff /data
cd /data/
git clone https://github.com/eBioKit/ebiokit-site.git
cd ebiokit-site/
git checkout minified
git clone https://github.com/fikipollo/PySiQ.git queue/
sudo ln -s /data/ebiokit-site/server $EBIOKIT_WWW_DIRECTORY/ebiokit
sudo ln -s /data/ebiokit-site/queue $EBIOKIT_WWW_DIRECTORY/queue
sudo chown -R $EBIOKIT_USER:$EBIOKIT_GROUP $EBIOKIT_WWW_DIRECTORY"/ebiokit"
sudo chown -R $EBIOKIT_USER:$EBIOKIT_GROUP $EBIOKIT_WWW_DIRECTORY"/queue"
# Step 4.2 Install python requirements
sudo -H pip install -r requirements.txt
# Step 4.3 Create the SECRET_KEY for the Django application at /etc/ebiokit_secretkey.txt
python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])' | sudo tee /etc/ebiokit_secretkey.txt
# Step 4.5 Initialize the database
cd server/
# Step 4.5.1 Erase the database
python manage.py flush
# Step 4.5.2 Prepare the database
python manage.py migrate
# Step 4.5.3 Fill the database with default values
sed -i "" 's/LINUX/OSX/g' config/default/settings.json
python manage.py loaddata config/default/*.json
# Step 4.5.4 Create the superuser for database backend (only accesible if Debug enabled)
python manage.py createsuperuser
# Step 4.6 Create the required directories
mkdir -p /data/ebiokit-data/nginx/sites-enabled/conf/
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-data
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-logs
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-services/init-scripts
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-services/launchers
mkdir -p /data/ebiokit-data/ebiokit_components/ebiokit-services/uninstallers
# Step 4.7 Initialize the default settings for UWSGI and the PySiQ
cp config/default/uwsgi_params /data/ebiokit-data/nginx/uwsgi_params
cp config/default/uwsgi-ini-osx /data/ebiokit-data/nginx/uwsgi.ini
cp config/default/queue-uwsgi-ini-osx /data/ebiokit-data/nginx/queue_uwsgi.ini
sed 's#$${EBIOKIT_WWW_DIRECTORY}#'${EBIOKIT_WWW_DIRECTORY}'\/ebiokit#g' config/default/queue.cfg > $EBIOKIT_WWW_DIRECTORY/queue/server.cfg
sudo chown -R $EBIOKIT_USER:$EBIOKIT_GROUP /data/ebiokit-data/
sudo chown -R $EBIOKIT_USER:$EBIOKIT_GROUP /data/ebiokit-site/

# --------------------------------------------------------------------------------
# Step 5. Install docker requirements
docker pull ebiokit/ultraextract

# --------------------------------------------------------------------------------
# Step 6. Configure Nginx to run as a reverse proxy and restart service
sudo brew services stop nginx
sudo cp /usr/local/etc/nginx/nginx.conf /usr/local/etc/nginx/nginx.conf_bk
sudo cp config/default/nginx-conf-osx /usr/local/etc/nginx/nginx.conf
sudo cp config/default/nginx-default-server /usr/local/etc/nginx/servers/default
sudo brew services start nginx

# --------------------------------------------------------------------------------
# Step 7. Launch UWSGI server
cd /data/ebiokit-data/nginx
mkdir -p /usr/local/var/log/uwsgi
kill -9 `cat /tmp/ebiokit.pid`; sudo rm /tmp/ebiokit.*
kill -9 `cat /tmp/ebiokit_queue.pid`; sudo rm /tmp/ebiokit_queue.*
sudo uwsgi --ini uwsgi.ini
sudo uwsgi --ini queue_uwsgi.ini --enable-threads
# TO STOP USE sudo kill -9 `cat /tmp/ebiokit.pid`; sudo rm /tmp/ebiokit.*
# TO STOP USE sudo kill -9 `cat /tmp/ebiokit_queue.pid`; sudo rm /tmp/ebiokit_queue.*

# --------------------------------------------------------------------------------
# Step 8. Link the service tools for managing the system as a OS tool
ln -s ${EBIOKIT_WWW_DIRECTORY}/ebiokit/admin_tools/service /usr/local/bin/ebservice

#TODO: CHANGE THE QUEUE FUNCTIONS LOCATION
