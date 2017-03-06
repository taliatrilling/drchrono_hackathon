from django import forms


class CheckInForm(forms.Form):
	"""

	Patient check-in, leads to access to UpdateInfo

	"""
	first_name = forms.CharField(label='First name:', max_length=50)
	last_name = forms.CharField(label='Last name:', max_length=50)
	dob = forms.DateField(widget=forms.widgets.DateInput(format=('%m-%d-%Y')), label='Date of Birth:')
	complaint = forms.CharField(label='What is the primary reason for your visit?', max_length=500)

class SeeingPatient(forms.Form):
	""" 

	Hidden form submitted when a doctor indicates that they are going to begin a specific appointment -- used to generate
	average waittimes for a given day

	"""
	seen_at = forms.CharField(widget=forms.HiddenInput())
	appt_id = forms.CharField(widget=forms.HiddenInput())
	checked_in_at = forms.CharField(widget=forms.HiddenInput())
	doctor_id = forms.CharField(widget=forms.HiddenInput())

class UpdateInfo(forms.Form):
	""" 

	Form for patient chart info, starts pre-populated with patient's existing chart info from API

	"""
	address = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Current address:', max_length=100)
	email = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Email address:', max_length=100)
	home_phone = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Home phone number:', max_length=20)
	cell_phone = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Cell phone number:', max_length=20)
	emergency_contact_phone = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Emergency contact phone number:', max_length=20)
	default_pharmacy = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Preferred pharmacy:', max_length=100)
	gender = forms.ChoiceField(choices=[('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')], label='Gender:')
	doctor_id = forms.IntegerField(widget=forms.HiddenInput())

