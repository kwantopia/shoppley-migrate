from django.core.management.base import NoArgsCommand,CommandError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress

from shoppleyuser.utils import sms_notify, parse_phone_number,map_phone_to_user
from shoppleyuser.models import ZipCode, Customer, Merchant, ShoppleyUser, ZipCodeChange
from offer.models import Offer, ForwardState, OfferCode, OfferCodeAbnormal, TrackingCode
from offer.utils import gen_offer_code, validateEmail, gen_random_pw, pluralize, pretty_datetime
from worldbank.models import Transaction
from googlevoice import Voice
from googlevoice.util import input
from googlevoice.extractsms import extractsms
from pyparsing import *
from random import choice
from datetime import datetime
import re
import string

pattern = "([\w]{%d})[ ]+\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})" % (settings.OFFER_CODE_LENGTH)
redemption_code_re = re.compile(pattern)

# Pattern used to parse text 
customer_pattern = "#" + Word(alphas+"_") + ZeroOrMore(Word(alphanums+"!@#$%^&*()_+=-`~,./<>?:;\'\"{}[]\\|"))
merchant_pattern = customer_pattern
DEFAULT_SHOPPLEY_NUM="508-690-0888"
# Customer commands:
BALANCE= "balance"
INFO = "info"
STOP = "stop"
START = "start"
FORWARD = "forward"

# Merchant commands:
REDEEM = "redeem"
OFFER = "offer"
STATUS = "status"

# others
SIGNUP = "signup"
MERCHANT_SIGNUP = "merchant"
HELP = "help"
ZIPCODE = ["zip", "zipcode"]
class Command(NoArgsCommand):
	help = "Check Google Voice inbox for posted offers from merchants"
	DEBUG = False
	def notify(self, phone, msg):
		if self.DEBUG:
			print _("\"%(msg)s\" sent to %(phone)s") % {"msg":msg, "phone":phone,}
		else:
			sms_notify(phone,msg)


	def info(self, offercode):

			return _("Redeem [%(offercode)s] at %(merchant)s \"%(description)s\" [expires: %(expiration)s]") %{
								"offercode": offercode.code,
								"description": offercode.offer.description,
								"merchant": offercode.offer.merchant,
								"expiration": pretty_datetime(offercode.expiration_time) ,
						}
			#return _("[%(code)s]\nmerchant: %(merchant)s; \nexpiration: %(expiration)s; \ndescription: %(description)s;\naddress: %(address)s") %{
		#						"code" : (offercode.code) ,
		#						"merchant" : offercode.offer.merchant,
			#					"expiration":pretty_datetime(offercode.expiration_time)	,
			#					"description":offercode.offer.description ,
			#					"address":offercode.offer.merchant.print_address(),
			#				}

	def forward_info(self, offercode):

			return _("%(merchant)s \"%(description)s\" [expires: %(expiration)s]") %{
								"description": offercode.offer.description,
								"merchant": offercode.offer.merchant,
								"expires": pretty_datetime(offercode.expiration_time) ,
						}

	def update_expired(self):
		
		expired_offers = [x for x in Offer.objects.all() if not x.is_active() and not x.is_merchant_txted]
		for offer in expired_offers:
			offer.is_merchant_txted=True
			offer.save()
			sentto = offer.num_init_sentto
			forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
			redeem = offer.offercode_set.filter(redeem_time__isnull=False).count()
			merchant_msg = _("%(offer)s expired [sent to %(sentto)d] [forwarded %(forwarded)d] [redeemed %(redeem)d]") %{ "offer": offer,"sentto":sentto,"forwarded":forwarded,"redeem":redeem,}
			self.notify(offer.merchant.phone,merchant_msg)
		return len(expired_offers)

	def customer_help(self):
		avail_commands = "- #info offercode(s): list information about an offercode or offercodes separated by spaces\n- #forward offercode number(s): forward an offer to your friend(s) separated by spaces\n-#zip new_zipcode: change to a new zipcode (only support 02139 02142)\n-#stop: stop receiving messages from us\n- #start: restart receiving messages from us\n- #help: list available commands\n- #balance: check point balance"
		return avail_commands

	def merchant_help(self):
		avail_commands = "- #redeem offercode number: redeem a customer's offercode\n- #offer description: start an offer with its description.\n-#zip new_zipcode: change to a new zipcode (only support 02139 02142)- #status trackingcode: check the status of an offer you started\n- #balance: check point balance"
		return avail_commands
		
	def check_email(self,email,phone):
		try:
			if not validateEmail(email):
				receipt_msg= _('"%s" is not a valid email address. Please provide a new and valid email')%email
				raise CommandError("Invalid email address")			
			user = User.objects.get(username__iexact =email)
			receipt_msg = _('"%s" is already registered with us. Please provide another email.') % email
			self.notify(phone,receipt_msg)
			raise CommandError("Email was already used")
		except User.DoesNotExist:
			return email
		
		### raise user already exist error
	def check_zipcode(self,code,phone):
		try:
			zipcode= ZipCode.objects.get(code=code)
			return code
		except ZipCode.DoesNotExist:
			receipt_msg = _('Zipcode "%s" does not exist. Please provide a correct zipcode.') % code
			self.notify(phone,receipt_msg)
			raise CommandError("Zipcode does not exist")

	def check_phone(self,phone):
		try:
			phone = parse_phone_number(phone)
			print phone			
			customer = ShoppleyUser.objects.get(phone__icontains=phone)
			receipt_msg=_('"%s" is already registered with us. You can now use our services.') % phone
			self.notify(phone,receipt_msg)
			raise CommandError("Phone number was already used")
		except ShoppleyUser.DoesNotExist:
			return phone
	
	def check_offercode(self,code,phone):
		try:
			code = code.lower()
			offercode = OfferCode.objects.get(code__iexact = code)
			return offercode
		except OfferCode.DoesNotExist:
			receipt_msg = _("Offercode %s does not exist.")% code
			self.notify(phone,receipt_msg)
			OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV",invalid_code=code).save()
			raise CommandError("Offercode does not exist")

	def test_handle(self,msg): # take msg: dict("from":phonenumber, "text":text)
		print "new message %s" % msg
		msg["from"] = parse_phone_number(msg["from"])
		if msg["from"] != "Me":
			su = map_phone_to_user(msg["from"])

			# ****************************** MERCHANT COMMANDS ***********************
			if su and su.is_merchant():
				text = msg["text"].strip()
				try:
					parsed = merchant_pattern.parseString(text)
				
					# offer code being redeemed by the customer
					# merchant sends offer code and the customer's phone number
					del parsed[0]
					# --------------------------- BALANCE: "balance"---------------
					if parsed[0].lower()==BALANCE:
						receipt_msg = _("You have %d points.") % su.balance
						self.notify(su.phone, receipt_msg)

					# --------------------------- REDEEM: "redeem<SPACE>offercode<SPACE>phone number here"---------------
					elif parsed[0].lower()==REDEEM:
						offer_code = self.check_offercode(parsed[1],su.phone)
						phone = parse_phone_number(parsed[2])
						if offer_code.offer.merchant != su.merchant:
							receipt_msg = _("Redeem Fail! %s was initiated by a different business, and not by you.") % offer_code.code
							self.notify(su.phone,receipt_msg)
							raise CommandError ("Merchant attempts to redeem an offer he does not own")
						phone = parse_phone_number(parsed[2])
						try:
							current_time = datetime.now()
							#print "total =" , OfferCode.objects.filter(code__iexact=offer_code.code)
							offercode_obj = OfferCode.objects.filter(expiration_time__gt=current_time, 
								time_stamp__lt=current_time).get(code__iexact=offer_code.code)
							# The offer code is a valid code, but it might come from referrals
							try:
								# Does the phone belong to a registered customer?
								customer = Customer.objects.get(phone__contains=phone)
								if offercode_obj.customer == customer:
									if not offercode_obj.redeem_time:
										offercode_obj.redeem_time = current_time
										offercode_obj.save()
										receipt_msg = _("%(offer_code)s is a valid offer code! Redeemed by %(customer)s.") % {
											"offer_code": offer_code.code,
											"customer": offercode_obj.customer
										}
										mtransaction = Transaction.objects.create(time_stamp = current_time,
															dst = su.merchant,
															offercode = offercode_obj,
															offer = offercode_obj.offer,
															ttype = "MOR")
										mtransaction.execute()
										self.notify(su.phone, receipt_msg)
										customer_msg = _("You have successfully redeemed your code at %(merchant)s.") %{
											"merchant": su.merchant.business_name
										}
										ctransaction = Transaction.objects.create(time_stamp = current_time,
															dst=offercode_obj.customer,
															offercode = offercode_obj,
															offer = offercode_obj.offer,
															ttype = "COR")

										ctransaction.execute()
										self.notify(phone, customer_msg)
										if offercode_obj.forwarder:
											ftransaction=Transaction.objects.create(time_stamp=current_time,
																dst=offercode_obj.forwarder,
																offercode = offercode_obj,
																offer = offercode_obj.offer,
																ttype="CFR")	

											ftransaction.execute()
									else:
										receipt_msg = _("Code reuse! %(offer_code)s was redeemed by %(customer)s at %(time)s.") % {
											"offer_code": offer_code.code,
											"customer": offercode_obj.customer,
											"time": pretty_datetime(offercode_obj.redeem_time),
										}
										#print "sent msg"
										self.notify(su.phone, receipt_msg)
										OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="DR", offercode=offercode_obj).save()
										raise CommandError("Customer attempts to reuse a code")
								else:
									receipt_msg = _("Redeem failed! %(offer_code)s does not belong to %(customer)s.") % {
										"offer_code":offer_code.code,
										"customer":offercode_obj.customer,
									}
									self.notify(su.phone, receipt_msg)
									raise CommandError("Customer attempts to redeem a code he doesnt own")
							except ObjectDoesNotExist:
								# Such phone number doesn't exist in customers' profiles, save it
								receipt_msg = _("%(phone)s is not in our record. %(offer_code)s offercode was not processed") % {
									"offer_code": offer_code.code,
									"phone": phone,
								}
								self.notify(su.phone, receipt_msg)
							except MultipleObjectsReturned, e:
								# Multiple customers registered with the same phone number, should be prevented
								print e
							
						except ObjectDoesNotExist:
							# The offer code is not found, or an invalid one
							receipt_msg = _("%(offer_code)s is not a valid offer code!") % {
								"offer_code": offer_code.code,
							}
							self.notify(su.phone, receipt_msg)
							OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV", invalid_code=offer_code.code).save()
						except MultipleObjectsReturned, e:																	# Multiple offer codes found, which indicates a programming error
							print e
					# --------------------------- ZIPCODE: "zipcode "---------------
					elif parsed[0].lower() in ZIPCODE:
						if len(parsed)<2:
							receipt_msg=_("Command Error! To change your zipcode, please use this command: #zipcode new_zipcode")
							self.notify(su.phone,receipt_msg)
							raise CommandError("Incorrectly formed offer command: %s" % msg["text"])
						code = self.check_zipcode(parsed[1],su.phone)
						zipcode = ZipCode.objects.get(code=code)
						ZipCodeChange.objects.create(user=su.merchant, time_stamp=datetime.now(), zipcode=zipcode)
						su.merchant.zipcode=zipcode
						su.merchant.save()
						receipt_msg=_("%s is your new zipcode. Your later offers will be distributed to customers in this new area.") % zipcode.code
						self.notify(su.phone,receipt_msg)
					# ------------------------OFFER : "offer<SPACE>description" ---------------
					elif parsed[0].lower() == OFFER:
						if len(parsed)<2:
							receipt_msg=_("Command Error! To start an offer, please use this command: #offer offer_description")
							self.notify(su.phone,receipt_msg)
							raise CommandError("Incorrectly formed offer command: %s" % msg["text"])
						# This is an offer made by the merchant, not a redemption code

						description = ''.join([i+' ' for i in parsed[1:]]).strip()
						offer = Offer(merchant=su.merchant, title=description[:80],
								description=description, time_stamp=datetime.now(),
								starting_time=datetime.now())
						offer.save()
						num_reached = offer.distribute()
					
						if num_reached ==0 :
							receipt_msg = _("There were no customers that could be reached at this moment. Txt #status %s to track this offer.") % offer.gen_tracking_code()
 
						elif num_reached == -2:
							receipt_msg = _("Your balance is %d. You do not have enough to reach customers. Please try again when you have enough balance.") % su.balance
							offer.delete()
						else:
							receipt_msg = _("We have received your offer message at %(time)s, %(number)d users have been reached. Track the status of the offer: \"%(offer)s\" by txting \"#status %(code)s\"") % {
								"time": pretty_datetime(offer.time_stamp),
								"offer": offer,
								"number": offer.num_received(),
								"code": offer.gen_tracking_code(),
							}
						
						self.notify(su.phone, receipt_msg)
					
					# --------------------- STATUS : "#status<SPACE>trackingcode" ---------------
					elif parsed[0].lower() == STATUS:
						if (len(parsed)==1):
							 
							offers = Offer.objects.filter(merchant__id=su.merchant.id).order_by("-time_stamp")
							if offers.count()>0:
								offer=offers[0]
								print offer
								trackingcode =offer.trackingcode
								sentto  = offer.num_init_sentto
								forwarded = OfferCode.objects.filter(offer=offer,forwarder__isnull=False).count()
								total = sentto + forwarded
								receipt_msg = _("[%(code)s] Your latest offer was sent to %(sentto)s, forwarded to %(forwarded)s, total: %(total)d customers reached. Redeemed by %(redeemer)d customers. To track the offer, txt \"#status %(code)s\"") % {
								"code":trackingcode.code,
								"sentto":sentto,
		                                        	"forwarded":forwarded,
			                                     	"total":total,
								"redeemer": offer.redeemers().count()
		                                        	}
							
								self.notify(su.phone,receipt_msg)
							else:
								receipt_msg=_("Fail to get status! You have not started an offer yet. To start an offer, txt \"#offer description\"")
								self.notify(su.phone,receipt_msg)
								#raise CommandError("Incorrectly formed status command: %s" % msg["text"])
						else:
							code = parsed[1].strip().lower()
					
							try:
								trackingcode = TrackingCode.objects.get(code__iexact=code)
							except TrackingCode.DoesNotExist:
								receipt_msg = _("The tracking code can not be found. Please enter a correct tracking code.")
								self.notify(su.phone,receipt_msg)
								raise CommandError ("Tracking code not found")
							offer = trackingcode.offer
							people_sentto = offer.num_init_sentto
							people_forwarded = OfferCode.objects.filter(offer=trackingcode.offer,forwarder__isnull=False).count()
							receipt_msg = _("[%(code)s] This offer was sent to %(sentto)s, forwarded to %(forwarded)s, total: %(total)d customers reached. Redeemed by %(redeemer)d customers.") % {
													"code":code,"sentto":people_sentto,
													"forwarded":people_forwarded,
													"total":int(people_sentto)+int(people_forwarded),
													"redeemer": offer.redeemers().count()
							}
							self.notify(su.phone,receipt_msg)
					# --------------------- RESIGNUP -------------------------
					elif parsed[0].lower() == MERCHANT_SIGNUP:
						receipt_msg = _("You are already a Shoppley merchant")
						self.notify(su.phone, receipt_msg)
		

					# --------------------- HELP: "help" -------------------------
					elif parsed[0].lower() == HELP:
						commands = self.merchant_help()
						self.notify(su.phone, commands)


					# --------------------- INCORRECT COMMAND: give them helps --------------
					else:
						receipt_msg=_("%s is not available. Here are the available commands:\n") % parsed[0]+ self.merchant_help()
						self.notify(su.phone,receipt_msg)
				except ParseException:
					sender_msg = _("%s is not a valid command. Our commands start with \"#\". Txt #help for all commands") % text
					self.notify(su.phone,sender_msg)


			#****************** COMMANDS FOR CUSTOMERS ********************************
			elif su and su.is_customer():
				text = msg["text"].strip()
				try:
					parsed = customer_pattern.parseString(text)
					del parsed[0]
					phone = su.phone
					# --------------------------- REDEEM: "#balance"---------------
					if parsed[0].lower()==BALANCE:
						receipt_msg = _("You have %d points.") % su.balance
						self.notify(su.phone, receipt_msg)		
					# ----------------- INFO : "#info<SPACE>offercode+"----------------
					elif parsed[0].lower() == INFO:
						if (len(parsed)==1):
							offercodes = OfferCode.objects.filter(customer=su.customer).order_by("-time_stamp")
							if offercodes.count()>0:
								offercode = offercodes[0]
								customer_msg = self.info(offercode)
								self.notify(phone,customer_msg)
							else:
								receipt_msg=_("Fail to find your offer! You have not received an offer yet.")
								self.notify(phone,receipt_msg)
								#raise CommandError('Incorrectly formed info command: "%s"' % msg["text"])

						else:
							customer_msg=""
							for i in parsed[1:]:
								parsed_offercode =i
								offercode = self.check_offercode(parsed_offercode,phone)			
								#print offercode		
								customer_msg = customer_msg+ self.info(offercode)
	
							self.notify(phone,customer_msg)
					# ------------------- STOP: "stop"----------------------
					elif parsed[0].lower() == STOP:
					
						if su.active:
							customer_msg = _("You chose to temporarily stop receiving offer messages. Please txt #start to %s to restart your service.") % DEFAULT_SHOPPLEY_NUM
							self.notify(phone,customer_msg)
							su.active = False
							su.save()

						else:
					 		customer_msg = _("You already elected to stop receiving offer messages. Please txt #start to %s to restart your service.") % DEFAULT_SHOPPLEY_NUM
							self.notify(phone,customer_msg)
					# ------------------- START: "start"-----------------------
					elif parsed[0].lower() == START :
					
						if not su.active:
							su.active = True
							su.save()
							customer_msg = _("Welcome back! You will start receiving offer messages again.")
							self.notify(phone, customer_msg)	
						else:
							customer_msg = _("You are active and receiving offer messages.")
							self.notify(phone, customer_msg)
					# --------------------------- ZIPCODE: "zipcode "---------------
					elif parsed[0].lower() in ZIPCODE:
						if len(parsed)<2:
							receipt_msg=_("Command Error! To change your zipcode, please use this command: #zipcode new_zipcode")
							self.notify(su.phone,receipt_msg)
							raise CommandError("Incorrectly formed offer command: %s" % msg["text"])
						code = self.check_zipcode(parsed[1], su.phone)
						zipcode = ZipCode.objects.get(code=code)
						ZipCodeChange.objects.create(user=su.customer, time_stamp=datetime.now(), zipcode=zipcode)
						su.customer.zipcode=zipcode
						su.customer.save()
						receipt_msg=_("%s is your new zipcode. You will receive offers from this new area.") % zipcode.code
						self.notify(su.phone,receipt_msg)
					#-------------------- FORWARD: "#forward<SPACE>offercode<SPACE>number+"---------------------
					elif parsed[0].lower() ==FORWARD:
						# TODO add sender to dst's friend list
						if (len(parsed) < 3):
							forwarder_msg='Fail to forward the offer! Please follow this command: "#forward offercode(s)" followed by one or more friends\' numbers separated by spaces'
							self.notify(su.phone,forwarder_msg)
							raise CommandError('Incorrectly formed forward command: "%s"' % msg["text"])
						ori_code = self.check_offercode(parsed[1],phone)
						ori_offer = ori_code.offer

						if (ori_code.customer!=su.customer):
							forwarder_msg= _("%s: Fail to forward! You are not the owner of this offercode.") % ori_code.code
							self.notify(phone,forwarder_msg)
							raise CommandError("Fail to forward! Customer attempts to forward an offercode he doesnt own")

						#f_state,created = ForwardState.objects.get_or_create(customer=su.customer,offer=ori_offer)
						parsed_numbers = [parse_phone_number(i) for i in parsed[2:]]
						#print "created:" , created
						#print "remaining:", f_state.remaining
						valid_receivers=set([ i for i in parsed_numbers if ori_offer.offercode_set.filter(customer__phone=i).count()==0 or Customer.objects.filter(phone=i).count()==0]) # those who havenot received the offer: new customers or customers who have not got the offer before
						invalid_receivers= set(parsed_numbers) - valid_receivers # those who have
						#allowed_forwards = f_state.allowed_forwards(len(valid_receivers))
						for r in invalid_receivers:
							su.customer.customer_friends.add(Customer.objects.get(phone=r))
						if len(valid_receivers)==0:
							forwarder_msg = _("[%s] All phone numbers you wanted to forward the code already received the offer.") % ori_code.code		
							self.notify(su.phone,forwarder_msg)
					
						else:
							forwarder_msg= _('[%s] was forwarded to ') % ori_code.code
							for r in valid_receivers:
								#f_state.update()
								friend_num = r
								friend_code, random_pw = ori_offer.gen_forward_offercode(ori_code,friend_num)	
								customer_msg = _("%(customer)s forwarded you an offer: %(info)s. Use [%(code)s] to redeem")%{
									"customer":su.customer,
									"info": self.forward_info(ori_code),
									"code": friend_code.code,
								}
							
								self.notify(friend_num,customer_msg)
								# the phone number is not one of our customers
								if random_pw:
									new_customer = friend_code.customer
									#print "created a customer for %s" % friend_num
									account_msg = _("Welcome to Shoppley! Here is your shoppley.com login info:\n - username: %(name)s\n - password: %(password)s")%{"name":new_customer.user.username,"password":random_pw,}
									self.notify(friend_num,account_msg)

							forwarder_msg= _('Offer [%s] was forwarded to ') % ori_code.code
							forwarder_msg= forwarder_msg+ ''.join([str(i)+' ' for i in valid_receivers]) + "\nYou will receive points when they redeem." 
							#% f_state.remaining
							self.notify(su.phone,forwarder_msg)
					# --------------------- HELP: "help" -------------------------
					elif parsed[0].lower() == HELP:
						commands = self.customer_help()
						self.notify(su.phone, commands)
					# --------------------- RESIGNUP -------------------------
					elif parsed[0].lower() == SIGNUP:
						receipt_msg = _("You are already a Shoppley customer")
						self.notify(su.phone, receipt_msg)
				
					# ---------------------------- INCORRECT COMMAND : give them help -----------
					else:
						customer_msg=_("%s command is not available. Here is a list of accepted commands:\n") % parsed[0]+self.customer_help()
						self.notify(su.phone,customer_msg)
				except ParseException:
					sender_msg = _("%s is not a valid command. Our commands start with \"#\". Txt #help for all commands") % text
					self.notify(su.phone,sender_msg)

			else:
				# TODO: We should save all messages
				if not su:
					text = msg["text"].strip()
					phone= msg["from"]
					try:
						parsed = customer_pattern.parseString(text)
						del parsed[0]
						#------------------------------- MERCHANT SIGNUP: "merchant<SPACE>email<SPACE>zipcode<SPACE>business_name"-----------
						if  parsed[0].lower() == MERCHANT_SIGNUP:
							if (len(parsed)<4):
								receipt_msg=_("Fail to sign up! Please follow this command: \'#merchant email zipcode business_name\'")
								self.notify(phone,receipt_msg)      
								raise CommandError('Incorrectly formed merchant signup command: "%s"' % msg["text"])

							parsed_email = parsed[1].lower()
							parsed_zip = parsed[2]
						
							business = ''.join(i+" " for i in parsed[3:]).strip()
							email = self.check_email(parsed_email,phone)
							zipcode= self.check_zipcode(parsed[2],phone)
							phone=self.check_phone(phone)
							randompassword = gen_random_pw()
							new_user = User.objects.create_user(email,email,randompassword)
							EmailAddress.objects.add_email(new_user,email)
							zipcode_obj = ZipCode.objects.get(code=parsed_zip)
							clean_phone = parse_phone_number(phone,zipcode_obj.city.region.country.code)
							new_merchant = Merchant(user=new_user,phone = clean_phone,zipcode= zipcode_obj,
										business_name = business, verified=True).save()
					

							receipt_msg = _("Sign up successfully! Please use these info to log in.\n username: %(email)s \n password: %(password)s") % {
								"email": email,
								"password": randompassword,
								}

							self.notify(phone,receipt_msg)	

						# ----------------------------------- SIGNUP: "signup<SPACE>email<SPACE>zipcode" ----------------
						elif parsed[0].lower() ==SIGNUP:
							if (len(parsed) <3):
								receipt_msg=_("Signup Error! Please follow this command: '#signup email zipcode'")
								self.notify(phone,receipt_msg)
								raise CommandError('Incorrectly formed signup command: "%s"' % msg["text"])

							parsed_email = parsed[1].lower()
							parsed_zip = parsed[2]	
							email = self.check_email(parsed_email,phone)
							zipcode= self.check_zipcode(parsed[2],phone)
							phone =self.check_phone(phone)
							randompassword = gen_random_pw()
							receipt_msg = _("Sign up successfully! Please use these info to log in.\n username: %(email)s \n password: %(password)s") % {
								"email": email,
								"password": randompassword,
								}
							self.notify(phone,receipt_msg)
							new_user = User.objects.create_user(parsed_email,parsed_email,randompassword)
							EmailAddress.objects.add_email(new_user,parsed_email)
							zipcode_obj = ZipCode.objects.get(code=parsed_zip)
							clean_phone = parse_phone_number(phone,zipcode_obj.city.region.country.code)		
							new_customer = Customer(user=new_user,phone = clean_phone,zipcode= zipcode_obj,verified=True).save()

						else:
						# -------------------------------- UNSUPPORTED NON-CUSTOMER COMMAND: ask them to sign up with us --------------
							receipt_msg=_("Welcome to Shoppley! You are currently not one of our users. Please sign up @ www.shoppley.com or send us a text message to %(shoppley_num)s with this command: \"#signup email zipcode\" to sign up as a customer or \"merchant email zipcode business_name\" to sign up as a business") % { "shoppley_num": "508-690-0888" }
							print phone
							self.notify(phone,receipt_msg)
					except ParseException:
						receipt_msg=_("Welcome to Shoppley! You are currently not one of our users. Please sign up @ www.shoppley.com or send us a text message to %(shoppley_num)s with this command: \"#signup email zipcode\" to sign up as a customer or \"merchant email zipcode business_name\" to sign up as a business") % { "shoppley_num": "508-690-0888" }
							
						self.notify(phone,receipt_msg)
	def handle_noargs(self, **options):
		voice = Voice()
		voice.login()
		smses = voice.sms()
		self.update_expired()
		#skipped_sms=[]
		#index = -1
		for msg in extractsms(voice.sms.html):
			#sms_notify(msg["from"], "hello")
			print datetime.now(), "- processing: ", msg
			try:
				self.test_handle(msg)
			except CommandError:
				continue
			except ObjectDoesNotExist, e:
				print str(e)
				continue
			except MultipleObjectsReturned, e:
				print str(e)
				continue
			#except Exception:
			#	skipped_sms.append(index)
			#	continue
		
		for message in voice.sms().messages:
		
			message.delete()
