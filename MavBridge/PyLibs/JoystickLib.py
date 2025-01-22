import pygame
from time import time, sleep
import sys
from threading import Thread, Event

# Load local libraries
sys.path.append("./../PyLibs")
from Instrumentation import Inst

class JoystickButton():

    def __init__(self):
        self.pressed = False
        self.risen = False
        self.timePressed = time()
    # def

    def SetState(self,pressed):
        if(not pressed):
            self.timePressed = time()
        # if
        self.pressed = pressed
    # def

    def Pressed(self):
        return self.pressed
    # def

    def PressedSecs(self):
        return time() - self.timePressed
    # if

    def LogRisingEdge(self):
        self.risen = True
    # def

    def Risen(self):
        return self.risen
    # def

    def ClearRisen(self):
        self.risen = False
    # def

# class

class Joystick():

    def __init__(self,gearing):
        self.inst = Inst()
        self.connected = False
        pygame.init()
        pygame.joystick.init()
        numJoysticks = pygame.joystick.get_count()
        self.inst.Print(Inst.CR,"Joysticks[" + str(numJoysticks) + "]")
        if(numJoysticks>0):
            self.connected = True
            self.inst.Print(Inst.CR,"Joysticks found:" + str(numJoysticks))
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.inst.Print(Inst.CR,"Using joystick [" + str(self.joystick.get_name()) + "]")
            self.inst.Print(Inst.CR,"Axes=" + str(self.joystick.get_numaxes()) + " Buttons=" + str(self.joystick.get_numbuttons()) + " Hats=" + str(self.joystick.get_numhats()))
            self.joystick.get_axis(0)

            # Stored state utility - to go separate object
            self.mode = 1000
            self.heartbeat = 0
        # if

        # Inputs
        self.joystickGearing = gearing
        self.stickLeftX  = 1500
        self.stickLeftY  = 1500
        self.stickRightX = 1500
        self.stickRightY = 1500
        self.steerLeft   = 1000
        self.steerRight  = 1000
        self.button0 = JoystickButton()
        self.button1 = JoystickButton()
        self.button2 = JoystickButton()
        self.button3 = JoystickButton()
        self.button4 = JoystickButton()
        self.button5 = JoystickButton()
        self.button6 = JoystickButton()
        self.button7 = JoystickButton()
        self.button8 = JoystickButton()
        self.button9 = JoystickButton()
        self.hatN    = JoystickButton()
        self.hatS    = JoystickButton()
        self.hatW    = JoystickButton()
        self.hatE    = JoystickButton()

        # Start management thread 
        self.joystickThreadClose = Event()
        self.joystickThread = Thread(target=self.JoystickThread)
        self.joystickThread.setDaemon(True)
        self.joystickThread.start()
    # def

    def Connected(self):
        return self.connected
    # def

    def Stop(self):
        self.joystickThreadClose.set()
    # def

    def ReadSticks(self):
        return (self.stickLeftX,self.stickLeftY,self.stickRightX,self.stickRightY,self.steerLeft,self.steerRight)
    # def

    def ReadHat(self):
        return (self.hatX,self.hatY)
    # def

    def ReadButtonStates(self):
        state = (self.button0.Pressed(),self.button1.Pressed(),self.button2.Pressed(),self.button3.Pressed(),
                 self.button4.Pressed(),self.button5.Pressed(),self.button6.Pressed(),self.button7.Pressed(),
                 self.button8.Pressed(),self.button9.Pressed())
        return state
    # def

    def ReadButtonEdges(self):
        state = (self.button0.Risen(),self.button1.Risen(),self.button2.Risen(),self.button3.Risen(),
                 self.button4.Risen(),self.button5.Risen(),self.button6.Risen(),self.button7.Risen(),
                 self.button8.Risen(),self.button9.Risen())

        # Perform destructive read 
        self.button0.ClearRisen()
        self.button1.ClearRisen()
        self.button2.ClearRisen()
        self.button3.ClearRisen()
        self.button4.ClearRisen()
        self.button5.ClearRisen()
        self.button6.ClearRisen()
        self.button7.ClearRisen()
        self.button8.ClearRisen()
        self.button9.ClearRisen()

        return state
    # def

    def ReadHatEdges(self):
        state = (self.hatN.Risen(),self.hatS.Risen(),self.hatW.Risen(),self.hatE.Risen())

        # Perform destructive read 
        self.hatN.ClearRisen()
        self.hatS.ClearRisen()
        self.hatW.ClearRisen()
        self.hatE.ClearRisen()
 
        return state
    # def

    def Scale(self,joyStickValue):
        # Convert -1->1 to 1000-2000
        pwm = int(1500.0 + (500.0 * joyStickValue))
        if(pwm < 1000): pwm = 1000
        return int(pwm)
    #def

    def ShowState(self):
        print("Stk[%d,%d] [%d,%d] [%d,%d]"         % (self.ReadSticks()) )
        print("Hat[%d,%d]"                         % (self.ReadHat()) )
        print("Btt[%d,%d,%d,%d,%d,%d,%d,%d,%d,%d]" % (self.ReadButtonStates()) )
    # def

    def JoystickThread(self):

        # Run continuously
        while(not self.joystickThreadClose.isSet()):
            event = pygame.event.wait()
            if event.type == pygame.JOYAXISMOTION:
                instMode = Inst.OFF
                if(abs(event.value) > 0.1):
                    self.inst.Print(instMode,"AxisMotion=" + str(event.dict))
                # if

                # Throttle
                # Deadband for pitch/roll/yaw
                #print(f"AxisMotion[{event.axis}]")
                if(event.axis==0):
                    self.stickLeftX = self.Scale(event.value / self.joystickGearing) 
                elif(event.axis==1):
                    self.stickLeftY = self.Scale(-event.value / self.joystickGearing)
                elif(event.axis==2):
                    self.stickRightX = self.Scale(event.value / self.joystickGearing)
                elif(event.axis==3):
                    self.stickRightY = self.Scale(-event.value / self.joystickGearing)
                elif(event.axis==4):
                    self.steerLeft = self.Scale(event.value / self.joystickGearing)
                elif(event.axis==5):
                    self.steerRight = self.Scale(event.value / self.joystickGearing)
                # if
            elif event.type == pygame.JOYHATMOTION:
                (self.hatX,self.hatY) = event.value
                #print(f"hat[{(self.hatX,self.hatY)}]")
                if((self.hatX==0) and (self.hatY==1)):    
                    self.hatN.SetState(True)
                    self.hatN.LogRisingEdge()
                elif((self.hatX==0) and (self.hatY==-1)):    
                    self.hatS.SetState(True)
                    self.hatS.LogRisingEdge()
                elif((self.hatX==-1) and (self.hatY==0)):    
                    self.hatW.SetState(True)
                    self.hatW.LogRisingEdge()
                elif((self.hatX==1) and (self.hatY==0)):    
                    self.hatE.SetState(True)
                    self.hatE.LogRisingEdge()
                # if
            elif event.type == pygame.JOYBUTTONDOWN:
                #print(f"Button [{event.button}]")
                if(event.button==0):    
                    self.button0.SetState(True)
                    self.button0.LogRisingEdge()
                elif(event.button==1): 
                    self.button1.SetState(True)
                    self.button1.LogRisingEdge()
                elif(event.button==2): 
                    self.button2.SetState(True)
                    self.button2.LogRisingEdge()
                elif(event.button==3): 
                    self.button3.SetState(True)
                    self.button3.LogRisingEdge()
                elif(event.button==4): 
                    self.button4.SetState(True)
                    self.button4.LogRisingEdge()
                elif(event.button==5): 
                    self.button5.SetState(True)
                    self.button5.LogRisingEdge()
                elif(event.button==6): 
                    self.button6.SetState(True)
                    self.button6.LogRisingEdge()
                elif(event.button==7): 
                    self.button7.SetState(True)
                    self.button7.LogRisingEdge()
                elif(event.button==8): 
                    self.button8.SetState(True)
                    self.button8.LogRisingEdge()
                elif(event.button==9): 
                    self.button9.SetState(True)
                    self.button9.LogRisingEdge()
            elif event.type == pygame.JOYBUTTONUP:
                if(event.button==0):   self.button0.SetState(False)
                elif(event.button==1): self.button1.SetState(False)
                elif(event.button==2): self.button2.SetState(False)
                elif(event.button==3): self.button3.SetState(False)
                elif(event.button==4): self.button4.SetState(False)
                elif(event.button==5): self.button5.SetState(False)
                elif(event.button==6): self.button6.SetState(False)
                elif(event.button==7): self.button7.SetState(False)
                elif(event.button==8): self.button8.SetState(False)
                elif(event.button==9): self.button9.SetState(False)
            # Plugged
            elif(event.type==1541):
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.inst.Print(Inst.CR,"Using joystick [" + str(self.joystick.get_name()) + "]")
                self.inst.Print(Inst.CR,"Axes=" + str(self.joystick.get_numaxes()) + " Buttons=" + str(self.joystick.get_numbuttons()) + " Hats=" + str(self.joystick.get_numhats()))
                self.joystick.get_axis(0)
                self.inst.Print(Inst.CR,"Joystick connected")
                self.connected = True
            # Unplugged
            elif(event.type==1542):
                self.inst.Print(Inst.CR,"Warning! Joystick disconnected")
                self.connected = False
            # if
            sleep(0.001)
        #end while
    # def


#end class

