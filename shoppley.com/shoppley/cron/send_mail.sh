#!/bin/sh

# TODO: adjust paths for production and crontab should indicate how often sms's are checked
PROAREA=/home/www/shoppley.com
WORKON_HOME=/home/pinax
PROJECT_ROOT=$PROAREA/shoppley

# activate virtual environment
. $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
# TODO: makes sure you have write access to cron_mail.log
python manage.py send_mail >> $PROJECT_ROOT/log/cron_mail.log 2>&1
