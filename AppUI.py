import datetime
import json
import logging
import sys
import tkinter
import webbrowser
import customtkinter
import os
from PIL import Image
import re
from json import JSONEncoder
import matplotlib.pyplot as plt
import numpy as np
import tkchart
from staticStrings import StringConstants

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

    # Line and Column values for various UI elements
    columnRelValues = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]
    lineRelValues = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]

    lineRelValuesCheckbox = [0.1, 0.22, 0.34, 0.46, 0.58, 0.70, 0.82, 0.95]
    checkboxRelXValue = .13

    columnRelValuesDisruption = [0.30, 0.42, 0.54, 0.66, 0.78, 0.88]
    lineRelValuesDisruption = [0.20, 0.32, 0.53, 0.65, 0.80]

    def __init__(self, fullClass, app) -> None:
        
        self.fullParser = fullClass

        self.app = app

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

        # Smaller inner window that contains discord tag
        self.smallerInnerWindowDiscordBox = customtkinter.CTkFrame(self.innerWindowBox, width = 130, height = 22, fg_color="#404040")
        self.smallerInnerWindowDiscordBox.pack_propagate(0)
        self.smallerInnerWindowDiscordBox.place(relx = self.columnRelValues[9] + .015, rely = .96, anchor = "center")

        # Discord tag and image
        self.discordTagLabel = customtkinter.CTkLabel(self.smallerInnerWindowDiscordBox, text = StringConstants.discordTagString, text_color = self.textColor, font = ("Arial", 11))
        self.discordTagLabel.place(relx = .43, rely = .5, anchor = "center")

        imageDiscordRaw = Image.open(resource_path("discordLogo.png"))

        imageDiscordLogo = customtkinter.CTkImage(light_image = imageDiscordRaw, dark_image = imageDiscordRaw, size=(16, 16))
        self.imageLabel = customtkinter.CTkLabel(self.smallerInnerWindowDiscordBox, text="", image = imageDiscordLogo)
        self.imageLabel.place(relx = 0.85, rely = 0.5, anchor = "center")

        # UI elements
        # Settings tab
        self.generalSettingsDisplay = customtkinter.CTkLabel(self.settingsWindow, text = StringConstants.generalSettingsString, text_color = self.textColor, font = ("Arial", 18))
        self.generalSettingsDisplay.place(relx = self.columnRelValues[1], rely = self.lineRelValues[1], anchor = "center")

        # Always on top checkbox
        self.alwaysOnTopCheckBoxValue = customtkinter.StringVar(value = "on")

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

        self.restartReadingButton = customtkinter.CTkButton(
            self.settingsWindow,
            text="Restart",
            font=("Arial", 18),
            width = 84,
            height = 32,
            command = self.restartReading
        )

        self.restartReadingButton.place(relx = self.columnRelValues[5], rely = self.lineRelValues[9], anchor = "center")

        self.restartReadingText = customtkinter.CTkLabel(self.settingsWindow, text = StringConstants.restartReadingTextString, text_color = self.textColor, font = ("Arial", 14))
        self.restartReadingText.place(relx = self.columnRelValues[5], rely = self.lineRelValues[10] - .02, anchor = "center")

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
        self.olympus5CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus6CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus10CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympus11CheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympusAssCheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympusConnCheckBoxValue = customtkinter.StringVar(value = "off")
        self.olympusCheckValuesList = [self.olympus1CheckBoxValue, 
                                       self.olympus2CheckBoxValue, 
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
        i = 0
        for x in self.olympusCheckValuesList:
            newCheckbox = customtkinter.CTkCheckBox(self.settingsWindow, 
                                                text = StringConstants.olympusListForCheckbox[i], 
                                                command = lambda i = i: self.updateCheckboxValueOlympus(i), 
                                                variable = self.olympusCheckValuesList[i], 
                                                onvalue = "on", 
                                                offvalue = "off", 
                                                font = ("Arial", 14),
                                                width = 20
                                                )
            
            self.olympusCheckboxes.append(newCheckbox)
            newCheckbox.place(relx = self.columnRelValues[8] - .025, rely = self.lineRelValues[i + 2], anchor = "w")

            i += 1

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
            width = 20,
            height = 20,
            command = self.previousRound
        )

        self.nextRoundButton = customtkinter.CTkButton(
            self.analyzerWindow,
            text=">",
            font=("Arial", 14),
            width = 20,
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
        self.disruptionRoundInputBox = customtkinter.CTkTextbox(self.analyzerWindow, 
                                                           width = 44, 
                                                           height = 20, 
                                                           corner_radius = 4,
                                                           border_width = 1,
                                                           activate_scrollbars = False,
                                                           wrap = "none"
                                                           )

        self.disrutpionUIElements = [self.keyInsertsStringDisplay, self.demoKillsStringDisplay, self.previousRoundTimeStringDisplay, self.currentAverageStringDisplay, self.expectedEndTimeStringDisplay,
                                self.bestRoundTimeStringDisplay, self.key1Display, self.key2Display, self.key3Display, self.key4Display, self.demo1Display, self.demo2Display, self.demo3Display, self.demo4Display,
                                self.previousRoundTimeDisplay, self.currentAverageDisplay, self.expectedEndTimeDisplay, self.bestRoundTimeDisplay, self.updateFromInputButton, self.previousRoundButton,
                                self.nextRoundButton, self.disruptionDataDumpedDisplay, self.disruptionRoundInputBox
                                ]


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    #                                   Class Funcs                                 #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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

        # Update values
        self.parseFromStartCheckBox.deselect()

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

        self.restartReadingButton.place(relx = self.columnRelValues[5], rely = self.lineRelValues[9], anchor = "center")
        self.restartReadingText.place(relx = self.columnRelValues[5], rely = self.lineRelValues[10] - .02, anchor = "center")

        if self.fullParser.restartReadingBool:
            self.fullParser.restartReadingBool = False
            self.app.after(self.fullParser.sleepBetweenCalls, self.fullParser.startParsing)
        else:
            self.app.after(self.fullParser.sleepBetweenCalls, self.fullParser.scanMissionStart)

    # Update UI to be ready for disruption run logging. Removes most other elements, adds new elements back in
    def updateUIForDisruptionLogging(self):
        if self.fullParser.loggingState:
            logging.info("In updateUIForDisruptionLogging()")

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

        self.previousRoundButton.place(relx = .43, rely = self.columnRelValuesDisruption[5], anchor = "c")
        self.nextRoundButton.place(relx = .46, rely = self.columnRelValuesDisruption[5], anchor = "c")

        self.disruptionRoundInputBox.place(relx = .5, rely = self.columnRelValuesDisruption[5], anchor = "c")
        self.updateFromInputButton.place(relx = .56, rely = self.columnRelValuesDisruption[5], anchor = "c")

        if self.fullParser.loggingState:
            logging.info("updateUIForDisruptionLogging() finished, moving to scanDisruptionProgress()")

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

        self.app.after(self.fullParser.sleepBetweenCalls, self.fullParser.scanMissionStart) 