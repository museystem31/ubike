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

    response = {}
    errorCode = 0
    result = []
   
    try:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        stations = getStationData()

        if not isValidLatLng(lat, lng):
            # input latlng is not valid
            errorCode = -1
            response = {"code": errorCode, "result": result}
            return JsonResponse(response)
    
        if not isInTaipeiCity(lat, lng):
            # input latlng not in Taipei City
            errorCode = -2
            response = {"code": errorCode, "result": result}
            return JsonResponse(response)

        validStations = filterStationFull(stations)

        if len(validStations)==0:
            # all stations are full
            errorCode = 1
            response = {"code": errorCode, "result": result}
            return JsonResponse(response)

        validStations = filterStationNoBike(validStations)
        result = getTwoNearestStationsHelper(lat, lng, validStations, result)
	
        response = {"code": 0, "result": result}
        return HttpResponse(json.dumps(response, indent=4, ensure_ascii=False, sort_keys=True))

    except:
        # system error

        errorCode = -3
        result = []
        response = {"code": errorCode, "result": result} 
        return JsonResponse(response)
    '''

    response = {}
    errorCode = 0
    result = []
   
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    stations = getStationData()

    if not isValidLatLng(lat, lng):
        # input latlng is not valid
        errorCode = -1
        response = {"code": errorCode, "result": result}
        return JsonResponse(response)
    
    if not isInTaipeiCity(lat, lng):
        # input latlng not in Taipei City
        errorCode = -2
        response = {"code": errorCode, "result": result}
        return JsonResponse(response)

    validStations = filterStationFull(stations)

    if len(validStations)==0:
        # all stations are full
        errorCode = 1
        response = {"code": errorCode, "result": result}
        return JsonResponse(response)

    validStations = filterStationNoBike(validStations)
    result = getTwoNearestStationsHelper(lat, lng, validStations, result)
	
    response = {"code": 0, "result": result}
    return HttpResponse(json.dumps(response, indent=4, ensure_ascii=False))
    '''


# receive ubike station data from api
def getStationData():
    url = "http://data.taipei/youbike"
    url = urllib.urlretrieve(url, "data.gz")
    jdata = gzip.open('data.gz', 'r').read()
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
    filtered = []
    '''
    for key,value in stations.iteritems():
        if int(value["bemp"]) == 0:
            stations.pop(value)
    return stations
    '''
    for key,value in stations.iteritems():
        if int(value["bemp"]) != 0:
            filtered.append(value)
    return filtered

# remove station that has no available bikes from data
def filterStationNoBike(stations):
    filtered = []
    '''
    for key,value in stations.iteritems():
        if int(value["sbi"]) == 0:
            stations.pop(value)
    return stations

    '''
    for value in stations:
        if int(value["sbi"]) != 0:
            filtered.append(value)
    return filtered

# return the nearest stations to the input latlng
def getTwoNearestStationsHelper(lat, lng, stations, result):

    nearestStations = []
    
    for value in stations:    
    #for key,value in stations.iteritems():
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
        entry = {"station": name, "num_ubike": numBike}
        result.append(entry)
	
    return result

def calculateDistance(point1,point2):
    return vincenty(point1, point2).miles
    

	