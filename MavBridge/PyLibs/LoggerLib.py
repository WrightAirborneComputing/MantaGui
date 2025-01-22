import datetime

class Logger():

    def __init__(self,videoPeriod):
        self.isArmed = False
        self.armStartSecs = 0.0
        self.armStartDate = ""
        self.armStartTime = ""

        # Video logging state
        self.videoOnNotOff = False
        self.videoPeriod = videoPeriod
        self.videoLoggingRunning = False
    # def

    def MergeImages(self,image1,image2):

        # Flip BGR to RGB
        rgbImage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
        rgbImage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)

        # Resize image2 to match the first
        height, width, numChannels = rgbImage1.shape
        rgbImage2 = cv2.resize(rgbImage2,(width,height))

        # Merge
        return np.concatenate((rgbImage1,rgbImage2), axis=1)
    #def 

    def Log(self,valid,armed):

        # Armed only counts if link is valid
        confirmedArmed = valid and armed

        # Check for armed rising edge
        if((self.isArmed==False) and (confirmedArmed==True)):
            self.armStartDate = datetime.now().strftime("%d/%m/%Y")
            self.armStartTime = datetime.now().strftime("%H.%M:%S")
            _inst.Print(CR,"Armed at [" + self.armStartDate + "] [" + self.armStartTime + "]")
            self.armStartSecs = time()

        # Check for armed falling edge
        elif((self.isArmed==True) and (confirmedArmed==False)):
            armedSecs = (int)(time() - self.armStartSecs)
            if(valid):
                statusText = "Disarmed"
            else:
                statusText = "Data-loss"
            # if
            f = open(".\\Log.csv", "a+")
            f.write(self.armStartDate +"," + self.armStartTime +"," + str(armedSecs) + "," +statusText + "\n")
            f.close()
            _inst.Print(CR,statusText + " at [" + datetime.now().strftime("%d/%m/%Y %H.%M:%S") + "] after [" + str(armedSecs) + "]secs")
        # if

        # Record for edge detection
        self.isArmed = confirmedArmed
    # def

#end class

