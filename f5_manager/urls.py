from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^virtualhost/(?P<hostname>.*)/(?P<host_id>[0-9]+)', 'f5_manager.views.virtualhost'),
    url(r'^virtualhost/(?P<host_id>[0-9]+)/new_mapping', 'f5_manager.views.create_mapping'),
    url(r'^virtualhost/(?P<host_id>[0-9]+)/new_offline', 'f5_manager.views.create_offline_rule'),
    url(r'^virtualhost/enable_rule', 'f5_manager.views.enable_rule'),
    url(r'^virtualhost/disable_rule', 'f5_manager.views.disable_rule'),
    url(r'', 'f5_manager.views.home'),
)
