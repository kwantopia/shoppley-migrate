#!/bin/sh

PROAREA=/home/www/shoppley.com
WORKON_HOME=/home/pinax
PROJECT_ROOT=$PROAREA/shoppley

# activate virtual environment
. $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py emit_notices >> $PROJECT_ROOT/log/cron_notices.log 2>&1

