from django.shortcuts import render

from django.views.generic.base import TemplateView

from django.template import Context

import requests

from .forms import CheckInForm

from datetime import datetime

from .logic import authenticate, get_name_from_patient_id


def start(request):
	"""Landing page following authorization: navigation to both doctor's appt overview 
	page as well as the check-in page for patients"""

	drchrono_login = authenticate(request)
	
	if not drchrono_login:
		return render(request, 'error.html')

	access_token_auth = 'Bearer ' + str(drchrono_login.access_token)
	headers = {'Authorization': access_token_auth}
	doctors_url = 'https://drchrono.com/api/doctors'
	data = requests.get(doctors_url, headers=headers)
	d = data.json()
	doctors = []
	for entry in d['results']:
		doc_dict = {}
		doc_dict[int(entry['id'])] = str(entry['last_name'])
		doctors.append(doc_dict)
	context = {'doctors': doctors, 'drchrono_login': drchrono_login}
	return render(request, 'start.html', context)


def check_in(request):
	""" """
	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	return render(request, 'check_in.html')

def checked_in(request):
	""" """

	if request.method == 'POST':
		form = CheckInForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			return render(request, 'update_chart.html', context=data)
	return render(request, 'error.html')

def appt_overview(request, doctor_id):
	""" """

	drchrono_login = authenticate(request)
	if not drchrono_login:
		return render(request, 'error.html')
	access_token = str(drchrono_login.access_token)
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	today = datetime.now().date().strftime('%Y-%m-%d')
	offices_url = 'https://drchrono.com/api/offices'
	office_response = (requests.get(offices_url, headers=headers)).json()
	office_id = office_response['results'][0]['id']
	appts_url = 'https://drchrono.com/api/appointments'
	data = {
		'doctor': doctor_id,
		'date': today,
		'office': office_id,
	}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	appts = []
	for entry in r['results']:
		patient_dict = {}
		patient_dict['time'] = entry['scheduled_time']
		patient_dict['duration'] = entry['duration']
		patient_dict['room'] = entry['exam_room']
		patient_id = entry['patient']
		patient_dict['name'] = get_name_from_patient_id(patient_id, access_token)
		#reflect waittimes based on check in
		appts.append(patient_dict)
	print appts
	context = {'appts': appts}	
	return render(request, 'appt_overview.html', context)

def update_chart(request):
	""" """

	return render(request, 'update_chart.html')







