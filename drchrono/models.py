from django.db import models

from datetime import datetime

import pytz

from pytz import timezone

class CheckIn(models.Model):
	"""For a given doctor, if a patient has checked in and what time they did so 
	(to calculate patient time waiting)"""

	appt_id = models.IntegerField()
	doctor_id = models.IntegerField()
	check_in_time = models.DateTimeField()
	appt_time = models.DateTimeField()
	chief_complaint = models.CharField(max_length=500)

	def __str__(self):
		western = timezone('US/Pacific')
		tz_aware = self.check_in_time.astimezone(western)
		return tz_aware.strftime("%X")


class Visit(models.Model):
	"""Records when a doctor indicates that they are about to see a patient, used to generate average wait times
	as well as remove patients from the day's agenda"""

	appt_id = models.IntegerField()
	seen_at = models.DateTimeField()
	checked_in_at = models.DateTimeField()
	doctor_id = models.IntegerField()

	def __str__(self):
		western = timezone('US/Pacific')
		tz_aware = self.seen_at.astimezone(western)
		return tz_aware.strftime("%X")