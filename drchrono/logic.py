import requests

from social.apps.django_app.default.models import UserSocialAuth

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

def get_name_from_patient_id(patient_id, access_token):
	""" """

	url = 'https://drchrono.com/api/patients_summary'
	access_token_auth = 'Bearer ' + access_token
	headers = {'Authorization': access_token_auth}
	r = (requests.get(url, headers=headers)).json()
	for entry in r['results']:
		if int(entry['id']) == int(patient_id):
			return (str(entry['first_name']) + ' ' + str(entry['last_name']))