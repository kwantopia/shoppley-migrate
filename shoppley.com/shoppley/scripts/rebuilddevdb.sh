su -m postgres -c "dropdb flashon"
su -m postgres -c "createdb flashon -T template_postgis -E unicode -O flashon"
python manage.py syncdb
python manage.py test_offer_mobile
