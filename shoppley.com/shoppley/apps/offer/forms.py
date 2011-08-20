from django import forms
from offer.models import Offer
from datetime import datetime, date, time
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _, ugettext
from shoppleyuser.utils import parse_phone_number
from shoppleyuser.models import Merchant, MerchantPhone
from django.contrib.admin.widgets import AdminTimeWidget,AdminDateWidget 
from common.utils import InputAndChoiceField, SelectTimeWidget

class MerchantSearchForm(forms.Form):
	business_name 	= forms.CharField(label=_("Business Name"), max_length=80, required=False)
	business_num	 = forms.CharField(label=_("Business Number"), max_length=20, required=False)

	def clean(self):
		#		raise forms.ValidationError(_("You must fill in at least one of the two fields testing."))
		if not "business_num" not in self.cleaned_data and not "business_name" in self.cleaned_data:
			raise	forms.ValidationError(_("You must fill in at least one of the two fields."))
		m=None
		if "business_num" in self.cleaned_data:
			
			business_num = parse_phone_number(self.cleaned_data["business_num"])
			if MerchantPhone.objects.filter(number=business_num).exists():
				m = MerchantPhone.objects.get(number=business_num).merchant
		elif "business_name" in self.cleaned_data:
			business_name = self.cleaned_data["business_name"].strip()
			if Merchant.objects.filter(business_name__icontains= business_name).exists():
				m = Merchant.objects.filter(business_name__icontains= business_name)[0]
		if m:
			return self.cleaned_data
		else:
			raise forms.ValidationError(_("We cannot find a merchant with the following information. Please create a merchant account for the merchant."))

class AdminStartOfferForm(forms.Form):
	merchant_id 	= forms.CharField(max_length=10, required=False, label=_("merchant id"), widget=forms.HiddenInput())
	OFFER_TYPE= (
                        (0, '%'),
                        (1, '$'),
                        (2, 'free'),
                        (3, 'custom'),
                        )

	offer_radio     = forms.ChoiceField(choices = OFFER_TYPE, label = _("Offer Type"), required = True, widget = forms.RadioSelect)

	value           = forms.CharField(label=_("Value"), max_length = 10, required = True)

	title           = forms.CharField(label=_("What is it?"), max_length=80, widget=forms.TextInput())
	#date            = forms.DateField(required=True, label=_("When"), widget=SelectDateWidget(years=[y for y in range(2011,2020)]))
	date		= forms.DateField(required=True, label=_("When"))
	now             = forms.BooleanField(label=_("now?"))
	description     = forms.CharField(label=_("Description"), widget=forms.widgets.Textarea())

	max_offers      = forms.IntegerField(label=_("Max quantity"), initial= "20")


	duration        = forms.IntegerField(label=_("Duration"), initial="120")


class StartOfferForm(forms.Form):
	title           = forms.CharField(label=_("What is it?"), max_length=80,widget=forms.TextInput(), help_text=_("Enter a short attractive offer headline. It will appear in text msgs sent to customers."))
	value		= forms.CharField(
				help_text=_("Enter the value of this offer before any discount."), 
				label=_("Value ($)"), max_length = 10, required = True)

	discount 	= InputAndChoiceField()
	date 		= forms.DateField(required=True, label=_("When"), help_text=_("When do you want to start this offer?"))
	time		= forms.TimeField(required=True, label=_("What time"), widget = SelectTimeWidget, help_text=_("At what time?"))
	#now 		= forms.BooleanField(label=_("now?"))
	description	= forms.CharField(label=_("Description"), widget=forms.widgets.Textarea(), help_text=_("Enter a long description about this offer"))

	max_offers	= forms.IntegerField(label=_("Max quantity"), initial= "20", help_text=_("Enter the maximum number of people you want this offer to reach."))

	duration 	= forms.IntegerField(label=_("Duration (minutes)"), 
					initial="120",
					help_text=_("How long do you want this offer to last"))

	def clean_time (self):
		date_obj= self.cleaned_data["date"]		
		time = self.cleaned_data["time"]
		time_stamp= datetime.combine(date_obj, time)
		if time_stamp <= datetime.now():
			raise forms.ValidationError("Sorry, you can only start an offer in the future.")
		return self.cleaned_data["time"]

	def clean_discount(self):
		discount = self.cleaned_data["discount"]
		discount_l = discount.split(':::')
		discount = discount_l[0]

		dtype = discount_l[1]
		if dtype == '%':
			if float(discount)>100:
				raise forms.ValidationError("Sorry, percentage discount must be between 0 to 100")
		elif dtype == '$':
			if float(discount) > float(self.cleaned_data["value"]):
				raise forms.ValidationError("Sorry, dollar discount must be between 0 to the value of the offer")
		return self.cleaned_data["discount"]
		#raise forms.ValidationError("hello")

	def clean_duration(self):
		if self.cleaned_data["duration"]<= 20:
			raise forms.ValidationError(_("The set duration is too short. Please allow more time so your customers can arrive on time."))
		return self.cleaned_data["duration"]	

class StartOfferForm1(forms.ModelForm):

	now = forms.BooleanField(label="Activate immediately", required=False)

	OFFER_TYPE = (
			(0, '%'),
			(1, '$')
			)

	offer_radio = forms.ChoiceField(choices=OFFER_TYPE, label="Offer Type", widget=forms.RadioSelect)

	def __init__(self, *args, **kw):
		super(forms.ModelForm, self).__init__(*args, **kw)
		self.fields.keyOrder = [
			'name',
			'description',
			'offer_radio',
			'percentage',
			'dollar_off',
			'now',
			'starting_time',
			'duration',
			'max_offers']

	def clean(self):
		description = self.cleaned_data["description"]
		name = self.cleaned_data["name"]
		if len(description) == 0 and len(name) == 0:
			raise forms.ValidationError(u"Name and/or Description needs to be filled out")

		starting_time = self.cleaned_data["starting_time"]
		now = self.cleaned_data.get("now", None)
		if not now and starting_time is None:
			raise forms.ValidationError(u"Choose a starting time or set it to activate immediately")
		return self.cleaned_data

	def save(self, force_insert=False, force_update=False, commit=True):
		m = super(StartOfferForm, self).save(commit=False)
		# do custom stuff
		name = self.cleaned_data.get("name")
		description = self.cleaned_data.get("description")
		if len(name) == 0:
			self.field['name'] = description[:64] 

		if self.cleaned_data.get("offer_radio") == "percentage":
			self.field['percentage'] = self.cleaned_data.get("percentage")	
		elif self.cleaned_data.get("offer_radio") == "amount":
			self.field['dollar_off'] = self.cleaned_data.get("dollar_off")	

		if commit:
			m.save()
		return m

	class Meta:
		model = Offer
		exclude = ['merchant', 'time_stamp']


