from datetime import datetime

from django import template

import pytz

register = template.Library()


@register.filter
def calculate_wait_time(check_in_obj):
	""" """

	time_checked_in = check_in_obj[0].check_in_time
	time_now = pytz.utc.localize(datetime.now())
	wait_time = time_now - time_checked_in
	return int((wait_time.total_seconds())/60)

@register.filter
def get_today_avg_waittime(doctor_id):
	""" """

	today = datetime.now().date().strftime('%Y-%m-%d')
	patients_already_seen = Visit.objects.all().filter(appt_time__icontains=today, doctor_id=doctor_id)
	waittimes = []
	for patient in patients_already_seen:
		patient.seen_at - patient.
	