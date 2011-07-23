from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.conf import settings

from datetime import datetime, timedelta
from sorl.thumbnail import ImageField
from timezones.forms import PRETTY_TIMEZONE_CHOICES
from django.contrib.gis.geos import fromstr


# Create your models here.
class Location(models.Model):
	location = models.PointField( )
	objects = models.GeoManager()
#				name2= models.CharField(max_length=5)
#				name = models.CharField(max_length=3)
#				users = models.ManyToManyField(User,related_name="user_locations")

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
	#zipcode												= models.ForeignKey(ZipCode, blank=True)
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
	verified_phone	= models.IntegerField(default=VERIFIED_PENDING, choices=VERIFIED_CHOICES)
	
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
			self.location = Location.objects.create(location=(fromstr("POINT(%s %s)" % (latlon[0], latlon[1]))))
			self.save()
			return
		
		latlon = get_lat_long(self.get_zipcode_address())
		if latlon!=-1:
			self.location = Location.objects.create(location=(fromstr("POINT(%s %s)" % (latlon[0], latlon[1]))))
			self.save()
		
	def set_location_from_latlon(self,lat , lon):
		self.location = Location.objects.create(location=(fromstr("POINT(%s %s)" % (lat,lon))))
		self.save()



class Merchant(ShoppleyUser):
	business_name	= models.CharField(max_length=64, blank=True)
	admin			= models.CharField(max_length=64, blank=True)
	banner			= ImageField(upload_to="banners/", blank=True)
	url				= models.URLField(null=True, blank=True)

	
	def save(self, *args, **kwargs):
		if not self.pk:
			self.balance = settings.INIT_MERCHANT_BALANCE
			super(Merchant, self).save(*args, **kwargs)
		ZipCodeChange.objects.create(user=self,time_stamp=datetime.now(),zipcode=self.zipcode)

	def __unicode__(self):
#		return "%s (%s %s)" % (self.business_name, self.user.username,self.phone)
		return "%s, %s [%s]" % (self.business_name, self.print_address(), self.phone)

	def get_banner(self):
		if self.banner:
			return self.banner.url
		else:
			return settings.DEFAULT_MERCHANT_BANNER_URL

	# return a list of pk's of customers within x miles from the merchant's lat/lon
	def get_customers_within_miles(self,x=5):
		from geopy.distance import distance as geopy_distance
		#print self.address_1 + " " + self.zipcode.code, self.location.location.x, self.location.location.y
		#for i in Customer.objects.all():
			#print i , i.location.location.x, i.location.location.y, geopy_distance(i.location.location,self.location.location).mi
		return [ i.pk for i in Customer.objects.all() if i.location and self.location and geopy_distance(i.location.location,self.location.location).mi<=x]

	def get_active_customers_miles(self, x=5):
		from geopy.distance import distance as geopy_distance
		#print self.address_1 + " " + self.zipcode.code, self.location.location.x, self.location.location.y
		#for i in Customer.objects.all():
			#print i , i.location.location.x, i.location.location.y, geopy_distance(i.location.location,self.location.location).mi
		return [ i.pk for i in Customer.objects.filter(active=True, offer_count=0) if i.location and self.location and geopy_distance(i.location.location,self.location.location).mi<=x]

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
		#for i in Offer.objects.all():
			#print geopy_distance(self.location.location,i.merchant.location.location).mi

		return [i for i in Offer.objects.all() if self.location and i.merchant.location and geopy_distance(self.location.location,i.merchant.location.location).mi<=x]

	def count_offers_within_miles (self, x=5):
		from offer.models import Offer
		from geopy.distance import distance as geopy_distance
		count = 0
		for i in Offer.objects.all():
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

#class Vote(models.Model):
#				customer								= models.ForeignKey(Customer)
#	from offer.models import Offer
#				offer							 = models.ForeignKey(Offer)
#				VOTE_CHOICES = (
#								(1, "yay"),
#								(-1,"nay"),
#								(0, "pending"),
#				)
#				vote										= models.IntegerField(default=0, choices = VOTE_CHOICES)

#			 def __unicode__(self):
#								return "%s: %s -> %s" % (self.vote, self.customer, self.offer)


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
			self.category = match_cat
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



#capture relationship between users
#class Relationship(models.Model):
#	types=(
#		(0,"Friend forwarding offer"),
#		)
#	rtype = models.IntegerField(choices=types,default=0)
#	user1 = models.ForeignField(ShoppleyUser,related_name="relationship_user1")
#	user2 = models.ForeignField(ShoppleyUser,related_name="relationship_user2")
#	offer = models.ManyToManyField(Offer)

#	def __unicode__(self):
#		if self.rtype=0:
#			return "%s forwarded offers to %s" % self.user1, self.user2


###############
# FOR BETA
##############
class BetaUser(models.Model):
	email			= models.CharField(max_length=64) # must have
	address_1		= models.CharField(max_length=64, blank=True)
	address_2		= models.CharField(max_length=64, blank=True)
	zipcode			= models.ForeignKey(ZipCode)
	phone			= models.CharField(max_length=20, blank=True)
	categories		= models.ManyToManyField(Category, null=True, blank=True)

	def is_betacustomer(self):
		return hasattr(self, "betacustomer")

	def is_betamerchant(self):
		return hasattr(self, "betamerchant")

	def print_address(self):
		if self.address_1=="":
			return "No address given"
		else:
			return self.address_1 + "\n" + self.address_2
	def __unicode__(self):
		if self.is_customer():
			return self.email
		else:
			return "%s (%s)" % (self.merchant.business_name, self.email)

class BetaCustomer(BetaUser):
	pass


class BetaMerchant(BetaUser):
	business_name	= models.CharField(max_length=64, blank=True)
	url				= models.URLField(null=True, blank=True)
	def __unicode__(self):
		return "%s (%s %s)" % (self.business_name,self.email)

