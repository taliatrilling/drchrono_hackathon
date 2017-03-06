from django.test import TestCase, LiveServerTestCase, RequestFactory

from django.contrib.auth.models import AnonymousUser, User

from django.contrib.sessions.middleware import SessionMiddleware

from django.test.client import Client

from django.conf import settings

import os

import requests

import sys

import mock

from selenium import webdriver

from .models import CheckIn, Visit

from .logic import authenticate, get_request_headers, get_name_from_patient_id, get_patient_obj_from_id, get_office_id_for_practice, get_appt_obj, get_doctor_id_from_appt, get_doctors_for_practice, get_todays_patients_for_doctor, get_patient_id_from_name_dob, get_patient_chart_info, put_new_values_in_chart, compare_old_to_new_chart, format_check_in_time

from .views import start, check_in, checked_in, appt_overview, update_chart, admin_update_chart

SOCIAL_AUTH_DRCHRONO_KEY = os.environ['SOCIAL_AUTH_DRCHRONO_KEY']
PASSWORD = os.environ['DR_CHRONO_SITE_PASS']


class LogicTestCase(TestCase):
	""" """

	def setUp(self):
		self.client = Client()
		CheckIn.objects.create(appt_id=1, doctor_id=1, check_in_time='2017-03-06 00:44:12.605017', 
			appt_time='2017-03-06 09:00:00', chief_complaint='stomach ache')

	def test_get_request_headers(self):
		self.assertEqual(get_request_headers('test123'), {'Authorization': 'Bearer test123'})


class PageTestCase(TestCase):

	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create_user(username='taliatrilling', password=PASSWORD)

	def test_start(self):
		request = self.factory.get('/start')
		request.user = self.user
		response = start(request)
		self.assertEqual(response.status_code, 200)

	def test_check_in(self):
		request = self.factory.get('/check-in')
		request.user = self.user
		response = check_in(request)
		self.assertEqual(response.status_code, 200)

	# def test_checked_in(self):
	# 	request = self.factory.post('/checked-in', {'first_name': 'Amanda', 'last_name': 'Jones', 'dob': '1977-08-23'})
	# 	middleware = SessionMiddleware()
	# 	middleware.process_request(request)
	# 	request.session.save()
	# 	request.user = self.user
	# 	response = checked_in(request)
	# 	self.assertEqual(response.status_code, 200)

	def test_appt_overview(self):
		request = self.factory.get('/appts/')
		request.user = self.user
		response = appt_overview(request, doctor_id=123272)
		self.assertEqual(response.status_code, 200)

	def test_update_chart(self):
		pass

	def test_admin_update_chart(self):
		request = self.factory.get('/chart-as-admin/')
		request.user = self.user
		response = admin_update_chart(request, patient_id=63252598, doctor_id=123272)
		self.assertEqual(response.status_code, 200)


class ServerTestCase(LiveServerTestCase):
	""" """
	#help from http://stackoverflow.com/questions/14320873/how-to-create-session-variables-in-selenium-django-unit-test

	def setUp(self):
		self.browser = webdriver.Chrome('/Users/taliatrilling/Downloads/chromedriver') 
		self.browser.implicitly_wait(5)
		self.client = Client()

	def tearDown(self):
		self.browser.implicitly_wait(5)
		self.browser.quit()







