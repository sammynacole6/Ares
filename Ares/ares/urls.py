from django.conf.urls import patterns, url

urlpatterns = patterns('ares.views',
    url(r'^index/$', 'login'),
    url(r'^index/(?P<user_id>[0-9]+)/$', 'projectselect'),
    url(r'^index/(?P<user_id>[0-9]+)/(?P<project_id>[0-9]+)/$', 'project'),
    url(r'^index/(?P<user_id>[0-9]+)/(?P<project_id>[0-9]+)/(?P<file_id>[0-9]+)/$', 'file'),
    url(r'^index/(?P<user_id>[0-9]+)/(?P<project_id>[0-9]+)/(?P<file_id>[0-9]+)/status$', 'file_status'),
    url(r'^index/(?P<user_id>[0-9]+)/(?P<project_id>[0-9]+)/(?P<file_id>[0-9]+)/ding$', 'ding'),

    url(r'^index.js$', 'js'),
    url(r'^jquery.layout-latest.js$', 'js_layout'),
    url(r'^index.css$', 'css')
)
