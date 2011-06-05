#!/bin/sh

PROAREA=/home
WORKON_HOME=/home/virtual
PROJECT_ROOT=$PROAREA/shoppley

# activate virtual environment
. $WORKON_HOME/shoppley-env/bin/activate

cd $PROJECT_ROOT
python manage.py check_sms >> $PROJECT_ROOT/log/check_sms.log 2>&1

