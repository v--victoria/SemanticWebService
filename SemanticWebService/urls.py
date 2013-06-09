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
    (r'^login/$', login),                                               #login to system
    (r'^logout/$', logout),                                             #logout from system
    (r'^base/$', show_base),                                            #show main page
    (r'^base/Section/$', show_base),                                    #show main page
    (r'^base/User/(\w+)/edit/$', show_user),                            #show/edit user settings
    (r'^base/Workspace/add/$', add_workspace),                          #add workspace
    (r'^base/Workspace/(\w+)/delete/$', delete_workspace),              #delete workspace
    (r'^base/Workspace/(\w+)/$', show_workspace),                       #show workspace section elements in logical order                      
    (r'^base/Section/(\w+)/$', show_section),                           #show current section elements
    (r'^base/Section/(\w+)/delete/$', delete_section),                  #delete section
    (r'^base/(\w+)/add/$', add_section_element),                        #add new section element to current section
    (r'^base/SectionElement/(\w+)/standard/$', show_section_element),   #show section element
    (r'^base/SectionElement/(\w+)/edit/$', edit_section_element),       #edit section element
    (r'^base/SectionElement/(\w+)/delete/$', delete_section_element),   #delete section element      
)
