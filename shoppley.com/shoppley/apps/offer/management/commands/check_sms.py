from django.core.management.base import NoArgsCommand,CommandError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress
from shoppleyuser.utils import sms_notify, parse_phone_number,map_phone_to_user, pretty_date
from shoppleyuser.models import ZipCode, Customer, Merchant, ShoppleyUser, ZipCodeChange, IWantRequest
from offer.models import Offer, ForwardState, OfferCode, OfferCodeAbnormal, TrackingCode
from offer.utils import gen_offer_code, validateEmail, gen_random_pw, pluralize, pretty_datetime, TxtTemplates
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
phone_pattern =Optional("(") + Word(nums, exact=3) +Optional(")") + Optional("-") + Word(nums,exact=3)+ Optional("-")+ Word(nums,exact=4)

DEFAULT_SITE = "www.shoppley.com"

# Customer commands:
BALANCE= "balance"
INFO = "info"
STOP = "stop"
START = "start"
FORWARD = "forward"
IWANT = "iwant"

# Merchant commands:
REDEEM = "redeem"
OFFER = "offer"
STATUS = "status"
REOFFER = "reoffer"
# others
SIGNUP = "signup"
MERCHANT_SIGNUP = "merchant"
HELP = "help"
ZIPCODE = ["zip", "zipcode"]

import logging
sms_logger = logging.getLogger("offer.management.commands.check_sms")

class Command(NoArgsCommand):
	help = "Check Google Voice inbox for posted offers from merchants"
	DEBUG = False
	def notify(self, phone, msg):
		if self.DEBUG:
			print _("\"%(msg)s\" sent to %(phone)s") % {"msg":msg, "phone":phone,}
		else:
			sms_notify(phone,msg)

	def validate_number(self, number, phone):
		try:
			a = phone_pattern.parseString(number)
			return parse_phone_number(number)
		except ParseException:
			t = TxtTemplates()
			msg = t.render(TxtTemplates.templates["SHARED"]["INVALID_NUMBER"],
					{
								"number": number,
					})
			self.notify(phone, msg)
			raise CommandError("INVALID NUMBER: %s is not a valid number." % number)

	def info(self, offercode):
			t = TxtTemplates()
			return t.render(TxtTemplates.templates["CUSTOMER"]["INFO"],
					{
								"offercode": offercode.code,
								"description": offercode.offer.description,
								"merchant": offercode.offer.merchant,
								"expiration": pretty_date(offercode.expiration_time, True) 
						})

			#return _("[%(code)s]\nmerchant: %(merchant)s; \nexpiration: %(expiration)s; \ndescription: %(description)s;\naddress: %(address)s") %{
		#						"code" : (offercode.code) ,
		#						"merchant" : offercode.offer.merchant,
			#					"expiration":pretty_datetime(offercode.expiration_time)	,
			#					"description":offercode.offer.description ,
			#					"address":offercode.offer.merchant.print_address(),
			#				}

	def forward_info(self, offercode):
			t = TxtTemplates()
			return t.render(TxtTemplates.templates["CUSTOMER"]["FORWARD_INFO"],{
								"description": offercode.offer.description,
								"merchant": offercode.offer.merchant,
								"expires": pretty_date(offercode.expiration_time, True) 
						})

	def update_expired(self):
		
		expired_offers = [x for x in Offer.objects.all() if not x.is_active() and not x.is_merchant_txted]
		t = TxtTemplates()
		for offer in expired_offers:
			offer.is_merchant_txted=True
			#offer.expire()
			offer.update_expired_codes()
			#print "tracking:", offer.trackingcode.code
			#print offer.offercode_set.values_list('code',flat=True)
			sentto = offer.num_init_sentto + offer.num_resent_to
			forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
			redeem = offer.offercode_set.filter(redeem_time__isnull=False).count()
			merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["EXPIRE_INFO"],{ "offer":offer,"sentto":sentto,"forwarded":forwarded,"redeem":redeem})
			self.notify(offer.merchant.phone,merchant_msg)
		return len(expired_offers)

	def customer_help(self):
		t = TxtTemplates()
		avail_commands = t.render(TxtTemplates.templates["CUSTOMER"]["HELP"],{})
		return avail_commands

	def merchant_help(self):
		t = TxtTemplates()
		avail_commands = t.render(TxtTemplates.templates["MERCHANT"]["HELP"],{})
		return avail_commands
		
	def check_email(self,email,phone):
		try:
			t = TxtTemplates()
			if not validateEmail(email):
				receipt_msg=t.render(TxtTemplates.templates["SHARED"]["INVALID_EMAIL"],{"email":email,})
				self.notify(phone,receipt_msg)
				raise CommandError("Invalid email address")			
			user = User.objects.get(username__iexact =email)
			receipt_msg = t.render(TxtTemplates.templates["SHARED"]["EMAIL_TAKEN"],{"email":email,})
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
			t = TxtTemplates()
			receipt_msg = t.render(TxtTemplates.templates["SHARED"]["INVALID_ZIPCODE"],{"zipcode": code,})
			self.notify(phone,receipt_msg)
			raise CommandError("Zipcode does not exist")
		except MultipleObjectsReturned:
			return code

	def check_phone(self,phone):
		try:
			phone = parse_phone_number(phone)
			#print phone			
			customer = ShoppleyUser.objects.get(phone__icontains=phone)
			receipt_msg = t.render(TxtTemplates.templates["SHARED"]["PHONE_TAKEN"],{"phone":phone,})
			self.notify(phone,receipt_msg)
			raise CommandError("Phone number was already used")
		except ShoppleyUser.DoesNotExist:
			return phone
	
	def check_offercode(self,code,phone):
		code = code.lower()
		t = TxtTemplates()
		offercodes = OfferCode.objects.filter(code__icontains = code)
		if offercodes.count() == 1:
			if not offercodes[0].offer.is_active():
				return -1
			else:
				return offercodes[0]
		elif offercodes.count() == 0:
			receipt_msg=t.render(TxtTemplates.templates["SHARED"]["OFFERCODE_NOT_EXIST"], {"code":code})
			self.notify(phone,receipt_msg)
			OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV",invalid_code=code).save()
			raise CommandError("Offercode does not exist")
		else:
			return -1
		
	def test_handle(self,msg): # take msg: dict("from":phonenumber, "text":text)
		t= TxtTemplates()
		#print "new message %s" % msg
		msg["from"] = parse_phone_number(msg["from"])
		#sms_logger.info("from %s : %s" % (msg["from"],msg["text"]))
		#print "logged"
		if msg["from"] != "Me" and msg["from"] != "":
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
						receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["BALANCE"],{"points": su.balance})
						self.notify(su.phone, receipt_msg)

					# --------------------------- REDEEM: "redeem<SPACE>offercode<SPACE>phone number here"---------------
					elif parsed[0].lower()==REDEEM:
						if len(parsed) < 3:
							# non enough parameters
							receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_PARAM_ERRORS"], {})
							self.notify(su.phone,receipt_msg)
							raise CommandError ("Merchant attempted redeem command without offer code or phone number: %s"%msg["text"])
							
						offer_code = self.check_offercode(parsed[1],su.phone)
						phone = self.validate_number(parsed[2],su.phone)
						if offer_code == -1 : # offercode expired
							receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_EXPIRED"], {"offer": parsed[1]})
							self.notify(su.phone,receipt_msg)
						else:
							if offer_code.offer.merchant != su.merchant:
								receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_WRONG_MERCHANT"],{"code": offer_code.code})
								self.notify(su.phone,receipt_msg)
								raise CommandError ("Merchant attempts to redeem an offer he does not own")
					
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
											receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_SUCCESS"], {
												"offer_code": offer_code.code,
												"customer": offercode_obj.customer
											})
											mtransaction = Transaction.objects.create(time_stamp = current_time,
																dst = su.merchant,
																offercode = offercode_obj,
																offer = offercode_obj.offer,
																ttype = "MOR")
											mtransaction.execute()
											self.notify(su.phone, receipt_msg)
											customer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["REDEEM_SUCCESS"],{
												"merchant": su.merchant.business_name
											})
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
											receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_CODE_REUSE"], {
												"offer_code": offer_code.code,
												"customer": offercode_obj.customer,
												"time": pretty_datetime(offercode_obj.redeem_time),
											})
											#print "sent msg"
											self.notify(su.phone, receipt_msg)
											OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="DR", offercode=offercode_obj).save()
											raise CommandError("Customer attempts to reuse a code")
									else:
										receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_WRONG_CUSTOMER"],  {
											"offer_code":offer_code.code,
											"customer":offercode_obj.customer,
										})
										self.notify(su.phone, receipt_msg)
										raise CommandError("Customer attempts to redeem a code he doesnt own")
								except ObjectDoesNotExist:
									# Such phone number doesn't exist in customers' profiles, save it
									receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_INVALID_CUSTOMER_NUM"], {
										"offer_code": offer_code.code,
										"phone": phone,
									})
									self.notify(su.phone, receipt_msg)
								except MultipleObjectsReturned, e:
									# Multiple customers registered with the same phone number, should be prevented
									#print e
									sms_logger.exception ("\"%s\" causes an error:" % msg)
							
							except ObjectDoesNotExist:
								# The offer code is not found, or an invalid one
								receipt_msg =t.render(TxtTemplates.templates["MERCHANT"]["REDEEM_INVALID_CODE"], {
									"offer_code": offer_code.code,
								})
								self.notify(su.phone, receipt_msg)
								OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV", invalid_code=offer_code.code).save()
							except MultipleObjectsReturned, e:																	# Multiple offer codes found, which indicates a programming error
								#print e
								sms_logger.exception ("\"%s\" causes an error:" % msg)

					# --------------------------- ZIPCODE: "zipcode "---------------
					elif parsed[0].lower() in ZIPCODE:
						if len(parsed)<2:
							receipt_msg=t.render(TxtTemplates.templates["MERCHANT"]["ZIPCODE_COMMAND_ERROR"])
							self.notify(su.phone,receipt_msg)
							raise CommandError("Incorrectly formed offer command: %s" % msg["text"])
						code = self.check_zipcode(parsed[1],su.phone)
						zipcode = ZipCode.objects.filter(code=code)[0]
						ZipCodeChange.objects.create(user=su.merchant, time_stamp=datetime.now(), zipcode=zipcode)
						su.merchant.zipcode=zipcode
						su.merchant.save()
						number = Customer.objects.filter(zipcode__code=code).count()
						receipt_msg=t.render(TxtTemplates.templates["MERCHANT"]["ZIPCODE_CHANGE_SUCCESS"], {"zipcode": zipcode.code,"number":number})
						self.notify(su.phone,receipt_msg)
					# ------------------------OFFER : "offer<SPACE>description" ---------------
					elif parsed[0].lower() == OFFER:
						if len(parsed)<2:
							receipt_msg=t.render(TxtTemplates.templates["MERCHANT"]["OFFER_COMMAND_ERROR"])
							self.notify(phone,receipt_msg)
							raise CommandError("Incorrectly formed offer command: %s" % msg["text"])
						# This is an offer made by the merchant, not a redemption code

						description = ''.join([i+' ' for i in parsed[1:]]).strip()
						offer = Offer(merchant=su.merchant, title=description[:80],
								description=description, time_stamp=datetime.now(),
								starting_time=datetime.now())
						offer.save()
						num_reached = offer.distribute()
					
						if num_reached ==0 :
							receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["OFFER_NO_CUSTOMER"], {"code":offer.gen_tracking_code()})
 
						elif num_reached == -2:

							receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["OFFER_NOTENOUGH_BALANCE"], {"points":su.balance})

							offer.delete()
						else:

							receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["OFFER_SUCCESS"], {
								"time": pretty_datetime(offer.time_stamp),
								"offer": offer,
								"number": offer.num_received(),
								"code": offer.gen_tracking_code(),
							})
						#print msg["from"], su.phone
						self.notify(msg["from"], receipt_msg)
					# --------------------------REOFFER: "reoffer<SPACE>TRACKINGCODE" ----------------
					elif parsed[0].lower() == REOFFER:
						if len(parsed)==1:
							offers = [o for o in su.merchant.offers_published.all() if o.is_active()==True]
							#offers = su.merchant.offers_published.filter(expired=False)
							if offers:
								offer = offers.order_by("-time_stamp")[0]
								resentto = offer.redistribute()

								#print "redistributed -- DONE", resentto
								if resentto == 0:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_ZERO_CUSTOMER"], {"code": offer.trackingcode.code})
								elif resentto==-2:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_NOTENOUGH_BALANCE"], {"points": su.balance})
								elif resentto==-3:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_NOT_ALLOWED"], {"offer": offer})

								else:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_SUCCESS"], {

										"title" : offer.title,
										"resentto": resentto,
										})
								self.notify(su.phone,merchant_msg)
							else:
								merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_NO_OFFER"],{})
								self.notify(su.phone,merchant_msg)
						else:
							code = parsed[1].strip().lower()
					

							try:
								trackingcode = TrackingCode.objects.get(code__iexact=code)
							except TrackingCode.DoesNotExist:
								receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_INVALID_TRACKING"],{"code":code})
								self.notify(su.phone,receipt_msg)
								raise CommandError ("Tracking code not found")
							offer = trackingcode.offer
							if offer.merchant.id != su.merchant.id:
								receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_WRONG_MERCHANT"],{"code":trackingcode.code})
								self.notify(su.phone,merchant_msg)
							else:
								
								resentto = offer.redistribute()

								if resentto == 0:
									merchant_msg =t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_ZERO_CUSTOMER"], {"code": offer.trackingcode.code})
								elif resentto == -2:
									merchant_msg =t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_NOTENOUGH_BALANCE"], {"points": su.balance})
								elif resentto == -3:
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_NOT_ALLOWED"], {"offer": offer})

								else:			
									merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["REOFFER_SUCCESS"], {
											"title" : offer.title,
											"resentto": resentto,
											})
								self.notify(su.phone,merchant_msg)
						# --------------------- STATUS : "#status<SPACE>trackingcode" ---------------
					elif parsed[0].lower() == STATUS:
						if (len(parsed)==1):
				
							offers = su.merchant.offers_published.order_by("-time_stamp")
							#offers = Offer.objects.filter(merchant__id=su.merchant.id).order_by("-time_stamp")
							if offers.count()>0:
								offer=offers[0]
								#print offer
								trackingcode =offer.trackingcode
								sentto  = offer.num_init_sentto + offer.num_resent_to
								forwarded = OfferCode.objects.filter(offer=offer,forwarder__isnull=False).count()

								receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["STATUS_SUCCESS"], {
								"code":trackingcode.code,
								"sentto":sentto,
		                                        	"forwarded":forwarded,
								"offer": offer,
								"redeemer": offer.redeemers().count()

		                                        	})
							
								self.notify(su.phone,receipt_msg)
							else:
								receipt_msg=t.render(TxtTemplates.templates["MERCHANT"]["STATUS_NO_OFFER"], {})
								self.notify(su.phone,receipt_msg)
								#raise CommandError("Incorrectly formed status command: %s" % msg["text"])
						else:
							code = parsed[1].strip().lower()
					
							try:
								trackingcode = TrackingCode.objects.get(code__iexact=code)
								
							except TrackingCode.DoesNotExist:
								receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["STATUS_INVALID_CODE"],{"code":code})
								self.notify(su.phone,receipt_msg)
								#sms_logger.exception("Tracking code not found:")
								raise CommandError ("Tracking code not found")
							offer = trackingcode.offer
							if offer.merchant.id != su.merchant.id:
								merchant_msg = t.render(TxtTemplates.templates["MERCHANT"]["STATUS_WRONG_MERCHANT"],{"code":trackingcode.code	})
								self.notify(su.phone,merchant_msg)
							else:
								offer = trackingcode.offer
								people_sentto = offer.num_init_sentto + offer.num_resent_to
								people_forwarded = OfferCode.objects.filter(offer=trackingcode.offer,forwarder__isnull=False).count()

								receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["STATUS_SUCCESS"], {

														"code":code,"sentto":people_sentto,
														"forwarded":people_forwarded,

														"redeemer": offer.redeemers().count(),
														"offer":offer
								})

								self.notify(su.phone,receipt_msg)
					# --------------------- RESIGNUP -------------------------
					elif parsed[0].lower() == MERCHANT_SIGNUP:
						receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["RESIGNUP"], {})
						self.notify(su.phone, receipt_msg)
		
					# --------------------- HELP: "help" -------------------------
					elif parsed[0].lower() == HELP:
						commands = self.merchant_help()
						self.notify(su.phone, commands)


					# --------------------- INCORRECT COMMAND: give them helps --------------
					else:
						receipt_msg= t.render(TxtTemplates.templates["MERCHANT"]["INCORRECT_COMMAND"], {"command":parsed[0], "help": self.merchant_help()})
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
						receipt_msg = t.render(TxtTemplates.templates["CUSTOMER"]["BALANCE"], {"points":su.balance})
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
								receipt_msg=t.render(TxtTemplates.templates["CUSTOMER"]["INFO_NO_OFFER"],{})
								self.notify(phone,receipt_msg)
								#raise CommandError('Incorrectly formed info command: "%s"' % msg["text"])

						else:
							customer_msg=""
							for i in parsed[1:]:
								parsed_offercode =i
								try:
									offercode = self.check_offercode(parsed_offercode,phone)			
									#print "offercode",offercode		
									if offercode == -1:
										offercodes = su.customer.offercode_set.filter(code__icontains=parsed_offercode)
										if offercodes.count()==1:
											t = TxtTemplates()
											offercode = offercodes[0]
											customer_msg = customer_msg +  t.render(TxtTemplates.templates["CUSTOMER"]["INFO"],
                                        							{	
                                                               						 "offercode": offercode.code[0:settings.OFFER_CODE_LENGTH],
                                                                					"description": offercode.offer.description,
                                                                					"merchant": offercode.offer.merchant,
                                                                					"expiration": "expired",
                                                						})

										
										else:
											customer_msg = customer_msg + "[%s] already expired;" % i
									else:
										customer_msg = customer_msg+ self.info(offercode) + ";"
								except CommandError:		
									continue
							#print "customer_msg" ,customer_msg
							if customer_msg != "":
								self.notify(phone,customer_msg)
					# ------------------- IWANT: "#iwant ..."----------------------
					elif parsed[0].lower() == IWANT:
						if len(parsed)<2:
							receipt_msg=t.render(TxtTemplates.templates["CUSTOMER"]["IWANT_COMMAND_ERROR"], {})
							self.notify(su.phone,receipt_msg)
							raise CommandError("Incorrectly formed iwant command: %s" % msg["text"])
						# This is an offer made by the merchant, not a redemption code

						request = ''.join([i+' ' for i in parsed[1:]]).strip()
						iwant = IWantRequest.objects.create(customer=su.customer,request=request,time_stamp=datetime.now())
						customer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["IWANT"],{"request": request})
						self.notify(su.phone, customer_msg)

					# ------------------- STOP: "stop"----------------------
					elif parsed[0].lower() == STOP:
					
						if su.active:
							customer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["STOP"], {"DEFAULT_SHOPPLEY": settings.SHOPPLEY_NUM })
							self.notify(phone,customer_msg)
							su.active = False
							su.save()

						else:
					 		customer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["RESTOP"], {"DEFAULT_SHOPPLEY": settings.SHOPPLEY_NUM })
							self.notify(phone,customer_msg)
					# ------------------- START: "start"-----------------------
					elif parsed[0].lower() == START :
					
						if not su.active:
							su.active = True
							su.save()
							customer_msg =t.render(TxtTemplates.templates["CUSTOMER"]["START"], {})
							self.notify(phone, customer_msg)	
						else:
							customer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["RESTART"], {})
							self.notify(phone, customer_msg)
					# --------------------------- ZIPCODE: "zipcode "---------------
					elif parsed[0].lower() in ZIPCODE:
						if len(parsed)<2:
							receipt_msg=t.render(TxtTemplates.templates["CUSTOMER"]["ZIPCODE_COMMAND_ERROR"], {})
							self.notify(su.phone,receipt_msg)
							raise CommandError("Incorrectly formed offer command: %s" % msg["text"])
						code = self.check_zipcode(parsed[1], su.phone)
						zipcode = ZipCode.objects.filter(code=code)[0]
						ZipCodeChange.objects.create(user=su.customer, time_stamp=datetime.now(), zipcode=zipcode)
						su.customer.zipcode=zipcode
						su.customer.save()
						number = Merchant.objects.filter(zipcode__code=code).count()
						receipt_msg=t.render(TxtTemplates.templates["CUSTOMER"]["ZIPCODE"],{"zipcode": zipcode.code,"number":number})
						self.notify(su.phone,receipt_msg)
					#-------------------- FORWARD: "#forward<SPACE>offercode<SPACE>number+"---------------------
					elif parsed[0].lower() ==FORWARD:
						# TODO add sender to dst's friend list
						if (len(parsed) < 3):
							forwarder_msg=t.render(TxtTemplates.templates["CUSTOMER"]["FORWARD_COMMAND_ERROR"], {})
							self.notify(su.phone,forwarder_msg)
							raise CommandError('Incorrectly formed forward command: "%s"' % msg["text"])
						ori_code = self.check_offercode(parsed[1],phone)
						if ori_code ==-1:
							forwarder_msg = "Sorry, %s already expired." % parsed[1]
							self.notify(phone,forwarder_msg)
						else:
							ori_offer = ori_code.offer

							if (ori_code.customer!=su.customer):
								forwarder_msg= t.render(TxtTemplates.templates["CUSTOMER"]["FORWARD_WRONG_FORWARDER"], {"code":ori_code.code})
								self.notify(phone,forwarder_msg)
								raise CommandError("Fail to forward! Customer attempts to forward an offercode he doesnt own")

							#f_state,created = ForwardState.objects.get_or_create(customer=su.customer,offer=ori_offer)
							parsed_numbers = [self.validate_number(i,su.phone) for i in parsed[2:]]
							#print "created:" , created
							#print "remaining:", f_state.remaining
							valid_receivers=set([ i for i in parsed_numbers if ori_offer.offercode_set.filter(customer__phone=i).count()==0 or Customer.objects.filter(phone=i).count()==0]) # those who havenot received the offer: new customers or customers who have not got the offer before
							invalid_receivers= set(parsed_numbers) - valid_receivers - set([su.phone]) # those who have
							#allowed_forwards = f_state.allowed_forwards(len(valid_receivers))
							for r in invalid_receivers:
								su.customer.customer_friends.add(Customer.objects.get(phone=r))
							if len(valid_receivers)==0:
								forwarder_msg = t.render(TxtTemplates.templates["CUSTOMER"]["FORWARD_ALL_RECEIVED"], {"code":ori_code.code	})
								self.notify(su.phone,forwarder_msg)
					
							else:
								#forwarder_msg= _('[%s] was forwarded to ') % ori_code.code
								for r in valid_receivers:
									#f_state.update()
									friend_num = r
									friend_code, random_pw = ori_offer.gen_forward_offercode(ori_code,friend_num)	
									customer_msg = t.render(TxtTemplates.templates["CUSTOMER"]["FORWARD_CUSTOMER_MSG"],{
										"customer":su.customer,
										"info": self.forward_info(ori_code),
										"code": friend_code.code,
									})
							
									self.notify(friend_num,customer_msg)
									# the phone number is not one of our customers
									if random_pw:
										new_customer = friend_code.customer
										#print "created a customer for %s" % friend_num
										account_msg = t.render(TxtTemplates.templates["CUSTOMER"]["FORWARD_NON_CUSTOMER_LOGIN"],{"name":new_customer.user.username,"password":random_pw,})
										self.notify(friend_num,account_msg)

								forwarder_msg= t.render(TxtTemplates.templates["CUSTOMER"]["FORWARD_SUCCESS"], {"code": ori_code.code, "numbers": ', '.join([str(i) for i in valid_receivers])}) 
								#% f_state.remaining
								self.notify(su.phone,forwarder_msg)
					# --------------------- HELP: "help" -------------------------
					elif parsed[0].lower() == HELP:
						commands = self.customer_help()
						self.notify(su.phone, commands)
					# --------------------- RESIGNUP -------------------------
					elif parsed[0].lower() == SIGNUP:
						receipt_msg = t.render(TxtTemplates.templates["CUSTOMER"]["RESIGNUP"],{})
						self.notify(su.phone, receipt_msg)
				
					# ---------------------------- INCORRECT COMMAND : give them help -----------
					else:
						customer_msg=t.render(TxtTemplates.templates["CUSTOMER"]["INCORRECT_COMMAND"], {"command": parsed[0], "help": self.customer_help()})
						self.notify(su.phone,customer_msg)
				except ParseException:
					sender_msg = t.render(TxtTemplates.templates["CUSTOMER"]["COMMAND_NOT_STARTED_W_#"],{"command":text})
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
								receipt_msg=t.render(TxtTemplates.templates["MERCHANT"]["SIGNUP_COMMAND_ERROR"],{})
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
							zipcode_obj = ZipCode.objects.filter(code=parsed_zip)[0]
							clean_phone = parse_phone_number(phone,zipcode_obj.city.region.country.code)
							#print "creating new merchant..."
							new_merchant = Merchant(user=new_user,phone = clean_phone,zipcode= zipcode_obj,
										business_name = business, verified=True).save()
							#print "merchant created!"

							number = Customer.objects.filter(zipcode__code= parsed_zip).count()
							receipt_msg = t.render(TxtTemplates.templates["MERCHANT"]["SIGNUP_SUCCESS"], {

								"email": email,
								"password": randompassword,
								"number": number,
								})

							self.notify(phone,receipt_msg)	

						# ----------------------------------- SIGNUP: "signup<SPACE>email<SPACE>zipcode" ----------------
						elif parsed[0].lower() ==SIGNUP:
							if (len(parsed) <3):
								receipt_msg=t.render(TxtTemplates.templates["CUSTOMER"]["SIGNUP_COMMAND_ERROR"],{})
								self.notify(phone,receipt_msg)
								raise CommandError('Incorrectly formed signup command: "%s"' % msg["text"])

							parsed_email = parsed[1].lower()
							parsed_zip = parsed[2]	
							email = self.check_email(parsed_email,phone)
							zipcode= self.check_zipcode(parsed[2],phone)
							phone =self.check_phone(phone)
							randompassword = gen_random_pw()
							number = Merchant.objects.filter(zipcode__code=parsed_zip).count()
							receipt_msg = t.render(TxtTemplates.templates["CUSTOMER"]["SIGNUP_SUCCESS"], {
								"email": email,
								"number": number,
								"password": randompassword,
								})
							self.notify(phone,receipt_msg)
							new_user = User.objects.create_user(parsed_email,parsed_email,randompassword)
							EmailAddress.objects.add_email(new_user,parsed_email)
							zipcode_obj = ZipCode.objects.filter(code=parsed_zip)[0]
							clean_phone = parse_phone_number(phone,zipcode_obj.city.region.country.code)
									
							new_customer = Customer(user=new_user,phone = clean_phone,zipcode= zipcode_obj,verified=True).save()

						else:
						# -------------------------------- UNSUPPORTED NON-CUSTOMER COMMAND: ask them to sign up with us --------------
							receipt_msg=t.render(TxtTemplates.templates["SHARED"]["NON_USER"],{"site":DEFAULT_SITE, "shoppley_num": settings.SHOPPLEY_NUM })
							self.notify(phone,receipt_msg)
					except ParseException:
						receipt_msg=t.render(TxtTemplates.templates["SHARED"]["NON_USER"],{"site":DEFAULT_SITE, "shoppley_num": settings.SHOPPLEY_NUM })
							
						self.notify(parse_phone_number(msg["from"]),receipt_msg)
	def handle_noargs(self, **options):
		voice = Voice()
		voice.login()
		smses = voice.sms()
		self.update_expired()
		#skipped_sms=[]
		#index = -1
		for msg in extractsms(voice.sms.html):
			#sms_notify(msg["from"], "hello")
			#print datetime.now(), "- processing: ", msg
			try:
				self.test_handle(msg)
				sms_logger.info("success: %s" % msg)
			except CommandError:
				continue
			except ObjectDoesNotExist, e:
				#print str(e)
				sms_logger.exception ("\"%s\" causes an error:" % msg)
				continue
			except MultipleObjectsReturned, e:
				#print str(e)
                                sms_logger.exception ("\"%s\" causes an error:" % msg)

				continue
			except Exception, e:
			#	skipped_sms.append(index)
				#print str(e)
                                sms_logger.exception ("\"%s\" causes an error:" % msg)

				continue
		
		for message in voice.sms().messages:
			message.delete()
