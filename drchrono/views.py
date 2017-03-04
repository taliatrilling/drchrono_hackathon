from django.shortcuts import render, redirect

from django.views.generic.base import TemplateView

from django.template import Context

from django.contrib import messages

import requests

from datetime import datetime, timedelta

import pytz

from pytz import timezone

from .forms import CheckInForm, SeeingPatient

from .logic import authenticate, get_request_headers, get_name_from_patient_id, get_patient_obj_from_id, get_office_id_for_practice, get_appt_obj, get_appt_id_for_patient_today, get_doctor_id_from_appt, get_doctors_for_practice, get_todays_patients_for_doctor, get_patient_id_from_name_dob, get_patient_chart_info

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
				messages.error(request, 'Your first name, last name or date of birth was inputed incorrectly. Please try again.')
				return redirect('/check-in') 
			office_id = get_office_id_for_practice(drchrono_login.access_token)
			if get_appt_id_for_patient_today(patient_id, drchrono_login.access_token) is None:
				return redirect('/check-in') #don't have an appt today
			appt_id = get_appt_id_for_patient_today(patient_id, drchrono_login.access_token)
			doctor_id = get_doctor_id_from_appt(appt_id, drchrono_login.access_token)
			data['doctor_id'] = doctor_id
			appt = get_appt_obj(patient_id, drchrono_login.access_token)
			if appt is None:
				messages.error(request, 'You do not have an appointment scheduled for today.')
				return redirect('/check-in') 
			appt_time = appt['scheduled_time']
			today = datetime.now().date().strftime('%Y-%m-%d')
			if CheckIn.objects.all().filter(appt_time__icontains=today, appt_id=appt_id):
				messages.info(request, 'You have already checked in for this appointment')
				return redirect('/check-in') 
			check_in_obj = CheckIn(appt_id=appt_id, doctor_id=doctor_id, check_in_time=pytz.utc.localize(datetime.now()),
			appt_time=appt_time)
			check_in_obj.save()
			info = {'stats': get_patient_chart_info(doctor_id, data['first_name'], data['last_name'], data['dob'], drchrono_login.access_token), 'first_name': data['first_name']}
			return render(request, 'update_chart.html', context=info)
	messages.error(request, 'Your first name, last name or date of birth was inputed incorrectly. Please try again.')
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
			actual_time = data['seen_at']
			checked_in_not_formatted = data['checked_in_at']
			checked_in_not_formatted = checked_in_not_formatted[0:20]
			if checked_in_not_formatted[7] == ',':
				checked_in_not_formatted = checked_in_not_formatted[0:6] + '0' + checked_in_not_formatted[6:]
			if checked_in_not_formatted[16] == ':':
				checked_in_not_formatted = checked_in_not_formatted[0:16] + '0' + checked_in_not_formatted[16:]
			checked_in_at = datetime.strptime(checked_in_not_formatted, '%B %d, %Y, %I:%M')
			checked_in_at = pytz.utc.localize(checked_in_at)
			appt_id = data['appt_id']
			visit_obj = Visit(appt_id=appt_id, seen_at=actual_time, checked_in_at=checked_in_at, doctor_id=doctor_id)
			visit_obj.save()
			return redirect('/appts/' + str(doctor_id))
	headers = get_request_headers(drchrono_login.access_token)
	office_id = get_office_id_for_practice(drchrono_login.access_token)
	appts = get_todays_patients_for_doctor(doctor_id, drchrono_login.access_token)
	context = {'appts': appts, 'doctor': doctor_id}	
	return render(request, 'appt_overview.html', context)

def update_chart(request):
	"""Landing page for patients following check-in to see if their chart needs to be updated"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	first_name = data['first_name']
	last_name = data['last_name']
	date_of_birth = data['dob']
	doctor_id = data['doctor_id']
	access_token = drchrono_login.access_token
	info = get_patient_chart_info(doctor_id, first_name, last_name, date_of_birth, access_token)
	return render(request, 'update_chart.html', context=info)

def updated_chart(request):
	""" """

	pass
	# drchrono_login = authenticate(request)
	# if not drchrono_login:
	# 	return render(request, 'error.html')
	# if request.method == 'POST':
	# 	form = UpdateInfo(request.POST)
	# 	if form.is_valid():
	# 		data = form.cleaned_data
	# 		for k, v in data.items():
	# 			if v == 'Not on File':
	# 				continue








