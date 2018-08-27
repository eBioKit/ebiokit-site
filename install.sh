#!/bin/bash

EBIOKIT_WWW_DIRECTORY="/var/www"

# INSTALL DEPENDECIES
sudo apt-get update
sudo apt-get install python-pip build-essential nginx uwsgi git uwsgi-plugin-python
sudo pip install --upgrade pip

# Install Docker CE, instructions from https://docs.docker.com/install/linux/docker-ce/ubuntu
# Install packages to allow apt to use a repository over HTTPS
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
# Add Docker’s official GPG key:
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# Set up the stable repository for x86_64 / amd64
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
# Update the apt package index.
sudo apt-get update
# Install the latest version of Docker CE
sudo apt-get install docker-ce
# Install the latest version for docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
# Create the user that will launch the dockers and run the uwsgi server
sudo adduser ebiokit
sudo usermod -aG docker ebiokit
# ebiokit
# vGH9HmDA?LtuZwY!


# Get the latest version for eBioKit
cd /data/
git clone https://github.com/eBioKit/ebiokit-site.git
cd ebiokit-site/
git checkout minified
sudo ln -s /data/ebiokit-site/server $EBIOKIT_WWW_DIRECTORY/ebiokit
sudo ln -s /data/ebiokit-site/queue $EBIOKIT_WWW_DIRECTORY/queue

# Prepare application
echo "Installing requirements"
sudo pip install -r requirements.txt

echo "Creating SECRET_KEY file at /etc/ebiokit_secretkey.txt"
python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])' | sudo tee /etc/ebiokit_secretkey.txt

echo "Preparing database"
cd server/
# Erase the database
python manage.py flush
# Prepare the database
python manage.py migrate
# Fill the database
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
sed 's#$${EBIOKIT_WWW_DIRECTORY}#'${EBIOKIT_WWW_DIRECTORY}'\/ebiokit#g' config/default/queue.cfg > /var/www/queue/server.cfg

sudo service nginx stop
sudo cp config/default/nginx-default-server /etc/nginx/sites-enabled/default

sudo chown -R ebiokit:ebiokit $EBIOKIT_WWW_DIRECTORY"/ebiokit"
sudo chown -R ebiokit:ebiokit $EBIOKIT_WWW_DIRECTORY"/queue"
sudo chown -R ebiokit:ebiokit /data/ebiokit-data/

sudo docker pull ebiokit/ultraextract

cd /data/ebiokit-data/nginx
sudo uwsgi --ini uwsgi.ini
sudo service nginx restart

# TO STOP USE sudo kill -9 `cat /tmp/ebiokit.pid`; sudo rm /tmp/ebiokit.*
#TODO: RUN THE QUEUE
#TODO: CHANGE THE QUEUE FUNCTIONS LOCATION


echo "Please download the eBioKit virtual machine from ftp://ftpuser@77.235.253.230/ebiokit-original.tar.gz"
echo "and import the machine in VirtualBox"
echo "You will need also to configure Nginx to run as a reverse proxy. Please use the provided site settings "
echo "located at config/default/settings and place it at /etc/nginx/sites-enabled/default:"
echo " $ sudo cp config/default/nginx-default-server /etc/nginx/sites-enabled/default "
echo " $ sudo service nginx restart"
echo ""
