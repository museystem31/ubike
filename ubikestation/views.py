# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from collections import OrderedDict
import urllib
import gzip
import json

# Create your views here.

# given a latlng input return two nearest ubike stations
def getTwoNearestStations(request):

    try:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        stations = getStationData()

        if not isValidLatLng(lat, lng):
            # input latlng is not valid
            response = [("code", -1), ("result", [])]
            response = OrderedDict(response)		
            return JsonResponse(response)
    
        if not isInTaipeiCity(lat, lng):
            # input latlng not in Taipei City
            response = [("code", -2), ("result", [])]
            response = OrderedDict(response)
            return JsonResponse(response)

        validStations = filterStationFull(stations)

        if isAllNull(validStations):
            # all stations are full
            response = [("code", 1), ("result", [])]
            response = OrderedDict(response)
            return JsonResponse(response)
			
        validStations = filterStationNoBike(validStations)
        
        if isAllNull(validStations):
            # all stations either in state full or no bikes, viewed as system error
            response = [("code", -3), ("result", [])]
            response = OrderedDict(response)
            return JsonResponse(response)

        result = getTwoNearestStationsHelper(lat, lng, validStations, [])
        response = [("code",0), ("result", result)]
        response = OrderedDict(response)
        
        return HttpResponse(json.dumps(response,ensure_ascii=False), 
                            content_type="application/json;charset=utf-8")

    except:
        # system error
        response = [("code", -3), ("result", [])]
        response = OrderedDict(response)
        return JsonResponse(response)


# receive ubike station data from api
def getStationData():
    url = "http://data.taipei/youbike"
    url = urllib.urlretrieve(url, "data.gz")
    jdata = gzip.open('data.gz', 'r').read().decode('utf-8')
    data = json.loads(jdata)
    return data["retVal"]

# return true if input latlng is valid, else false
def isValidLatLng(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
        return (lat<=90 and lat>=-90) and (lng<=180 and lng>=-180)       
    except:
        return False

# return true if input latlng is in Taipei City, else false
def isInTaipeiCity(lat, lng):
    geolocator = Nominatim()
    location = geolocator.reverse(str(lat) + ", " + str(lng), timeout=180)
    taipei_city = "臺北市"
    return taipei_city in location.address

# remove station that is full from data
def filterStationFull(stations):
    for key,value in stations.iteritems():
        if int(value["bemp"]) == 0:
            stations[key] = None
    return stations

# remove station that has no available bikes from data
def filterStationNoBike(stations):
    for key, value in stations.iteritems():
        if not stations[key] is None:
            if int(value["sbi"]) == 0:
                stations[key] = None
    return stations
        

# return the nearest stations to the input latlng
def getTwoNearestStationsHelper(lat, lng, stations, result):

    nearestStations = []

    for key, value in stations.iteritems():
        if not stations[key] is None:
            station_point = (float(value["lat"]), float(value["lng"]))
            input_point = (lat, lng)
            distance = calculateDistance(station_point, input_point)
        
            if len(nearestStations)<2 :
                if len(nearestStations)<1:
                    nearestStations.append([value,distance])
                else:
                    #ensure nearestStations is in ascending order
                    if distance<nearestStations[0][1]:
                        nearestStations.append(nearestStations[0])
                        nearestStations[0] = [value,distance]
                    else:
                        nearestStations.append([value,distance])
        
            elif distance<nearestStations[0][1]:
                nearestStations[1] = nearestStations[0]
                nearestStations[0] = [value,distance]            

            elif distance<nearestStations[1][1]:
                nearestStations[1] = [value,distance]
	
    for station in nearestStations:
        name = station[0]["sna"]
        numBike = int(station[0]["sbi"])
        station = [("station", name), ("num_ubike", numBike)]
        station = OrderedDict(station)
        result.append(station)
	
    return result

def calculateDistance(point1,point2):
    return vincenty(point1, point2).miles

def isAllNull(stations):
    for key, value in stations.iteritems():
        if not stations[key] is None:
            return False
    return True
    