from django.conf.urls import include, url
from django.views.generic import TemplateView

import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),

    url(r'', include('social.apps.django_app.urls', namespace='social')),

    url(r'start', views.start, name='start'),

    url(r'^appts/(?P<doctor_id>[0-9]+)/$', views.appt_overview, name='appts'),
]
