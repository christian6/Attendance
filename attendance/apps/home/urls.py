from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('attendance.apps.home.views',
	url(r'^$','view_home',name='vw_home'),
	url(r'^register/$','view_register_now',name='vw_register_now'),
	url(r'^attendance/employee/$','view_show_details_employee',name='vw_show_details_employee'),
	url(r'^report/$','view_report',name='vw_report'),
	url(r'^test/$','view_test_pdf',name='wv_test'),
	url(r'^single/$','rpt_single_hours',name='wv-single'),
	## request ajax method JSON
	url(r'^ws/request/months/$','view_getter_month'),
)