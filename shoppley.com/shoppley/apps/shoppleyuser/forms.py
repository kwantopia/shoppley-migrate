from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.translation import ungettext_lazy, string_concat
from django.contrib.auth.models import User
import re

from emailconfirmation.models import EmailAddress
alnum_re = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
phone_red = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')

class MerchantSignupForm(forms.Form):
	username = forms.CharField(label=_("Username"), max_length=30, widget=forms.TextInput())
	password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
	password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput(render_value=False))

	if settings.ACCOUNT_REQUIRED_EMAIL or settings.ACCOUNT_EMAIL_VERIFICATION:
		email = forms.EmailField(
			label = _("Email"),
			required = True,
			widget = forms.TextInput()
		)
	else:
		email = forms.EmailField(
			label = _("Email (optional)"),
			required = False,
			widget = forms.TextInput()
		)

	confirmation_key = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
	business_name	= forms.CharField(max_length=64)
	address_1		= forms.CharField(max_length=64)
	phone			= forms.CharField(max_length=20)

	def clean_username(self):
		if not alnum_re.search(self.cleaned_data["username"]):
			raise forms.ValidationError(_("Usernames can only contain letters, numbers and underscores."))
		try:
			user = User.objects.get(username__iexact=self.cleaned_data["username"])
		except User.DoesNotExist:
			return self.cleaned_data["username"]
		raise forms.ValidationError(_("This username is already taken. Please choose another."))
	
	def clean_phone(self):
		if not phone_red.search(self.cleaned_data["phone"]):
			raise forms.ValidationError(_("This phone number is not recognized as a valid one."))

	def clean(self):
		if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
			if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
				raise forms.ValidationError(_("You must type the same password each time."))
		return self.cleaned_data

	def save(self):
		username = self.cleaned_data["username"]
		email = self.cleaned_data["email"]
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
				
		return username, password # required for authenticate()

