#!/bin/sh

sudo /etc/init.d/nginx restart
sudo /etc/init.d/apache2 restart
sudo /etc/init.d/celeryd restart
sudo /etc/init.d/celerybeat restart
