from django import forms


class CheckInForm(forms.Form):
	first_name = forms.CharField(label='First name:', max_length=50)
	last_name = forms.CharField(label='Last name:', max_length=50)
	dob = forms.DateField(label='Date of Birth:')

class SeeingPatient(forms.Form):
	seen_at = forms.CharField(widget=forms.HiddenInput())
	appt_id = forms.CharField(widget=forms.HiddenInput())
	checked_in_at = forms.CharField(widget=forms.HiddenInput())
	doctor_id = forms.CharField(widget=forms.HiddenInput())
