from social.apps.django_app.default.models import UserSocialAuth

from django.shortcuts import render

from django.views.generic.base import TemplateView

from django.template import Context

import requests


def start(request):
	"""Landing page following authorization: navigation to both doctor's appt overview 
	page as well as the check-in page for patients"""

	user = request.user
	try:
		drchrono_login = user.social_auth.get(provider='drchrono')
	except UserSocialAuth.DoesNotExist:
		drchrono_login = None
	except AttributeError:
		drchrono_login = None
	if not drchrono_login:
		return render(request, 'error.html')

	access_token_auth = 'Bearer ' + str(drchrono_login.access_token)
	headers = {
		'Authorization': access_token_auth
	}
	doctors_url = 'https://drchrono.com/api/doctors'
	data = requests.get(doctors_url, headers=headers)
	d = data.json()
	doctors = []
	i = 1
	for entry in d['results']:
		doc_dict = {}
		doc_dict[i] = str(entry['last_name'])
		doctors.append(doc_dict)
		i += 1
	print doctors
	context = {'doctors': doctors, 'drchrono_login': drchrono_login}
	return render(request, 'start.html', context)


def check_in(request):
	""" """
	pass


def appt_overview(request, doctor_id):
	""" """

	user = request.user
	try:
		drchrono_login = user.social_auth.get(provider='drchrono')
	except UserSocialAuth.DoesNotExist:
		drchrono_login = None
	except AttributeError:
		drchrono_login = None
	if not drchrono_login:
		return render(request, 'error.html')

	return render(request, 'appt_overview.html')


