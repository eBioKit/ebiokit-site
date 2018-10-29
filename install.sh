#!/bin/bash

# --------------------------------------------------------------------------------
# Step 0. Define const
EBIOKIT_WWW_DIRECTORY="/var/www"
EBIOKIT_USER="ebiokit"
# vGH9HmDA?LtuZwY!

# --------------------------------------------------------------------------------
# Step 1. Install general dependencies
# sudo add-apt-repository main
# sudo add-apt-repository universe
# sudo add-apt-repository restricted
# sudo add-apt-repository multiverse
sudo apt-get update
sudo apt-get install python-pip build-essential nginx uwsgi git uwsgi-plugin-python
sudo pip install --upgrade pip

# --------------------------------------------------------------------------------
# Step 2. Install Docker CE
#         Instructions from https://docs.docker.com/install/linux/docker-ce/ubuntu
# Step 2.1 Install packages to allow apt to use a repository over HTTPS
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
# Step 2.2 Add Docker’s official GPG key:
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# Step 2.3 Set up the stable repository for x86_64 / amd64
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
# Step 2.4 Update the apt package index.
sudo apt-get update
# Step 2.5 Install the latest version of Docker CE
sudo apt-get install docker-ce
# Step 2.6 Install the latest version for docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version

# --------------------------------------------------------------------------------
# Step 3. Create the user that will launch the dockers and run the uwsgi server
sudo adduser $EBIOKIT_USER
sudo usermod -aG docker $EBIOKIT_USER

# --------------------------------------------------------------------------------
# Step 4. Install eBioKit application
# Step 4.1 Get the latest version of the eBioKit application
# sudo mkdir /data
# sudo chown $USER:$USER .
cd /data/
git clone https://github.com/eBioKit/ebiokit-site.git
cd ebiokit-site/
git checkout minified
git clone https://github.com/fikipollo/PySiQ.git queue/
sudo ln -s /data/ebiokit-site/server $EBIOKIT_WWW_DIRECTORY/ebiokit
sudo ln -s /data/ebiokit-site/queue $EBIOKIT_WWW_DIRECTORY/queue
sudo chown -R $EBIOKIT_USER:$EBIOKIT_USER $EBIOKIT_WWW_DIRECTORY"/ebiokit"
sudo chown -R $EBIOKIT_USER:$EBIOKIT_USER $EBIOKIT_WWW_DIRECTORY"/queue"
# Step 4.2 Install python requirements
sudo pip install -r requirements.txt
# Step 4.3 Create the SECRET_KEY for the Django application at /etc/ebiokit_secretkey.txt
python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])' | sudo tee /etc/ebiokit_secretkey.txt
# Step 4.5 Initialize the database
cd server/
# Step 4.5.1 Erase the database
python manage.py flush
# Step 4.5.2 Prepare the database
python manage.py migrate
# Step 4.5.3 Fill the database with default values
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
cp config/default/uwsgi.ini /data/ebiokit-data/nginx/uwsgi.ini
cp config/default/queue_uwsgi.ini /data/ebiokit-data/nginx/queue_uwsgi.ini
sed 's#$${EBIOKIT_WWW_DIRECTORY}#'${EBIOKIT_WWW_DIRECTORY}'\/ebiokit#g' config/default/queue.cfg > $EBIOKIT_WWW_DIRECTORY/queue/server.cfg
sudo chown -R $EBIOKIT_USER:$EBIOKIT_USER /data/ebiokit-data/
sudo chown -R $EBIOKIT_USER:$EBIOKIT_USER /data/ebiokit-site/

# --------------------------------------------------------------------------------
# Step 5. Install docker requirements
sudo docker pull ebiokit/ultraextract

# --------------------------------------------------------------------------------
# Step 6. Configure Nginx to run as a reverse proxy and restart service
sudo service nginx stop
sudo cp config/default/nginx-default-server /etc/nginx/sites-enabled/default
sudo service nginx start
#sudo service nginx status

# --------------------------------------------------------------------------------
# Step 7. Launch UWSGI server
cd /data/ebiokit-data/nginx
sudo uwsgi --ini uwsgi.ini
# TO STOP USE sudo kill -9 `cat /tmp/ebiokit.pid`; sudo rm /tmp/ebiokit.*
sudo uwsgi --ini queue_uwsgi.ini
# TO STOP USE sudo kill -9 `cat /tmp/ebiokit_queue.pid`; sudo rm /tmp/ebiokit_queue.*

#TODO: RUN THE QUEUE
#TODO: CHANGE THE QUEUE FUNCTIONS LOCATION
