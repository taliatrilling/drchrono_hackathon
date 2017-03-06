from django.test import TestCase

from django.test.client import Client

from django.test import LiveServerTestCase

from django.conf import settings

import os

import requests

import sys

from selenium import webdriver

from .models import CheckIn, Visit

from .logic import authenticate, get_request_headers, get_name_from_patient_id, get_patient_obj_from_id, get_office_id_for_practice, get_appt_obj, get_doctor_id_from_appt, get_doctors_for_practice, get_todays_patients_for_doctor, get_patient_id_from_name_dob, get_patient_chart_info, put_new_values_in_chart, compare_old_to_new_chart, format_check_in_time


SOCIAL_AUTH_DRCHRONO_KEY = os.environ['SOCIAL_AUTH_DRCHRONO_KEY']
PASSWORD = os.environ['DR_CHRONO_SITE_PASS']
ACCESS_TOKEN = ''

class LogicTestCase(TestCase):
	""" """

	def setUp(self):
		self.client = Client()
		# CheckIn.objects.create(appt_id=1, doctor_id=1, check_in_time='2017-03-06 00:44:12.605017', 
		# 	appt_time='2017-03-06 09:00:00', chief_complaint='stomach ache')

	#test authenticate 

	def test_get_request_headers(self):
		self.assertEqual(get_request_headers('test123'), {'Authorization': 'Bearer test123'})

	def test_get_name_from_patient_id(self):
		pass

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

	def test_home(self):
		print ACCESS_TOKEN
		session_store = create_session_store()
		session_items = session_store





