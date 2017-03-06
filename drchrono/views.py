from django.shortcuts import render, redirect

from django.views.generic.base import TemplateView

from django.template import Context

from django.contrib import messages

import requests

from datetime import datetime #timedelta

import pytz

from .forms import CheckInForm, SeeingPatient, UpdateInfo, NewAppt

from .logic import authenticate, get_request_headers, get_name_from_patient_id, get_patient_obj_from_id, get_office_id_for_practice, get_appt_obj, get_doctor_id_from_appt, get_doctors_for_practice, get_todays_patients_for_doctor, get_patient_id_from_name_dob, get_patient_chart_info, put_new_values_in_chart, compare_old_to_new_chart, format_check_in_time, add_new_appt, get_doctor_name_from_id, get_all_patients_for_a_given_doctor

from .models import CheckIn, Visit


def start(request):
	"""

	Landing page following authorization: navigation to both doctor's appt overview 
	page as well as the check-in page for patients

	"""

	drchrono_login = authenticate(request)
	
	if not drchrono_login:
		return render(request, 'error.html')

	doctors = get_doctors_for_practice(drchrono_login.access_token)
	return render(request, 'start.html', context={'doctors': doctors, 'drchrono_login': drchrono_login})


def check_in(request):
	"""

	View for patient check-in

	"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	form = CheckInForm()
	return render(request, 'check_in.html', {'form':form})

def checked_in(request):
	"""

	Processes patient check-in, redirects to check-in home if patient credentials incorrect

	"""

	drchrono_login = authenticate(request)
	if request.method == 'POST':
		form = CheckInForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			patient_id = get_patient_id_from_name_dob(data['first_name'], data['last_name'], data['dob'], drchrono_login.access_token)
			office_id = get_office_id_for_practice(drchrono_login.access_token)
			if patient_id is None: #checking that they are a patient/inputed their info correctly
				messages.error(request, 'Your first name, last name or date of birth was inputed incorrectly. Please try again.')
				return redirect('/check-in') 
			if get_appt_obj(patient_id, drchrono_login.access_token) is None: #checking that they have an appt today
				messages.error(request, 'You do not have an appointment scheduled for today.')
				return redirect('/check-in')
			appt = get_appt_obj(patient_id, drchrono_login.access_token)
			doctor_id = get_doctor_id_from_appt(appt['id'], drchrono_login.access_token)
			today = datetime.now().date().strftime('%Y-%m-%d')
			if CheckIn.objects.all().filter(appt_time__icontains=today, appt_id=appt['id']): #checking to see if the database already has an obj for their check in
				messages.info(request, 'You have already checked in for this appointment')
				return redirect('/check-in') 
			check_in_obj = CheckIn(appt_id=appt['id'], doctor_id=doctor_id, check_in_time=pytz.utc.localize(datetime.now()),
			appt_time=appt['scheduled_time'], chief_complaint=data['complaint'])
			check_in_obj.save()

			stats = get_patient_chart_info(doctor_id, data['first_name'], data['last_name'], data['dob'], drchrono_login.access_token)
			chart = {}
			for k, v in stats.items():
				chart[k] = v
			chart['patient_id'] = patient_id
			chart['doctor_id'] = doctor_id
			request.session['chart'] = chart 
			return render(request, 'update_chart.html', context={'first_name': data['first_name'], 'form': UpdateInfo(initial=chart)})

	messages.error(request, 'You are using an invalid method to access the check-in route, please try again.')
	return redirect('/check-in')


def appt_overview(request, doctor_id):
	"""

	Appointment overview for doctors to view the day's appts as well as wait times

	"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	if request.method == 'POST':
		form = SeeingPatient(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			actual_time = data['seen_at']
			checked_in_at = format_check_in_time(data['checked_in_at'])
			visit_obj = Visit(appt_id=data['appt_id'], seen_at=actual_time, checked_in_at=checked_in_at, doctor_id=doctor_id)
			visit_obj.save()
			messages.info(request, 'Your portal has been updated to reflect that you have begun this appointment')
			return redirect('/appts/' + str(doctor_id))
	headers = get_request_headers(drchrono_login.access_token)
	office_id = get_office_id_for_practice(drchrono_login.access_token)
	appts = get_todays_patients_for_doctor(doctor_id, drchrono_login.access_token)
	#I want to refactor this form to use the forms.py formatting but I'm not sure how to use it so that it creates one for each patient
	return render(request, 'appt_overview.html', context={'appts': appts, 'doctor': doctor_id})

def update_chart(request):
	"""

	Landing page for patients following check-in to see if their chart needs to be updated

	"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	access_token = drchrono_login.access_token
	if request.method == 'POST':
		form = UpdateInfo(request.POST)
		if form.is_valid():
			original_values = request.session.get('chart')
			data = form.cleaned_data
			if compare_old_to_new_chart(original_values, data):
				new_values = compare_old_to_new_chart(original_values, data)
				print new_values
				success = put_new_values_in_chart(new_values, drchrono_login.access_token)
				if success:
					messages.info(request, 'Your chart was successfully updated.')
					del request.session['chart']
					return redirect('/check-in')
				else:
					messages.error(request, 'Your chart failed to update')
					return redirect('/check-in')
			del request.session['chart']
			return redirect('/check-in')
		del request.session['chart']
		messages.error(request, 'Your new chart data was entered in an invalid way, please alert your doctor that you need your chart updated.')
		return redirect('/check-in')
	del request.session['chart']
	messages.error(request, 'You are using an invalid method to update your chart, please alert your doctor that you need your chart updated.')
	return redirect('/check-in')

def add_new_visit(request, doctor_id):
	"""
	"""

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	if request.method == 'POST':
		pass
	patients = [(x['id'], x['name']) for x in get_all_patients_for_a_given_doctor(doctor_id, drchrono_login.access_token)]
	form = NewAppt(patients, initial={'doctor': doctor_id})
	doc_name = get_doctor_name_from_id(doctor_id, drchrono_login.access_token)
	return render(request, 'new_visit.html', context={'form': form, 'doc_name': doc_name, 'doctor_id': doctor_id})

def update_chart_as_admin(request):
	pass

