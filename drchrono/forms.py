from django import forms
from django.contrib.admin.widgets import AdminDateWidget

class CheckInForm(forms.Form):
	first_name = forms.CharField(label='First name:', max_length=50)
	last_name = forms.CharField(label='Last name:', max_length=50)
	dob = forms.DateField(label='Date of Birth:')
