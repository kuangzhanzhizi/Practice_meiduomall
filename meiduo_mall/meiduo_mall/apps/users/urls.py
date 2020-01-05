from django.conf.urls import url
from . import views

urlpatterns = [
	url('^register/$', views.RegisterView.as_view()),
	url('^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
	url('^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCountView.as_view()),
	url('^login/$', views.LoginView.as_view()),
	url('^logout/$', views.LogoutView.as_view()),
	url('^info/$', views.UserCenterInfoView.as_view()),

]