import cv2
import numpy as np
import math
from HaversineLib import LatLonPlusMetresDegrees

# List of maps, populated by MapsTable
_globalMapList = []

class Coordinate:

	def __init__(self,x,y): 
		self.x = x
		self.y = y
	# end def 

# end class

class Bounds:

	def __init__(self,topLeft,botRight): 
		self.topLeft  = topLeft
		self.botRight = botRight
		self.centreX = (self.botRight.x + self.topLeft.x) / 2
		self.width   = self.botRight.x - self.topLeft.x
		self.height  = self.topLeft.y  - self.botRight.y
		self.centreY = (self.topLeft.y  + self.botRight.y) / 2
	# end def 

	def IsInside(self,x,y):
		
		# Check for beyond North
		if(y > self.topLeft.y):
			return False
		# Check for beyond South
		elif (y < self.botRight.y):
			return False
		# Check for beyond East
		elif (x > self.botRight.x):
			return False
		# Check for beyond West
		elif (x < self.topLeft.x):
			return False

		# All tests passed - is inside
		return True

	# end def

	def RatioCoordinate(self,x,y):

		# Calculate x coordinate as ratio of width
		xCentreRatio = (self.centreX - self.topLeft.x) / self.width
		xOffsetRatio = (x - self.topLeft.x) / self.width
		xRatio = (x - self.topLeft.x) / self.width

		# Calculate y coordinate as ratio of height
		yRatio = (y - self.botRight.y) / self.height

		# Flip upward axis of map to downward axis of image
		yRatio = 1.0 - yRatio 

		return xRatio,yRatio
	#end def

# end class

class Map:

	def __init__(self,mapFileName): 

		# Create a background to scribble on
		if(mapFileName==None):
			self.height = 603  # Chosen to match a typical global map
			self.width  = 1364 #                "                   "
			self.numChannels = 3
			self.baseImage = np.zeros((self.height,self.width,self.numChannels), np.uint8)
			self.baseImage[:] = (255,255,255)
		else:
			print("Loading " + mapFileName)
			self.baseImage = cv2.cvtColor(cv2.imread(mapFileName), cv2.COLOR_BGR2RGB)
			self.height, self.width, self.numChannels = self.baseImage.shape
		#end if

		# Create bounds field
		self.bounds = None

	# end def 

	def DrawPositionMarker(self,xRatio,yRatio,z,angle,redNotBlue):

		# Calculate pixel position on image
		x = int(self.width  * xRatio)
		y = int(self.height * yRatio)
		position = (x,y)
		
		# Draw target symbol
		armLen = 40
		if(redNotBlue):
			colour = (255,0,0)
		else:
			colour = (0,0,255)
		# if
		thickness = 3
		cv2.circle(self.scratchImage, position, int(armLen/2), colour, thickness) 
		cv2.circle(self.scratchImage, position, int(armLen/4), colour, thickness) 

		# Draw heading arm
		angle = angle - 90.0
		angleRadians = angle * 3.14159265359 / 180.0 
		x2 = x + int(armLen * math.cos(angleRadians))
		y2 = y + int(armLen * math.sin(angleRadians))
		cv2.line(self.scratchImage, (x, y), (x2, y2), colour, thickness) 

		# Add vertical as text
		font                   = cv2.FONT_HERSHEY_SIMPLEX
		fontScale              = 1
		lineType               = 2
		cv2.putText(self.scratchImage, str(round(z, 2)) + "m", (x + int(armLen/2),y - int(armLen/2)), font, fontScale, colour, lineType)

	#end def

	def DrawGridMarker(self,x,y,shade,addCircle):

		# Select appearance
		armLen    = int(10)
		thickness = int(1)
		colour    = (shade,shade,shade)
		
		# Get location on map as ratio of width/height
		xRatio,yRatio = self.bounds.RatioCoordinate(x,y)

		# Calculate pixel position on image
		x = int(self.width  * xRatio)
		y = int(self.height * yRatio)
		position = (x,y)
		
		# Draw arms
		armLen = 10
		x1 = x + armLen
		x2 = x - armLen
		y1 = y + armLen
		y2 = y - armLen
		cv2.line(self.baseImage, (x,  y1), (x,  y2), colour, thickness) 
		cv2.line(self.baseImage, (x1, y ), (x2, y ), colour, thickness) 

		# Draw circle
		if(addCircle):
			cv2.circle(self.baseImage, (x,y) , armLen, colour, thickness) 
		#end if

	# end def

	def AddGrid(self,separation):

		# Calculate start/end in each dimensions
		xStart = int((self.bounds.topLeft.x)  / separation) - 1
		xEnd   = int((self.bounds.botRight.x) / separation) + 1
		yStart = int((self.bounds.botRight.y) / separation) - 1
		yEnd   = int((self.bounds.topLeft.y)  / separation) + 1

		# Populate with 1-unit markers
		colour = (200,200,200) # Pale grey
		for i in range(xStart,xEnd):
			for j in range(yStart,yEnd):
				self.DrawGridMarker(i * separation,j * separation, 200, False)
			# end for
		# end for

		# Add origin in different shade
		self.DrawGridMarker(0.0,0.0,50,True)

	# end def 

	def AspectRatio(self):
		return self.width / self.height 
	# end def

	def MarkedImage(self,lon,lat,z,heading,circleLon,circleLat,circleRad):

		# Create a scratch copy to scribble on 
		self.scratchImage = self.baseImage.copy()
		
		# Get location on map as ratio of width/height
		xRatio,yRatio = self.bounds.RatioCoordinate(lon,lat)

		# Scribble on scratch image
		self.DrawPositionMarker(xRatio,yRatio,z,heading,True)

		if(circleLon != None):

			# Select appearance
			thickness = int(2)
			colour = (0,0,255)
		
			# Calculate pixel position on image
			xRatio,yRatio = self.bounds.RatioCoordinate(circleLon,circleLat)
			centreX = int(self.width  * xRatio)
			centreY = int(self.height * yRatio)
			centre = (centreX,centreY)

			# Calculate circle radius on image
			(circEdgeLat,circEdgeLon) = LatLonPlusMetresDegrees(circleLat,circleLon,circleRad,90.0)
			xRatioCirc,yRatio = self.bounds.RatioCoordinate(circleLon,0)
			xRatioEdge,yRatio = self.bounds.RatioCoordinate(circEdgeLon,0)
			radius = int(self.width  * math.fabs(xRatioCirc - xRatioEdge))
		
			# Draw circle
			cv2.circle(self.baseImage, centre , radius, colour, thickness) 

		# if

		# Report image for painting
		return self.scratchImage

	# end def 

	def MarkedImage2(self,x1,y1,z1,h1,x2,y2,z2,h2):

		# Create a scratch copy to scribble on 
		self.scratchImage = self.baseImage.copy()
		
		# Get locations on map as ratio of width/height
		xRatio1,yRatio1 = self.bounds.RatioCoordinate(x1,y1)
		xRatio2,yRatio2 = self.bounds.RatioCoordinate(x2,y2)

		# Scribble on scratch image
		self.DrawPositionMarker(xRatio1,yRatio1,z1,h1,False)
		self.DrawPositionMarker(xRatio2,yRatio2,z2,h2,True)

		# Report image for painting
		return self.scratchImage

	# end def 

# end class

class GlobalMap:

	def __init__(self,topLeftLat,topLeftLong,botRightLat,botRightLong,fileName): 
		self.fileName   = "./../PyLibs/Maps/" + fileName
		self.map        = Map(self.fileName)

		# Note swap of latitude/longitude to x/y
		self.map.bounds = Bounds( Coordinate(topLeftLong,topLeftLat), Coordinate(botRightLong,botRightLat) )
	# end def 

# end class

class LocalMap:

	def __init__(self,xCoord,yCoord): 

		# Create blank map
		self.map = Map(None)

		# Calculate dimensions (metres)
		self.width = 100.0;
		self.height  = self.width / self.map.AspectRatio()

		# Calculate local map bounds (metres)
		self.topLeft    = Coordinate( -(self.width/2),  self.height/2  )
		self.botRight   = Coordinate(   self.width/2 ,-(self.height/2) )
		self.map.bounds = Bounds(self.topLeft,self.botRight)

		# Add 1-unit (metres in this context) markers
		self.map.AddGrid(1.0)

	# end def 

# end class

class MapManager:

	def __init__(self): 
		pass
	# end def 

	def BlankMap(self):
		# Create a default map background
		return Map(None).baseImage
	# end def

	def DrawLocalMap(self,longitude,latitude,altitude,heading):

		# Create a local map and mark with live info
		localMap    = LocalMap(longitude,latitude)
		markedImage = localMap.map.MarkedImage(longitude,latitude,altitude,heading,None,None,None)

		# Report
		return markedImage 
	# end def

	def DrawGlobalMap(self,latitude,longitude,altitude,heading):

		# Scan global map list for one containing the coordinates
		for globalMap in _globalMapList:
			if(globalMap.map.bounds.IsInside(longitude,latitude)):
				# Mark with live info
				markedImage = globalMap.map.MarkedImage(longitude,latitude,altitude,heading,None,None,None)
				return markedImage
			# end if
		# end for

		# Error
		_inst.Print(CR,"No map found for Lat=" + str(latitude) + " Long=" + str(longitude))
		return None
	# end def 

	def GlobalMap(self,lat1,lon1,alt1,head1):

		# ROZ at Brigade Hill Fort Irwin
		rozLat = 35.319167
		rozLon = -116.6125
		rozRad = 250.0

		# Stub for dev
		#(lat1,lon1) = LatLonPlusMetresDegrees(rozLat,rozLon,100.0,-45.0)
		#alt1 = 0.123
		#head1 = 45

		# Scan global map list for one containing the coordinates
		for globalMap in _globalMapList:
			if(globalMap.map.bounds.IsInside(lon1,lat1)):
				# Mark with live info
				markedImage = globalMap.map.MarkedImage(lon1,lat1,alt1,head1,rozLon,rozLat,rozRad)
				return markedImage
			# end if
		# end for

		# Error
		_inst.Print(CR,"No map found for Lat=" + str(lat1) + " Long=" + str(lon1))
		return None
	# end def 

	def GlobalMap2(self,lat1,lon1,alt1,head1,lat2,lon2,alt2,head2):

		# Scan global map list for one containing the coordinates
		for globalMap in _globalMapList:
			if(globalMap.map.bounds.IsInside(lon1,lat1) and globalMap.map.bounds.IsInside(lon2,lat2)):
				# Mark with live info
				markedImage = globalMap.map.MarkedImage2(lon1,lat1,alt1,head1,lon2,lat2,alt2,head2)
				return markedImage
			# end if
		# end for

		# Error
		_inst.Print(CR,"No map found for Lat=" + str(latitude) + " Long=" + str(longitude))
		return None
	# end def 

# end class

# Load table of maps
exec(open("./../PyLibs/Maps/MapsTable.py").read())
