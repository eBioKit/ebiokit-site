#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

echo "Upgrading application code"
git pull origin minified

echo "Enabling virtualenv at $DIR"
virtualenv .env
source .env/bin/activate

echo "Installing requirements"
pip install -r requirements.txt

echo "Upgrading database"
cd server/
python manage.py makemigrations
python manage.py migrate
