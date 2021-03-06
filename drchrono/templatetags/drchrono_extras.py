from datetime import datetime, timedelta

from django import template

import pytz

from ..models import Visit, CheckIn

register = template.Library()


@register.filter
def calculate_wait_time(check_in_obj):
	"""Calculate the current amount of time a patient has been waiting"""

	time_checked_in = check_in_obj[0].check_in_time
	time_now = pytz.utc.localize(datetime.now())
	wait_time = time_now - time_checked_in
	return int((wait_time.total_seconds())/60)

@register.filter
def get_today_avg_waittime(doctor_id):
	"""Calculate the day's average wait time for patients"""

	today = datetime.now().date().strftime('%Y-%m-%d')
	patients_already_seen = Visit.objects.all().filter(checked_in_at__icontains=today, doctor_id=doctor_id)
	patients_waiting = CheckIn.objects.all().filter(check_in_time__icontains=today, doctor_id=doctor_id)
	waittimes = []
	appts_seen = []
	for patient in patients_already_seen:
		wait = patient.seen_at - patient.checked_in_at 
		print patient.seen_at
		print patient.checked_in_at
		waittimes.append(wait)
		appts_seen.append(patient.appt_id)
	for patient in patients_waiting:
		if patient.appt_id in appts_seen:
			continue
		else:
			wait = pytz.utc.localize(datetime.now()) - patient.check_in_time
			waittimes.append(wait)
	if len(waittimes) == 0:
		return 0
	total = timedelta(seconds=0)
	print waittimes
	for wait in waittimes:
		total = total + wait
	avg = total/(len(waittimes))
	time = int((avg.total_seconds())/60)
	return time


