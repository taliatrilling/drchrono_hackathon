from django.shortcuts import render, redirect

from django.views.generic.base import TemplateView

from django.template import Context

import requests

from .forms import CheckInForm

from .logic import authenticate, get_name_from_patient_id, get_patient_obj_from_id, get_office_id_for_practice, get_appt_id_for_patient_today, get_doctor_id_from_appt, get_doctors_for_practice, get_request_headers, get_todays_patients_for_doctor

from .models import CheckIn


def start(request):
	"""Landing page following authorization: navigation to both doctor's appt overview 
	page as well as the check-in page for patients"""

	drchrono_login = authenticate(request)
	
	if not drchrono_login:
		return render(request, 'error.html')

	doctors = get_doctors_for_practice(access_token)
	context = {'doctors': doctors, 'drchrono_login': drchrono_login}
	return render(request, 'start.html', context)


def check_in(request):
	"""View for patient check-in"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	return render(request, 'check_in.html')

def checked_in(request):
	"""Processes patient check-in, redirects to check-in home if patient credentials incorrect"""

	if request.method == 'POST':
		form = CheckInForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			patient = get_patient_obj_from_id(patient_id, access_token)
			office_id = get_office_id_for_doctor(access_token)
			# doctor_id = 
			appt_id = get_appt_id_for_patient_today(patient_id, office_id, doctor_id, access_token)
			check_in_obj = CheckIn(patient_id=patient['id'], )
			return render(request, 'update_chart.html', context=data)
	#error message about credentials being incorrect
	return redirect('/check-in')

def appt_overview(request, doctor_id):
	"""Appointment overview for doctors to view the day's appts as well as wait times"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	headers = get_request_headers(drchrono_login.access_token)
	office_id = get_office_id_for_practice(drchrono_login.access_token)
	appts = get_todays_patients_for_doctor(doctor_id, drchrono_login.access_token)
	context = {'appts': appts}	
	return render(request, 'appt_overview.html', context)

def update_chart(request):
	"""Landing page for patients following check-in to see if their chart needs to be updated"""

	return render(request, 'update_chart.html')







