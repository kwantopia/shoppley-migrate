from django import forms
from offer.models import Offer

class StartOfferForm(forms.ModelForm):


	now = forms.BooleanField(label="Activate immediately")

	def __init__(self, *args, **kw):
		super(ModelForm, self).__init__(*args, **kw)
		self.fields.keyOrder = [
			'name',
			'description',
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
		now = self.cleaned_data["now"]
		if not now and starting_time is None:
			raise forms.ValidationError(u"Choose")
		return cleaned_data

	def save(self, force_insert=False, force_update=False, commit=True):
		m = super(StartOfferForm, self).save(commit=False)
		# do custom stuff
		name = self.cleaned_data.get("name")
		description = self.cleaned_data.get("description")
		if len(name) == 0:
			self.field['name'] = description[:64] 

		# TODO: need to save timestamp		

		if commit:
			m.save()
		return m

	class Meta:
		model = Offer
		exclude = ['merchant', 'time_stamp']


