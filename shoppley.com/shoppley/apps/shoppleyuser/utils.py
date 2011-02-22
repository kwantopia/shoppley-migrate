from shoppleyuser.models import Country, Region, City, ZipCode, ShoppleyUser
import os, csv
from googlevoice import Voice

FILE_ROOT = os.path.abspath(os.path.dirname(__file__))

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

def sms_notify(number, text):
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
	try:
		su = ShoppleyUser.objects.get(phone=cleaned_phone)
		# What's returned is a ShoppleyUser, not a User
		return su
	except Exception, e:
		return None
	
