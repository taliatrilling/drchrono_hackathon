from django import forms


class CheckInForm(forms.Form):
	first_name = forms.CharField(label='First name:', max_length=50)
	last_name = forms.CharField(label='Last name:', max_length=50)
	dob = forms.DateField(label='Date of Birth:')
	complaint = forms.CharField(label='What is the primary reason for your visit?', max_length=500)

class SeeingPatient(forms.Form):
	seen_at = forms.CharField(widget=forms.HiddenInput())
	appt_id = forms.CharField(widget=forms.HiddenInput())
	checked_in_at = forms.CharField(widget=forms.HiddenInput())
	doctor_id = forms.CharField(widget=forms.HiddenInput())

class UpdateInfo(forms.Form):
	address = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Current address:', max_length=100)
	email = forms.EmailField(widget=forms.TextInput(attrs={'size':80}), label='Email address:', max_length=100)
	home_phone = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Home phone number:', max_length=20)
	cell_phone = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Cell phone number:', max_length=20)
	emergency_contact_phone = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Emergency contact phone number:', max_length=20)
	default_pharmacy = forms.CharField(widget=forms.TextInput(attrs={'size':80}), label='Preferred pharmacy:', max_length=100)
	gender = forms.ChoiceField(choices=[('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')], label='Gender:')
	doctor_id = forms.IntegerField(widget=forms.HiddenInput())

