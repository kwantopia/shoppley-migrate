#!/bin/bash

X="$PWD"
PINAX_HOME=/home/pinax
cp profiles.patch $PINAX_HOME/pinax-env/lib/python2.6/site-packages/pinax/apps/profiles
cd $PINAX_HOME/pinax-env/lib/python2.6/site-packages/pinax/apps/profiles
patch urls.py < profiles.patch
cd $X

cp microblogging.patch $PINAX_HOME/pinax-env/lib/python2.6/site-packages/microblogging
cd $PINAX_HOME/pinax-env/lib/python2.6/site-packages/microblogging
patch urls.py < microblogging.patch
cd $X


