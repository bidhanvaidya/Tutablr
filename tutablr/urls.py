from django.conf.urls import patterns, include, url
from dajaxice.core import dajaxice_autodiscover
from django.conf import settings

dajaxice_autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
    # Examples:
    # url(r'^$', 'tutablr.views.home', name='home'),
    # url(r'^tutablr/', include('tutablr.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
