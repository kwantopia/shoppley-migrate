from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.conf import settings

from datetime import datetime, timedelta
from sorl.thumbnail import ImageField
from timezones.forms import PRETTY_TIMEZONE_CHOICES
from django.contrib.gis.geos import fromstr

import random

# Create your models here.
class Location(models.Model):
	location = models.PointField( )
	objects = models.GeoManager()

class Country(models.Model):
	name			= models.CharField(max_length=64)
	code			= models.CharField(max_length=10)

class Region(models.Model):
	name			= models.CharField(max_length=32)
	code			= models.CharField(max_length=10)
	country			= models.ForeignKey(Country)
	
	def __unicode__(self):
		return self.name

class City(models.Model):
	name			= models.CharField(max_length=32)
	region			= models.ForeignKey(Region)
	
	def __unicode__(self):
		return self.name

class ZipCode(models.Model):

	code			= models.CharField(max_length=32)
	city			= models.ForeignKey(City)

	latitude		= models.FloatField(blank=True, null=True)
	longitude		= models.FloatField(blank=True, null=True)

	def __unicode__(self):
		return "%s in %s"%(self.code, self.city.name)

	def citystate(self):
		return "%s, %s %s"%(self.city, self.city.region.code.upper(), self.code)


class Category(models.Model):
	name			= models.CharField(max_length=32)
	parent			= models.ForeignKey("self",null=True)
	tag			= models.CharField(max_length=32)
	def __unicode__(self):
		if self.parent:
			return "%s: %s" % (self.parent.name, self.name)
		else:
			return self.name


class ShoppleyUser(models.Model):
	user			= models.OneToOneField(User)
	address_1		= models.CharField(max_length=64, blank=True)
	address_2		= models.CharField(max_length=64, blank=True)
	zipcode			= models.ForeignKey(ZipCode, null=True, blank=True, on_delete=models.SET_NULL) # current zipcode
	# this phone should be used for merchants only ( this is the business phone number )
	# To support multiple numbers, create a ShoppleyPhone object for each manager's phone
	# Dont' use this for customers; instead create a ShoppleyPhone object for each customer. (shoppleyuser.phone will never be queried)
	phone			= models.CharField(max_length=20, blank=True) 
	categories		= models.ManyToManyField(Category, null=True, blank=True)
	balance			= models.IntegerField(default=0)

	#: set to False when customer issues #stop command
	active 			= models.BooleanField(default=True)
	#: verified by logging in when invited by friends
	verified		= models.BooleanField(default=False)
	timezone		= models.CharField(max_length=255, choices=PRETTY_TIMEZONE_CHOICES, blank=True, null=True )	
	location		= models.ForeignKey(Location, null=True, blank=True)
	is_fb_connected		= models.BooleanField(default=False)
	
	VERIFIED_YES = 0
	VERIFIED_NO = 1
	VERIFIED_PENDING = 2
	VERIFIED_CHOICES = (
			(VERIFIED_YES, 'Yes'),
			(VERIFIED_NO, 'No'),
		(VERIFIED_PENDING, 'Pending'),
	)
	verified_phone	= models.IntegerField(default=2, choices=VERIFIED_CHOICES)
	
	def is_customer(self):
		return hasattr(self, "customer")

	def is_merchant(self):
		return hasattr(self, "merchant")
	def print_name(self):
		splits = self.user.username.split("|")
		if len(splits)==3:
			return splits[2]
		else:
			return self.user.username

	def print_address(self):
		if self.address_1=="":
			return "No address given"
		else:
			return self.address_1 + "\n" + self.address_2
	def __unicode__(self):
		if self.is_customer():
			if self.user.get_full_name():
				return self.user.get_full_name()
			else:
				return self.user.username
		else:
			return "%s (%s)" % (self.merchant.business_name, self.user.username)

	def get_gmap_src (self, sizex= 256, sizey = 256):
		if self.location:
			return "http://maps.google.com/maps/api/staticmap?center=%(lat)s,%(lon)s&zoom=14&size=%(x)dx%(y)d&maptype=roadmap&markers=size:mid|color:red|%(lat)s,%(lon)s&sensor=false" % { "lat": self.location.location.y, "lon": self.location.location.x , "x": sizex, "y":sizey, }
		else:
			return "-1"

	def get_full_address(self):
		return self.address_1 + " "+ self.zipcode.city.name + " " + self.zipcode.city.region.name + " " + self.zipcode.code

	def get_zipcode_address(self):
		return self.zipcode.city.name + " " + self.zipcode.city.region.name + " " + self.zipcode.code

	def set_location_from_address(self, address = None):
		if not address:
			address =self.get_full_address()
		from shoppleyuser.utils import get_lat_long
		latlon = get_lat_long(address)
		#print address, latlon
		if latlon!=-1:
			#print self.location
			self.location = Location.objects.create(location=(fromstr("POINT(%s %s)" % (latlon[1], latlon[0]))))
			self.save()
			#print self.location
			return
		
		latlon = get_lat_long(self.get_zipcode_address())
		if latlon!=-1:
			self.location = Location.objects.create(location=(fromstr("POINT(%s %s)" % (latlon[1], latlon[0]))))
			self.save()
		
	def set_location_from_latlon(self, lat , lon):
		self.location = Location.objects.create(location=(fromstr("POINT(%s %s)" % (lon, lat))))
		self.save()

class Merchant(ShoppleyUser):
	business_name	= models.CharField(max_length=64, blank=True)
	admin			= models.CharField(max_length=64, blank=True)
	banner			= ImageField(upload_to="banners/", blank=True)
	url			= models.URLField(null=True, blank=True)
	yelp_url		= models.URLField(null=True, blank=True)
	fb_url			= models.URLField(null=True, blank=True)
	twitter_url		= models.URLField(null=True, blank=True)
	customer_data_file	= models.FileField(null=True, blank=True, upload_to="data")	

	def save(self, *args, **kwargs):
		if not self.pk:
			self.balance = settings.INIT_MERCHANT_BALANCE
		super(Merchant, self).save(*args, **kwargs)
		if self.zipcode:
			ZipCodeChange.objects.create(user=self,time_stamp=datetime.now(),zipcode=self.zipcode)

	def __unicode__(self):
		return "%s (%s [%s])" % (self.business_name, self.print_address(), self.phone)

	def get_data_file(self):
		if self.customer_data_file:
			return self.customer_data_file.url
		else:
			return None

	def get_banner(self):
		if self.banner:
			return self.banner.url
		else:
			return settings.DEFAULT_MERCHANT_BANNER_URL

	# return a list of pk's of customers within x miles from the merchant's lat/lon
	def get_customers_within_miles(self,x=5):
		from geopy.distance import distance as geopy_distance
		return [ i.pk for i in Customer.objects.all() if i.location and self.location and geopy_distance(i.location.location,self.location.location).mi<=x]

	def get_active_customers_miles(self, x=5, filter_pks=[]):
		from geopy.distance import distance as geopy_distance
		if len(filter_pks) > 0:
			return [ i.pk for i in Customer.objects.exclude(pk__in=filter_pks).filter(verified=True, active=True, offer_count=0) if i.location and self.location and geopy_distance(i.location.location,self.location.location).mi<=x]
		else:
			return [ i.pk for i in Customer.objects.filter(verified=True, active=True, offer_count=0) if i.location and self.location and geopy_distance(i.location.location,self.location.location).mi<=x]

	# faster than get_customers_within_miles().count() because dont have to create a new list
	def count_customers_within_miles(self, x=5):
		from geopy.distance import distance as geopy_distance

		count = 0
		for i in	Customer.objects.all():
			if i.location and self.location:
				if geopy_distance(i.location.location,self.location.location).mi<=x:
					count = count + 1
		return count
			
class Customer(ShoppleyUser):
	EVERY_HR = 0
	EVERY_TWO_HRS = 1
	THREE_PER_DAY = 2
	TWICE_A_DAY = 3
	ONCE_A_DAY = 4
	ONCE_A_WEEK = 5

	FREQUENCY_CHOICES = (
			( 0, 'Every Hour'),
			( 1, 'Every 2 hrs'),
			( 2, '3 times a day'),
			( 3, 'Twice a day'),
			( 4, 'Once a day'),
			( 5, 'Once a week'),
			)

	STOP_RECEIVE = 0
	ONE_TO_FIVE = 5
	UP_TO_TEN = 10
	UNLIMITED = 100000

	LIMIT_CHOICES= (
			( 0, 'None'),
			( 5, '1-5'),
			( 10, '6-10'),

			( 100000, 'Unlimited'),

			)

	frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=4)
	daily_limit = models.IntegerField(choices=LIMIT_CHOICES, default=5) # daily limit on num of offers
	offer_count = models.IntegerField(default=0) # track offer received each day
	weekdays_only = models.BooleanField(default=False)
	weekends_only = models.BooleanField(default=False)
	merchant_likes = models.ManyToManyField(Merchant, related_name="fans")
	merchant_dislikes = models.ManyToManyField(Merchant, related_name="antifans")
	customer_friends = models.ManyToManyField("self", related_name="friends")

	def print_daily_limit(self):
		if self.daily_limit==0:
			return "none"
		elif self.daily_limit==5:
			return "1-5"
		elif self.daily_limit==10:
			return "6-10"
		else:
			return "unlimited"

	def is_taking_offers(self):
		return self.offer_count < self.daily_limit

	def get_offers_within_miles(self,x=5):
		from offer.models import Offer
		from geopy.distance import distance as geopy_distance
		"""
		# for testing
		print "All offers: %d"%Offer.objects.all().count()
		for i in Offer.objects.all():
			print "Customer location:", self.location.location
			print "Merchant location:", i.merchant.location.location
			print "Distance:", geopy_distance(self.location.location, i.merchant.location.location).mi
		"""

		return [i for i in Offer.objects.filter(expired_time__gt=datetime.now()) if self.location and i.merchant.location and geopy_distance(self.location.location, i.merchant.location.location).mi<=x]

	def count_offers_within_miles (self, x=5):
		from offer.models import Offer
		from geopy.distance import distance as geopy_distance
		count = 0
		for i in Offer.objects.filter(expired_time__gt=datetime.now()):
			if self.location and i.merchant.location:
				if geopy_distance(self.location.location,i.merchant.location.location).mi<=x:
					count = count + 1
		return count 

				# return a list of pk's of merchants within x miles from the customer's lat/lon
	def get_merchants_within_miles(self,x=5):
		from geopy.distance import distance as geopy_distance
		#print self.address_1 + " " + self.zipcode.code, self.location.location.x, self.location.location.y
		#for i in Merchant.objects.all():
			#print i , i.location.location.x, i.location.location.y, geopy_distance(i.location.location,self.location.location).mi
		return [ i.pk for i in Merchant.objects.all() if i.location and self.location and geopy_distance(i.location.location,self.location.location).mi<=x]


	def count_merchants_within_miles(self, x=5):
		from geopy.distance import distance as geopy_distance
		count = 0
		for i in Merchant.objects.all() :
			if i.location and self.location:
				if geopy_distance(i.location.location,self.location.location).mi<=x:
					count = count + 1
		return count

	def print_daily_limit(self):
		if self.daily_limit == 100000:
			return "Unlimited"
		elif self.daily_limit == 0:
			return "none"
		elif self.daily_limit == 5:
			return "5"
		elif self.daily_limit == 10:
			return "10"
	def update_offer_count(self):
		self.offer_count=self.offer_count + 1
		self.save()
	
	def daily_reset(self):
		self.offer_count=0
		self.save()

	def save(self, *args, **kwargs):
		if not self.pk:
			self.balance = settings.INIT_CUSTOMER_BALANCE
		super(Customer, self).save(*args, **kwargs)
		if self.zipcode:
			ZipCodeChange.objects.create(user=self,time_stamp=datetime.now(),zipcode=self.zipcode)

class ShoppleyPhone(models.Model):
	number		= models.CharField(max_length=20, blank = True)

	def save(self, *args, **kwargs):
		from shoppleyuser.utils import parse_phone_number
		self.number = parse_phone_number(self.number)
		super(ShoppleyPhone, self).save(*args, **kwargs)
	def is_customerphone(self):
		return hasattr(self, "customerphone")

        def is_merchantphone(self):
		return hasattr(self, "merchantphone")

# separate merchant from customer's phones . 
# phone number used by shoppleyuser to start offers ...
class MerchantPhone (ShoppleyPhone):
	merchant		= models.ForeignKey(Merchant)

	def __unicode__(self):
		return "%s" % self.number

class CustomerPhone(ShoppleyPhone):
	customer		= models.OneToOneField(Customer)

	def __unicode__(self):
		return "%s" % self.number

class IWantRequest(models.Model):
	customer		= models.ForeignKey(Customer)
	time_stamp 		= models.DateTimeField()
	request			= models.TextField()
	processed = models.BooleanField()
	category = models.ForeignKey(Category, null=True)

	def __unicode__(self):
		return "%s, customer %s wants: %s" % (self.time_stamp, self.customer, self.request)

	def match_category(self):
		"""
			Analyzes the category and matches one
		"""

		# if an admin manually assigned category
		if self.category:
			return self.category

		categories = Category.objects.all()
		if categories.count() > 0:
			# TODO: need to come up with intelligent algorithm to category iwants
			match_cat = random.sample(categories, 1)
			self.category = match_cat[0]
			self.save()
		return None

class MerchantOfTheDay(models.Model):
	merchant		= models.ForeignKey(Merchant)
	date			= models.DateField()

	def __unicode__(self):
		return "%s - %s" % (self.date, self.merchant.business_name)

class ZipCodeChange(models.Model):
	zipcode			= models.ForeignKey(ZipCode) # current zipcode, the one a user just changed to
	user			= models.ForeignKey(ShoppleyUser)
	time_stamp		= models.DateTimeField()

	def __unicode__(self):
		return "%s, user %s switched his zipcode from %s to %s" % (self.time_stamp, self.user, self.user.zipcode, self.zipcode)


class YelpBusiness(models.Model):
	yelp_id		= models.CharField(max_length=300)
	in_shoppley	= models.BooleanField(default= False)
	#rating		= models.FloatField(default = 0)
	#vote_count	= models.IntegerField(default= 0)
	
	def __unicode__(self):
		return self.yelp_id
	def get_info(self):
		from common.yelp_search import business_request
		return business_request (id=self.yelp_id)

class BusinessVote(models.Model):
	customer        = models.ForeignKey(Customer)
	time_stamp      = models.DateTimeField()
	business        = models.ForeignKey(YelpBusiness)
	def __unicode__(self):
		return "%s, %s voted for %s", (self.time_stamp, self.customer,self.business,)
class TextMsg(models.Model):
	from_number 	= models.CharField(max_length=20, blank = True)
	text 		= models.CharField(max_length = 300, blank = True)
	STATUS		= ((0, "Not processed"),
			(1, "Processing"),
			(2, "Processed"))

	status		=	models.IntegerField(choices=STATUS, default=0)
	start_time 	= models.DateTimeField()
	end_time 	= models.DateTimeField(blank=True, null = True)
	def __unicode__(self):
		if self.status == 2:
			return "%s- %s: %s was processed at %s" % (self.start_time, self.from_number, self.text, self.end_time)
		else:
			return "%s- %s: %s -- %d" % (self.start_time, self.from_number,self.text, self.status)
