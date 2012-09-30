from django.conf.urls import patterns, url

urlpatterns = patterns('ares.views',
    url(r'^index.html$', 'index'),
    url(r'^index.js$', 'js'),
    url(r'^jquery.layout-latest.js$', 'js_layout'),
    url(r'^index.css$', 'css')
)
