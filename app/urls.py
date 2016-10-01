from django.conf.urls import url,include
from . import views as app_v


from django.contrib.auth import views
from app.forms import LoginForm


urlpatterns = [
    url(r'^$',app_v.index, name='home'),
    url(r'^login/$', views.login, {'template_name': 'app/login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/$', views.logout, {'next_page': '/app/'}, name='logout'),
    url(r'^register/$', app_v.register, name="register"),
    url(r'^success/', app_v.success, name="success"),
    url(r'^check/username/(?P<username>[-\w.]+)/$', app_v.check),
    url(r'^create/$', app_v.createPromo, name="createPromo"),
]