from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^v1/ubike-station/taipei$', views.getTwoNearestStations, name='getTwoNearestStations')
]