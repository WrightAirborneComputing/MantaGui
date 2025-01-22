import tkinter
import socket
from time import time, sleep

# Load local libraries
import sys
sys.path.append("./../PyLibs")
from Instrumentation import Inst
from GuiLib import Window, Frame, Canvas, Label, Console, Logo, Button, Timer
from MapLib import MapManager
from MavlinkLib import Mavlink
from JoystickLib import Joystick

# Button controls
_enableDataRefresh = True

def ArmClicked(evt=None):
    _droneConnection.ArmDisarm(1,0) # Arm, non-emergency
#end def

def DisarmClicked(evt=None):
    _droneConnection.ArmDisarm(0,1) # Disarm, emergency
#end def

def RebootClicked():
    _droneConnection.RequestReboot() 
#end def

def SetOriginClicked():
    _droneConnection.SetDefaultGlobalOrigin(51.46700, -2.5992000, 0.0)
# SetOriginClicked

def Throttle50Clicked():
    throttlePwm        = 1500.0
    rollPwm            = 1500.0
    pitchPwm           = 1500.0
    yawPwm             = 1500.0
    _droneConnection.RcChannelOverride(channel1 = int(rollPwm), channel2 = int(pitchPwm), channel3 = int(throttlePwm), channel4 = int(yawPwm))
# def

def StartMissionClicked():
    _droneConnection.MissionStart()
#def

def MinClicked():
    _window.Min()
#def

def CloseClicked():
    _window.Close()
#def

def Throttle0Clicked():
    throttlePwm        = 1000.0
    rollPwm            = 1500.0
    pitchPwm           = 1500.0
    yawPwm             = 1500.0
    _droneConnection.RcChannelOverride(channel1 = int(rollPwm), channel2 = int(pitchPwm), channel3 = int(throttlePwm), channel4 = int(yawPwm))
    # ThrottleClicked

def QStabilizeClicked(evt=None):
    _droneConnection.SetFlightMode(1,17) 
#end def

def QHoverClicked(evt=None):
    _droneConnection.SetFlightMode(1,18) 
#end def

def QLoiterClicked(evt=None):
    _droneConnection.SetFlightMode(1,19) 
#end def

def PosHoldClicked(evt=None):
    _droneConnection.SetFlightMode(1,16) 
#end def

def QrtlClicked(evt=None):
    _droneConnection.SetFlightMode(1,21) 
#end def

def AutoClicked(evt=None):
    _droneConnection.SetFlightMode(1,3) 
#end def

def TakeoffClicked(evt=None):
    _droneConnection.TakeOff(1.0)
#end def

def LandClicked(evt=None):
    _droneConnection.Land()
#end def

def SetAltClicked(evt=None):
    _droneConnection.SetTargetPosition(1.0) 
#end def

def UpdateClock(label):
    label.Update(datetime.now().strftime("%H:%M:%S"),False)
#end def

def UpdateDataRate(label):

    # Check for update tick
    if(_dataRateTimer.Tick()==False):
        return

    # Extract profiling
    mavlinkPacketRate,mavlinkByteRate = _droneConnection.DataRate()
    videoPacketRate,videoByteRate = 0,0 # _videoConnection.outConnection.DataRate()
    label.Update("Mavlink[" + str(mavlinkPacketRate) + "/" + str(mavlinkByteRate) + "]/s Video[" + str(videoPacketRate) + "/"  + str(videoByteRate) + "]/s",True)
#end def

def UpdateAirdata(statusLabel,batteryLabel,attitudeLabel,gpsLabel,navigationLabel,rcChannelLabel):

    # Check for update tick
    if(_airDataTimer.Tick()==False):
        return
    # if

    # Unpack multi-use items
    lidarAlt   = 999.0

    # Get MavLink status
    mavlinkValid = _droneConnection.GetStatus()

    # Update status label
    modeText = _droneConnection.DecodeModeFlags()
    statusLabel.Update( "Mode[" + modeText + "]",mavlinkValid)
    if("Armed" in modeText):
        statusLabel.SetColour("orange","white")
    elif(mavlinkValid):
        attitudeLabel.SetColour("white","black")
    else:
        attitudeLabel.SetColour("white","gray")
    # end if

    # Update attitude label
    attitudeLabel.Update("Pitch[" + str(_droneConnection.pitch) + chr(176) + "] Roll[" + str(_droneConnection.roll)  + chr(176) + "] Yaw[" + str(_droneConnection.yaw) + chr(176) + "]",mavlinkValid)
    if( (_droneConnection.pitch < -45.0) or (_droneConnection.pitch > 45.0)):
        attitudeLabel.SetColour("orange","white")
    elif(mavlinkValid):
        attitudeLabel.SetColour("white","black")
    else:
        attitudeLabel.SetColour("white","gray")
    # end if
    
    # Update battery field
    batteryLabel.Update("Battery[" + str(_droneConnection.voltage) + "V]",mavlinkValid)
    if(_droneConnection.voltage < 0.1):
        batteryLabel.SetColour("green","white") # Probably bad data
    elif(_droneConnection.voltage < 10.1):
        batteryLabel.SetColour("red","white")
    elif(_droneConnection.voltage < 10.6):
        batteryLabel.SetColour("orange","white")
    elif(mavlinkValid):
        batteryLabel.SetColour("white","black")
    else:
        batteryLabel.SetColour("white","gray")
    # end if

    # Update GPS label
    gpsLabel.Update("Sats[" + str(_droneConnection.sats) + "] Speed[" + str(_droneConnection.speed) + "cm/s] Pos[" + str(_droneConnection.lat) + chr(176) + " " + str(_droneConnection.lon) + chr(176) + "]",mavlinkValid)
    if(mavlinkValid):
        gpsLabel.SetColour("white","black")
    elif(_droneConnection.fix == 0):                    # No fix
        gpsLabel.SetColour("red","white")
    elif(_droneConnection.fix == 1):                    # 2D fix
        gpsLabel.SetColour("orange","white")
    elif(mavlinkValid):
        attitudeLabel.SetColour("white","black")        # 3D fix
    else:
        attitudeLabel.SetColour("white","gray")
    # end if

    # Update navigation label
    navigationLabel.Update("AGL[" + str(_droneConnection.altAgl) + "m] ASL[" + str(_droneConnection.altAsl) + "m] GPS[" + str(_droneConnection.gpsAlt) + "m] LiDAR[" + str(_droneConnection.lidarAlt) + "m]",mavlinkValid)

    # Update raw channel label
    (stickLeftX,stickLeftY,stickRightX,stickRightY,steerLeft,steerRight) = _joystick.ReadSticks()
    rcChannelLabel.Update("Throt[" + str(_droneConnection.channel3) + "] Yaw[" + str(_droneConnection.channel4) + "] Roll[" + str(_droneConnection.channel1) + "] Pit[" + str(_droneConnection.channel2) + "] Arm[" + str(_droneConnection.channel9) + "]  Kill[" + str(_droneConnection.channel7) + "]",mavlinkValid)
    # Grey out unusable buttons
    if(_droneConnection.channel7>1900):
        rcChannelLabel.SetColour("red","white")
    else:
        rcChannelLabel.SetColour("white","black")
    # if

    # Draw map/satellite for coordinates
    image = _mapManager.GlobalMap(_droneConnection.lat,_droneConnection.lon,_droneConnection.altAgl,_droneConnection.yaw)
    
    # Update panel
    _mapCanvas.Update(mavlinkValid,image,"")

# def

def GetLocalIp():
    try:
        # Create a socket to find the local IP without internet connectivity
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Use a common local IP address for communication
            s.connect(("192.168.1.1", 80))  # Local network gateway example
            return s.getsockname()[0]
        # with
    except Exception as e:
        print(f"Error obtaining local IP address: {e}")
        return None
    # try
# def

def UpdateConsole():
    # Flush the instrumentation
    _console.Print()
# def

def UpdateMantaControl(sticks,buttons,buttonEdges,hatEdges):

    # Unpack the user inputs
    (throttle,yaw,pitch,roll,l,r) = sticks
    (button0,button1,button2,button3,button4,button5,button6,button7,button8,button9) = buttons
    (buttonEdge0,buttonEdge1,buttonEdge2,buttonEdge3,buttonEdge4,buttonEdge5,buttonEdge6,buttonEdge7,buttonEdge8,buttonEdge9) = buttonEdges
    (hatEdgeN,hatEdgeS,hatEdgeW,hatEdgeE) = hatEdges

    # Arm/Disarm
    armDisarm = _droneConnection.channel9
    if(buttonEdge3==True):
        # Flip arm-switch if button pressed
        if(armDisarm<1100):
            armDisarm = 2000
        else:
            armDisarm = 1000 # Disarm if in doubt
        # if
    # if

    # E-Stop
    emergencyStop = _droneConnection.channel7
    if(hatEdgeN or hatEdgeS or hatEdgeW or hatEdgeE):
        # Flip kill-switch if button pressed
        if(emergencyStop<1100):
            emergencyStop = 2000
        else:
            emergencyStop = 1000 # Kill if in doubt
        # if

    # if

    # Mode-change requests
    if(buttonEdge0==True):
        _droneConnection.SetFlightMode(1,18) # QHOVER
    elif(buttonEdge2==True):
        _droneConnection.SetFlightMode(1,19) # QLOITER
    # if

    # Virtual stick inputs
    _droneConnection.RcChannelSet(throttle,yaw,pitch,roll,emergencyStop,1500,armDisarm)
    _droneConnection.RcChannelOverride()
# def

def UpdateControl():

    # Send data stream request
    if(_requestDataTimer.Tick()==True):
        _droneConnection.RequestData()
    # if

    # Check for update tick
    if(_controlTimer.Tick()==False):
        return
    # if

    # Read the drone status
    modeText = _droneConnection.DecodeModeFlags()
    mavlinkValid = _droneConnection.GetStatus()

    # Grey out unusable buttons
    if("Armed" in modeText):
        _armButton.SetColour("white","gray")
        _disarmButton.SetColour("white","black")
    elif("Disarmed" in modeText):
        _armButton.SetColour("white","black")
        _disarmButton.SetColour("white","gray")
    else:
        _armButton.SetColour("white","gray")
        _disarmButton.SetColour("white","gray")
    # if

    # Proceed to control injection if joystick connected
    if(not _joystick.Connected()): return

    # Run the handset command configuration
    UpdateMantaControl(_joystick.ReadSticks(),_joystick.ReadButtonStates(),_joystick.ReadButtonEdges(),_joystick.ReadHatEdges())

# def

def Update():
    UpdateDataRate(_dataRateLabel)
    UpdateAirdata(_statusLabel,_batteryLabel,_attitudeLabel,_gpsLabel,_navigationLabel,_rcChannelLabel)
    UpdateControl()
    UpdateConsole()

    # Iterate
    _window.Update(10, Update) # run itself again 
# def

#################################
#### Start of main function ####
#################################

# Open the instrumentation system 
_inst = Inst()

# Create the main window 
_window = Window("Manta Controller")
_window.Max()

# Create map/video displays
_upperFrame   = Frame(_window,1,1)
_upperFrame.Centre(0.0,"n")
_console      = Console(_upperFrame,1,1,57,9,True) 
_mapCanvas    = Canvas(_upperFrame,2,1)
_buttonFrame  = Frame(_upperFrame,3  ,1)
_armButton       = Button(_buttonFrame,1,1,"Arm       ", ArmClicked)
_disarmButton    = Button(_buttonFrame,1,2,"Disarm    ", DisarmClicked)
_modeButton      = Button(_buttonFrame,2,1,"QStabilize", QStabilizeClicked)
_modeButton      = Button(_buttonFrame,2,2,"QHover    ", QHoverClicked)
_modeButton      = Button(_buttonFrame,2,3,"QLoiter   ", QLoiterClicked)
_minButton       = Button(_buttonFrame,3,3,"  ESC     ", CloseClicked)
#_videoCanvas = Canvas(_upperFrame,2,1)

# Create right-hand data and control frame
_lowerFrame = Frame(_window,1,2)
_lowerFrame.Centre(1.0,"s")

# Text output

# Create and populate data display frame, with separate refresh rates for each label
_dataFrame        = Frame(_lowerFrame,2,2)
_statusLabel      = Label(_dataFrame,0,1)
_attitudeLabel    = Label(_dataFrame,0,2)
_batteryLabel     = Label(_dataFrame,0,3)
_gpsLabel         = Label(_dataFrame,0,4)
_navigationLabel  = Label(_dataFrame,0,5)
_rcChannelLabel   = Label(_dataFrame,0,6)
_dataRateLabel    = Label(_dataFrame,0,7)

# Add the logo
_logo = Logo(_upperFrame,0.1,"ne",3,1,"./../PyLibs/AAV Logo.jpg")

# Create and populate lower-right
_leftFrame = Frame(_lowerFrame,1,2)
_lStick = Logo(_leftFrame,0.3,"sw",1,2,"./../PyLibs/LeftStick.jpg")

# Create and populate lower-left
_rightFrame = Frame(_lowerFrame,3,2)
_rStick = Logo(_rightFrame,0.3,"se",1,2,"./../PyLibs/RightStick.jpg")

# Connect the joystick
_joystick = Joystick(1.0)

# Select server address
serverIpAddress = GetLocalIp()

# Open the MavLink port 
_droneConnection= Mavlink(True)
_droneConnection.Connect(serverIpAddress,14550)
#_droneConnection.Connect(serverIpAddress,8)

# Open the GPS manager
_mapManager = MapManager()

# Initiate iterative updating
_dataRateTimer     = Timer(1.0)
_airDataTimer      = Timer(0.1)
_requestDataTimer  = Timer(1.0)
_controlTimer      = Timer(0.1)
_videoRefreshTime  = time()
Update()

# Run the window loop
_window.Run()

# Fall through on close - shutdown services
_droneConnection.Disconnect();
_inst.Print(Inst.CR,"GUI closing")

