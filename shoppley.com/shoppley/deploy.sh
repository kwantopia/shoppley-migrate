#!/bin/bash

# Script to setup the production server

SHOPPLEY_HOME=/home/www/shoppley.com/shoppley

source /home/virtual/shoppley-env/bin/activate
cd $SHOPPLEY_HOME 

cp patches/facebox.prod.patch $SHOPPLEY_HOME/packages/facebox
cd $SHOPPLEY_HOME/packages/facebox
patch -p0 < facebox.prod.patch

cd $SHOPPLEY_HOME/apps/googlevoice
cp gvoice.production gvoice

cd $SHOPPLEY_HOME

python manage.py collectstatic
