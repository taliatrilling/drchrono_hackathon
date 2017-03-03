from django.shortcuts import render, redirect

from django.views.generic.base import TemplateView

from django.template import Context

import requests

from datetime import datetime, timedelta

import pytz

from pytz import timezone

from .forms import CheckInForm, SeeingPatient

from .logic import authenticate, get_request_headers, get_name_from_patient_id, get_patient_obj_from_id, get_office_id_for_practice, get_appt_obj, get_appt_id_for_patient_today, get_doctor_id_from_appt, get_doctors_for_practice, get_todays_patients_for_doctor, get_patient_id_from_name_dob

from .models import CheckIn, Visit



def start(request):
	"""Landing page following authorization: navigation to both doctor's appt overview 
	page as well as the check-in page for patients"""

	drchrono_login = authenticate(request)
	
	if not drchrono_login:
		return render(request, 'error.html')

	doctors = get_doctors_for_practice(drchrono_login.access_token)
	context = {'doctors': doctors, 'drchrono_login': drchrono_login}
	return render(request, 'start.html', context)


def check_in(request):
	"""View for patient check-in"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	form = CheckInForm()
	return render(request, 'check_in.html', {'form':form})

def checked_in(request):
	"""Processes patient check-in, redirects to check-in home if patient credentials incorrect"""

	drchrono_login = authenticate(request)
	if request.method == 'POST':
		form = CheckInForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			patient_id = get_patient_id_from_name_dob(data['first_name'], data['last_name'], data['dob'], drchrono_login.access_token)
			if patient_id is None:
				return redirect('/check-in') #error message
			office_id = get_office_id_for_practice(drchrono_login.access_token)
			appt_id = get_appt_id_for_patient_today(patient_id, drchrono_login.access_token)
			doctor_id = get_doctor_id_from_appt(appt_id, drchrono_login.access_token)
			appt = get_appt_obj(patient_id, drchrono_login.access_token)
			if appt is None:
				return redirect('/check-in') ## error message: no appt today?
			appt_time = appt['scheduled_time'] #indices to actually get time?
			today = datetime.now().date().strftime('%Y-%m-%d')
			if CheckIn.objects.all().filter(appt_time__icontains=today, patient_id=patient_id):
				return redirect('/check-in') #message that you've already checked in 
			check_in_obj = CheckIn(patient_id=patient_id, doctor_id=doctor_id, check_in_time=datetime.now(),
			appt_time=appt_time)
			check_in_obj.save()
			return render(request, 'update_chart.html', context=data)
	#error message if credentials are incorrect
	return redirect('/check-in')


def appt_overview(request, doctor_id):
	"""Appointment overview for doctors to view the day's appts as well as wait times"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	if request.method == 'POST':
		form = SeeingPatient(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			actual_time = data['time']
			appt_time = data['appt_time']
			appt_id = data['appt_id']
			visit_obj = Visit(appt_id=appt_id, seen_at=actual_time, appt_time=appt_time)
			visit_obj.save()
			return render(request, 'appts' + str(doctor_id))
	headers = get_request_headers(drchrono_login.access_token)
	office_id = get_office_id_for_practice(drchrono_login.access_token)
	appts = get_todays_patients_for_doctor(doctor_id, drchrono_login.access_token)
	context = {'appts': appts}	
	return render(request, 'appt_overview.html', context)

def update_chart(request):
	"""Landing page for patients following check-in to see if their chart needs to be updated"""

	return render(request, 'update_chart.html')








