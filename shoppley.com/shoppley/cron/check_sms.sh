#!/bin/sh

PROAREA=/home/www/webuy.mit.edu
WORKON_HOME=/home/virtual
PROJECT_ROOT=$PROAREA/shoppley

# activate virtual environment
. $WORKON_HOME/shoppley-env/bin/activate

cd $PROJECT_ROOT
mkdir check_sms
python manage.py check_sms >> $PROJECT_ROOT/log/check_sms.log 2>&1

