#!/bin/bash

# patching git projects: http://tamsler.blogspot.com/2009/02/patching-with-git-diff.html

X="$PWD"

# dev server
SHOPPLEY_HOME=/home/www/webuy-dev.mit.edu/shoppley
# deployment
SHOPPLEY_HOME=/home/www/shoppley.com/shoppley
# local
#SHOPPLEY_HOME=$HOME/workspace/shoppley

# TODO: need to modify PINAX_HOME to the home of your pinax environment
PINAX_HOME=/home/virtual/shoppley-env
#PINAX_HOME=$HOME/Documents/virtual/shoppley-env
#PINAX_HOME=$HOME/workspace/virtual/shoppley-env
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

cd ../packages
./download.sh
cd $X
cp facebox.patch $SHOPPLEY_HOME/packages/facebox
cd $SHOPPLEY_HOME/packages/facebox
patch -p0 < facebox.patch
