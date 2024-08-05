import os
import sys
from tkinter import *
import tkinter as tk
import win32gui
import win32con
from PIL import Image
import customtkinter
from staticStrings import StringConstants

def resource_pathAnnoying(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class InspectorAppOverlayUI:
    
    # Dimensions
    width = 500 
    height = 500 
    
    overlayWidth = 880 
    overlayHeight = 220 
    
    overlayPositionX = -326
    overlayPositionY = -92
    
    def __init__(self, parser, overlayFontSize, fontName, posX, posY) -> None:
        self.fullParser = parser
        
        self.overlayFontSize = overlayFontSize
        self.fontName = fontName
        
        self.overlayWindow = Toplevel()
        self.overlayWindow.geometry("%dx%d+%d+%d" % (self.overlayWidth, self.overlayHeight, posX, posY))

        self.overlayWindow.overrideredirect(True)
        self.overlayWindow.config(bg='#00FF00')
        self.overlayWindow.attributes("-alpha", 1)
        self.overlayWindow.wm_attributes("-topmost", 1)
        self.overlayWindow.attributes('-transparentcolor', '#00FF00', '-topmost', 1)
        
        self.overlayLocked = False

        self.overlayLabel = tk.Label(self.overlayWindow, 
                        text = StringConstants.overlayRoundString + "0:00" + StringConstants.overlaySpaceString + StringConstants.overlayExpectedString + "??:??", 
                        bg = "black", 
                        fg = "white", 
                        font = (self.fontName, self.overlayFontSize), 
                        bd = 0, 
                        padx = 18, 
                        pady = 10
                        )
        self.overlayLabel.place(relx = .5, rely = .5, anchor = "center")

        imageLockRaw = Image.open(resource_pathAnnoying("lock_white.png"))
        lockImage = customtkinter.CTkImage(light_image = imageLockRaw,
                                        dark_image = imageLockRaw,
                                        size = (40, 40)
                                        )

        self.lockOverlayButton = customtkinter.CTkButton(self.overlayWindow, 
                                            image = lockImage,
                                            width = 50, 
                                            height = 50,
                                            text = "",
                                            bg_color = 'black',
                                            command = self.lockOverlayFunction
                                            )
        self.lockOverlayButton.place(relx = .5, rely = .5, anchor = "center")
            
        self.overlayWindow.bind("<ButtonPress-1>", self.overlay_start_move)
        self.overlayWindow.bind("<ButtonRelease-1>", self.overlay_stop_move)
        self.overlayWindow.bind("<B1-Motion>", self.overlay_do_move)
        
    def overlay_start_move(self, event):
        self.overlay_x_pos = event.x
        self.overlay_y_pos = event.y

    def overlay_stop_move(self, event):
        # Update overlay position in config file
        self.fullParser.updateConfigFile("Overlay", "overlayposx", str(self.overlayWindow.winfo_x()))
        self.fullParser.updateConfigFile("Overlay", "overlayposy", str(self.overlayWindow.winfo_y()))
        
        self.fullParser.appUI.overlayPositionX = self.overlayWindow.winfo_x()
        self.fullParser.appUI.overlayPositionY = self.overlayWindow.winfo_y()
        
        self.overlay_x_pos = None
        self.overlay_y_pos = None

    def overlay_do_move(self, event):
        deltax = event.x - self.overlay_x_pos
        deltay = event.y - self.overlay_y_pos
        x = self.overlayWindow.winfo_x() + deltax
        y = self.overlayWindow.winfo_y() + deltay
        self.overlayWindow.geometry(f"+{x}+{y}")
            
    # Turns a tkinter element into "transparent", allowing click through
    def setClickthrough(self, hwnd):
        # print("setting window properties")
        try:
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        except Exception as e:
            print(e)

    # On lock button click, disable drag function and enable click through
    def lockOverlayFunction(self):
        self.lockOverlayButton.place_forget()
        
        self.overlayWindow.unbind("<ButtonPress-1>")
        self.overlayWindow.unbind("<ButtonRelease-1>")
        self.overlayWindow.unbind("<B1-Motion>")
        
        self.overlayLocked = True
        
        self.setClickthrough(self.overlayLabel.winfo_id())
                
    def displayDisruptionRoundData(self, roundTime, expectedEnd):
        self.overlayLabel.configure(text = 
                                    StringConstants.overlayRoundString + 
                                    roundTime + 
                                    StringConstants.overlaySpaceString + 
                                    StringConstants.overlayExpectedString + 
                                    expectedEnd
                                    )
        
    def updateOverlayWithTextRaw(self, textToDisplay):
        self.overlayLabel.configure(text = textToDisplay)
    
    def updateThingsBasedOnNewFontSize(self, newFontSize):
        self.overlayFontSize = newFontSize
                    
        self.overlayLabel.configure(font = (self.fontName, self.overlayFontSize))
        
      