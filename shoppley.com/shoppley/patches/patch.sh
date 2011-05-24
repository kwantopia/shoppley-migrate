#!/bin/bash

X="$PWD"
# TODO: need to modify PINAX_HOME to the home of your pinax environment
PINAX_HOME=/home/pinax/shoppley-env
#PINAX_HOME=/Users/kwan/workspace/pinax/shoppley-env
cp profiles.patch $PINAX_HOME/lib/python2.7/site-packages/pinax/apps/profiles
cd $PINAX_HOME/lib/python2.7/site-packages/pinax/apps/profiles
patch urls.py < profiles.patch
cd $X

cp microblogging.patch $PINAX_HOME/lib/python2.7/site-packages/microblogging
cd $PINAX_HOME/lib/python2.7/site-packages/microblogging
patch urls.py < microblogging.patch
cd $X

cp account_openid_consumer.patch $PINAX_HOME/lib/python2.7/site-packages/pinax/apps/account
cd $PINAX_HOME/lib/python2.7/site-packages/pinax/apps/account
patch openid_consumer.py < account_openid_consumer.patch
cd $X


