#!/bin/bash

OLD_PWD=$(pwd)

# Copy the app code to a temporal location
rm -rf /tmp/ebiokit-site
echo "Copying the app code..."
rsync -ar ../../ebiokit-site/ /tmp/ebiokit-site
cd /tmp/ebiokit-site
echo "Copying the app code... DONE"

# Build client
cd client/
mkdir dist
echo "Compiling client application..."
~/Desktop/workspace/app_minifier/minify /tmp/ebiokit-site/client
mv /tmp/minified/client/* dist
echo "Compiling client application... DONE"

cd ../server/
echo "Compiling server application... "
# Disable the DEBUG mode
sed -i 's/DEBUG = True/DEBUG = False/' config/settings.py
# Collect the static files
python manage.py collectstatic
# Remove unused files
rm -r .idea
echo "Compiling server application... DONE"
