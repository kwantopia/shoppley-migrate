#!/bin/bash

source /home/pinax/pinax-env/bin/activate
cd /home/www/shoppley.com/shoppley
rm -rf site_media
python manage.py build_media --all --interactive 
cd site_media/static/css/
ln -s ../../../packages/blueprint-css/blueprint
