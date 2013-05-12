from django.conf.urls.defaults import patterns, include, url
from AppSemanticWebService.views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SemanticWebService.views.home', name='home'),
    # url(r'^SemanticWebService/', include('SemanticWebService.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    ('^$', test),
    (r'^base/$', show_base),
    (r'^base/Section/$', show_sections),
    (r'^base/Section/(\w+)/$', show_section), #same as show all current section elements
    (r'^base/SectionElement/(\w+)/$', show_section_element),
)
