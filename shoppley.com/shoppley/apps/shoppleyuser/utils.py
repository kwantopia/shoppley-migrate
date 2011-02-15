from shoppleyuser.models import Country, Region, City, ZipCode
import os, csv

FILE_ROOT = os.path.abspath(os.path.dirname(__file__))

def load_zipcodes():
	f = open(FILE_ROOT+"/data/US.txt", "r")
	zip_reader = csv.reader(f, delimiter="\t")
	for row in zip_reader:
		country_obj, created = Country.objects.get_or_create(name="United States", code=row[0])			
		region = row[3]
		region_code = row[4]
		city = row[2] 
		zip_code = row[1]
		region_obj, created = Region.objects.get_or_create(name=region, code=region_code, country=country_obj)			
		city_obj, created = City.objects.get_or_create(name=city, region=region_obj)					
		zip_obj, created = ZipCode.objects.get_or_create(code=zip_code, city=city_obj)	  
