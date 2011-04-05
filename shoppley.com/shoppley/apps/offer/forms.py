from django import forms
from offer.models import Offer

class StartOfferForm(forms.ModelForm):

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


