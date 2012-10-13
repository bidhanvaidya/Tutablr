from django.conf.urls import patterns, include, url
from dajaxice.core import dajaxice_autodiscover
from django.views.generic.simple import direct_to_template
from django.conf import settings
from tutablr_app.forms import ProfileForm
from tutablr_app.forms import YourRegistrationForm
from registration.views import activate
from registration.views import register
from registration.backends.default import DefaultBackend


dajaxice_autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
	# Examples:
	# url(r'^$', 'django_test_project.views.home', name='home'),
	# url(r'^django_test_project/', include('django_test_project.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	# Uncomment the next line to enable the admin:
	('^profiles/edit', 'profiles.views.edit_profile', {'form_class': ProfileForm,}),
	(r'^profiles/', include('profiles.urls')),
	 url(r'^admin/', include(admin.site.urls)),
	 url(r'^$', direct_to_template, {'template': 'index.html'}, 'index'),
	 url(r'^index/$',  direct_to_template, {'template': 'index.html'}, 'index'),
	 #url(r'^accounts/register/$', register,
	#	{'backend': 'registration.backends.default.DefaultBackend', 'form_class' : YourRegistrationForm},
	#	name='registration_register'),
	 url(r'^accounts/profile/', direct_to_template, {'template': 'index.html'}, 'index'),
	 url(r'^accounts/', include('registration.backends.default.urls')),
	 #url(r'^accounts/register/$', 'tutablr.views.register', {'template_name' : 'registration/register.html'}),
	 #url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name' : 'registration/login.html'}),
	 #url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name' : 'registration/logout/html'}),
	 #url(r'^accounts/profile/$', 'tutablr.views.index'),
)
