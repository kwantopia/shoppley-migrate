from django.core.management.base import NoArgsCommand,CommandError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.contrib.auth.models import User

from emailconfirmation.models import EmailAddress
from shoppleyuser.utils import sms_notify, parse_phone_number,map_phone_to_user, pretty_date
from shoppleyuser.models import ZipCode, Customer, Merchant, ShoppleyUser, ZipCodeChange, IWantRequest, ShoppleyPhone, CustomerPhone, MerchantPhone, TextMsg
from offer.models import Offer, ForwardState, OfferCode, OfferCodeAbnormal, TrackingCode, Vote
from offer.utils import gen_offer_code, validateEmail, gen_random_pw, pluralize, pretty_datetime, TxtTemplates
from worldbank.models import Transaction
from common.user import verify_phone
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
BALANCE= ["balance","b"]
INFO = ["info","i"]
STOP = ["stop"]
START = ["start"]
FORWARD = ["forward","f"]
IWANT = ["iwant", "w"]
VOTE = ["yay", "nay"]
# Merchant commands:
REDEEM = ["redeem","r"]
OFFER = ["offer","o"]
STATUS = ["status","s"]
REOFFER = ["reoffer","re"]
ADD = ["add", "a"]
# others
SIGNUP = ["signup","c"]
MERCHANT_SIGNUP = ["merchant","m"]
HELP = ["help","h"]
ZIPCODE = ["zip", "zipcode","z"]

import logging
FORMAT = '%(asctime)-15s: %(message)s'
logging.basicConfig(format=FORMAT)
sms_logger = logging.getLogger("offer.management.commands.check_sms")
reg_logger = logging.getLogger("txt_registration")
DEBUG = settings.SMS_DEBUG
t = TxtTemplates()
templates = TxtTemplates.templates
class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		voice = Voice()
		voice.login()
		smses = voice.sms()
		self.update_expired()
		for msg in extractsms(voice.sms.html):
			
			if len(msg["from"]) == 0:
				continue
			if msg["from"] == "Me:":
				continue
			TextMsg.objects.create(text = msg["text"], from_number = msg["from"], start_time = datetime.now())
		for message in voice.sms().messages:
			message.delete()

		texts=TextMsg.objects.filter(status=0)
		for m in texts:
			m.status = 1
			m.save()
			msg={}
			msg["from"] = m.from_number
			msg["text"] = m.text		
			try:
				self.test_handle(msg)
				sms_logger.info("success: %s" % msg)
				m.status = 2
				m.end_time = datetime.now()
				m.save()

			except CommandError:
					continue
			except ObjectDoesNotExist, e:
					sms_logger.exception ("\"%s\" causes an error:" % msg)
					continue
			except MultipleObjectsReturned, e:
					sms_logger.exception ("\"%s\" causes an error:" % msg)
					continue
			except Exception, e:
					sms_logger.exception ("\"%s\" causes an error:" % msg)
					continue
			continue


	def notify(self, phone, msg):
		if DEBUG:
			print _("TXT: \"%(msg)s\" sent to %(phone)s") % {"msg":msg, "phone":phone,}
		else:
			return	sms_notify(phone,msg)
			
	def validate_number(self,number, phone):
		try:
			a = phone_pattern.parseString(number)
			return parse_phone_number(number)
		except ParseException:
			msg = t.render(templates["SHARED"]["INVALID_NUMBER"], 
						{"number": number, })
			self.notify(phone, msg)
			raise CommandError("INVALID NUMBER: %s is an invalid number." % number)
		
	def info(self,offercode):
		#print "description", offercode.offer.description, "title:" , offercode.offer.title
		return t.render(templates["CUSTOMER"]["INFO"],
					{
						"offercode": offercode.code,
						"description": offercode.offer.description,
						"merchant": offercode.offer.merchant,
						"expiration": pretty_date(offercode.expiration_time, True),
					})
		
	def forward_info(self, offercode):
		print "forward expiration:", offercode.expiration_time
		return t.render(templates["CUSTOMER"]["FORWARD_INFO"],
					{
						"description": offercode.offer.description,
						"merchant": offercode.offer.merchant,
						"expires": pretty_date(offercode.expiration_time, True),
					})
		
	def update_expired(self):
		expired_offers = Offer.objects.filter(is_merchant_txted=False, expired_time__lt=datetime.now())
		for offer in expired_offers:

			sentto = offer.num_init_sentto + offer.num_resent_to
			forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
			redeem = offer.offercode_set.filter(redeem_time__isnull=False).count()
			merchant_msg = t.render(templates["MERCHANT"]["EXPIRE_INFO"], 
								{
									"offer": offer,
									"sentto": sentto,
									"forwarded": forwarded,
									"redeem": redeem,
								})

			phone = offer.merchant.merchantphone_set.all()[0]
			if offer.starter_phone:
				self.notify(offer.starter_phone.number, merchant_msg)
			else:	
				self.notify(phone, merchant_msg)
			# update offer's stats
			offer.is_merchant_txted = True
			offer.save()
			offer.update_expired_codes()
		return expired_offers.count()
	
	def customer_help(self):
		avai_commands = t.render(templates["CUSTOMER"]["HELP"], {})
		return avai_commands
	
	def merchant_help(self):
		avai_commands = t.render(templates["MERCHANT"]["HELP"], {})
		return avai_commands		
	
	def check_email(self, email, phone):
		try :
			if not validateEmail(email):
				receipt_msg=t.render(templates["SHARED"]["INVALID_EMAIL"], {"email":email,})
				self.notify(phone,receipt_msg)
				raise CommandError("Invalid Email Address")
			user = User.objects.get(username__iexact=email)
			receipt_msg = t.render(templates["SHARED"]["EMAIL_TAKEN"], {"email":email,})
			self.notify(phone, receipt_msg)
			raise CommandError("Email was already used")
		except User.DoesNotExist:
			return email
		
	def check_zipcode(self,code,phone):
		try:
			zipcode = ZipCode.objects.get(code=code)
			return code
		except ZipCode.DoesNotExist:
			receipt_msg = t.render(templates["SHARED"]["INVALID_ZIPCODE"], {"zipcode":code})
			self.notify(phone, receipt_msg)
			raise CommandError("Zipcode does not exist")
		except MultipleObjectsReturned:
			return code
		
	def check_phone(self, from_number, phone):
		self.validate_number(phone, from_number)
		phone = parse_phone_number(phone)
	
		if ShoppleyPhone.objects.filter(number__icontains=phone).exists():
			receipt_msg = t.render(templates["SHARED"]["PHONE_TAKEN"], {"phone":phone,})
			self.notify(from_number, receipt_msg)
			raise CommandError("Phone number was already used")
		else:
			return phone
		
	def check_offercode(self,code,phone):
		code=code.lower()
		offercodes = OfferCode.objects.filter(code__icontains=code)
		if offercodes.count()==1:
			if not offercodes[0].offer.is_active():
				return -1
			else:
				return offercodes[0]
		elif offercodes.count()==0:
			receipt_msg = t.render(templates["SHARED"]["OFFERCODE_NOT_EXIST"], {"code":code,})
			self.notify(phone,receipt_msg)
			OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV", invalid_code=code).save()
			raise CommandError("OfferCode does not exist")
		else:
			actives = [o for o in offercodes.order_by("-time_stamp") if o.offer.is_active()==True]
			if len(actives)==0:
				return -1
			return actives[0]
	
	def handle_unverified_number(self, su, from_number, text):
		if su and su.is_customer() and su.verified_phone!=0:
			if text=="1":
				verify_phone(su, True)
			elif text=="0":
				verify_phone(su. False)
			else:
				msg = t.render(templates["CUSTOMER"]["VERIFY_PHONE"],{})
				self.notify(from_number, msg)
			raise CommandError ("Unverified phone")
		

	PARAMS = {
			REDEEM[0]: (3, t.render(templates["MERCHANT"]["REDEEM_PARAM_ERRORS"])),
                        REDEEM[1]: (3, t.render(templates["MERCHANT"]["REDEEM_PARAM_ERRORS"])),

			ZIPCODE[0]: (2, t.render(templates["MERCHANT"]["ZIPCODE_COMMAND_ERROR"])),
                        ZIPCODE[1]: (2, t.render(templates["MERCHANT"]["ZIPCODE_COMMAND_ERROR"])),
			ZIPCODE[2]: (2, t.render(templates["MERCHANT"]["ZIPCODE_COMMAND_ERROR"])),


			OFFER[0]: (2, t.render(templates["MERCHANT"]["OFFER_COMMAND_ERROR"])),
                        OFFER[1]: (2, t.render(templates["MERCHANT"]["OFFER_COMMAND_ERROR"])),

			IWANT[0]: (2, t.render(templates["CUSTOMER"]["IWANT_COMMAND_ERROR"])),
                        IWANT[1]: (2, t.render(templates["CUSTOMER"]["IWANT_COMMAND_ERROR"])),

			FORWARD[0]: (3, t.render(templates["CUSTOMER"]["FORWARD_COMMAND_ERROR"])),
                        FORWARD[1]: (3, t.render(templates["CUSTOMER"]["FORWARD_COMMAND_ERROR"])),

			SIGNUP[0]: (3, t.render(templates["CUSTOMER"]["SIGNUP_COMMAND_ERROR"])),
                        SIGNUP[1]: (3, t.render(templates["CUSTOMER"]["SIGNUP_COMMAND_ERROR"])),

			MERCHANT_SIGNUP[0]: (4, t.render(templates["MERCHANT"]["SIGNUP_COMMAND_ERROR"])),
                        MERCHANT_SIGNUP[1]: (4, t.render(templates["MERCHANT"]["SIGNUP_COMMAND_ERROR"])),

			ADD[0] : (2, t.render(templates["MERCHANT"]["ADD_COMMAND_ERROR"])),
			ADD[1] : (2, t.render(templates["MERCHANT"]["ADD_COMMAND_ERROR"])),
	}
		
	def handle_lack_params(self, from_number, command, text, parsed):
		if len(parsed)< self.PARAMS[command][0]:
			send_msg = self.PARAMS[command][1]
			self.notify(from_number, send_msg)
			raise CommandError("Command lacking params: %s" % text)
	
	# -------------- MERCHANT COMMANDS HANDLING FUNCTIONS --------------------#
	def handle_balance(self, su, from_number, parsed):
		msg = t.render(templates["MERCHANT"]["BALANCE"], {"points": su.balance,})
		self.notify(from_number, msg)
	
	def handle_redeem(self, su, from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		code = parsed[1]
		client_number = parsed[2]
		offercode = self.check_offercode(code, from_number)
		phone = self.validate_number(  client_number, from_number)
		
		# offercode expired
		if offercode == -1:
			sender_msg = t.render(templates["MERCHANT"]["REDEEM_EXPIRED"], {"offer": code,})
			self.notify(from_number, sender_msg)
		else:
			if offercode.offer.merchant != su.merchant:
				msg   = t.render(templates["MERCHANT"]["REDEEM_WRONG_MERCHANT"], {"code": code,})
				self.notify(from_number, msg)
				raise CommandError("Merchant attempts to redeem an offer he does not own")
			try:
				current_time = datetime.now()
				offercode_obj = OfferCode.objects.filter(expiration_time__gt=current_time, time_stamp__lt=current_time).get(code__iexact=offercode.code)
				try:
					p = CustomerPhone.objects.get(number__icontains=phone)
					customer = p.customer
					
					if offercode_obj.customer==customer:
						if not offercode_obj.redeem_time:
							offercode_obj.redeem_time=current_time
							offercode_obj.save()
							# informing merchant + trans
							sender_msg = t.render(templates["MERCHANT"]["REDEEM_SUCCESS"], {
																													"offer_code": offercode_obj.code,
									"customer": offercode_obj.customer
																														})
							mtransaction = Transaction.objects.create(time_stamp = current_time,
																dst = su.merchant, 														offercode = offercode_obj,
												offer = offercode_obj.offer,
												ttype = "MOR")
							mtransaction.execute()
							self.notify(from_number,sender_msg)
							
							# informing customer + trans
							customer_msg = t.render(templates["CUSTOMER"]["REDEEM_SUCCESS"], {
											"merchant": su.merchant.business_name
												})
							ctransaction = Transaction.objects.create(time_stamp = current_time,
												dst = offercode_obj.customer,															offercode = offercode_obj,
													offer = offercode_obj.offer,
												ttype = "COR")
							ctransaction.execute()
							self.notify(phone, customer_msg)
							
							# informing forwarders
							if offercode_obj.forwarder:
								ftransaction = Transaction.objects.create(time_stamp = current_time,
												dst = offercode_obj.forwarder,																offercode = offercode_obj,
													offer = offercode_obj.offer,
													ttype = "CFR")
								ftransaction.execute()
						else:
							sender_msg = t.render(templates["MERCHANT"]["REDEEM_CODE_REUSE"], {
										"offer_code": offercode_obj.code,
										"customer": offercode_obj.customer,
										"time": pretty_datetime(offercode_obj.redeem_time),
												})
							self.notify(from_number, sender_msg)
							OfferCodeAbnormal(time_stamp=current_time, ab_type="DR", offercode=offercode_obj).save()
							raise CommandError("Customer attempts to reuse a code")
					else:
						sender_msg = t.render(templates["MERCHANT"]["REDEEM_WRONG_CUSTOMER"],{
										"offer_code":offercode_obj.code,
										"customer": offercode_obj.customer,})
						self.notify(from_number, sender_msg)
						raise CommandError("Customer attempts to redeem a code he does not own")
				except ObjectDoesNotExist:
					sender_msg = t.render(templates["MERCHANT"]["REDEEM_INVALID_CUSTOMER_NUM"], {
									"offer_code": offercode.code,
									"phone" : phone,})
					self.notify(from_number, sender_msg)
					
				except MultipleObjectsReturned, e:
					sms_logger.exception("\"%s\" causes an error: " % text)
			except ObjectDoesNotExist:
				sender_msg = t.render(templates["MERCHANT"]["REDEEM_INVALID_CODE"], {
								"offer_code": offercode.code,})
				self.notify(from_number, sender_msg)
				OfferCodeAbnormal(time_stamp=datetime.now(), ab_type="IV", invalid_code=offercode.code).save()
			except MultipleObjectsReturned, e:
				sms_logger.exception("\"%s\" causes an error: " % text)
					
	def handle_merchant_zipcode (self, su, from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		code = self.check_zipcode(parsed[1], from_number)
		zipcode = ZipCode.objects.filter(code=code)[0]
		ZipCodeChange.objects.create(user=su.merchant, time_stamp=datetime.now(), zipcode=zipcode)
		su.merchant.zipcode = zipcode
		su.merchant.save()
		su.merchant.set_location_from_address(address=zipcode.city.name+" " + zipcode.city.region.name + " " + zipcode.code)
		number = su.merchant.count_customers_within_miles()
		receipt_msg = t.render(templates["MERCHANT"]["ZIPCODE_CHANGE_SUCCESS"], {"zipcode": zipcode.code, "number": number,})
		self.notify(from_number, receipt_msg)
		
	def handle_offer(self, su, from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		description = ''.join([i + ' ' for i in parsed[1:]]).strip()
		try:
			starter_phone = MerchantPhone.objects.get(number=from_number)
			offer = Offer(merchant=su.merchant, title = description[:80],
                                        description = description, time_stamp = datetime.now(),
                                        starting_time=datetime.now(), starter_phone = starter_phone).save()
			offer.expired_time=offer.starting_time + timedelta(minutes=offer.duration)
			offer.save()
		except MerchantPhone.DoesNotExist:
			
			offer = Offer(merchant=su.merchant, title = description[:80],
					description = description, time_stamp = datetime.now(), 
					starting_time=datetime.now()).save()
			offer.expired_time=offer.starting_time + timedelta(minutes=offer.duration)
			offer.save()
			
	def handle_reoffer(self, su, from_number, command, text, parsed):
		if len(parsed)==1:
			# resend latest offer (no tracking code)
			offers = su.merchant.offers_published.filter(expired_time__gt=datetime.now())
			if offers.exists():
				offer = offers.order_by("-time_stamp")[0]
				if offer.redistribute():
					pass
				else:
					merchant_msg = t.render(templates["MERCHANT"]["REOFFER_NOT_ALLOWED"], {"offer": offer,})
					self.notify(from_number, merchant_msg)
					
		else:
			code = parsed[1].strip().lower()
			try:
				trackingcode = TrackingCode.objects.get(code__iexact=code)
			except TrackingCode.DoesNotExist:
				receipt_msg = t.render(templates["MERCHANT"]["REOFFER_INVALID_TRACKING"], {"code": code,})
				self.notify(from_number, receipt_msg)
				raise CommandError ("Tracking code not found")
			
			offer = trackingcode.offer
			if not offer.is_active():
				receipt_msg = t.render(templates["MERCHANT"]["REOFFER_EXPIRED_OFFER"], {"code": code,})
				self.notify(from_number, receipt_msg)
				raise CommandError ("Offer expired, cant reoffer")

			if offer.merchant.id != su.merchant.id:
				receipt_msg = t.render(templates["MERCHANT"]["REOFFER_WRONG_MERCHANT"], {"code": trackingcode.code})
				self.notify(from_number, receipt_msg)
				raise CommandError ("Reoffer trackingcode wrong merchant")
			else:
				if offer.redistribute():
					pass
				else:
					merchant_msg = t.render(templates["MERCHANT"]["REOFFER_NOT_ALLOWED"], {"offer": offer,})
					self.notify(from_number, merchant_msg)
					
	def handle_status (self, su, from_number, command, text, parsed):
		if len(parsed)==1:
			offers = su.merchant.offers_published.order_by("-time_stamp")
			if offers.count()>0:
				offer = offers[0]
				trackingcode = offer.trackingcode
				sentto = offer.num_init_sentto + offer.num_resent_to
				forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
				sender_msg = t.render(templates["MERCHANT"]["STATUS_SUCCESS"], {
								"code": trackingcode.code,
								"sentto": sentto,
								"forwarded": forwarded,
								"offer": offer,
								"redeemer": offer.redeemers().count(),
								})
				self.notify(from_number, sender_msg)
			else:
				sender_msg = t.render(templates["MERCHANT"]["STATUS_NO_OFFER"], {})
				self.notify(from_number, sender_msg)
		else:
			code = parsed[1].strip().lower()
			try:
				trackingcode = TrackingCode.objects.get(code__iexact=code)
			except TrackingCode.DoesNotExist:
				sender_msg = t.render(templates["MERCHANT"]["STATUS_INVALID_CODE"], {"code":code})
				self.notify(from_number, sender_msg)
				raise CommandError("tracking code not found")
			offer = trackingcode.offer
			if offer.merchant.id != su.merchant.id:
				merchant_msg = t.render(templates["MERCHANT"]["STATUS_WRONG_MERCHANT"], {"code": trackingcode.code})
				self.notify(from_number, merchant_msg)
			else:
				sentto = offer.num_init_sentto + offer.num_resent_to
				forwarded = offer.offercode_set.filter(forwarder__isnull=False).count()
				merchant_msg = t.render(templates["MERCHANT"]["STATUS_SUCCESS"], {
									"code": trackingcode.code,
									"forwarded" : forwarded,
									"sentto": sentto,
									"redeemer": offer.redeemers().count(),
									"offer": offer,})
				self.notify(from_number, merchant_msg)
				
	def handle_info(self, su, from_number, command, text, parsed):
		if len(parsed)==1:
			offercodes  = su.customer.offercode_set.order_by("-time_stamp")
			if offercodes.count()>0:
				offercode = offercodes[0]
				customer_msg = self.info(offercode)
				self.notify(from_number, customer_msg)
			else:
				customer_msg = t.render(templates["CUSTOMER"]["INFO_NO_OFFER"], {})
				self.notify(from_number, customer_msg)
				
		else:
			customer_msg = ""
			for i in parsed[1:]:
				parsed_offercode= i
				try:
					offercode = self.check_offercode(parsed_offercode, from_number)
					if offercode == -1:
						offercodes = su.customer.offercode_set.filter(code__icontains=parsed_offercode).order_by("-time_stamp")
						if offercodes.count()>0:
							offercode = offercodes[0]
							customer_msg = customer_msg + t.render(templates["CUSTOMER"]["INFO"], {
										"offercode": offercode.code[0:settings.OFFER_CODE_LENGTH],
										"description": offercode.offer.title,
										"merchant": offercode.offer.merchant,
										"expiration": "expired",}) + "; "
						
					else:
						customer_msg = customer_msg + self.info(offercode) + "; "
				except CommandError:
					continue
			if len(customer_msg) >0:
				self.notify(from_number, customer_msg)

	def handle_iwant(self,su,from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		request = ''.join([i+' ' for i in parsed[1:]]).strip()
		iwant = IWantRequest.objects.create(customer=su.customer, request=request, time_stamp=datetime.now())
		customer_msg = t.render(templates["CUSTOMER"]["IWANT"], {"request": request})
		self.notify(from_number, customer_msg)
		
		
	def handle_vote(self, su, from_number, command, text, parsed):
		vote = parsed[0].lower()
		if vote=="yay":
			vote_num = 1
		else:
			vote_num = -1
			
		if len(parsed) == 1:
			offers = su.customer.offercode_set.order_by("-time_stamp")
			if offers.count()==0:
				receipt_mg = t.render(templates["CUSTOMER"]["VOTE_NO_OFFER"], {})
				self.notify(from_number, receipt_msg)
				raise CommandError("Customer tried to vote but has no offer yet")
			else:
				offer = offers[0].offer
				if offer.vote_set.filter(customer=su.customer).exists():
					receipt_msg = t.render(templates["CUSTOMER"]["VOTE_REVOTE"], {"offer": offer.title,})
					self.notify(from_number, receipt_msg)
				else:
					v = Vote.objects.create(customer=su.customer, offer=offer, vote=vote_num, time_stamp=datetime.now())
					receipt_msg = t.render(templates["CUSTOMER"]["VOTE_SUCCESS"], {"offer": offer.title, "vote":vote,})
					self.notify(from_number, receipt_msg)
		else:
			if len(parsed)>2:
				receipt_msg = t.render(templates["CUSTOMER"]["VOTE_COMMAND_ERROR"])
				self.notify(from_number, receipt_msg)
				raise CommandError("Incorrectly formed vote command")
			else:
				offercode = parsed[1]
				offers = su.customer.offercode_set.filter(code__contains=parsed[1]).order_by("-time_stamp")
				if offers.count() ==0:
					receipt_msg = t.render(templates["CUSTOMER"]["VOTE_UNOWNED_OFFER"], {"offercode": offercode,})
					self.notify(from_number, receipt_msg)
				elif offers.count()>0:
					offer = offers[0].offer
					if offer.vote_set.filter(customer=su.customer).exists():
						receipt_msg = t.render(templates["CUSTOMER"]["VOTE_REVOTE"], {"offer": offer.title,})
						self.notify(from_number, receipt_msg)
					else:
						v = Vote.objects.create(customer = su.customer, offer=offer, vote=vote_num, time_stamp=datetime.now())
						receipt_msg = t.render(templates["CUSTOMER"]["VOTE_SUCCESS"], {"offer":offer.title, "vote": vote,})
						self.notify(from_number, receipt_msg)
						
	def handle_stop(self, su, from_number):
		if su.active:
			customer_msg = t.render(templates["CUSTOMER"]["STOP"], {"DEFAULT_SHOPPLEY": settings.SHOPPLEY_NUM,})
			self.notify(from_number, customer_msg)
			su.active = False
			su.save()
		else:
			customer_msg = t.render(templates["CUSTOMER"]["RESTOP"], {"DEFAULT_SHOPPLEY": settings.SHOPPLEY_NUM,})
			self.notify(from_number, customer_msg)
			
	def handle_start(self, su, from_number):
		if not su.active:
			customer_msg = t.render(templates["CUSTOMER"]["START"],{})
			self.notify(from_number, customer_msg)
			su.active = True
			su.save()
		else:
			customer_msg = t.render(templates["CUSTOMER"]["RESTART"], {})
			self.notify(from_number, customer_msg)
			
			
	def handle_customer_zipcode(self, su, from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		code = self.check_zipcode(parsed[1], from_number)
		zipcode = ZipCode.objects.filter(code=code)[0]
		ZipCodeChange.objects.create(user=su.customer, time_stamp = datetime.now(), zipcode= zipcode)
		su.customer.zipcode = zipcode
		su.customer.save()
		su.customer.set_location_from_address(address=zipcode.city.name + " " + zipcode.city.region.name + " " + zipcode.code)
		number = su.customer.count_merchants_within_miles()
		receipt_msg  = t.render(templates["CUSTOMER"]["ZIPCODE"], {"zipcode": zipcode.code, "number": number,})
		self.notify(from_number, receipt_msg)
		
	def handle_forward (self, su, from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		ori_code = self.check_offercode(parsed[1], from_number)
		if ori_code == -1:
			forwarder_msg = "Sorry, %s already expired." % parsed[1]
			self.notify(from_number, forwarder_msg)
		else:
			ori_offer = ori_code.offer
			if ori_code.customer!=su.customer:
				forwarder_msg = t.render(templates["CUSTOMER"]["FORWARD_WRONG_FORWARDER"], {"code": ori_code.code,})
				self.notify(from_number, forwarder_msg)
				raise CommandError("Fail to forward! Customer attempts to forward an offercode he doesnt own")

			parsed_numbers = [self.validate_number( i,from_number) for i in parsed[2:]]
			receivers_pk = ori_offer.offercode_set.values_list("customer", flat=True)

			valid_receivers = set([i for i in parsed_numbers 
								if	(not CustomerPhone.objects.filter(number=i).exists())
								 or (not CustomerPhone.objects.get(number=i).customer.offercode_set.filter(offer=ori_offer).exists())])
			invalid_receivers = set(parsed_numbers) -valid_receivers - set([from_number])
			
			for r in invalid_receivers:
				if CustomerPhone.objects.filter(number=r).exists():
					su.customer.customer_friends.add(CustomerPhone.objects.get(number=r).customer)
			if len(valid_receivers)==0:
				forwarder_msg = t.render(templates["CUSTOMER"]["FORWARD_ALL_RECEIVED"], {"code": ori_code.code,})
				self.notify(from_number, forwarder_msg)
			else:
				for r in valid_receivers:
					friend_num = r
					friend_code, random_pw = ori_offer.gen_forward_offercode(ori_code,friend_num)
					customer_msg = t.render(templates["CUSTOMER"]["FORWARD_CUSTOMER_MSG"], {
											"customer":su.customer,
											"info": self.forward_info(ori_code),
											"code": friend_code.code,})
					self.notify(friend_num, customer_msg)
					
					if random_pw:
						new_customer = friend_code.customer
						number = new_customer.count_merchants_within_miles()
						account_msg = t.render(templates["CUSTOMER"]["FORWARD_NON_CUSTOMER_LOGIN"], {
											"name":new_customer.user.username,
											"password": random_pw,
											"number": number,})
						self.notify(friend_num, account_msg)
				forwarder_msg = t.render(templates["CUSTOMER"]["FORWARD_SUCCESS"], {
											"code":ori_code.code,
											"numbers": ', '.join([str(i) for i in valid_receivers])})
				self.notify(from_number, forwarder_msg)
				
	def handle_customer_help(self, from_number):
		commands = self.customer_help()
		self.notify(from_number, commands)
						
	def handle_customer_resignup(self, from_number):
		sender_msg = t.render(templates["CUSTOMER"]["RESIGNUP"])
		self.notify(from_number, sender_msg)
		reg_logger.info("customer-signup: %s -- failure (resignup)" % from_number)
	
	def handle_merchant_signup(self, su, from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		parsed_email = parsed[1].lower()
		parsed_zip = parsed[2]
		business = ''.join(i+' ' for i in parsed[3:]).strip()
		email = self.check_email(parsed_email, from_number)
		zipcode = self.check_zipcode(parsed_zip, from_number)
		phone = self.check_phone(from_number, from_number)
		randompassword = gen_random_pw()
		new_user = User.objects.create_user(email,email,randompassword)
		EmailAddress.objects.add_email(new_user,email)
		zipcode_obj = ZipCode.objects.filter(code=parsed_zip)[0]
		clean_phone = parse_phone_number(phone, zipcode_obj.city.region.country.code)
		new_merchant = Merchant.objects.create(user=new_user,
											phone=clean_phone,
											zipcode=zipcode_obj,
											business_name=business,
											verified=True,
											verified_phone=0)
		new_merchant.set_location_from_address()
		p=MerchantPhone.objects.create(number=clean_phone,merchant=new_merchant)
		number = new_merchant.count_customers_within_miles()
		receipt_msg = t.render(templates["MERCHANT"]["SIGNUP_SUCCESS"], {													"email":email,
				"password":randompassword,
				"number":number})
		self.notify(from_number, receipt_msg)
		reg_logger.info("merchant-signup: %s -- success" % from_number)
		
	def handle_customer_signup(self, su, from_number, command, text, parsed):	
		self.handle_lack_params(from_number, command, text, parsed)
		parsed_email = parsed[1].lower()
		parsed_zip = parsed[2]
		email = self.check_email(parsed_email, from_number)
		zipcode = self.check_zipcode(parsed_zip, from_number)
		phone = self.check_phone(from_number, from_number)
		randompassword = gen_random_pw()
		
		new_user = User.objects.create_user(email,email,randompassword)
		EmailAddress.objects.add_email(new_user,email)
		zipcode_obj = ZipCode.objects.filter(code=parsed_zip)[0]
		clean_phone = parse_phone_number(phone,zipcode_obj.city.region.country.code)
		
		new_customer = Customer.objects.create(user=new_user,
											phone=clean_phone,
											zipcode=zipcode_obj,
											verified=True,
											verified_phone=0)
		new_customer.set_location_from_address()
		p =CustomerPhone.objects.create(number=clean_phone,customer=new_customer)
		number = new_customer.count_merchants_within_miles()
		receipt_msg = t.render(templates["CUSTOMER"]["SIGNUP_SUCCESS"], {
						"email":email,
						"password":randompassword,
						"number":number,})
		self.notify(from_number, receipt_msg)
		reg_logger.info("customer-signup: %s -- success" % from_number)
		
	def handle_add(self, su, from_number, command, text, parsed):
		self.handle_lack_params(from_number, command, text, parsed)
		parsed_number = parsed[1]
		phone = self.check_phone(from_number, parsed_number)
		MerchantPhone.objects.create(merchant = su.merchant, number= phone)
		sender_msg = t.render(templates["MERCHANT"]["ADD_SUCCESS"], {
					"phone": phone, })

		self.notify(from_number, sender_msg)


	#msg: dict("from":phonenumber, "text":text)
	def test_handle(self,msg):
		from_number = parse_phone_number(msg["from"])
		text = msg["text"].strip()
		su = map_phone_to_user(from_number)
		
		# ************* HANDLE UNVERIFIED NUMBER *****************
		self.handle_unverified_number(su, from_number, text)
		# ************* MERCHANT COMMANDS ******************
		if su and su.is_merchant():
			try:
				parsed = merchant_pattern.parseString(text)
				del parsed[0]
				command = parsed[0].lower()
				print "command" , command
				# ************************* BALANCE ********************
				if command in BALANCE:
					self.handle_balance(su, from_number, parsed)
					
				# ************************* REDEEM *********************
				elif command in REDEEM:
					self.handle_redeem(su, from_number,command, text, parsed)
					
				# ************************* ZIPCODE *********************
				elif command in ZIPCODE:
					self.handle_merchant_zipcode(su, from_number,command, text, parsed)
					
				# ************************* OFFER *********************
				elif command in OFFER:
					self.handle_offer(su, from_number, command, text, parsed)
				# ************************* REOFFER *********************
				elif command in REOFFER:
					self.handle_reoffer(su, from_number, command, text, parsed)
					
				# ************************* STATUSs *********************
				elif command in STATUS:
					self.handle_status(su, from_number, command, text, parsed)
					
				# ************************* RESIGNUP *********************
				elif command in MERCHANT_SIGNUP:
					sender_msg = t.render(templates["MERCHANT"]["RESIGNUP"], {})
					self.notify(from_number, sender_msg)
					reg_logger.info("merchant-signup: %s -- failure (resignup)" % from_number)
				# *************************ADD *********************
				elif command in ADD:
					self.handle_add(su, from_number, command, text, parsed)	
				# ************************* HELP *********************

				elif command in HELP:
					commands = self.merchant_help()
					self.notify(from_number, commands)
					
				# ************************* UNHANDLED COMMAND *********************
				else:
					receipt_msg = t.render(templates["MERCHANT"]["INCORRECT_COMMAND"], {
										"command": command,
										"help": self.merchant_help()})
					self.notify(from_number, receipt_msg)
					
			except ParseException:
				sender_msg = _("%s is not a valid command. Our commands start with # sign. Txt #help for all commands.") % text
				self.notify(from_number, sender_msg)
				
		# ************* CUSTOMER COMMANDS ******************
		elif su and su.is_customer():
			try:
				parsed = customer_pattern.parseString(text)
				del parsed[0]
				command = parsed[0].lower()
				# ************************* BALANCE *********************
				if command in BALANCE:
					self.handle_balance(su, from_number, parsed)
				# ************************* INFO *********************
				elif command in INFO:
					self.handle_info(su, from_number, command, text, parsed)
				# ************************* IWANT *********************
				elif command in IWANT:
					self.handle_iwant(su, from_number, command, text, parsed)
				# ************************* YAY/NAY *********************
				elif command in VOTE:
					self.handle_vote(su, from_number, command, text, parsed)
				# ************************* STOP *********************
				elif command in STOP:
					self.handle_stop(su, from_number)
				# ************************* START *********************
				elif command in START:
					self.handle_start(su, from_number)
				# ************************* ZIPCODE *********************
				elif command in ZIPCODE:
					self.handle_customer_zipcode(su, from_number,command, text, parsed)
				# ************************* FORWARD *********************
				elif command in FORWARD:
					self.handle_forward(su, from_number, command, text, parsed)
				# ************************* HELP *********************
				elif command in HELP:
					self.handle_customer_help(from_number)
				# ************************* RESIGNUP *********************
				elif command in SIGNUP:
					self.handle_customer_resignup( from_number)
				# ************************* UNHANDLED COMMAND *********************
				else:
					receipt_msg = t.render(templates["CUSTOMER"]["INCORRECT_COMMAND"], {
										"command": command,
										"help": self.customer_help()})
					self.notify(from_number, receipt_msg)
					
					
			except ParseException:
				
				sender_msg = _("%s is not a valid command. Our commands start with # sign. Txt #help for all commands.") % text
				self.notify(from_number, sender_msg)				
				
		else:
			if not su:
				try:
					parsed = customer_pattern.parseString(text)
					del parsed[0]
					command = parsed[0].lower()
					# ************************* MERCHANT SIGNUP *********************
					if command in MERCHANT_SIGNUP:
						self.handle_merchant_signup(su, from_number, command, text, parsed)
					# ************************* CUSTOMER SIGNUP *********************
	
					elif command in SIGNUP:
						self.handle_customer_signup(su, from_number, command, text, parsed)
						
					else:
						sender_msg = t.render(templates["SHARED"]["NON_USER"], {
										"site":DEFAULT_SITE,
										"shoppley_num": settings.SHOPPLEY_NUM,})
						self.notify(from_number, sender_msg)
						
				except ParseException:
					sender_msg = t.render(templates["SHARED"]["NON_USER"], {
										"site":DEFAULT_SITE,
										"shoppley_num": settings.SHOPPLEY_NUM,})
					self.notify(from_number, sender_msg)
