from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^virtualhost/(?P<hostname>.*)/(?P<host_id>[0-9]+)', 'f5_manager.views.virtualhost'),
    url(r'', 'f5_manager.views.home'),
)
