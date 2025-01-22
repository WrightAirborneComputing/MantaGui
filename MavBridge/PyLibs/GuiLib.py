import sys
import os
import tkinter
from time import time
import cv2
import numpy as np
from tkinter import Canvas
from tkinter import PhotoImage

class Window:

    def __init__(self,title): 
        self.tkObj = tkinter.Tk()
        self.tkObj.configure(background='black')
        self.tkObj.title(title)
    # def 

    def Max(self):
        self.tkObj.attributes('-fullscreen',True)
    # def 

    def Min(self):
        self.tkObj.attributes('-fullscreen',False)
    # def 

    def ConnectKey(self,key,func):
        self.tkObj.bind(key, func)
    # def 

    def Run(self):
        self.tkObj.mainloop()
    # def 

    def Update(self,delay,cmd):
        self.tkObj.after(delay, cmd) 
    # def 

    def Close(self):
        self.tkObj.destroy()
    # def 

# class

class Canvas:

    def __init__(self,host,col,row): 
        #scaler = 0.9
        scaler = 0.4
        self.width = int(1365 * scaler)
        self.height = int(605 * scaler)
        self.tkObj = tkinter.Canvas(host.tkObj, width = self.width, height = self.height, bg="black", borderwidth=4, relief="groove")
        self.tkObj.grid(column=col, row=row, padx=10, pady=10)

        # Create static image storage area 
        self.pilImage = None
        self.canvasImage = self.tkObj.create_image(0, 0, anchor=tkinter.NW)  # Create a placeholder image in Canvas

    # def 

    def Update(self, imageValid, updateImage, osd):
        # Check for null image
        if not imageValid:
            canvasImage = np.zeros((self.height, self.width, 3), np.uint8)
            canvasImage[:] = (0, 0, 0)

            # Add warning text
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            colour = (255, 0, 0)
            lineType = 2
            text = "NO DATA"
            textSize = cv2.getTextSize(text, font, fontScale, lineType)[0]
            textX = int(self.width / 2) - int(textSize[0] / 2)
            textY = int(self.height / 2) + int(textSize[1] / 2)
            cv2.putText(canvasImage, text, (textX, textY), font, fontScale, colour, lineType)
        else:
            try:
                # Resize to the canvas
                canvasImage = cv2.resize(updateImage, (self.width, self.height))

                # Add On-screen-display text
                if osd != "":
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    fontScale = 0.5
                    colour = (255, 0, 0)
                    lineType = 2
                    textX = 20
                    textY = 20
                    cv2.putText(canvasImage, osd, (textX, textY), font, fontScale, colour, lineType)
            except Exception as e:
                print(f"Bad image size: {str(len(updateImage))}, error: {e}")
                return  # Exit on error
            # try
        # if

        # Convert BGR (OpenCV) to RGB for Tkinter
        #canvasImage = cv2.cvtColor(canvasImage, cv2.COLOR_BGR2RGB)

        # Convert NumPy array to byte data
        photo = PhotoImage(width=self.width, height=self.height)
        photo.put(" ".join(["{" + " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in row) + "}" for row in canvasImage]))

        # Add image to the Canvas
        self.tkObj.itemconfig(self.canvasImage, image=photo)
        self.tkObj.image = photo  # Keep a reference to avoid garbage collection
    #def

# class

class Frame:

    def __init__(self,host,col,row): 
        self.host = host
        self.tkObj = tkinter.Frame(host.tkObj, bg="gray", borderwidth=4, relief="groove")
        self.tkObj.configure(background='black')
        self.tkObj.grid(column=col, row=row, padx=10, pady=10)
    # def 

    def Centre(self,yPos,anchor):
        self.tkObj.place(relx=0.5, rely=yPos, anchor=anchor)
    # def

    def Update(self):
        pass
    # def 

# class

class Label:

    def __init__(self,host,col,row,labelWidth=60): 
        self.tkObj = tkinter.Label(host.tkObj, width=labelWidth, bg="white", borderwidth=4, relief="groove", anchor="w", font=("Helvetica", 10))
        self.tkObj.grid(column=col, row=row, padx=2, pady=2)
    # def 

    def Update(self,text,valid):

        # Only display if valid
        if(valid==False):
            self.SetColour("white","gray")
        else:
            self.SetColour("white","black")

            # Record update for refresh timer
            self.lastRefresh = time()
        # end if 
        self.tkObj.config(text=text)

        # Force repaint of label
        self.tkObj.update()

    # def 

    def SetColour(self,bgColour,fgColour):
        self.tkObj.configure(bg=bgColour,fg=fgColour)
    # def 

# class

class Logo:
    def __init__(self, host, scaler, sticky, col, row, path):
        try:
            # Load the image using OpenCV
            img = cv2.imread(path)

            if img is None:
                raise ValueError(f"Unable to load image from path: {path}")

            # Convert the image from BGR to RGB (Tkinter requires RGB format)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Calculate new dimensions
            new_width = int(img.shape[1] * scaler)
            new_height = int(img.shape[0] * scaler)

            # Resize the image to the desired dimensions
            img = cv2.resize(img, (new_width, new_height))

            # Convert the image to a format suitable for Tkinter's PhotoImage
            photo = tkinter.PhotoImage(
                width=new_width, height=new_height
            )
            photo.put(" ".join(
                ["{" + " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in row) + "}" for row in img]
            ))

            # Store the image and create the Tkinter Label
            self.photoImage = photo  # Keep a reference to avoid garbage collection
            self.tkObj = tkinter.Label(host.tkObj, image=self.photoImage)
            self.tkObj.grid(row=row, column=col, sticky=sticky)  # Position the Label

        except Exception as e:
            print(f"Error loading or displaying image: {e}")
        # try
    # def
# class

class Button:

    def __init__(self,host,col,row,text,cmd):
        self.tkObj = tkinter.Button(host.tkObj, text=text, width=10, command=cmd, font=("Helvetica", 8))
        self.tkObj.grid(column=col, row=row, padx=2, pady=2)
        self.SetColour("white","black")
    # def 

    def SetColour(self,bgColour,fgColour):
        self.tkObj.configure(bg=bgColour,fg=fgColour)
    # def 

    def Update(self):
        pass
    # def 

# class

class OnOffButton:
    
    def __init__(self,host,col,row,text,initState):
        self.name = text
        self.button = Button(host,col,row,text,self.Click)
        if(initState==True):
            self.Set()
        else:
            self.Clear()
        # if
        self.clearedButton = None
    # def 

    def Set(self):
        self.on = True
        self.button.SetColour("orange","white")
    # def

    def Clear(self):
        self.on = False
        self.button.SetColour("white","black")
    # def

    def InstallClearedSwitch(self,clearedButton):
        self.clearedButton = clearedButton
    # def

    def Click(self):
        if(not self.on):
            self.Set()
        else:
            self.Clear()
        # if 
        _inst.Print(CR,self.name + " to " + str(self.on))
        if(self.clearedButton!=None):
            self.clearedButton.Clear()
        # if
    # def

    def Get(self):
        return self.on
    # def 

# class

class Slider:

    def __init__(self,host,col,row,text,initValue):
        self.tkObj = tkinter.Scale(host.tkObj, length=250, width=10, from_=100, to=-100)
        self.tkObj.set(initValue)
        self.tkObj.grid(column=col, row=row, padx=2, pady=2)
    # def 

    def Get(self):
        return self.tkObj.get()
    # def 

# class

class Timer:

    def __init__(self,refreshSecs): 
        # Rememember runtime parameters
        self.refreshSecs = refreshSecs
        self.lastRefresh = time()
    # def 

    def Tick(self):
        now = time()
        if((now - self.lastRefresh) > self.refreshSecs):
            self.lastRefresh = now
            return True
        else:
            return False
        # end if 
    # def 

# class

class Console:
    def __init__(self, host, col, row, panelWidth, panelHeight, opToWindow):
        self.opToWindow = opToWindow

        # Create and populate data display frame, with separate refresh rates for each label
        self.tkObj = tkinter.Text(host.tkObj, width=panelWidth, height=panelHeight, borderwidth=4,
                                  relief="groove", wrap="word", font=("Helvetica", 8))
        self.tkObj.grid(column=col, row=row, padx=2, pady=2)

        if self.opToWindow:
            self.stdout_redirector = TextRedirector(self.tkObj, "stdout")
            self.stderr_redirector = TextRedirector(self.tkObj, "stderr")
            sys.stdout = DualRedirector(sys.stdout, self.stdout_redirector)
            sys.stderr = DualRedirector(sys.stderr, self.stderr_redirector)
        # if
    # def

    def Print(self):
        if self.opToWindow:
            self.stdout_redirector.Print()
            self.stderr_redirector.Print()
    # def

# class

class TextRedirector:
    def __init__(self, widget, tag):
        self.widget = widget
        self.tag = tag
        self.text = ""
    # def

    def write(self, string):
        self.text += string
    # def

    def Print(self):
        if self.text:
            self.widget.insert("end", self.text)
            self.text = ""
            self.widget.see("end")
        # if
#    # def

    def flush(self):
        pass
    # def

# class

class DualRedirector:
    def __init__(self, original_stream, redirector):
        self.original_stream = original_stream
        self.redirector = redirector
    # def

    def write(self, string):
        self.original_stream.write(string)
        self.redirector.write(string)
    # def

    def flush(self):
        self.original_stream.flush()
        self.redirector.flush()
    # def

# class

