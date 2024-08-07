import datetime
import json
import logging
import sys
import tkinter
import webbrowser
import customtkinter
import os
from PIL import Image
from json import JSONEncoder
import matplotlib.pyplot as plt
import numpy as np
from staticStrings import StringConstants
import pyperclip
import InspectorAppOverlayUI

# Get absolute path to resource, used for images so that they can be added to .exe
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def openInBrowser(url):
    webbrowser.open_new_tab(url)

class AppUI:

    # Text colors
    textColor = "light gray"
    textColorRed = "red"
    textColorGreen = "green"
    textColorHyperlink = "#4499e3"
    
    buttonBlueColor = "#1F6AA5"
    buttonBlueColorHover = "#144870"
    buttonRedColor = "red"
    buttonRedColorHover = "red"
    buttonGreenColor = "green"
    buttonGreenColorHover = "#14701D"
    
    toxinColor = "#00ff00"
    defaultWindowColor = "gray17"
    defaultOverlayColor = "black"

    # Line and Column values for various UI elements
    columnRelValues = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]
    lineRelValues = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]

    lineRelValuesCheckbox = [0.1, 0.22, 0.34, 0.46, 0.58, 0.70, 0.82, 0.95]
    checkboxRelXValue = .13

    columnRelValuesDisruption = [0.30, 0.42, 0.54, 0.66, 0.78, 0.88]
    lineRelValuesDisruption = [0.20, 0.32, 0.53, 0.65, 0.80]
    
    displayInKappaMode = False

    def __init__(self, fullClass, app, fontSize, fontName, posX, posY) -> None:
        
        self.fullParser = fullClass

        self.app = app
        self.overlayFontSize = fontSize
        try:
            self.overlayFontName = fontName
        except:
            self.overlayFontName = "Arial"
        self.overlayPositionX = posX
        self.overlayPositionY = posY

        self.kappaRegBadList = [StringConstants.kappa3, StringConstants.kappa4, StringConstants.kappa6]
        self.apolloRegBadList = [StringConstants.apollo6]
        self.olympusRegBadList = [StringConstants.olympus3, StringConstants.olympus4]

        # Tab list
        self.innerWindowBox = customtkinter.CTkTabview(app, width = app._current_width - 20, height = app._current_height - 20)
        self.innerWindowBox.pack_propagate(0)
        self.innerWindowBox.place(relx = .5, rely = .01, anchor = tkinter.N)

        self.settingsWindow = self.innerWindowBox.add("Settings")  
        self.analyzerWindow = self.innerWindowBox.add("Analyzer")  
        self.chartWindow = None

        # Smaller inner window that contains discord tag and version number
        self.smallerInnerWindowDiscordBox = customtkinter.CTkFrame(self.innerWindowBox, width = 130, height = 34, fg_color = "#404040")
        self.smallerInnerWindowDiscordBox.pack_propagate(0)
        self.smallerInnerWindowDiscordBox.place(relx = self.columnRelValues[9] + .015, rely = .95, anchor = "center")
        # self.smallerInnerWindowDiscordBox.place(relx = self.columnRelValues[9] + .015, rely = .96, anchor = "center")

        # Discord tag and image
        self.discordTagLabel = customtkinter.CTkLabel(self.smallerInnerWindowDiscordBox, text = StringConstants.discordTagString, text_color = self.textColor, font = ("Arial", 11))
        self.discordTagLabel.place(relx = .43, rely = .3, anchor = "center")

        imageDiscordRaw = Image.open(resource_path("discordLogo.png"))

        imageDiscordLogo = customtkinter.CTkImage(light_image = imageDiscordRaw, dark_image = imageDiscordRaw, size=(16, 16))
        self.imageLabel = customtkinter.CTkLabel(self.smallerInnerWindowDiscordBox, text="", image = imageDiscordLogo)
        self.imageLabel.place(relx = 0.85, rely = 0.5, anchor = "center")

        # Version text
        self.versionNumberLabel = customtkinter.CTkLabel(
                                                self.smallerInnerWindowDiscordBox, 
                                                text = "v" + self.fullParser.currentVersion, 
                                                text_color = self.textColor, 
                                                fg_color = "transparent",
                                                font = ("Arial", 11),
                                                anchor = "n"
                                                )
        self.versionNumberLabel.place(relx = .43, rely = .9, anchor = "center")

        # UI elements
        # Settings tab
        self.generalSettingsDisplay = customtkinter.CTkLabel(self.settingsWindow, text = StringConstants.generalSettingsString, text_color = self.textColor, font = ("Arial", 18))
        self.generalSettingsDisplay.place(relx = self.columnRelValues[1], rely = self.lineRelValues[1], anchor = "center")

        # Always on top checkbox
        self.alwaysOnTopCheckBoxValue = customtkinter.StringVar(value = "off")

        self.alwaysOnTopCheckBox = customtkinter.CTkCheckBox(self.settingsWindow, 
                                                   text = "Always on top", 
                                                   command = self.alwaysOnTopCheckBox_event, 
                                                   variable = self.alwaysOnTopCheckBoxValue, 
                                                   onvalue = "on", 
                                                   offvalue = "off", 
                                                   font = ("Arial", 14)
                                                   )
        self.alwaysOnTopCheckBox.place(relx = self.columnRelValues[0] + .025, rely = self.lineRelValues[2], anchor = "w")

        # Parse from file start checkbox
        self.parseFromStartCheckBoxValue = customtkinter.StringVar(value = "off")

        self.parseFromStartCheckBox = customtkinter.CTkCheckBox(self.settingsWindow, 
                                                   text = "Parse full log\n(for finished runs)", 
                                                   command = self.parseFromStartCheckBox_event, 
                                                   variable = self.parseFromStartCheckBoxValue, 
                                                   onvalue = "on", 
                                                   offvalue = "off", 
                                                   font = ("Arial", 14)
                                                   )
        self.parseFromStartCheckBox.place(relx = self.columnRelValues[0] + .025, rely = self.lineRelValues[3], anchor = "w")

        # Host/client network code connection related things
        self.hostCodeStringDisplay = customtkinter.CTkLabel(self.settingsWindow, text = StringConstants.hostCodeDisplayString, text_color = self.textColor, font = ("Arial", 18))
        self.hostCodeStringDisplay.place(relx = self.columnRelValues[0] + .025, rely = self.lineRelValues[4], anchor = "w")
        
        self.hostCodeActualDisplay = customtkinter.CTkLabel(self.settingsWindow, text = "", text_color = self.textColor, font = ("Arial", 14))
        self.hostCodeActualDisplay.place(relx = self.columnRelValues[0] + .025, rely = self.lineRelValues[5] - .035, anchor = "w")
            
        self.copyCodeToClipboardButton = customtkinter.CTkButton(
            self.settingsWindow,
            text = "Copy",
            font = ("Arial", 14, "bold"),
            width = 80,
            height = 30,
            command = self.copyCodeToClipboardFunction
        )
        self.copyCodeToClipboardButton.place(relx = self.columnRelValues[2] + .028, rely = self.lineRelValues[5] - .035, anchor = "w")
        
        self.connectToHostButton = customtkinter.CTkButton(
            self.settingsWindow,
            text = "Connect",
            font = ("Arial", 14, "bold"),
            width = 80,
            height = 30,
            fg_color = "#1F6AA5",
            command = self.connectToHostFunction
        )
        self.connectToHostButton.place(relx = self.columnRelValues[2] + .028, rely = self.lineRelValues[6] - .06, anchor = "w")
        
        self.hostCodeInputBox = customtkinter.CTkTextbox(
            self.settingsWindow, 
            width = 170, 
            height = 20, 
            corner_radius = 4,
            border_width = 1,
            activate_scrollbars = False,
            wrap = "none"
        )
        self.hostCodeInputBox.place(relx = self.columnRelValues[0] + .025, rely = self.lineRelValues[6] - .06, anchor = "w")
        
        # Overlay related settings
        self.overlayStringDisplay = customtkinter.CTkLabel(self.settingsWindow, text = "Overlay (Disruption)", text_color = self.textColor, font = ("Arial", 18))
        self.overlayStringDisplay.place(relx = self.columnRelValues[0] + .025, rely = self.lineRelValues[7] - .06, anchor = "w")
        
        self.fontSizeStringDisplay = customtkinter.CTkLabel(self.settingsWindow, text = "Font size", text_color = self.textColor, font = ("Arial", 14))
        self.fontSizeStringDisplay.place(relx = self.columnRelValues[0] + .025, rely = self.lineRelValues[8] - .095, anchor = "w")
        
        self.fontSizeInputBox = customtkinter.CTkTextbox(
            self.settingsWindow, 
            width = 60, 
            height = 20, 
            corner_radius = 4,
            border_width = 1,
            activate_scrollbars = False,
            wrap = "none"
        )
        self.fontSizeInputBox.place(relx = self.columnRelValues[1] + .01, rely = self.lineRelValues[8] - .095, anchor = "w")
        self.fontSizeInputBox.insert('end', self.overlayFontSize)
        
        self.fontSizeInputBox.bind('<<Modified>>', self.updateOverlayFontFunction)
        
        self.toggleOverlayButton = customtkinter.CTkButton(
            self.settingsWindow,
            text = StringConstants.openOverlayString,
            font = ("Arial", 14, "bold"),
            width = 120,
            height = 30,
            command = self.toggleOverlayFunction
        )
        self.toggleOverlayButton.place(relx = self.columnRelValues[2] - .015, rely = self.lineRelValues[8] - .095, anchor = "w")

        # Update available window bottom left
        self.updateAvailableWindow = customtkinter.CTkFrame(self.settingsWindow, width = 260, height = 70, fg_color="#404040")
        self.updateAvailableWindow.pack_propagate(0)
        
        self.updatedVersionAvailableText = customtkinter.CTkLabel(self.updateAvailableWindow, text = StringConstants.updateAvailableString, text_color = self.textColorRed, font = ("Arial", 28, "bold"))
        self.updatedVersionAvailableText.place(relx = .5, rely = .35, anchor = "center")
        
        self.updatedVersionAvailableHyperlink = customtkinter.CTkLabel(self.updateAvailableWindow, 
                                                                       text = StringConstants.updateAvailableHyperlinkString, 
                                                                       text_color = self.textColorHyperlink, 
                                                                       font = ("Arial", 18, "bold"),
                                                                       cursor = "hand2")
        self.updatedVersionAvailableHyperlink.place(relx = .5, rely = .7, anchor = "center") 
        self.updatedVersionAvailableHyperlink.bind("<Button-1>", lambda e:openInBrowser(StringConstants.updateUrl))
        

        # Analyzer Tab
        self.missionNameDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.replacedByMissionNameString, text_color = self.textColor, font = ("Arial", 28))
        self.missionNameDisplay.place(relx = .5, rely = self.lineRelValues[3], anchor = "center")

        self.foundTileDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.waitingForMissionStart, text_color = self.textColor, font = ("Arial", 32))
        self.foundTileDisplay.place(relx = .5, rely = self.lineRelValues[5], anchor = "center")

        self.whatIsBeingParsedDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.whatIsBeingParsedText, text_color = self.textColor, font = ("Arial", 18))
        self.whatIsBeingParsedDisplay.place(relx = self.columnRelValues[9] + .02, rely = self.lineRelValues[4], anchor = "center")

        self.disruptionDataDumpedDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.disruptionDataDumpedString, text_color = self.textColorGreen, font = ("Arial", 22))

        # Checkboxes for each of the possible main tiles - Kappa
        self.kappa1CheckBoxValue = customtkinter.StringVar(value = "off")
        self.kappa3CheckBoxValue = customtkinter.StringVar(value = "on")
        self.kappa4CheckBoxValue = customtkinter.StringVar(value = "on")
        self.kappa6CheckBoxValue = customtkinter.StringVar(value = "on")
        self.kappa7CheckBoxValue = customtkinter.StringVar(value = "off")
        self.kappa8CheckBoxValue = customtkinter.StringVar(value = "off")
        self.kappaCheckValuesList = [self.kappa1CheckBoxValue, self.kappa3CheckBoxValue, self.kappa4CheckBoxValue, self.kappa6CheckBoxValue, self.kappa7CheckBoxValue, self.kappa8CheckBoxValue]
        self.kappaCheckboxes = []

        self.selectBadTilesKappaDisplay = customtkinter.CTkLabel(self.settingsWindow, 
                                                            text = StringConstants.selectBadTilesKappaString, 
                                                            text_color = self.textColorHyperlink, 
                                                            font = ("Arial", 18),
                                                            cursor = "hand2"
                                                            )
        self.selectBadTilesKappaDisplay.place(relx = self.columnRelValues[4], rely = self.lineRelValues[1], anchor = "center")
        self.selectBadTilesKappaDisplay.bind("<Button-1>", lambda e:openInBrowser("https://imgur.com/a/cKyEWnp"))

        # Create checkboxes for all kappa tiles
        i = 0
        for x in self.kappaCheckValuesList:
            newCheckbox = customtkinter.CTkCheckBox(self.settingsWindow, 
                                                   text = StringConstants.kappaListForCheckbox[i], 
                                                   command = lambda i = i: self.updateCheckboxValueKappa(i), 
                                                   variable = self.kappaCheckValuesList[i], 
                                                   onvalue = "on", 
                                                   offvalue = "off", 
                                                   font = ("Arial", 14),
                                                   width = 20
                                                   )
            
            self.kappaCheckboxes.append(newCheckbox)
            newCheckbox.place(relx = self.columnRelValues[4], rely = self.lineRelValues[i + 2], anchor = "center")

            i += 1

        # Checkboxes for each of the possible main tiles - Apollo
        self.apollo1CheckBoxValue = customtkinter.StringVar(value = "off")
        self.apollo2CheckBoxValue = customtkinter.StringVar(value = "off")
        self.apollo3CheckBoxValue = customtkinter.StringVar(value = "off")
        self.apollo4CheckBoxValue = customtkinter.StringVar(value = "off")
        self.apollo5CheckBoxValue = customtkinter.StringVar(value = "off")
        self.apollo6CheckBoxValue = customtkinter.StringVar(value = "on")
        self.apollo7CheckBoxValue = customtkinter.StringVar(value = "off")
        self.apolloCheckValuesList = [self.apollo1CheckBoxValue, self.apollo2CheckBoxValue, self.apollo3CheckBoxValue, self.apollo4CheckBoxValue, self.apollo5CheckBoxValue, self.apollo6CheckBoxValue, self.apollo7CheckBoxValue]
        self.apolloCheckboxes = []

        self.selectBadTilesApolloDisplay = customtkinter.CTkLabel(self.settingsWindow, 
                                                             text = StringConstants.selectBadTilesApolloString, 
                                                             text_color = self.textColorHyperlink, 
                                                             font = ("Arial", 18), 
                                                             cursor = "hand2"
                                                             )
        self.selectBadTilesApolloDisplay.place(relx = self.columnRelValues[6], rely = self.lineRelValues[1], anchor = "center")
        self.selectBadTilesApolloDisplay.bind("<Button-1>", lambda e:openInBrowser("https://imgur.com/a/cKyEWnp"))

        # Create checkboxes for all apollo tiles
        i = 0
        for x in self.apolloCheckValuesList:
            newCheckbox = customtkinter.CTkCheckBox(self.settingsWindow, 
                                                   text = StringConstants.apolloListForCheckbox[i], 
                                                   command = lambda i = i: self.updateCheckboxValueApollo(i), 
                                                   variable = self.apolloCheckValuesList[i], 
                                                   onvalue = "on", 
                                                   offvalue = "off", 
                                                   font = ("Arial", 14),
                                                   width = 20
                                                   )
            
            self.apolloCheckboxes.append(newCheckbox)
            newCheckbox.place(relx = self.columnRelValues[6] - .062, rely = self.lineRelValues[i + 2], anchor = "w")

            i += 1

        # Checkboxes for each of the possible main tiles - Olympus
        self.olympus1CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus2CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus3CheckBoxValue = customtkinter.StringVar(value = "on")
        self.olympus4CheckBoxValue = customtkinter.StringVar(value = "on")
        self.olympus5CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus6CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus10CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus11CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympusAssCheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympusConnCheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympusCheckValuesList = [self.olympus1CheckBoxValue, 
                                       self.olympus2CheckBoxValue, 
                                       self.olympus3CheckBoxValue, 
                                       self.olympus4CheckBoxValue, 
                                       self.olympus5CheckBoxValue, 
                                       self.olympus6CheckBoxValue, 
                                       self.olympus10CheckBoxValue, 
                                       self.olympus11CheckBoxValue, 
                                       self.olympusAssCheckBoxValue, 
                                       self.olympusConnCheckBoxValue
                                       ]
        self.olympusCheckboxes = []

        self.selectBadTilesOlympusDisplay = customtkinter.CTkLabel(self.settingsWindow, 
                                                            text = StringConstants.selectBadTilesOlympusString, 
                                                            text_color = self.textColorHyperlink, 
                                                            font = ("Arial", 18), 
                                                            cursor = "hand2"
                                                            )
        self.selectBadTilesOlympusDisplay.place(relx = self.columnRelValues[8], rely = self.lineRelValues[1], anchor = "center")
        self.selectBadTilesOlympusDisplay.bind("<Button-1>", lambda e:openInBrowser("https://imgur.com/a/cKyEWnp"))

        # Create checkboxes for all olympus tiles
        index = 0
        counterSpecial = 0
        midIndexOlympusList = len(self.olympusCheckValuesList)/2
        for x in self.olympusCheckValuesList:
            newCheckbox = customtkinter.CTkCheckBox(self.settingsWindow, 
                                                text = StringConstants.olympusListForCheckbox[index], 
                                                command = lambda index = index: self.updateCheckboxValueOlympus(index), 
                                                variable = self.olympusCheckValuesList[index], 
                                                onvalue = "on", 
                                                offvalue = "off", 
                                                font = ("Arial", 14),
                                                width = 20
                                                )
            
            self.olympusCheckboxes.append(newCheckbox)
            
            # Reset line placement counter after mid point has been reached
            if (index == midIndexOlympusList):
                counterSpecial = 0
            
            if(index < midIndexOlympusList):
                newCheckbox.place(relx = self.columnRelValues[8] - .065, rely = self.lineRelValues[counterSpecial + 2], anchor = "w")
            else:
                newCheckbox.place(relx = self.columnRelValues[8] + .020, rely = self.lineRelValues[counterSpecial + 2], anchor = "w")

            index += 1
            counterSpecial += 1

        # UI elements for disruption
        self.keyInsertsStringDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.disruptionKeyInsertsStaticString, text_color = self.textColor, font = ("Arial", 24))
        self.demoKillsStringDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.disruptionDemoKillsString, text_color = self.textColor, font = ("Arial", 24))
        self.previousRoundTimeStringDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.disruptionPreviousRunAverateString, text_color = self.textColor, font = ("Arial", 24))
        self.currentAverageStringDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.disruptionCurrentAverateString, text_color = self.textColor, font = ("Arial", 24))
        self.expectedEndTimeStringDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.disruptionExpectedEndString, text_color = self.textColor, font = ("Arial", 24))
        self.bestRoundTimeStringDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = StringConstants.bestRoundTimeString, text_color = self.textColor, font = ("Arial", 24))

        self.key1Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.key2Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.key3Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.key4Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))

        self.demo1Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.demo2Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.demo3Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.demo4Display = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))

        self.keyDisplays = [self.key1Display, self.key2Display, self.key3Display, self.key4Display]
        self.demoDisplays = [self.demo1Display, self.demo2Display, self.demo3Display, self.demo4Display]

        self.previousRoundTimeDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.currentAverageDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.expectedEndTimeDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))
        self.bestRoundTimeDisplay = customtkinter.CTkLabel(self.analyzerWindow, text = "", text_color = self.textColor, font = ("Arial", 24))

        # UI elements for scrolling through rounds
        self.previousRoundButton = None
        self.nextRoundButton = None

        # Next/Prev run buttons 
        self.previousRoundButton = customtkinter.CTkButton(
            self.analyzerWindow,
            text="<",
            font=("Arial", 14),
            width = 28,
            height = 20,
            command = self.previousRound
        )

        self.nextRoundButton = customtkinter.CTkButton(
            self.analyzerWindow,
            text=">",
            font=("Arial", 14),
            width = 28,
            height = 20,
            command = self.nextRound
        )

        # Update button for UI update from input 
        self.updateFromInputButton = customtkinter.CTkButton(
            self.analyzerWindow,
            text="Update",
            font=("Arial", 14),
            width = 50,
            height = 20,
            command = self.updateRoundFromInput
        )

        self.inputBoxValue = tkinter.StringVar()

        # Input box for going to specific round number in disruption run 
        self.disruptionRoundInputBox = customtkinter.CTkTextbox(
            self.analyzerWindow, 
            width = 44, 
            height = 20, 
            corner_radius = 4,
            border_width = 1,
            activate_scrollbars = False,
            wrap = "none"
        )
        
        # Button for parsing of a new run after one has been finished
        self.continueParsingButton = customtkinter.CTkButton(
            self.analyzerWindow,
            text="New Run",
            font=("Arial", 24, "bold"),
            width = 140,
            height = 40,
            command = self.startNewRunAfterAnotherFinished
        )

        self.disrutpionUIElements = [self.keyInsertsStringDisplay, self.demoKillsStringDisplay, self.previousRoundTimeStringDisplay, self.currentAverageStringDisplay, self.expectedEndTimeStringDisplay,
                                self.bestRoundTimeStringDisplay, self.key1Display, self.key2Display, self.key3Display, self.key4Display, self.demo1Display, self.demo2Display, self.demo3Display, self.demo4Display,
                                self.previousRoundTimeDisplay, self.currentAverageDisplay, self.expectedEndTimeDisplay, self.bestRoundTimeDisplay, self.updateFromInputButton, self.previousRoundButton,
                                self.nextRoundButton, self.disruptionDataDumpedDisplay, self.disruptionRoundInputBox
                                ]


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    #                                   Class Funcs                                 #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Function to enable or disable update available msg
    def toggleUpdateAvailableMsg(self, newState):
        if newState:
            self.updateAvailableWindow.place(relx = self.columnRelValues[0], rely = .99, anchor = "sw")
        else:
            self.updateAvailableWindow.place_forget()
            

    # Function that manages Always on Top Checkbox value
    def alwaysOnTopCheckBox_event(self):
        logging.info("Changed status of On Top Window to " + self.alwaysOnTopCheckBoxValue.get())

        if self.alwaysOnTopCheckBoxValue.get() == "on":
            self.app.attributes('-topmost', True)
        else:
            self.app.attributes('-topmost', False)
            
    # Function that manages Parse From Start value
    def parseFromStartCheckBox_event(self):
        if self.fullParser.loggingState:
            logging.info("Changed status of Parse From Start to " + self.parseFromStartCheckBoxValue.get())

        if self.parseFromStartCheckBoxValue.get() == "on":
            self.fullParser.parseFromEnd = False
            self.fullParser.restartReadingBool = True
            self.app.after(self.fullParser.sleepBetweenCalls + 100, self.resetAnalyzerUI)
        else:
            self.fullParser.parseFromEnd = True

    # Function that manages Restart Reading button presses
    def restartReading(self):
        if self.fullParser.loggingState:
            logging.info("Restart reading button pressed")

        self.fullParser.restartReadingBool = True

        self.app.after(self.fullParser.sleepBetweenCalls, self.restartReadingActual)

    def restartReadingActual(self):
        self.fullParser.file.seek(self.fullParser.fileRollbackPosition)
        self.app.after(10, self.resetDisplay)

    # Function for adding/removeing bad tile of kappa based on checkbox that called the update func
    def updateCheckboxValueKappa(self, checkboxToUpdate):
        if self.fullParser.loggingState:
            logging.info("Updating checkbox value of Kappa " + StringConstants.kappaList[checkboxToUpdate])

        if self.kappaCheckValuesList[checkboxToUpdate].get() == "on": 
            self.kappaRegBadList.append(StringConstants.kappaList[checkboxToUpdate])
        else:
            self.kappaRegBadList.remove(StringConstants.kappaList[checkboxToUpdate])
    
    # Add/remove bad tile of apollo based on checkbox that called the update func
    def updateCheckboxValueApollo(self, checkboxToUpdate):
        if self.fullParser.loggingState:
            logging.info("Updating checkbox value of Apollo " + StringConstants.apolloList[checkboxToUpdate])

        if self.apolloCheckValuesList[checkboxToUpdate].get() == "on": 
            self.apolloRegBadList.append(StringConstants.apolloList[checkboxToUpdate])
        else:
            self.apolloRegBadList.remove(StringConstants.apolloList[checkboxToUpdate])

    # Add/remove bad tile of olympus based on checkbox that called the update func
    def updateCheckboxValueOlympus(self, checkboxToUpdate):
        if self.fullParser.loggingState:
            logging.info("Updating checkbox value of Olympus " + StringConstants.olympusList[checkboxToUpdate])

        if self.olympusCheckValuesList[checkboxToUpdate].get() == "on": 
            self.olympusRegBadList.append(StringConstants.olympusList[checkboxToUpdate])
        else:
            self.olympusRegBadList.remove(StringConstants.olympusList[checkboxToUpdate])

    # Function called by next round button, changes UI values to next round's
    def previousRound(self):       
        if self.fullParser.currentRoundShown > 1:
            self.fullParser.currentRoundShown -= 1

        self.updateDisruptionUIValues(self.fullParser.currentRoundShown)

        self.disruptionRoundInputBox.delete('0.0', 'end')
        self.disruptionRoundInputBox.insert('end', self.fullParser.currentRoundShown)

        if self.fullParser.loggingState:
            logging.info("Previous round button pressed, with updated value of " + str(self.fullParser.currentRoundShown))

    # Function called by previous round button, changes UI values to previous round's
    def nextRound(self):
        if self.fullParser.currentRoundShown < len(self.fullParser.disruptionRun.rounds):
            self.fullParser.currentRoundShown += 1

        self.updateDisruptionUIValues(self.fullParser.currentRoundShown)
            
        self.disruptionRoundInputBox.delete('0.0', 'end')
        self.disruptionRoundInputBox.insert('end', self.fullParser.currentRoundShown)

        if self.fullParser.loggingState:
            logging.info("Next round button pressed, with updated value of " + str(self.fullParser.currentRoundShown))

    # Function called by the update round button, changes UI values to given round if possible
    def updateRoundFromInput(self):        
        tempRound = 0
        
        try:
            tempRound = int(self.disruptionRoundInputBox.get('1.0', "end-1c"))
        except:
            logging.error("Given value for round is not a valid number (or not a number at all)")

        if tempRound > len(self.fullParser.disruptionRun.rounds):
            self.fullParser.currentRoundShown = len(self.fullParser.disruptionRun.rounds)
        elif tempRound <= 0:
            self.fullParser.currentRoundShown = 1
        else:
            self.fullParser.currentRoundShown = tempRound

        self.disruptionRoundInputBox.delete('0.0', 'end')
        self.disruptionRoundInputBox.insert('end', self.fullParser.currentRoundShown)

        self.updateDisruptionUIValues(self.fullParser.currentRoundShown)

        if self.fullParser.loggingState:
            logging.info("Updating display round value based on input with value of " + str(self.fullParser.currentRoundShown))

    # Reset analyzer UI
    def resetAnalyzerUI(self):

        # Logging
        if self.fullParser.loggingState:
            logging.info("In resetAnalyzerUI()")

        self.displayInKappaMode = False

        # Update values
        self.parseFromStartCheckBox.deselect()

        # Reset current round indicator to 1
        self.disruptionRoundInputBox.delete('0.0', 'end')
        self.disruptionRoundInputBox.insert('end', 1)

        # Disable disruption related UI elements
        for x in self.disrutpionUIElements:
            x.place_forget()

        try:
            self.innerWindowBox.delete("Chart")
        except:
            logging.warning("Attempt to remove Chart window without it existing")

        # Reset various variables
        self.fullParser.currentRoundShown = -1
        self.fullParser.disruptionTilesFoundList = []

        # Re-enable original display info
        self.missionNameDisplay.place(relx = .5, rely = self.lineRelValues[3], anchor = "center")
        self.foundTileDisplay.place(relx = .5, rely = self.lineRelValues[5], anchor = "center")
        self.whatIsBeingParsedDisplay.place(relx = self.columnRelValues[9] + .02, rely = self.lineRelValues[4], anchor = "center")

        self.foundTileDisplay.configure(text = StringConstants.waitingForMissionStart, text_color = self.textColor)
        self.missionNameDisplay.configure(text = StringConstants.replacedByMissionNameString, text_color = self.textColor)

        self.key1Display.configure(text = "")
        self.key2Display.configure(text = "")
        self.key3Display.configure(text = "")
        self.key4Display.configure(text = "")

        self.demo1Display.configure(text = "")
        self.demo2Display.configure(text = "")
        self.demo3Display.configure(text = "")
        self.demo4Display.configure(text = "")
        
        self.previousRoundTimeDisplay.configure(text = "")
        self.currentAverageDisplay.configure(text = "")
        self.expectedEndTimeDisplay.configure(text = "")
        self.bestRoundTimeDisplay.configure(text = "")
        
        self.expectedEndTimeStringDisplay.configure(text = StringConstants.disruptionExpectedEndString)

        self.fullParser.missionLoadEndReached = False

        if(not self.fullParser.connectedToHostBool):
            if self.fullParser.restartReadingBool:
                self.fullParser.restartReadingBool = False
                self.app.after(self.fullParser.sleepBetweenCalls, self.fullParser.startParsing)
            else:
                self.app.after(self.fullParser.sleepBetweenCalls, self.fullParser.scanMissionStart)

    # Update UI to be ready for disruption run logging. Removes most other elements, adds new elements back in
    def updateUIForDisruptionLogging(self):
        if self.fullParser.loggingState:
            logging.info("In updateUIForDisruptionLogging()")

        self.displayInKappaMode = True

        # Remove old un-needed elements    
        self.missionNameDisplay.place_forget()
        self.foundTileDisplay.place_forget()
        self.whatIsBeingParsedDisplay.place_forget()
        self.disruptionDataDumpedDisplay.place_forget()

        # Add new elements
        self.keyInsertsStringDisplay.place(relx = self.columnRelValuesDisruption[0], rely = self.lineRelValuesDisruption[0], anchor = "e")
        self.demoKillsStringDisplay.place(relx = self.columnRelValuesDisruption[0], rely = self.lineRelValuesDisruption[1], anchor = "e")
        
        self.bestRoundTimeStringDisplay.place(relx = self.columnRelValuesDisruption[3], rely = self.lineRelValuesDisruption[2], anchor = "e")
        self.previousRoundTimeStringDisplay.place(relx = self.columnRelValuesDisruption[0], rely = self.lineRelValuesDisruption[2], anchor = "e")
        
        self.currentAverageStringDisplay.place(relx = self.columnRelValuesDisruption[0], rely = self.lineRelValuesDisruption[3], anchor = "e")
        self.expectedEndTimeStringDisplay.place(relx = self.columnRelValuesDisruption[3], rely = self.lineRelValuesDisruption[3], anchor = "e")

        i = 0
        for x in self.keyDisplays:
            self.keyDisplays[i].place(relx = self.columnRelValuesDisruption[i + 1], rely = self.lineRelValuesDisruption[0], anchor = "center")
            self.demoDisplays[i].place(relx = self.columnRelValuesDisruption[i + 1], rely = self.lineRelValuesDisruption[1], anchor = "center")
            i += 1

        self.previousRoundTimeDisplay.place(relx = self.columnRelValuesDisruption[1], rely = self.lineRelValuesDisruption[2], anchor = "center")
        self.currentAverageDisplay.place(relx = self.columnRelValuesDisruption[1], rely = self.lineRelValuesDisruption[3], anchor = "center")
        self.expectedEndTimeDisplay.place(relx = self.columnRelValuesDisruption[4], rely = self.lineRelValuesDisruption[3], anchor = "center")
        self.bestRoundTimeDisplay.place(relx = self.columnRelValuesDisruption[4], rely = self.lineRelValuesDisruption[2], anchor = "center")

        if(not self.fullParser.connectedToHostBool):
            self.previousRoundButton.place(relx = .42, rely = self.columnRelValuesDisruption[5] - .05, anchor = "c")
            self.nextRoundButton.place(relx = .455, rely = self.columnRelValuesDisruption[5] - .05, anchor = "c")

            self.disruptionRoundInputBox.place(relx = .5, rely = self.columnRelValuesDisruption[5] - .05, anchor = "c")
            self.updateFromInputButton.place(relx = .56, rely = self.columnRelValuesDisruption[5] - .05, anchor = "c")

        if self.fullParser.loggingState:
            logging.info("updateUIForDisruptionLogging() finished, moving to scanDisruptionProgress()")

        if(not self.fullParser.connectedToHostBool):
            self.app.after(self.fullParser.sleepBetweenCalls, self.fullParser.scanDisruptionProgress)

    # Clean current disruption round values
    def cleanDisruptionUI(self):
        if self.fullParser.loggingState:
            logging.info("In cleanDisruptionUI()")

        i = 0
        for x in self.keyDisplays:
            self.keyDisplays[i].configure(text = "", text_color = self.textColor)
            self.demoDisplays[i].configure(text = "", text_color = self.textColor)
            i += 1

        self.previousRoundTimeDisplay.configure(text = "", text_color = self.textColor)


    # Update disruption UI with values of a given set
    def updateDisruptionUIValues(self, runNumberToDisplay):        
        if self.fullParser.loggingState:
            logging.info("In updateDisruptionUIValues() with run to display " + str(runNumberToDisplay))

        try:
            roundToDisplay = self.fullParser.disruptionRun.rounds[runNumberToDisplay - 1]

            self.cleanDisruptionUI()

            i = 0
            for x in self.keyDisplays:
                self.keyDisplays[i].configure(text = roundToDisplay.keyInsertTimesString[i], text_color = self.textColor)
                self.demoDisplays[i].configure(text = roundToDisplay.demoKillTimesString[i], text_color = self.textColor)
                i += 1

            if roundToDisplay.totalRoundTimeInSecondsString != None:
                self.previousRoundTimeDisplay.configure(text = roundToDisplay.totalRoundTimeInSecondsString, text_color = self.textColor)
        
        except:
            logging.error("Given run number is out of bounds of the array (too big, or too small)")


    # Reset display to default text and colors
    def resetDisplay(self):
        if self.fullParser.loggingState:
            logging.info("In resetDisplay()")

        self.fullParser.restartReadingBool = False

        self.foundTileDisplay.configure(text = StringConstants.waitingForMissionStart, text_color = self.textColor)
        self.missionNameDisplay.configure(text = StringConstants.replacedByMissionNameString, text_color = self.textColor)

        self.fullParser.missionLoadEndReached = False

        if(not self.fullParser.connectedToHostBool):
            self.app.after(self.fullParser.sleepBetweenCalls, self.fullParser.scanMissionStart) 
        
    # Used to toggle the button that allows for the parsing of new run after one has been finished
    def toggleNewRunButton(self, newState):
        if newState:
            self.continueParsingButton.place(relx = .5, rely = self.columnRelValuesDisruption[5] + .05, anchor = "c")
        else:
            self.continueParsingButton.place_forget()
    
    # Used to start new run after one has been finished
    def startNewRunAfterAnotherFinished(self):
        self.toggleNewRunButton(False)
        self.resetAnalyzerUI()
    
    # Used to copy host code to clipboard
    def copyCodeToClipboardFunction(self):
        pyperclip.copy(self.fullParser.hostCodeString)
        self.copyCodeToClipboardButton.configure(text = "Copied")
        
        self.app.after(1500, self.revertCopyCodeButtonText)
        
    # Used to revert back to copy host code on the button
    def revertCopyCodeButtonText(self):
        self.copyCodeToClipboardButton.configure(text = "Copy")
        
        
    # Used to copy host code to clipboard
    def connectToHostFunction(self):
        codeToConnect = str(self.hostCodeInputBox.get('1.0', "end-1c"))
        codeToConnect = codeToConnect.replace(" ", "")
                
        if(len(codeToConnect) == 20 and codeToConnect != self.fullParser.hostCodeString):
            self.fullParser.connectedToHostString = codeToConnect
            self.fullParser.connectedToHostBool = True
            self.fullParser.restartReadingBool = True
            self.connectToHostButton.configure(text = "Done", fg_color = self.buttonGreenColor, hover_color = self.buttonGreenColorHover)
                        
            # self.fullParser.connection.mqttClient.userdata = self.fullParser.selfWarframeUsername
            # print(self.fullParser.connection.mqttClient.userdata)
            # print(self.fullParser.selfWarframeUsername)
            self.fullParser.connection.stopConnection()
            
            self.app.after(self.fullParser.sleepBetweenCalls + 100, self.resetAnalyzerUI)
            self.app.after(1500, self.connectToHostActual, codeToConnect)
            
        else:
            self.connectToHostButton.configure(text = "Buh", fg_color = self.buttonRedColor, hover_color = self.buttonRedColorHover)
            
        self.hostCodeInputBox.delete('0.0', 'end')
        self.hostCodeInputBox.insert('end', "")
        
        self.app.after(1000, self.revertConnectToHostButtonText)
        
    # Used to revert back to copy host code on the button
    def revertConnectToHostButtonText(self):        
        self.fullParser.restartReadingBool = False
        self.connectToHostButton.configure(text = "Connect", fg_color = self.buttonBlueColor, hover_color = self.buttonBlueColorHover)
    
    # Used to revert back to copy host code on the button
    def connectToHostActual(self, codeToConnect):
        self.innerWindowBox.set("Analyzer")
        
        self.fullParser.connection.mqttTopic = codeToConnect
        self.fullParser.connection.startConnection()
    
    def displayMissionAndTiles(self, missionName, tiles, goodTilesBoolean):
        text_colorNew = ""
        if(goodTilesBoolean):
            text_colorNew = self.textColorGreen
        else:
            text_colorNew = self.textColorRed
                    
        self.foundTileDisplay.configure(text = tiles)
        self.missionNameDisplay.configure(text = missionName, text_color = text_colorNew)
        
        self.app.after(5000, self.updateUIForDisruptionLogging)
        
    def displayDisruptionRoundFromHostData(self, dataFromHost):
        i = 0
        for x in dataFromHost["keyInsertTimes"]:
            self.keyDisplays[i].configure(text = dataFromHost["keyInsertTimes"][i])
            self.demoDisplays[i].configure(text = dataFromHost["demoKillTimes"][i])
            i += 1
            
        self.previousRoundTimeDisplay.configure(text = dataFromHost["totalRoundTimeInSeconds"])
        self.currentAverageDisplay.configure(text = dataFromHost["currentAvg"])
        self.bestRoundTimeDisplay.configure(text = dataFromHost["bestRound"])
        self.expectedEndTimeDisplay.configure(text = dataFromHost["expectedEnd"])
           
    # Toggle overlay button function
    def toggleOverlayFunction(self):
        if(self.fullParser.overlayWindow == None):
            self.fullParser.overlayWindow = InspectorAppOverlayUI.InspectorAppOverlayUI(self.fullParser, 
                                                                                        self.overlayFontSize,
                                                                                        self.overlayFontName,
                                                                                        self.overlayPositionX,
                                                                                        self.overlayPositionY
                                                                                        )
            self.toggleOverlayButton.configure(text = StringConstants.closeOverlayString)
        else:
            self.fullParser.overlayWindow.overlayWindow.destroy()
            self.fullParser.overlayWindow = None
            self.toggleOverlayButton.configure(text = StringConstants.openOverlayString)
            
    def updateOverlayFontFunction(self, event):
        newFontSize = None
        cleanedText = self.fontSizeInputBox.get('1.0', "end-1c").replace(" ", "")
        try:
            newFontSize = int(cleanedText)
            if(newFontSize > 40):
                self.overlayFontSize = 40
                self.fontSizeInputBox.delete('0.0', 'end')
                self.fontSizeInputBox.insert('end', "")
            elif(newFontSize <= 6):
                self.overlayFontSize = 6
            else:
                self.overlayFontSize = newFontSize
        except:
            self.fontSizeInputBox.delete('0.0', 'end')
            self.fontSizeInputBox.insert('end', "")
            
        self.fullParser.updateConfigFile("Overlay", "overlayfontsize", str(self.overlayFontSize))
        
        if(self.fullParser.overlayWindow != None):
            self.fullParser.overlayWindow.updateThingsBasedOnNewFontSize(self.overlayFontSize)
            
        # Force edit modified back to default false, otherwise new edit detections don't get caught
        self.fontSizeInputBox.edit_modified(False)
        
    def updateInterfaceForToxin(self, toxinBool):
        if(toxinBool):
            # self.analyzerWindow.configure(fg_color = self.toxinColor)
            if(self.fullParser.overlayWindow != None):
                self.fullParser.overlayWindow.updateInterfaceForToxin(self.toxinColor)
                self.fullParser.app.after(10000, self.updateInterfaceForToxin, False)
        else:
            # self.analyzerWindow.configure(fg_color = self.defaultWindowColor)
            if(self.fullParser.overlayWindow != None):
                self.fullParser.overlayWindow.updateInterfaceForToxin(self.defaultOverlayColor)
            