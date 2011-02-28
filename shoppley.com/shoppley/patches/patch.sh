#!/bin/bash

X="$PWD"
cp profiles.patch ../pinax/pinax-env/lib/python2.6/site-packages/pinax/apps/profiles
cd ../pinax/pinax-env/lib/python2.6/site-packages/pinax/apps/profiles
patch urls.py < profiles.patch
cd $X

cp microblogging.patch ../pinax/pinax-env/lib/python2.6/site-packages/microblogging
cd ../pinax/pinax-env/lib/python2.6/site-packages/microblogging
patch urls.py < microblogging.patch
cd $X


