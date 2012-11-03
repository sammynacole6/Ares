from django.conf.urls import patterns, url

urlpatterns = patterns('ares.views',
    url(r'^index/$', 'login'),
    url(r'^index/(?P<user>[0-9]+)/$', 'projectselect'),
    url(r'^index/(?P<user>[0-9]+)/(?P<project>[0-9]+)/$', 'project'),

    url(r'^index.js$', 'js'),
    url(r'^jquery.layout-latest.js$', 'js_layout'),
    url(r'^index.css$', 'css')
)
