from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from offer.utils import TxtTemplates
from shoppleyuser.models import ZipCode, ShoppleyUser, Merchant
from shoppleyuser.utils import sms_notify

# return None if cannot log in
def user_authenticate(request, credential, password):
	data = {}
		
	user = authenticate(username=credential, password=password)
	
	if user is None:
		user = authenticate(phone=credential, password=password)
		
	if user is None:
		emails = EmailAddress.objects.filter(email=credential)
		print emails
		if len(emails) > 0:
			print emails[0].user.username
			user = authenticate(username=emails[0].user.username, password=password)
	
	if user is not None:
		login(request, user)
		return user
	else:
		# ERROR: problem authenticating user
		return None

def clean_phone_number(raw_number, country_code="US"):
	cleaned_number = filter(lambda x: x.isdigit(), raw_number)
	if country_code == "US":
		if len(cleaned_number) >= 10:
			return cleaned_number[-10:]
	return cleaned_number
	
# check_xxx return None for invalid values
def check_email(email):
	from django.core.validators import validate_email
	from django.core.exceptions import ValidationError
	
	email = email.lower()

	try:
		validate_email(email)
	except ValidationError:
		return None
	
	if EmailAddress.objects.filter(email__iexact=email).exists():
		return None
	
	return email

def check_zipcode(zipcode):
	try:
		return ZipCode.objects.filter(code=zipcode)[0]
	except IndexError:
		return None
			
def check_phone(phone):
	phone = clean_phone_number(phone)
	if ShoppleyUser.objects.filter(phone__icontains=phone).exists():
		return None
	return phone

def verify_phone(shoppleyUser, isVerify):
	t = TxtTemplates()
	
	if isVerify:
		shoppleyUser.verified_phone = shoppleyUser.VERIFIED_YES
		msg = t.render(TxtTemplates.templates["CUSTOMER"]["VERIFY_SUCCESS"], {})

	else:
		shoppleyUser.verified_phone = shoppleyUser.VERIFIED_NO
		msg = t.render(TxtTemplates.templates["CUSTOMER"]["VERIFY_NO_SUCCESS"], {})
		
	shoppleyUser.save()
	sms_notify(shoppleyUser.phone, msg)
	