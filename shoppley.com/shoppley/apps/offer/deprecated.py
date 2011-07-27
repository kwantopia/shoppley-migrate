	# distribute within x-mile radius from the merchant
	def distribute_deprecated(self, radius = 5):
		"""
			identify all customers that this offer should go to
			Generate messages, and send messages to them

			Send out offers by generating offer codes

			This should be ideally an asynchronous process
			
			Need to select the users that it will send out to

			- first check for users that are following the merchant
			- then select some extra people that are not following, who
			have not black listed the merchant
			- report back the number of customers being reached
			
		"""
		
		self.is_processing = True
		self.save()
		enough_points = True 
		
		t = TxtTemplates()

		#print "Sending out offers"

		# 70 percent of old customers, 30 percent of new
		max_offers = self.max_offers
		existing_num = int(round(0.7*max_offers))

		merchant = self.merchant
		
		nearby_customers = self.merchant.get_customers_within_miles(radius)
		fans = merchant.fans.filter(pk__in=nearby_customers, verified_phone=0).exclude(active=False).exclude(verified=False).order_by('?').values_list('pk', flat=True)
		antifans = merchant.antifans.all().values_list('pk', flat=True)
		# TODO: geographically filter
		
		nonfans = Customer.objects.filter(pk__in=nearby_customers, verified_phone=0).exclude(active=False).exclude(verified=False).exclude(pk__in=fans).exclude(pk__in=antifans).values_list('pk',flat=True)
		#nonfans = Customer.objects.exclude(active=False).exclude(verified=False).exclude(pk__in=fans).exclude(pk__in=antifans).filter(zipcode=merchant.zipcode).values_list('pk', flat=True)

		print "Num fans:",fans.count()
		print "Num nonfans:",nonfans.count()
		fan_target = set(list(fans))
		nonfan_target = set(list(nonfans))	
		target = fan_target | nonfan_target
		if len(target) > max_offers:
			target_list = random.sample(target, max_offers)
		else:
			target_list = list(target)

		from worldbank.models import Transaction

		allowed_number =int( self.merchant.balance/abs(Transaction.points_table["MOD"]))
		#print "balance=" ,self.merchant.balance
		#print "allowed_number", allowed_number
		if allowed_number == 0:
			# check if there's enough balance
			enough_points = False

		if len(target_list) > allowed_number:
			target_list = random.sample(target_list, allowed_number)
		sentto = self.gen_offer_codes(Customer.objects.filter(pk__in=target_list))	
		#print "count=" , self.offercode_set.all().count()
		for o in self.offercode_set.all():
			offer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["OFFER_RECEIVED"],{ "merchant":self.merchant.business_name, "title":self.title, "code":o.code })		
			sms_notify(o.customer.phone, offer_msg, SMS_DEBUG)
			transaction = Transaction.objects.create(time_stamp=datetime.now(),
							offer = self,
							offercode = o,
							dst = self.merchant,
							ttype = "MOD")
			transaction.execute()

		self.num_init_sentto =sentto
		self.is_processing = False
		self.expired_time = self.starting_time + timedelta(minutes=self.duration)
		self.save()

	

		
		if enough_points: 
			# number of people sent to, it can be 0 
			return self.num_init_sentto
		else:
			# not enough points to send to
			return -2
			


	def redistribute_deprecated(self,radius=5):
		self.redistribute_processing=True
		self.save()

		if not self.redistributable:
			# already redistributed, so not allowed any more
			self.redistribute_processing= False
			self.save()
			return -3

		"""
			Offer can be redistributed multiple number of times and all the parameters would be the
			same except extending the duration.

			Need to find targets that have not been reached at all and also have not gone over quota
		"""
		#self.num_resent_to += 5
		#self.save() 
		#print "balance before redist=", self.merchant.balance
		t= TxtTemplates()
		enough_points = True 
		max_resent = 50 - self.num_init_sentto - self.num_resent_to

		# 70 percent of old customers, 30 percent of new

		existing_num = int(round(0.7*max_resent))

		merchant = self.merchant
		
		old_offercodes = self.offercode_set.all()

		# send extension message to old customers
		for oc in old_offercodes:
			#print "before reset" , pretty_datetime(oc.expiration_time), " duration=", self.duration
			oc.expiration_time = datetime.now() + timedelta(minutes=self.duration)
			#print "time added" , datetime.now() + timedelta(minutes=self.duration)
			oc.save()
			
			#print "set expiration to " , pretty_datetime(oc.expiration_time)
			offer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["REOFFER_EXTENSION"],{
						"code": oc.code,
						"title": self.title,
						"merchant": self.merchant.business_name,
						"address": self.merchant.print_address(),
						"expiration": pretty_datetime(oc.expiration_time),})
			sms_notify(oc.customer.phone, offer_msg, SMS_DEBUG)


		# customers who have received the offers
		old_pks = old_offercodes.values_list('customer',flat=True)
		#print "old_pks", old_pks
		nearby_customers = self.merchant.get_customers_within_miles(radius)
		fans = merchant.fans.filter(pk__in=nearby_customers, verified_phone=0).exclude(active=False).exclude(verified=False).exclude(pk__in=old_pks).order_by('?').values_list('pk', flat=True)
		#fans = merchant.fans.exclude(active=False).exclude(verified=False).exclude(pk__in=old_pks).order_by('?').values_list('pk', flat=True)
		antifans = merchant.antifans.all().values_list('pk', flat=True)

		# TODO: geographically filter
		nonfans = Customer.objects.filter(pk__in=nearby_customers, verified_phone=0).exclude(active=False).exclude(verified=False).exclude(pk__in=fans).exclude(pk__in=antifans).exclude(pk__in=old_pks).filter(zipcode=merchant.zipcode).values_list('pk', flat=True)

		#print "Num fans:",fans.count()
		#print "Num nonfans:",nonfans.count()
		fan_target = set(list(fans))
		nonfan_target = set(list(nonfans))	
		target = fan_target | nonfan_target
		#print "target: ", target
		if len(target) > max_resent:
			target_list = random.sample(target, max_resent)
		else:
			target_list = list(target)
		#print "target_list: ", target_list
		from worldbank.models import Transaction

		allowed_number =int( self.merchant.balance/abs(Transaction.points_table["MOD"]))
		#print "balance=" ,self.merchant.balance
		#print "allowed_number", allowed_number
		if allowed_number == 0:
			# check if there's enough balance
			enough_points = False

		if len(target_list) > allowed_number:
			target_list = random.sample(target_list, allowed_number)
		resentto = self.gen_offer_codes(Customer.objects.filter(pk__in=target_list))	
		#print "final target_list: ", target_list
		for oc in self.offercode_set.filter(customer__pk__in=target_list):
			oc.expiration_time = datetime.now() + timedelta(minutes=self.duration)
			oc.save()
			offer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["REOFFER_NEWCUSTOMER_RECEIVED"],{ "merchant":self.merchant.business_name, "title":self.title, "code":oc.code })
			
			sms_notify(oc.customer.phone, offer_msg, SMS_DEBUG)
			transaction = Transaction.objects.create(time_stamp=datetime.now(),
							offer = self,
							offercode = oc,
							dst = self.merchant,
							ttype = "MOD")
			transaction.execute()
		
		self.num_resent_to = resentto
		self.redistribute_processing = False
		self.save()
		
		#print "balance after redist=", self.merchant.balance

		# make redistributable false even if the merchant does not have enough
		# points to redistribute.  If the merchant refills more points, they
		# will be able to start new offers instead of being able to redistribute
		# just so they don't keep on trying to redistribute when they don't have
		# enough points and throttle our server.
		self.redistributable = False 
		self.expired_time = datetime.now() + timedelta(minutes=self.duration)
		self.save()

		if enough_points: 
			# number of people sent to, it can be 0 

			self.save()
			return self.num_resent_to

		else:
			# not enough points to send to
			return -2
		return -2

