import requests

from social.apps.django_app.default.models import UserSocialAuth

from datetime import datetime

def authenticate(request):
	"""Authentication"""
	
	user = request.user
	try:
		drchrono_login = user.social_auth.get(provider='drchrono')
	except UserSocialAuth.DoesNotExist:
		drchrono_login = None
	except AttributeError:
		drchrono_login = None
	return drchrono_login

def get_request_headers(access_token):
	"""Takes in access token from OAuth, formats for API request headers"""

	access_token_auth = 'Bearer ' + str(access_token)
	headers = {'Authorization': access_token_auth}
	return headers

def get_name_from_patient_id(patient_id, access_token):
	"""For a patient id, returns the patient's full name in string form"""

	url = 'https://drchrono.com/api/patients_summary'
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	r = (requests.get(url, headers=headers)).json()
	for entry in r['results']:
		if int(entry['id']) == int(patient_id):
			return (str(entry['first_name']) + ' ' + str(entry['last_name']))

def get_patient_obj_from_id(patient_id, access_token):
	"""For a patient id, returns the full patient object from the API database"""

	url = 'https://drchrono.com/api/patients_summary'
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	r = (requests.get(url, headers=headers)).json()
	for entry in r['results']:
		if int(entry['id']) == int(patient_id):
			return entry

def get_appt_id_for_patient_today(patient_id, access_token):
	"""For a patient id, return appt id for an appt scheduled for today"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	appts_url = 'https://drchrono.com/api/appointments'
	data = {'doctor': doctor_id}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	for entry in r['results']:
		if entry['patient'] == patient_id:
			return entry['id']

def get_office_id_for_practice(access_token):
	"""For a practice that has granted the application access, return the office id"""

	#ask: can a practice have multiple office ids? how would this change the code?

	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	offices_url = 'https://drchrono.com/api/offices'
	office_response = (requests.get(offices_url, headers=headers)).json()
	office_id = office_response['results'][0]['id']
	return office_id

def get_appt_obj(access_token, patient_id):
	"""For a patient id, get the full appt object for their appt scheduled for today"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	appts_url = 'https://drchrono.com/api/appointments' 
	data = {'date': today}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	for entry in r['results']:
		if entry['patient'] == patient_id:
			return entry

def get_doctor_id_from_appt(appt_id, access_token):
	"""For a given appt id, return the id of the doctor who is scheduled to attend to that appt"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	appts_url = 'https://drchrono.com/api/appointments' 
	data = {'date': today}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	for entry in r['results']:
		if entry['id'] == appt_id:
			return entry['doctor']

def get_doctors_for_practice(access_token):
	"""For a practice that has given the application access, return a list of doctors that is a dictionary of 
	their ids as well as last names"""

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
	"""For today's date and a given doctor id, returns a list of appointments -- each list element
	contains a dictionary of information relevant to the appt"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	headers = get_request_headers(access_token)
	appts_url = 'https://drchrono.com/api/appointments'
	office_id = get_office_id_for_practice(access_token)
	data = {'doctor': doctor_id, 'date': today, 'office': office_id}
	r = (requests.get(appts_url, params=data, headers=headers)).json()
	appts = []
	for entry in r['results']:
		patient_dict = {}
		patient_dict['time'] = entry['scheduled_time']
		patient_dict['duration'] = entry['duration']
		patient_dict['room'] = entry['exam_room']
		patient_id = entry['patient']
		patient_dict['name'] = get_name_from_patient_id(patient_id, access_token)
		patient_dict['appt_id'] = entry['id']
		#reflect waittimes based on check in: need to fetch check-in instance
		appts.append(patient_dict)
	return appts

def get_patient_id_from_name_dob(fname, lname, dob, access_token):
	"""For a given first name, last name and DOB, return the patient_id or None if inputs invalid"""
	
	headers = get_request_headers(access_token)
	patients_url = 'https://drchrono.com/api/patients_summary'
	data = {'first_name':fname, 'last_name':lname, 'date_of_birth':dob} 
	r = (requests.get(patients_url, parms=data, headers=headers)).json()
	return r['results']['id']

