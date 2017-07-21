# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import urllib
import gzip
import json

# Create your views here.

# given a latlng input return two nearest ubike stations
def getTwoNearestStations(request):

    lat = float(request.GET.get('lat'))
    lng = float(request.GET.get('lng'))
    errorCode = 0
    response = {}
    nearestStations = []
    stations = getStationData()

    if not isValidLatLng(lat, lng):
        errorCode = -1
        response = {"code": errorCode, "result": nearestStations}
        return JsonResponse(response)
    
    if not isInTaipeiCity(lat, lng):
        errorCode = -2
        response = {"code": errorCode, "result": nearestStations}
        return JsonResponse(response)

    validStations = filterStationFull(stations)
    if len(validStations)==0:
        errorCode = 1
        response = {"code": errorCode, "result": nearestStations}
        return JsonResponse(response)

    validStations = filterStationNoBike(validStations)
    nearestStations = getTwoNearestStationsHelper(lat, lng, validStations, nearestStations)
	
    response = {"code": 0, "result": nearestStations}
    return JsonResponse(json.dumps(response), safe = False)


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


# return true if input latlng is in Taipei City, else false
def isInTaipeiCity(lat, lng):
    geolocator = Nominatim()
    location = geolocator.reverse(str(lat) + ", " + str(lng), timeout=500)
    taipei_city = "臺北市"
    return taipei_city in location.address

# remove station that is full from data
def filterStationFull(stations):
    for key,value in stations.iteritems():
        if value["bemp"] == 0:
            stations.pop(value)
    return stations

# remove station that has no available bikes from data
def filterStationNoBike(stations):
    for key,value in stations.iteritems():
        if value["sbi"] == 0:
            stations.pop(value)
    return stations

# return the nearest stations to the input latlng
def getTwoNearestStationsHelper(lat, lng, stations, nearestStations):
    result = []
    for key,value in stations.iteritems():
        station_point = (float(value["lat"]), float(value["lng"]))
        input_point = (lat, lng)
        distance = calculateDistance(station_point, input_point)
        if len(nearestStations)<2 :
            nearestStations.append([value,distance])
        elif distance<nearestStations[0][1]:
            nearestStations[0] = [value,distance]
        elif distance<nearestStations[1][1]:
            nearestStations[1] = [value,distance]
	
    for station in nearestStations:
        name = station[0]["sna"]
        numBike = station[0]["sbi"]
        entry = {"station":name, "num_ubike":numBike}
        result.append(entry)			
	return result

def calculateDistance(point1,point2):
    return vincenty(point1, point2).miles
    

	