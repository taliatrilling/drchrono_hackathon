import requests

from social.apps.django_app.default.models import UserSocialAuth

from datetime import datetime

import pytz

from .models import CheckIn, Visit


def authenticate(request):
	"""

	Authentication via OAuth Social Auth

	"""
	
	user = request.user
	try:
		drchrono_login = user.social_auth.get(provider='drchrono')
	except UserSocialAuth.DoesNotExist:
		drchrono_login = None
	except AttributeError:
		drchrono_login = None
	return drchrono_login

def get_request_headers(access_token):
	"""

	Takes in access token from OAuth, formats for API request headers

	"""

	access_token_auth = 'Bearer ' + str(access_token)
	headers = {'Authorization': access_token_auth}
	return headers

def get_name_from_patient_id(patient_id, access_token):
	"""

	For a patient id, returns the patient's full name in string form

	"""

	url = 'https://drchrono.com/api/patients_summary'
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	r = (requests.get(url, headers=headers)).json()
	for entry in r['results']:
		if int(entry['id']) == int(patient_id):
			return (str(entry['first_name']) + ' ' + str(entry['last_name']))

def get_patient_obj_from_id(patient_id, access_token):
	"""

	For a patient id, returns the full patient object from the API database

	"""

	url = 'https://drchrono.com/api/patients_summary'
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	r = (requests.get(url, headers=headers)).json()
	for entry in r['results']:
		if int(entry['id']) == int(patient_id):
			return entry

def get_office_id_for_practice(access_token):
	"""

	For a practice that has granted the application access, return the office id

	"""

	#ask: can a practice have multiple office ids? how would this change the code?

	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	offices_url = 'https://drchrono.com/api/offices'
	office_response = (requests.get(offices_url, headers=headers)).json()
	office_id = office_response['results'][0]['id']
	return office_id

def get_appt_obj(patient_id, access_token):
	"""

	For a patient id, get the full appt object for their appt scheduled for today

	"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	headers = get_request_headers(access_token)
	appts_url = 'https://drchrono.com/api/appointments' 
	data = {'date': today, 'patient': patient_id}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	for entry in r['results']:
		return entry

def get_doctor_id_from_appt(appt_id, access_token):
	"""

	For a given appt id, return the id of the doctor who is scheduled to attend to that appt

	"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	headers = get_request_headers(access_token)
	appts_url = 'https://drchrono.com/api/appointments' 
	data = {'date': today}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	for entry in r['results']:
		if entry['id'] == appt_id:
			return entry['doctor']

def get_doctors_for_practice(access_token):
	"""

	For a practice that has given the application access, return a list of doctors that is a dictionary of 
	their ids as well as last names

	"""

	headers = get_request_headers(access_token)
	doctors_url = 'https://drchrono.com/api/doctors'
	data = (requests.get(doctors_url, headers=headers)).json()
	doctors = []
	for entry in data['results']:
		doc_dict = {}
		doc_dict[int(entry['id'])] = str(entry['last_name'])
		doctors.append(doc_dict)
	return doctors

def get_todays_patients_for_doctor(doctor_id, access_token):
	"""

	For today's date and a given doctor id, returns a list of appointments -- each list element
	contains a dictionary of information relevant to the appt

	"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	headers = get_request_headers(access_token)
	appts_url = 'https://drchrono.com/api/appointments'
	office_id = get_office_id_for_practice(access_token)
	data = {'doctor': doctor_id, 'date': today, 'office': office_id}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	patients_already_seen = Visit.objects.filter(checked_in_at__icontains=today)
	seen_ids = []
	appts = []
	for p in patients_already_seen:
			seen_ids.append(int(p.appt_id))
	for entry in r['results']:
		patient_dict = {}
		if int(entry['id']) in seen_ids:
			continue
		patient_dict['appt_id'] = entry['id']
		patient_dict['time'] = entry['scheduled_time']
		patient_dict['duration'] = entry['duration']
		patient_dict['room'] = entry['exam_room']
		patient_id = entry['patient']
		patient_dict['name'] = get_name_from_patient_id(patient_id, access_token)
		patient_dict['patient_id'] = entry['patient']
		patient_dict['doctor'] = entry['doctor']
		patient_dict['checkin'] = CheckIn.objects.filter(appt_time__icontains=today, appt_id=patient_dict['appt_id'])
		for item in patient_dict['checkin']:
			patient_dict['complaint'] = item.chief_complaint
		if patient_dict['checkin'] is None:
			patient_dict['checkin'] = []
		appts.append(patient_dict)
	return appts

def get_patient_id_from_name_dob(fname, lname, dob, access_token):
	"""

	For a given first name, last name and DOB, return the patient_id or None if inputs invalid

	"""
	
	headers = get_request_headers(access_token)
	patients_url = 'https://drchrono.com/api/patients_summary'
	data = {'first_name':fname, 'last_name':lname, 'date_of_birth':dob} 
	r = (requests.get(patients_url, params=data, headers=headers)).json()
	if r['results'] == []:
		return None
	return r['results'][0]['id']

def get_patient_chart_info(doctor_id, first_name, last_name, date_of_birth, access_token):
	"""

	For a given patient, fetch chart information

	"""

	headers = get_request_headers(access_token)
	patients_url = 'https://drchrono.com/api/patients'
	data = {'doctor': doctor_id, 'first_name': first_name, 'last_name': last_name, 'date_of_birth': date_of_birth}
	r = (requests.get(patients_url, params=data, headers=headers).json())
	for entry in r['results']:
		info = {}
		info['emergency_contact_phone'] = entry['emergency_contact_phone']
		info['home_phone'] = entry['home_phone']
		info['address'] = entry['address']
		info['email'] = entry['email']
		info['cell_phone'] = entry['cell_phone']
		info['default_pharmacy'] = entry['default_pharmacy']
		info['gender'] = entry['gender']
	for k, v in info.items():
		if v == '':
			info[k] = 'Not on File'
	return info

def put_new_values_in_chart(new_values, access_token):
	"""

	Update a patient's chart

	"""

	headers = get_request_headers(access_token)
	patients_url = 'https://drchrono.com/api/patients/' + str(new_values['id'])
	r = requests.put(patients_url, data=new_values, headers=headers)
	if r.status_code == 200 or r.status_code == 204:
		return True

def compare_old_to_new_chart(old_chart, new_chart):
	"""

	Compare old to new chart, if no differences, returns None, if differences, returns a valid new dict to use for pushing to API

	"""

	changes = new_chart.viewitems() - old_chart.viewitems()
	if len(changes) != 0:
		new_values = {}
		for change in changes:
			new_values[change[0]] = change[1]
		if 'gender' not in new_values:
			new_values['gender'] = old_chart['gender']
		new_values['doctor'] = old_chart['doctor_id']
		new_values['id'] = old_chart['patient_id']
		return new_values

def format_check_in_time(naive_unformated_dt): 
	"""

	For a naive, unformated date/time, formats it so that it can be inputed as a datetime in UTC format

	"""

	checked_in_not_formatted = naive_unformated_dt[0:20]
	if checked_in_not_formatted[7] == ',':
		checked_in_not_formatted = checked_in_not_formatted[0:6] + '0' + checked_in_not_formatted[6:]
	if checked_in_not_formatted[16] == ':':
		checked_in_not_formatted = checked_in_not_formatted[0:16] + '0' + checked_in_not_formatted[16:]
	checked_in_at = datetime.strptime(checked_in_not_formatted, '%B %d, %Y, %I:%M')
	checked_in_at = pytz.utc.localize(checked_in_at)
	return checked_in_at


def add_new_appt(patient_id, doctor_id, appt_time, duration_in_min, exam_room, access_token):
	""" 

	Function to allow a doctor (or other administrator) to add an appt

	"""

	headers = get_request_headers(access_token)
	appts_url = 'https://drchrono.com/api/appointments' 
	appt_time_ISO = appt_time.isoformat()
	data = {'doctor': doctor_id, 'patient': patient_id, 'duration': duration_in_min, 'exam_room': exam_room, 
	'scheduled_time': appt_time_ISO}
	r = requests.post(appts_url, data=data, headers=headers)
	if r.status_code == 200 or r.status_code == 204:
		return True
	if r.status_code == 409:
		return 'taken'

def get_doctor_name_from_id(doctor_id, access_token):
	"""

	For a given doctor id at the authenticated practice, return the doctor's last name

	"""

	docs = get_doctors_for_practice(access_token)
	for doc in docs:
		if int(doctor_id) in doc:
			return doc[int(doctor_id)]

def get_all_patients_for_a_given_doctor(doctor_id, access_token):
	"""

	For a given doctor id, return a list of patient dictionaries (patient_id and full name)

	"""

	headers = get_request_headers(access_token)
	patients_url = 'https://drchrono.com/api/patients'
	data = {'doctor': doctor_id}
	r = (requests.get(patients_url, params=data, headers=headers)).json()
	patients = []
	for entry in r['results']:
		patient_info = {}
		patient_info['id'] = entry['id']
		patient_info['name'] = entry['first_name'] + ' ' + entry['last_name']
		patients.append(patient_info)
	return patients

def get_patient_chart_by_doc_and_patient_id(patient_id, doctor_id, access_token):
	"""

	Get patient chart info from doctor and patient ids (rather than demographic info)

	"""
	headers = get_request_headers(access_token)
	patients_url = 'https://drchrono.com/api/patients'
	data = {'doctor': doctor_id}
	r = (requests.get(patients_url, params=data, headers=headers).json())
	info = {}
	for entry in r['results']:
		if entry['id'] == int(patient_id):
			info['emergency_contact_phone'] = entry['emergency_contact_phone']
			info['home_phone'] = entry['home_phone']
			info['address'] = entry['address']
			info['email'] = entry['email']
			info['cell_phone'] = entry['cell_phone']
			info['default_pharmacy'] = entry['default_pharmacy']
			info['gender'] = entry['gender']
			for k, v in info.items():
				if v == '':
					info[k] = 'Not on File'
	return info







