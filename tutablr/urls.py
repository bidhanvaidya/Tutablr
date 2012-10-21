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
	 #url(r'^calendar/$', 'tutablr_app.views.calendar'),
	# (r'^banana/$', direct_to_template, {
        	#	'template': 'index.html'
    	#}),
	#(r'^test$', login_required(direct_to_template), {'template': 'test.html'}),
	 url(r'^login$','tutablr_app.views.loginAjax'),
	 #url ( r'^calendar/user/(.*)$' , TemplateView . as_view ( template_name = "user_calendar.html" ), name = 'user_calendar' ),
	 url( r'^calendar/user/(?P<id>\d+)/$', 'tutablr_app.views.calendar_view', name='user_calendar'),
	 url ( r'^calendar/user_events.json/(?P<id>\d+)/$' , 'tutablr_app.views.user_calendar' , name = 'user_events.json' ),
	 url ( r'^calendar/$' , login_required(TemplateView . as_view ( template_name = "calendar.html" )), name = 'calendar' ),
     url ( r'^calendar/events.json$' , 'tutablr_app.views.calendar' , name = 'events.json' ),
	(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
	url(r'^$',auth_views.login,{'template_name':'index.html'},name='auth_login'), # home page
	url(r'^index$',auth_views.login,{'template_name':'index.html'},name='auth_login'), # home page
	(r'^search$','tutablr_app.views.tutor_search'),
	
	(r'^delete$','tutablr_app.views.delete'),
	(r'^update$','tutablr_app.views.update'),
	(r'drop_event/(?P<id>\d+)/$','tutablr_app.views.drop_event'),
	(r'^add_unavailable$','tutablr_app.views.add_unavailable'),
	(r'^update_unavailable$','tutablr_app.views.update_unavailable'),
	(r'^delete_unavailable$','tutablr_app.views.delete_unavailable'),
	(r'^update_booking/(?P<other_id>\d+)/$','tutablr_app.views.update_booking'),
	(r'^confirm_booking/(?P<other_id>\d+)/$','tutablr_app.views.confirm_booking'),
	(r'^reject_booking/(?P<other_id>\d+)/$','tutablr_app.views.reject_booking'),
	(r'^add_booking/(?P<id>\d+)/$','tutablr_app.views.add_booking'),
	(r'^delete_booking/(?P<tutor_id>\d+)/$','tutablr_app.views.delete_booking'),
	(r'^update_session/(?P<other_id>\d+)/$','tutablr_app.views.update_session'),
	(r'^delete_session/(?P<tutor_id>\d+)/$','tutablr_app.views.delete_session'),
	# Examples:
	# url(r'^$', 'django_test_project.views.home', name='home'),
	# url(r'^django_test_project/', include('django_test_project.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	# Uncomment the next line to enable the admin:
	('^profiles/edit', 'profiles.views.edit_profile', {'form_class': ProfileForm,}),
	(r'^profiles/', include('profiles.urls')),
	 url(r'^admin/', include(admin.site.urls)),
	 url(r'^$',auth_views.login,{'template_name':'index.html'},name='auth_login'),
	 url(r'^index$',auth_views.login,{'template_name':'index.html'},name='auth_login'),	 	
	 url(r'^messages/', include('postman.urls')),
	 #url(r'^accounts/register/$', register,
	#	{'backend': 'registration.backends.default.DefaultBackend', 'form_class' : YourRegistrationForm},
	#	name='registration_register'),
	 url(r'^accounts/profile/', direct_to_template, {'template': 'index.html'}, 'index'),
	 url(r'^accounts/', include('registration.backends.default.urls')),
	 #url(r'^accounts/register/$', 'tutablr.views.register', {'template_name' : 'registration/register.html'}),
	 #url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name' : 'registration/login.html'}),
	 #url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name' : 'registration/logout/html'}),
	 #url(r'^accounts/profile/$', 'tutablr.views.index'),
	url(r'^dashboard$','tutablr_app.views.dashboard'),
	 #(r'^dashboard$', login_required(direct_to_template), {'template': 'dashboard.html'}),
)
