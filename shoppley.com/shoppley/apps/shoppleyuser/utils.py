from shoppleyuser.models import Country, Region, City, ZipCode, ShoppleyUser, CustomerPhone, MerchantPhone

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.conf import settings

import os, csv
from googlevoice import Voice
import sys
import urllib


FILE_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_lat_long(location):
	key = settings.GOOGLE_API_KEY
	output= "csv"
	location = urllib.quote_plus(location)
	request = "http://maps.google.com/maps/geo?q=%s&output=%s&key=%s" % (location, output, key)
	data = urllib.urlopen(request).read()
	dlist = data.split(',')
	if dlist[0]=='200':
		return [dlist[2],dlist[3]]
	else:
		return -1

def pretty_date(time=False, future=True):
	"""
	Get a datetime object or a int() Epoch timestamp and return a
	pretty string like 'an hour ago', 'Yesterday', '3 months ago',
	'just now', etc
	"""

	if not future:	
		suffix = " ago"
	else:
		suffix = ""
	from datetime import datetime, timedelta
	now = datetime.now()
	if type(time) is int:
		diff = now - datetime.fromtimestamp(time)
	elif isinstance(time,datetime):
		#diff = now - time 
		diff = time - now
	elif isinstance(time,timedelta):
		diff = time
	elif not time:
		diff = now - now
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return "Expired" 

	if day_diff == 0:
		if second_diff < 0:
			return "Expired"
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return str(second_diff) + " seconds" + suffix
		if second_diff < 120:
			return  "a minute" + suffix
		if second_diff < 3600:
			return str( second_diff / 60 ) + " minutes" + suffix
		if second_diff < 7200:
			return "an hour" + suffix
		if second_diff < 86400:
			return str( second_diff / 3600 ) + " hours" + suffix
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(day_diff) + " days" + suffix
	if day_diff < 31:
		days = day_diff/7
		if days == 1:
			return str(days) + " week" + suffix
		else:
			return str(days) + " weeks" + suffix
	if day_diff < 365:
		months = day_diff/30
		if months == 1:
			return str(months) + " month" + suffix
		else:
			return str(months) + " months" + suffix
	else:
		years = day_diff/365
		if years == 1:
			return str(years) + " year" + suffix
		else:
			return str(years) + " years" + suffix

def load_zipcodes():
	f = open(FILE_ROOT+"/data/US.txt", "r")
	zip_reader = csv.reader(f, delimiter="\t")
	for row in zip_reader:
		country_obj, created = Country.objects.get_or_create(name="United States", code=row[0])			
		zip_code = row[1]
		city = row[2] 
		region = row[3]
		region_code = row[4]
		latitude = row[9]
		longitude = row[10]
		region_obj, created = Region.objects.get_or_create(name=region, 
				code=region_code, country=country_obj)			
		city_obj, created = City.objects.get_or_create(name=city, region=region_obj)					
		zip_obj, created = ZipCode.objects.get_or_create(code=zip_code, 
				city=city_obj, latitude=latitude, longitude=longitude)

def sms_notify(number, text, debug=settings.SMS_DEBUG):
	if debug:
		print _("TXT: \"%(msg)s\" sent to %(phone)s") % {"msg":text, "phone":number,}
	else:
		voice = Voice()
		voice.login()
		voice.send_sms(number, text) 
		
def sms_notify_list(number_list, text):
	voice = Voice()
	voice.login() 
	for number in number_list:
		voice.send_sms(number, text)

def parse_phone_number(raw_number, country_code="US"):

	cleaned_number = filter(lambda x: x.isdigit(), raw_number)
	if country_code == "US":
		if len(cleaned_number) >= 10:
			return cleaned_number[-10:]
	return cleaned_number

def map_phone_to_user(raw_number):
	cleaned_phone = parse_phone_number(raw_number)
	if CustomerPhone.objects.filter(number=cleaned_phone).exists():
		return CustomerPhone.objects.get(number=cleaned_phone).customer
	if MerchantPhone.objects.filter(number=cleaned_phone).exists():
		return MerchantPhone.objects.get(number=cleaned_phone).merchant
	return None
#	try:
#		su = ShoppleyUser.objects.filter(phone=cleaned_phone)[0]
		# What's returned is a ShoppleyUser, not a User
#		return su
#	except Exception, e:
#		return None

