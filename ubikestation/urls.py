from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ubike-station/taipei$', views.getTwoNearestStations, name='getTwoNearestStations')
]