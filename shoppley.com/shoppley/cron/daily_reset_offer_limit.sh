#!/bin/sh

PROAREA=/home/smengl
WORKON_HOME=/home/virtual
PROJECT_ROOT=$PROAREA/Workspace/startup/shoppley

# activate virtual environment
. $WORKON_HOME/shoppley-env/bin/activate

cd $PROJECT_ROOT
python manage.py daily_reset_offer_limit >> $PROJECT_ROOT/log/daily_reset.log 2>&1

