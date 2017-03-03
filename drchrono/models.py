from django.db import models

from datetime import datetime

import pytz

from pytz import timezone

class CheckIn(models.Model):
	"""For a given doctor, if a patient has checked in and what time they did so 
	(to calculate patient time waiting)"""

	patient_id = models.IntegerField()
	doctor_id = models.IntegerField()
	check_in_time = models.DateTimeField()
	appt_time = models.DateTimeField()

	def __str__(self):
		western = timezone('US/Pacific')
		tz_aware = self.check_in_time.astimezone(western)
		return tz_aware.strftime("%X")

		