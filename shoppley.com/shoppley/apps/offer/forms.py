from django import forms
from offer.models import Offer

class StartOfferForm(forms.ModelForm):

	def clean_name(self):
		return name

	def clean(self):
		if len(description) == 0 and len(name) == 0:
			raise forms.ValidationError(u"Name and/or Description needs to be filled out")
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


