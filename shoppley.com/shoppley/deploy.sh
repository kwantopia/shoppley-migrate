#!/bin/bash

source /home/virtual/shoppley-env/bin/activate
cd /home/www/shoppley.com/shoppley
python manage.py collectstatic
