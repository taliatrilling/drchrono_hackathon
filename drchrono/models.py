from django.db import models

class CheckIn(models.Model):
	"""For a given doctor, if a patient has checked in and what time they did so 
	(to calculate patient time waiting)"""

	patient_id = models.IntegerField()
	doctor_id = models.IntegerField()
	check_in_time = models.DateTimeField(auto_now = True)
	appt_time = models.DateTimeField()

	def __str__(self):
		return self.check_in_time

		