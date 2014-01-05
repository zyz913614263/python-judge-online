from django.conf.urls import *
from views import index,show_problem,top,hello,show_detail,problem_submit,problem_judge,show_status
from views import show_source,show_compileinfo

urlpatterns = patterns(
    '',
    #url(r'^index/',index),
    url(r'^$',index),
    url(r'^top',top),
    url(r'^hello',hello),
    url(r'^problem$/|^problem.html$',show_problem),
    url(r'^problem\&(\d+)',show_detail),
    url(r'^problemsubmit\&(\d+)',problem_submit),
    url(r'^judge',problem_judge),
    url(r'^status',show_status),
    url(r'^showsource\&(\d+)',show_source),
    url(r'^showcompileinfo\&(\d+)',show_compileinfo),
)
