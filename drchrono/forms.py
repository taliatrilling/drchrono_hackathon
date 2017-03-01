from django import forms

class CheckInForm(forms.Form):
	first_name = forms.CharField(label='first_name', max_length=50)
	last_name = forms.CharField(label='last_name', max_length=50)
	dob = forms.DateField(label='dob')
