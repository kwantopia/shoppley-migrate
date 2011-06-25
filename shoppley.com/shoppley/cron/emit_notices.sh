#!/bin/sh


PROAREA=/home/www/webuy.mit.edu
WORKON_HOME=/home/virtual
PROJECT_ROOT=$PROAREA/shoppley

# activate virtual environment
. $WORKON_HOME/shoppley-env/bin/activate

cd $PROJECT_ROOT
python manage.py emit_notices >> $PROJECT_ROOT/log/cron_notices.log 2>&1

