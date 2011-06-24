from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.translation import ungettext_lazy, string_concat
from django.contrib.auth.models import User
import re

from emailconfirmation.models import EmailAddress
from shoppleyuser.models import ShoppleyUser, Merchant, Customer, ZipCode, City
from shoppleyuser.utils import parse_phone_number
alnum_re = re.compile(r'^[a-zA-Z0-9_\.]+$')
phone_red = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')

class MerchantSignupForm(forms.Form):
	email = forms.EmailField(label = _("Email"), required = True, widget=forms.TextInput())

	username = forms.CharField(label=_("Username"), required=True, widget=forms.TextInput())
	business_name   = forms.CharField(max_length=64)
	address_1               = forms.CharField(label=_("Business address"), max_length=64, required=True)


	zip_code                = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class':'zip_code'}))
	phone                   = forms.CharField(max_length=20)

	password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
	password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(render_value=False))

	confirmation_key = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())

	# address_2		= forms.CharField(label=_("line 2"), max_length=64, required=False)
	

	def clean_zip_code(self):
		try:
			zipcode = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
			return self.cleaned_data["zip_code"]
		except ZipCode.DoesNotExist:
			raise forms.ValidationError(_("Not a valid zip code."))

	def clean_username(self):
		username = self.cleaned_data["username"]
		try:
			user = User.objects.get(username__iexact=username)
		except User.DoesNotExist:
			return self.cleaned_data["username"]
		raise forms.ValidationError(_("This username is already registered. Please choose another."))

	def clean_email(self):
		email = self.cleaned_data["email"]
		try:
			email = EmailAddress.objects.get(email__iexact=email)
		except EmailAddress.DoesNotExist:
			return self.cleaned_data["email"]
		except EmailAddress.MultipleObjectsReturned:
		## TODO: This should NOT have happened
			raise forms.ValidationError(_("This email address is already registered. Please choose another."))

		raise forms.ValidationError(_("This email address is already registered. Please choose another."))
	
	def clean_phone(self):
		if not phone_red.search(self.cleaned_data["phone"]):
			raise forms.ValidationError(_("This phone number is not recognized as a valid one."))
		 
		su=ShoppleyUser.objects.filter(phone=self.cleaned_data["phone"])
		if su.count()>0:
			raise forms.ValidationError(_("This phone number is being used by another user"))
		#except Exception, e:
		#	pass
		else:
			return self.cleaned_data["phone"]

	def clean(self):
		if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
			if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
				raise forms.ValidationError(_("You must type the same password each time."))
		return self.cleaned_data

	def save(self):
		username = self.cleaned_data["username"].lower()
		email = self.cleaned_data["email"].lower()
		password = self.cleaned_data["password1"]
		
		if self.cleaned_data["confirmation_key"]:
			from friends.models import JoinInvitation # @@@ temporary fix for issue 93
			try:
				join_invitation = JoinInvitation.objects.get(confirmation_key = self.cleaned_data["confirmation_key"])
				confirmed = True
			except JoinInvitation.DoesNotExist:
				confirmed = False
		else:
			confirmed = False
		
		# @@@ clean up some of the repetition below -- DRY!
		
		if confirmed:
			if email == join_invitation.contact.email:
				new_user = User.objects.create_user(username, email, password)
				join_invitation.accept(new_user) # should go before creation of EmailAddress below
				new_user.message_set.create(message=ugettext(u"Your email address has already been verified"))
				# already verified so can just create
				EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
			else:
				new_user = User.objects.create_user(username, "", password)
				join_invitation.accept(new_user) # should go before creation of EmailAddress below
				if email:
					new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
					EmailAddress.objects.add_email(new_user, email)
		else:
			new_user = User.objects.create_user(username, "", password)
			if email:
				new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
				EmailAddress.objects.add_email(new_user, email)
		
		if settings.ACCOUNT_EMAIL_VERIFICATION:
			new_user.is_active = False
			new_user.save()

		zipcode_obj = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
		phone = parse_phone_number(self.cleaned_data["phone"], zipcode_obj.city.region.country.code)
		new_merchant = Merchant(user=new_user,
						address_1=self.cleaned_data["address_1"],
						# address_2=self.cleaned_data["address_2"],
						phone=phone,
						zipcode=zipcode_obj,
						business_name=self.cleaned_data["business_name"]
					).save()
		return username, password # required for authenticate()


class MerchantProfileEditForm(forms.Form):
	username		= forms.CharField(label=_("Username"))
	business_name		= forms.CharField(label=_("Business Name"), max_length=64, required=True)	
	address1		= forms.CharField(label=_("Street Address"), max_length=64, required=True)
	zip_code		= forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class':'zip_code'}))
	phone			= forms.CharField(max_length=20)
	user_id			= forms.CharField(max_length=10, required=False, widget=forms.HiddenInput())


	def clean_zip_code(self):
		try:
			zipcode = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
			return self.cleaned_data["zip_code"]
		except ZipCode.DoesNotExist:
			raise forms.ValidationError(_("Not a valid zip code."))

	def clean_username(self):
		username = self.cleaned_data["username"]
		user = User.objects.get(id=self.cleaned_data["user_id"])
		
		try:
			if username == user.username:
				return self.cleaned_data["username"]
			user = User.objects.get(username__iexact=username)
			
		except User.DoesNotExist:
			
			return self.cleaned_data["username"]
		user.message_set.create(message=ugettext(u"This username is already registered, Please choose another."))	
		raise forms.ValidationError(_("This username is already registered. Please choose another."))

	def clean_email(self):
		email = self.cleaned_data["email"]
		user = User.objects.get(id=self.cleaned_data["user_id"])

		try:
			if email == user.email:
				return self.cleaned_data["email"]
			email = EmailAddress.objects.get(email__iexact=email)
		except EmailAddress.DoesNotExist:
			return self.cleaned_data["email"]
		except EmailAddress.MultipleObjectsReturned:
               
## TODO: This should NOT have happened
			raise forms.ValidationError(_("This email address is already registered. Please choose another."))


		raise forms.ValidationError(_("This email address is already registered. Please choose another."))
		

	def clean_phone(self):
		
		if not phone_red.search(self.cleaned_data["phone"]):
			raise forms.ValidationError(_("This phone number is not recognized as a valid one. %s"%self.cleaned_data["phone"]))
		phone = parse_phone_number(self.cleaned_data["phone"])
		user = User.objects.get(id=self.cleaned_data["user_id"])

		merchant = Merchant.objects.get(user__id=user.id)
		if merchant.phone == phone:
			return self.cleaned_data["phone"]	 
		su = ShoppleyUser.objects.filter(phone=phone)
		if su.count()>0:
			raise forms.ValidationError(_("This phone number is being used by another user"))
		else:
			return self.cleaned_data["phone"]
		#except Customer.DoesNotExist:
		#	return self.cleaned_data["phone"]
		#raise forms.ValidationError(_("This phone number is being used by another customer"))

	def save(self, user_id):
		username = self.cleaned_data["username"].lower()	
		address = self.cleaned_data["address1"].lower()
		u = User.objects.get(pk = user_id)
		u.username = self.validate_username(user_id)
		u.save()
		zipcode_obj = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
		phone = parse_phone_number(self.cleaned_data["phone"], zipcode_obj.city.region.country.code)
		m = Merchant.objects.get(user__pk = user_id)
		m.address1 = self.cleaned_data["address"]
		m.business_name = self.cleaned_data["business_name"]
		m.save()

class CustomerProfileEditForm(forms.Form):
	username		= forms.CharField(label=_("Username"))
	address1		= forms.CharField(label=_("Street Address"), max_length=64, required=False)
	zip_code		= forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class':'zip_code'}))
	phone			= forms.CharField(max_length=20)

	def clean_zip_code(self):
		try:
			zipcode = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
			return self.cleaned_data["zip_code"]
		except ZipCode.DoesNotExist:
			raise forms.ValidationError(_("Not a valid zip code."))

	def clean_username(self):
		username = self.cleaned_data["username"]
		try:
			user = User.objects.get(username__iexact=username)
		
		except User.DoesNotExist:
			
			return self.cleaned_data["username"]
		
		raise forms.ValidationError(_("This username is already registered. Please choose another."))

	def clean_email(self):
		email = self.cleaned_data["email"]
		try:
			email = EmailAddress.objects.get(email__iexact=email)
		except EmailAddress.DoesNotExist:
			return self.cleaned_data["email"]
		except EmailAddress.MultipleObjectsReturned:
                ## TODO: This should NOT have happened
			raise forms.ValidationError(_("This email address is already registered. Please choose another."))


		raise forms.ValidationError(_("This email address is already registered. Please choose another."))
		

	def clean_phone(self):
		if not phone_red.search(self.cleaned_data["phone"]):
			raise forms.ValidationError(_("This phone number is not recognized as a valid one. %s"%self.cleaned_data["phone"]))
		 
		su = ShoppleyUser.objects.filter(phone__icontains=self.cleaned_data["phone"])
		if su.count()>0:
			raise forms.ValidationError(_("This phone number is being used by another user"))
		else:
			return self.cleaned_data["phone"]
		#except Customer.DoesNotExist:
		#	return self.cleaned_data["phone"]
		#raise forms.ValidationError(_("This phone number is being used by another customer"))

	def save(self, user_id):
		username = self.cleaned_data["username"].lower()	
		address = self.cleaned_data["address1"].lower()
		u = User.objects.get(pk = user_id)
		u.username = username
		u.save()
		zipcode_obj = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
		phone = parse_phone_number(self.cleaned_data["phone"], zipcode_obj.city.region.country.code)
		c = Customer.objects.get(user__pk = user_id)
		c.address1 = address
		c.save()


class PasswordChangeForm(forms.Form):
	old_password		= forms.CharField(label=_("Old Password"), widget=forms.PasswordInput(render_value=False))
	new_password1		= forms.CharField(label=_("New Password"), widget=forms.PasswordInput(render_value=False))
	new_password2		= forms.CharField(label=_("New Password (again)"), widget=forms.PasswordInput(render_value=False))
	def clean(self):
		if not "old_password" in self.cleaned_data:
			raise forms.ValidationError(_("You must input your old password."))
		if "new_password1" in self.cleaned_data and "new_password2" in self.cleaned_data:
			if self.cleaned_data["new_password1"] != self.cleaned_data["new_password2"]:
				raise forms.ValidationError(_("You must type the same password each time."))
		return self.cleaned_data


	def save(self, request):
		data=self.clean()
		old_password = data["old_password"]
		new_password = data["new_password1"]
		

class CustomerSignupForm(forms.Form):
	email = forms.EmailField( label = _("Email"), required = True, widget = forms.TextInput())
	
	username = forms.CharField(label=_("Username"), required=True, widget=forms.TextInput())
	address_1               = forms.CharField(label=_("Street Address"), max_length=64, required=False)

	zip_code                = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class':'zip_code'}))
	phone                   = forms.CharField(max_length=20)
	
#	email = forms.EmailField( label = _("Email"), required = True, widget = forms.TextInput())
	password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
	password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(render_value=False))
	confirmation_key = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
	#address_1		= forms.CharField(label=_("Street Address"), max_length=64, required=False)
	# address_2		= forms.CharField(max_length=64, required=False)
	#zip_code		= forms.CharField(max_length=10)
	#phone			= forms.CharField(max_length=20)

	def clean_zip_code(self):
		try:
			zipcode = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
			return self.cleaned_data["zip_code"]
		except ZipCode.DoesNotExist:
			raise forms.ValidationError(_("Not a valid zip code."))

	def clean_username(self):
		username = self.cleaned_data["username"]
		try:
			user = User.objects.get(username__iexact=username)
		
		except User.DoesNotExist:
			
			return self.cleaned_data["username"]
		
		raise forms.ValidationError(_("This username is already registered. Please choose another."))

	def clean_email(self):
		email = self.cleaned_data["email"]
		try:
			email = EmailAddress.objects.get(email__iexact=email)
		except EmailAddress.DoesNotExist:
			return self.cleaned_data["email"]
		except EmailAddress.MultipleObjectsReturned:
                ## TODO: This should NOT have happened
			raise forms.ValidationError(_("This email address is already registered. Please choose another."))


		raise forms.ValidationError(_("This email address is already registered. Please choose another."))
		

	def clean_phone(self):
		if not phone_red.search(self.cleaned_data["phone"]):
			raise forms.ValidationError(_("This phone number is not recognized as a valid one. %s"%self.cleaned_data["phone"]))
		 
		su = ShoppleyUser.objects.filter(phone__icontains=self.cleaned_data["phone"])
		if su.count()>0:
			raise forms.ValidationError(_("This phone number is being used by another user"))
		else:
			return self.cleaned_data["phone"]
		#except Customer.DoesNotExist:
		#	return self.cleaned_data["phone"]
		#raise forms.ValidationError(_("This phone number is being used by another customer"))

	def clean(self):
		if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
			if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
				raise forms.ValidationError(_("You must type the same password each time."))
		return self.cleaned_data

	def save(self):
		# assign email as user name
		username = self.cleaned_data["username"].lower()
		email = self.cleaned_data["email"].lower()
		password = self.cleaned_data["password1"]
		
		if self.cleaned_data["confirmation_key"]:
			from friends.models import JoinInvitation # @@@ temporary fix for issue 93
			try:
				join_invitation = JoinInvitation.objects.get(confirmation_key = self.cleaned_data["confirmation_key"])
				confirmed = True
			except JoinInvitation.DoesNotExist:
				confirmed = False
		else:
			confirmed = False
		
		# @@@ clean up some of the repetition below -- DRY!
		
		if confirmed:
			if email == join_invitation.contact.email:
				new_user = User.objects.create_user(username, email, password)
				join_invitation.accept(new_user) # should go before creation of EmailAddress below
				new_user.message_set.create(message=ugettext(u"Your email address has already been verified"))
				# already verified so can just create
				EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
			else:
				new_user = User.objects.create_user(username, "", password)
				join_invitation.accept(new_user) # should go before creation of EmailAddress below
				if email:
					new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
					EmailAddress.objects.add_email(new_user, email)
		else:
			new_user = User.objects.create_user(username, "", password)
			if email:
				new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
				EmailAddress.objects.add_email(new_user, email)
		
		if settings.ACCOUNT_EMAIL_VERIFICATION:
			new_user.is_active = False
			new_user.save()

		zipcode_obj = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
		phone = parse_phone_number(self.cleaned_data["phone"], zipcode_obj.city.region.country.code)
		new_customer = Customer(user=new_user,
						address_1=self.cleaned_data["address_1"],
						# address_2=self.cleaned_data["address_2"],
						phone=phone,
						zipcode=zipcode_obj,
						verified=True,
					).save()
				
		return username, password # required for authenticate()

##############
# FOR BETA
#############
class CustomerBetaSubscribeForm( forms.Form ):
	email = forms.EmailField( label = _("Email"), required = True, widget = forms.TextInput())
	address_1		= forms.CharField(label=_("Street Address"), max_length=64, required=False)
	zip_code		= forms.CharField(max_length=10)
	phone			= forms.CharField(max_length=20)

	def clean_zip_code(self):
		try:
			zipcode = ZipCode.objects.get(code=self.cleaned_data["zip_code"])
			return self.cleaned_data["zip_code"]
		except ZipCode.DoesNotExist:
			raise forms.ValidationError(_("Not a valid zip code."))

	def clean_email(self):
		email = self.cleaned_data["email"]
		try:
			BetaCustomer = BetaCustomer.objects.get(email__iexact=email)
		except User.DoesNotExist:
			return self.cleaned_data["email"]
		raise forms.ValidationError(_("This email address is already registered. Please choose another."))
		

	def clean_phone(self):
		if not phone_red.search(self.cleaned_data["phone"]):
			raise forms.ValidationError(_("This phone number is not recognized as a valid one. %s"%self.cleaned_data["phone"]))
		try: 
			BetaCustomer = BetaCustomer.objects.get(phone__icontains=self.cleaned_data["phone"])
		except Customer.DoesNotExist:
			return self.cleaned_data["phone"]
		raise forms.ValidationError(_("This phone number is being used by another customer"))


	#create a new beta customer and return the customer object
	def save(self):
		zipcode = self.clean_zip_code()
		email = self.clean_email()
		phone = self.clean_phone()
		newbCustomer=BetaCustomer.objects.create(email = email, 
							phone= phone,
							address_1 = self.cleaned_data["address_1"], 
							zipcode=ZipCode.objects.get(code=zipcode))
		return newbCustomer

