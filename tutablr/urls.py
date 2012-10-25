from dajaxice.core import dajaxice_autodiscover
from django.views.generic.simple import direct_to_template
from django.conf import settings
from tutablr_app.forms import ProfileForm
from tutablr_app.forms import YourRegistrationForm
from registration.views import activate
from registration.views import register
from registration.backends.default import DefaultBackend
from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns('',
	 url(r'^login$','tutablr_app.views.loginAjax'),
	 #url ( r'^calendar/user/(.*)$' , TemplateView . as_view ( template_name = "user_calendar.html" ), name = 'user_calendar' ),
	 url( r'^calendar/user/(?P<cal_id>\d+)/$', 'tutablr_app.views.calendar_view', name='user_calendar'),
	 url( r'^calendar/$', 'tutablr_app.views.calendar_user', name='calendar'),
	 url ( r'^calendar/user_events.json/(?P<cal_id>\d+)/$' , 'tutablr_app.views.user_calendar' , name = 'user_events.json' ),
	 #url ( r'^calendar/$' , login_required(TemplateView . as_view ( template_name = "calendar.html" )), name = 'calendar' ),
     	url ( r'^calendar/events.json/*$' , 'tutablr_app.views.calendar' , name = 'events.json' ),
	 url(r'^contact$',auth_views.login,{'template_name':'contact.html'},name='auth_login'), # home page
	 url(r'^submitContact$','tutablr_app.views.contactFormAjax'),
	 url(r'^get_lock/$', 'tutablr_app.views.get_lock'),
	url(r'^unlock_request/$', 'tutablr_app.views.unlock_request'),
	(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
	url(r'^$',auth_views.login,{'template_name':'index.html'},name='auth_login'), # home page
	url(r'^index$',auth_views.login,{'template_name':'index.html'},name='auth_login'), # home page
	(r'^search/$','tutablr_app.views.tutor_search'),
	#(r'^delete$','tutablr_app.views.delete'),
	#(r'^update$','tutablr_app.views.update'),
	(r'drop_event/(?P<cal_id>\d+)/$','tutablr_app.views.drop_event'),
	(r'^add_unavailable/$','tutablr_app.views.add_unavailable'),
	(r'^update_unavailable/$','tutablr_app.views.update_unavailable'),
	(r'^delete_unavailable$','tutablr_app.views.delete_unavailable'),
	(r'^update_booking/(?P<cal_id>\d+)/$','tutablr_app.views.update_booking'),
	(r'^confirm_booking/(?P<cal_id>\d+)/$','tutablr_app.views.confirm_booking'),
	(r'^reject_booking/(?P<cal_id>\d+)/$','tutablr_app.views.reject_booking'),
	(r'^add_booking/(?P<cal_id>\d+)/$','tutablr_app.views.add_booking'),
	(r'^delete_booking/(?P<cal_id>\d+)/$','tutablr_app.views.delete_booking'),
	(r'^update_session/(?P<cal_id>\d+)/$','tutablr_app.views.update_session'),
	(r'^delete_session/(?P<cal_id>\d+)/$','tutablr_app.views.delete_session'),
	('^profiles/edit', 'profiles.views.edit_profile', {'form_class': ProfileForm,}), #remove later
	(r'^profiles/', include('profiles.urls')), # remove later
	 url(r'^admin/', include(admin.site.urls)),
	 url(r'^$',auth_views.login,{'template_name':'index.html'},name='auth_login'),
	 url(r'^index$',auth_views.login,{'template_name':'index.html'},name='auth_login'),	 	
	 url(r'^messages/', include('postman.urls')),
	 url(r'^accounts/profile/', direct_to_template, {'template': 'index.html'}, 'index'),
	 url(r'^accounts/', include('registration.backends.default.urls')),
	url(r'^dashboard$','tutablr_app.views.dashboard'),
	url(r'^reviews$','tutablr_app.views.reviews'),
	url( r'^reviews/users/(?P<cal_id>\d+)/$', 'tutablr_app.views.user_reviews'),

	################# LOCATION URLS  #################
	url(r'^profile/locations$','tutablr_app.views.location'),
	#url(r'^profile/locations/tutoring/edit$','tutablr_app.views.locationSelector'),
	url(r'^profile/locations/tutoring/add$','tutablr_app.views.locationAddTutoring'),
	url(r'^profile/locations/personal/edit$','tutablr_app.views.locationEditPersonal'),
	################# LOCATION URLS  #################
)
