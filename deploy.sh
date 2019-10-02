#!/bin/bash

echo "Please type the new version number."
echo "Check latest version here: https://github.com/eBioKit/ebiokit-site/releases"
version=$(date +"%y.%m")
read -p "New version (e.g. ${version}):" VERSION

if [[ "$VERSION" == "" ]]; then
  echo "Version number not specified. Using ${version}"
  VERSION=${version}
fi

OLD_PWD=$(pwd)

# Copy the app code to a temporal location
rm -rf /tmp/ebiokit-site
echo "Copying the app code..."
rsync -ar ../ebiokit-site/ /tmp/ebiokit-site
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
echo "Updating version number"
sed -i 's/APP_VERSION = [0-9\.]*/APP_VERSION = '$VERSION'/' config/settings.py
echo "eBioKit $VERSION" > ../VERSION

echo "Compiling server application... "
# Disable the DEBUG mode
sed -i 's/DEBUG = True/DEBUG = False/' config/settings.py
# Collect the static files
python manage.py collectstatic
# Remove unused files
rm -r .idea
cd ..
rm -r client/
rm -r docs/
rm -r .env/
echo "Compiling server application... DONE"

echo ""
echo ""
echo "DONE! Now you could send the changes as a new release. "
echo "For example:"
echo "cd /tmp/ebiokit-site/"
echo "git push origin :minified"
echo "git branch -d minified"
echo "git checkout -b minified"
echo "git add -A"
echo "git commit -m \"Minified (v`cat VERSION | cut -d' ' -f2`)\""
echo "git push origin minified"
echo ""
echo "Run server with uwsgi --ini uwsgi.ini"
