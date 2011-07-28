from common.user import clean_phone_number, check_email, check_zipcode, check_phone
from datetime import datetime
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from emailconfirmation.models import EmailAddress
from offer.utils import TxtTemplates
from shoppleyuser.models import Customer, IWantRequest
from shoppleyuser.utils import sms_notify

def customer_authenticate(request, username, password):
	data = {}
	
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		data["result"] = 1
		data["result_msg"] = "User authenticated successfully."
		return data
	else:
		# ERROR: problem authenticating user
		data["result"] = -3
		data["result_msg"] = "Authentication error, possibly the user is not activated."
		return data

# Caller must check for existence of all required fields, and
# must also send welcome messages
def customer_register(email, username, zipcode, phone, password, address, method):
	data = {}
	
	# sanitize inputs
	if email is not None:
		email = check_email(email)
		if email is None:
			data["result"] = -1
			data["result_msg"] = "Email address is used by another user."
			return data
	
	if zipcode is not None:
		zipcode = check_zipcode(zipcode)
		if zipcode is None:
			data["result"] = -2
			data["result_msg"] = "Zip Code is invalid or not in the system."
			return data
	
	if phone is not None:
		phone = check_phone(phone)
		if phone is None:
			data["result"] = -3
			data["result_msg"] = "Phone number is used by another user."
			return data
	
	if username is None:
		if email is not None:
			username = email
		elif phone is not None:
			username = phone
		else:
			data["result"] = -4
			data["result_msg"] = "Either email address, phone number or username is required."
			return data
			
	is_random_password = False
	if password is None:
		s = string.lowercase + string.digits
		password = ''.join(random.sample(s,6))
		is_random_password = True
	
	try:
		user = User.objects.create_user(username, "", password)
		user.save()
	except IntegrityError:
		data["result"] = -5
		data["result_msg"] = "'" + username + "' is used by the other user."
		return data
	
	# create customer information
	c = Customer(user=user, zipcode=zipcode, phone=phone, verified=True)
	c.save()
	c.set_location_from_address()
	
	num_merchants = c.count_merchants_within_miles()
	
	t = TxtTemplates()
	args = {"email": email, "number": num_merchants}
	if is_random_password:
		args["password"] = password,
		welcome_msg = t.render(TxtTemplates.templates["CUSTOMER"]["SIGNUP_SUCCESS"], args)
	else:
		welcome_msg = t.render(TxtTemplates.templates["CUSTOMER"]["SIGNUP_SUCCESS_NO_PASSWORD"], args)
	
	if email is not None:
		e = EmailAddress(user=user, email=email, verified=True, primary=True)
		e.save()
		send_mail('Welcome to Shoppley', welcome_msg, 'support@shoppley.com', [email], fail_silently=True)		
		
	if phone is not None:
		if method == "SMS":
			sms_notify(phone, welcome_msg)
		else:
			# send verification sms
			verify_msg = t.render(TxtTemplates.templates["CUSTOMER"]["VERIFY_PHONE"], {})
			sms_notify(phone, verify_msg)
		
	data["result"] = 1
	data["result_msg"] = "User registered successfully."
	data["username"] = username
	data["password"] = password
	
	return data;
	
def customer_iwant(customer, request_text):
	return IWantRequest.objects.create(customer=customer,request=request_text,time_stamp=datetime.now())
	