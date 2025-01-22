# Wrapper for manipulating latitude/longitude

import math
from haversine import haversine,inverse_haversine,Unit

def MetresMetresToDegrees(y,x):

	# Convert 0-360 to -180-180
	if(y==0.0):
		rad = 90.0
	elif((x > 0.0) and (y<0.0)):
		rad =  math.atan(x/y) + math.radians(180) # radians
	elif((x < 0.0) and (y<0.0)):
		rad =  math.atan(x/y) - math.radians(180) # radians
	elif((x < 0.0) and (y>0.0)):
		rad =  math.atan(x/y)  # radians
	else:
		rad =  math.atan(x/y)  # radians
	# if

	return math.degrees(rad)
# def

def LatLonPlusMetresDegrees(lat,lon,dist,deg):
	return inverse_haversine((lat,lon), dist / 1000.0, math.radians(deg))
# def

def LatLonPlusMetresMetres(lat,lon,y,x):
	# Distance by pythagorus
	metres = math.sqrt(math.pow(x,2) + math.pow(y,2))

	# Get direction in -180-180
	degrees = MetresMetresToDegrees(y,x)

	return LatLonPlusMetresDegrees(lat,lon,metres,degrees)
# def

def LatLonsToMetres(latlon0,latlon1):
	(lat0,lon0) = latlon0
	(lat1,lon1) = latlon1
	return haversine((lat0,lon0),(lat1,lon1), unit=Unit.METERS)
# def

def LatLonsToMetresMetres(latlon0,latlon1):
	(lat0,lon0) = latlon0
	(lat1,lon1) = latlon1
	x = haversine((lat0,lon0),(lat0,lon1), unit=Unit.METERS)
	if(lon1<lon0):
		x = -x
	# if
	y = haversine((lat0,lon0),(lat1,lon0), unit=Unit.METERS)
	if(lat1<lat0):
		y = -y
	# if
	return y,x
# def

def LatLonsToDegrees(latlon0,latlon1):
	y,x = LatLonsToMetresMetres(latlon0,latlon1)
	return MetresMetresToDegrees(y,x)
# def
