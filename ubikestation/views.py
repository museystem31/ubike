# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from geopy.geocoders import Nominatim
import urllib
import gzip
import json

# Create your views here.

# given a latlng input return two nearest ubike stations
def getTwoNearestStations(request):

    lat = float(request.GET.get('lat'))
    lng = float(request.GET.get('lng'))
    errorCode = 0
    nearestStations = []
    stations = getStationData()

    if not isValidLatLng(lat, lng):
        errorCode = -1
    
    if not isInTaipeiCity(lat, lng):
        errorCode = -2
	
    return HttpResponse(errorCode)

#TODO
# receive ubike station data from api
def getStationData():
    url = "http://data.taipei/youbike"
    url = urllib.urlretrieve(url, "data.gz")
    jdata = gzip.open('data.gz', 'r').read()
    data = json.loads(jdata)
    return data["retVal"]

# return true if input latlng is valid, else false
def isValidLatLng(lat, lng):
    return (lat<=90 and lat>=-90) and (lng<=180 and lng>=-180)

#TODO
# return true if input latlng is in Taipei City, else false
def isInTaipeiCity(lat, lng):
    geolocator = Nominatim()
    location = geolocator.reverse(str(lat) + ", " + str(lng), timeout=500)
    taipei_city = "臺北市"
    return taipei_city in location.address

	