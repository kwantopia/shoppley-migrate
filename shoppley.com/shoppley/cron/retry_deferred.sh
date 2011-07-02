#!/bin/sh

PROAREA=/home/www/shoppley.com
#PROAREA=/home/www/webuy.mit.edu
WORKON_HOME=/home/virtual
PROJECT_ROOT=$PROAREA/shoppley

# activate virtual environment
. $WORKON_HOME/shoppley-env/bin/activate

cd $PROJECT_ROOT
python manage.py retry_deferred >> $PROJECT_ROOT/log/cron_retry.log 2>&1

