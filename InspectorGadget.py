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

# Logging status
logging.basicConfig(filename = 'inspectorLog.log', encoding = 'utf-8', filemode='w', level = logging.DEBUG, format='%(asctime)s %(message)s')
loggingState = False

# Start parsing from end of file onwards
parseFromEnd = True

# Set the file path for ee.log
filename = os.getenv('LOCALAPPDATA') + r'\Warframe\EE.log'
file = None

# Rollback positions for parser to return to if incomplete lines are read, or required rollbacks
fileRollbackPosition = None
fileRollbackPositionSmall = None
restartReadingBool = False

# Time to sleep between each parsing progression, in millis
sleepBetweenCalls = 1000

# System Settings
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")
customtkinter.deactivate_automatic_dpi_awareness()

# Open url in web browser
def openInBrowser(url):
   webbrowser.open_new_tab(url)

# Get absolute path to resource, used for images so that they can be added to .exe
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

appLogo = resource_path("peepoHmm.ico")

# App window - Size, Title, icon and always on top setting
app = customtkinter.CTk()
app.geometry("960x512")
app.title("InspectorGadget")
app.iconbitmap(appLogo)
app.attributes('-topmost', True)

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

# Some misc variables
currentMission = ""
kappaRegBadList = [StringConstants.kappa3, StringConstants.kappa7]
apolloRegBadList = [StringConstants.apollo6]
disruptionTilesFoundList = []
disruptionRun = None
disruptionCurrentRound = None

# Tab list
innerWindowBox = customtkinter.CTkTabview(app, width = app._current_width - 20, height = app._current_height - 20)
innerWindowBox.pack_propagate(0)
innerWindowBox.place(relx = .5, rely = .01, anchor = tkinter.N)

settingsWindow = innerWindowBox.add("Settings")  
# tilesWindow = innerWindowBox.add("Tiles")  
analyzerWindow = innerWindowBox.add("Analyzer")  
chartWindow = None

# Smaller inner window that contains discord tag
smallerInnerWindowDiscordBox = customtkinter.CTkFrame(innerWindowBox, width = 130, height = 22, fg_color="#404040")
smallerInnerWindowDiscordBox.pack_propagate(0)
smallerInnerWindowDiscordBox.place(relx = columnRelValues[9] + .015, rely = .96, anchor = "center")

# Discord tag and image
discordTagLabel = customtkinter.CTkLabel(smallerInnerWindowDiscordBox, text = StringConstants.discordTagString, text_color = textColor, font = ("Arial", 11))
discordTagLabel.place(relx = .43, rely = .5, anchor = "center")

imageDiscordRaw = Image.open(resource_path("discordLogo.png"))

imageDiscordLogo = customtkinter.CTkImage(light_image = imageDiscordRaw, dark_image = imageDiscordRaw, size=(16, 16))
imageLabel = customtkinter.CTkLabel(smallerInnerWindowDiscordBox, text="", image = imageDiscordLogo)
imageLabel.place(relx = 0.85, rely = 0.5, anchor = "center")


# Reset analyzer UI
def resetAnalyzerUI():
    global restartReadingBool
    global parseFromEnd 
    global loggingState 
    global currentRoundShown 
    global disruptionTilesFoundList 

    # Logging
    if loggingState:
        logging.info("In resetDisplay()")

    # Update values
    restartReadingBool = False
    parseFromEnd = False
    parseFromStartCheckBox.deselect()

    # Disable disruption related UI elements
    keyInsertsStringDisplay.place_forget()
    demoKillsStringDisplay.place_forget() 
    previousRoundTimeStringDisplay.place_forget() 
    currentAverageStringDisplay.place_forget() 
    expectedEndTimeStringDisplay.place_forget() 
    bestRoundTimeStringDisplay.place_forget() 

    key1Display.place_forget()
    key2Display.place_forget()
    key3Display.place_forget()
    key4Display.place_forget()

    demo1Display.place_forget()
    demo2Display.place_forget()
    demo3Display.place_forget()
    demo4Display.place_forget()

    previousRoundTimeDisplay.place_forget() 
    currentAverageDisplay.place_forget() 
    expectedEndTimeDisplay.place_forget()
    bestRoundTimeDisplay.place_forget() 
    updateFromInputButton.place_forget()

    disruptionDataDumpedDisplay.place_forget()

    previousRoundButton.place_forget()
    nextRoundButton.place_forget()
    disruptionRoundInputBox.place_forget()

    try:
        innerWindowBox.delete("Chart")
    except:
        logging.warning("Attempt to hide Chart window without it existing")

    # Reset various variables
    currentRoundShown = -1
    disruptionTilesFoundList = []

    # Re-enable original display info
    missionNameDisplay.place(relx = .5, rely = lineRelValues[3], anchor = "center")
    foundTileDisplay.place(relx = .5, rely = lineRelValues[5], anchor = "center")
    whatIsBeingParsedDisplay.place(relx = columnRelValues[9] + .02, rely = lineRelValues[4], anchor = "center")

    foundTileDisplay.configure(text = StringConstants.waitingForMissionStart, text_color = textColor)
    missionNameDisplay.configure(text = StringConstants.replacedByMissionNameString, text_color = textColor)

    restartReadingButton.place(relx = columnRelValues[5], rely = lineRelValues[9], anchor = "center")
    restartReadingText.place(relx = columnRelValues[5], rely = lineRelValues[10] - .02, anchor = "center")

    app.after(sleepBetweenCalls, startParsing)

# UI elements
# Settings tab
generalSettingsDisplay = customtkinter.CTkLabel(settingsWindow, text = StringConstants.generalSettingsString, text_color = textColor, font = ("Arial", 18))
generalSettingsDisplay.place(relx = columnRelValues[1], rely = lineRelValues[1], anchor = "center")

# Always on top checkbox
alwaysOnTopCheckBoxValue = customtkinter.StringVar(value = "on")

def alwaysOnTopCheckBox_event():
    if loggingState:
        logging.info("Changed status of On Top Window to " + alwaysOnTopCheckBoxValue.get())

    if alwaysOnTopCheckBoxValue.get() == "on":
        app.attributes('-topmost', True)
    else:
        app.attributes('-topmost', False)

alwaysOnTopCheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "Always on top", 
                                           command = alwaysOnTopCheckBox_event, 
                                           variable = alwaysOnTopCheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14)
                                           )
alwaysOnTopCheckBox.place(relx = columnRelValues[0] + .025, rely = lineRelValues[2], anchor = "w")

# Parse from file start checkbox
parseFromStartCheckBoxValue = customtkinter.StringVar(value = "off")

def parseFromStartCheckBox_event():
    global parseFromEnd
    global restartReadingBool

    if loggingState:
        logging.info("Changed status of Parse From Start to " + parseFromStartCheckBoxValue.get())

    if parseFromStartCheckBoxValue.get() == "on":
        parseFromEnd = False
        restartReadingBool = True
        app.after(sleepBetweenCalls, resetAnalyzerUI)
    else:
        parseFromEnd = True

parseFromStartCheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "Read from start", 
                                           command = parseFromStartCheckBox_event, 
                                           variable = parseFromStartCheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14)
                                           )
parseFromStartCheckBox.place(relx = columnRelValues[0] + .025, rely = lineRelValues[3], anchor = "w")

# Logging checkbox
loggingCheckBoxValue = customtkinter.StringVar(value = "off")

def loggingCheckBox_event():
    global loggingState

    if loggingState:
        logging.info("Logging set to " + loggingCheckBoxValue.get())

    if loggingCheckBoxValue.get() == "on":
        loggingState = True
    else:
        loggingState = False

loggingCheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "Enable logging", 
                                           command = loggingCheckBox_event, 
                                           variable = loggingCheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14)
                                           )
loggingCheckBox.place(relx = columnRelValues[0] + .025, rely = lineRelValues[4], anchor = "w")

# Restart reading button
def restartReading():
    global fileRollbackPosition
    global restartReadingBool

    if loggingState:
        logging.info("Restart reading button pressed")

    restartReadingBool = True

    app.after(sleepBetweenCalls, restartReadingActual)

def restartReadingActual():
    global fileRollbackPosition

    file.seek(fileRollbackPosition)
    app.after(10, resetDisplay)


restartReadingButton = customtkinter.CTkButton(
    settingsWindow,
    text="Restart",
    font=("Arial", 18),
    width = 84,
    height = 32,
    command = restartReading
)

restartReadingButton.place(relx = columnRelValues[5], rely = lineRelValues[9], anchor = "center")

restartReadingText = customtkinter.CTkLabel(settingsWindow, text = StringConstants.restartReadingTextString, text_color = textColor, font = ("Arial", 14))
restartReadingText.place(relx = columnRelValues[5], rely = lineRelValues[10] - .02, anchor = "center")


# Tiles tab
# imageKappa1Raw = Image.open(resource_path("kappa1.png"))
# imageKappa1 = customtkinter.CTkImage(light_image = imageKappa1Raw, dark_image = imageKappa1Raw, size = (300, 169))
# imageKappa1Label = customtkinter.CTkLabel(tilesWindow, text="", image = imageKappa1)
# imageKappa1Label.place(relx = columnRelValues[1] + .05, rely = lineRelValues[3], anchor = "center")

# imageKappa3Raw = Image.open(resource_path("kappa3.png"))
# imageKappa3 = customtkinter.CTkImage(light_image = imageKappa3Raw, dark_image = imageKappa3Raw, size = (300, 169))
# imageKappa3Label = customtkinter.CTkLabel(tilesWindow, text="", image = imageKappa3)
# imageKappa3Label.place(relx = columnRelValues[5], rely = lineRelValues[3], anchor = "center")

# imageKappa4Raw = Image.open(resource_path("kappa4.png"))
# imageKappa4 = customtkinter.CTkImage(light_image = imageKappa4Raw, dark_image = imageKappa4Raw, size = (300, 169))
# imageKappa4Label = customtkinter.CTkLabel(tilesWindow, text="", image = imageKappa4)
# imageKappa4Label.place(relx = columnRelValues[9] - .05, rely = lineRelValues[3], anchor = "center")

# imageKappa6Raw = Image.open(resource_path("kappa6.png"))
# imageKappa6 = customtkinter.CTkImage(light_image = imageKappa6Raw, dark_image = imageKappa6Raw, size = (300, 169))
# imageKappa6Label = customtkinter.CTkLabel(tilesWindow, text="", image = imageKappa6)
# imageKappa6Label.place(relx = columnRelValues[1] + .05, rely = lineRelValues[7], anchor = "center")

# imageKappa7Raw = Image.open(resource_path("kappa7.png"))
# imageKappa7 = customtkinter.CTkImage(light_image = imageKappa7Raw, dark_image = imageKappa7Raw, size = (300, 169))
# imageKappa7Label = customtkinter.CTkLabel(tilesWindow, text="", image = imageKappa7)
# imageKappa7Label.place(relx = columnRelValues[5], rely = lineRelValues[7], anchor = "center")

# imageKappa8Raw = Image.open(resource_path("kappa8.png"))
# imageKappa8 = customtkinter.CTkImage(light_image = imageKappa8Raw, dark_image = imageKappa8Raw, size = (300, 169))
# imageKappa8Label = customtkinter.CTkLabel(tilesWindow, text="", image = imageKappa8)
# imageKappa8Label.place(relx = columnRelValues[9] - .05, rely = lineRelValues[7], anchor = "center")

# urlLinkToImgur = customtkinter.CTkLabel(tilesWindow, text = StringConstants.urlFindMore, text_color = textColorHyperlink, font = ("Arial", 18), cursor = "hand2")
# urlLinkToImgur.place(relx = columnRelValues[5], rely = columnRelValues[10] - .02, anchor = "center")
# urlLinkToImgur.bind("<Button-1>", lambda e:openInBrowser("https://imgur.com/a/cKyEWnp"))

# Analyzer Tab
missionNameDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.replacedByMissionNameString, text_color = textColor, font = ("Arial", 28))
missionNameDisplay.place(relx = .5, rely = lineRelValues[3], anchor = "center")

foundTileDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.waitingForMissionStart, text_color = textColor, font = ("Arial", 32))
foundTileDisplay.place(relx = .5, rely = lineRelValues[5], anchor = "center")

whatIsBeingParsedDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.whatIsBeingParsedText, text_color = textColor, font = ("Arial", 18))
whatIsBeingParsedDisplay.place(relx = columnRelValues[9] + .02, rely = lineRelValues[4], anchor = "center")

disruptionDataDumpedDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.disruptionDataDumpedString, text_color = textColorGreen, font = ("Arial", 22))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#  I hate how this is done but I don't have the brains to make it correctly   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# Checkboxes for each of the possible main tiles - Kappa
kappa1CheckBoxValue = customtkinter.StringVar(value = "off")
kappa3CheckBoxValue = customtkinter.StringVar(value = "on")
kappa4CheckBoxValue = customtkinter.StringVar(value = "off")
kappa6CheckBoxValue = customtkinter.StringVar(value = "off")
kappa7CheckBoxValue = customtkinter.StringVar(value = "on")
kappa8CheckBoxValue = customtkinter.StringVar(value = "off")

selectBadTilesKappaDisplay = customtkinter.CTkLabel(settingsWindow, 
                                                    text = StringConstants.selectBadTilesKappaString, 
                                                    text_color = textColorHyperlink, 
                                                    font = ("Arial", 18),
                                                    cursor = "hand2"
                                                    )
selectBadTilesKappaDisplay.place(relx = columnRelValues[4], rely = lineRelValues[1], anchor = "center")
selectBadTilesKappaDisplay.bind("<Button-1>", lambda e:openInBrowser("https://imgur.com/a/cKyEWnp"))

def kappa1Checkbox_event():
    if kappa1CheckBoxValue.get() == "on":
        kappaRegBadList.append(StringConstants.kappa1)
    else:
        kappaRegBadList.remove(StringConstants.kappa1)
    
    if loggingState:
        logging.info("Kappa 1 checkbox value changed to " + kappa1CheckBoxValue.get())

kappa1CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "1", 
                                           command = kappa1Checkbox_event, 
                                           variable = kappa1CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
kappa1CheckBox.place(relx = columnRelValues[4], rely = lineRelValues[2], anchor = "center")



def kappa3Checkbox_event():
    if kappa3CheckBoxValue.get() == "on":
        kappaRegBadList.append(StringConstants.kappa3)
    else:
        kappaRegBadList.remove(StringConstants.kappa3)
    
    if loggingState:
        logging.info("Kappa 3 checkbox value changed to " + kappa3CheckBoxValue.get())

kappa3CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "3", 
                                           command = kappa3Checkbox_event, 
                                           variable = kappa3CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
kappa3CheckBox.place(relx = columnRelValues[4], rely = lineRelValues[3], anchor = "center")



def kappa4Checkbox_event():
    if kappa4CheckBoxValue.get() == "on":
        kappaRegBadList.append(StringConstants.kappa4)
    else:
        kappaRegBadList.remove(StringConstants.kappa4)
    
    if loggingState:
        logging.info("Kappa 4 checkbox value changed to " + kappa4CheckBoxValue.get())

kappa4CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "4", 
                                           command = kappa4Checkbox_event, 
                                           variable = kappa4CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
kappa4CheckBox.place(relx = columnRelValues[4], rely = lineRelValues[4], anchor = "center")



def kappa6Checkbox_event():
    if kappa6CheckBoxValue.get() == "on":
        kappaRegBadList.append(StringConstants.kappa6)
    else:
        kappaRegBadList.remove(StringConstants.kappa6)
    
    if loggingState:
        logging.info("Kappa 6 checkbox value changed to " + kappa6CheckBoxValue.get())

kappa6CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "6", 
                                           command = kappa6Checkbox_event, 
                                           variable = kappa6CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
kappa6CheckBox.place(relx = columnRelValues[4], rely = lineRelValues[5], anchor = "center")



def kappa7Checkbox_event():
    if kappa7CheckBoxValue.get() == "on":
        kappaRegBadList.append(StringConstants.kappa7)
    else:
        kappaRegBadList.remove(StringConstants.kappa7)
    
    if loggingState:
        logging.info("Kappa 7 checkbox value changed to " + kappa7CheckBoxValue.get())

kappa7CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "7", 
                                           command = kappa7Checkbox_event, 
                                           variable = kappa7CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
kappa7CheckBox.place(relx = columnRelValues[4], rely = lineRelValues[6], anchor = "center")



def kappa8Checkbox_event():
    if kappa8CheckBoxValue.get() == "on":
        kappaRegBadList.append(StringConstants.kappa8)
    else:
        kappaRegBadList.remove(StringConstants.kappa8)
    
    if loggingState:
        logging.info("Kappa 8 checkbox value changed to " + kappa8CheckBoxValue.get())
    

kappa8CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "8", 
                                           command = kappa8Checkbox_event, 
                                           variable = kappa8CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
kappa8CheckBox.place(relx = columnRelValues[4], rely = lineRelValues[7], anchor = "center")



# Checkboxes for each of the possible main tiles - Apollo
apollo1CheckBoxValue = customtkinter.StringVar(value = "off")
apollo2CheckBoxValue = customtkinter.StringVar(value = "off")
apollo3CheckBoxValue = customtkinter.StringVar(value = "off")
apollo4CheckBoxValue = customtkinter.StringVar(value = "off")
apollo5CheckBoxValue = customtkinter.StringVar(value = "off")
apollo6CheckBoxValue = customtkinter.StringVar(value = "on")
apollo7CheckBoxValue = customtkinter.StringVar(value = "off")

selectBadTilesApolloDisplay = customtkinter.CTkLabel(settingsWindow, 
                                                     text = StringConstants.selectBadTilesApolloString, 
                                                     text_color = textColorHyperlink, 
                                                     font = ("Arial", 18), 
                                                     cursor = "hand2"
                                                     )
selectBadTilesApolloDisplay.place(relx = columnRelValues[6], rely = lineRelValues[1], anchor = "center")
selectBadTilesApolloDisplay.bind("<Button-1>", lambda e:openInBrowser("https://imgur.com/a/cKyEWnp"))


def apollo1Checkbox_event():
    if apollo1CheckBoxValue.get() == "on":
        apolloRegBadList.append(StringConstants.apollo1)
    else:
        apolloRegBadList.remove(StringConstants.apollo1)
    
    if loggingState:
        logging.info("Apollo 1 checkbox value changed to " + apollo1CheckBoxValue.get())

apollo1CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "BotGarden", 
                                           command = apollo1Checkbox_event, 
                                           variable = apollo1CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
apollo1CheckBox.place(relx = columnRelValues[6] - .062, rely = lineRelValues[2], anchor = "w")



def apollo2Checkbox_event():
    if apollo2CheckBoxValue.get() == "on":
        apolloRegBadList.append(StringConstants.apollo2)
    else:
        apolloRegBadList.remove(StringConstants.apollo2)
    
    if loggingState:
        logging.info("Apollo 2 checkbox value changed to " + apollo2CheckBoxValue.get())

apollo2CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "Cloister", 
                                           command = apollo2Checkbox_event, 
                                           variable = apollo2CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
apollo2CheckBox.place(relx = columnRelValues[6] - .062, rely = lineRelValues[3], anchor = "w")



def apollo3Checkbox_event():
    if apollo3CheckBoxValue.get() == "on":
        apolloRegBadList.append(StringConstants.apollo3)
    else:
        apolloRegBadList.remove(StringConstants.apollo3)
    
    if loggingState:
        logging.info("Apollo 3 checkbox value changed to " + apollo3CheckBoxValue.get())

apollo3CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "Endurance", 
                                           command = apollo3Checkbox_event, 
                                           variable = apollo3CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
apollo3CheckBox.place(relx = columnRelValues[6] - .062, rely = lineRelValues[4], anchor = "w")



def apollo4Checkbox_event():
    if apollo4CheckBoxValue.get() == "on":
        apolloRegBadList.append(StringConstants.apollo4)
    else:
        apolloRegBadList.remove(StringConstants.apollo4)
    
    if loggingState:
        logging.info("Apollo 4 checkbox value changed to " + apollo4CheckBoxValue.get())

apollo4CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "HallsOfJudge", 
                                           command = apollo4Checkbox_event, 
                                           variable = apollo4CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
apollo4CheckBox.place(relx = columnRelValues[6] - .062, rely = lineRelValues[5], anchor = "w")



def apollo5Checkbox_event():
    if apollo5CheckBoxValue.get() == "on":
        apolloRegBadList.append(StringConstants.apollo5)
    else:
        apolloRegBadList.remove(StringConstants.apollo5)
    
    if loggingState:
        logging.info("Apollo 5 checkbox value changed to " + apollo5CheckBoxValue.get())

apollo5CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "Power", 
                                           command = apollo5Checkbox_event, 
                                           variable = apollo5CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
apollo5CheckBox.place(relx = columnRelValues[6] - .062, rely = lineRelValues[6], anchor = "w")



def apollo6Checkbox_event():
    if apollo6CheckBoxValue.get() == "on":
        apolloRegBadList.append(StringConstants.apollo6)
    else:
        apolloRegBadList.remove(StringConstants.apollo6)
    
    if loggingState:
        logging.info("Apollo 6 checkbox value changed to " + apollo6CheckBoxValue.get())
    

apollo6CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "RuinedPiaza", 
                                           command = apollo6Checkbox_event, 
                                           variable = apollo6CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
apollo6CheckBox.place(relx = columnRelValues[6] - .062, rely = lineRelValues[7], anchor = "w")



def apollo7Checkbox_event():
    if apollo7CheckBoxValue.get() == "on":
        apolloRegBadList.append(StringConstants.apollo7)
    else:
        apolloRegBadList.remove(StringConstants.apollo7)
    
    if loggingState:
        logging.info("Apollo 7 checkbox value changed to " + apollo7CheckBoxValue.get())
    

apollo7CheckBox = customtkinter.CTkCheckBox(settingsWindow, 
                                           text = "Stealth", 
                                           command = apollo7Checkbox_event, 
                                           variable = apollo7CheckBoxValue, 
                                           onvalue = "on", 
                                           offvalue = "off", 
                                           font = ("Arial", 14),
                                           width = 20
                                           )
apollo7CheckBox.place(relx = columnRelValues[6] - .062, rely = lineRelValues[8], anchor = "w")


# Class that stores all disruption run information (rounds, avg, etc)
class DisruptionRun:
    def __init__(self) -> None:
    
        self.rounds = []
        self.runTimeStartInSeconds = 0
        self.round45TimeEndInSeconds = 0
        self.round45TimeDurationSeconds = 0
        self.round45TimeDurationString = ""
        self.sumOfRoundTimesInSeconds = 0
        self.expectedRunTimeInSeconds = 0

        self.keysCompleted = 0

        self.bestRunTime = 99999
        self.bestRunTimeString = 0
        self.bestRunTimeRoundNr = 0

# Class that stores a single disruption round's information
class DisruptionRound:
    def __init__(self) -> None:
    
        self.keyInsertTimes = [0,0,0,0]
        self.demoKillTimes = [0,0,0,0]

        self.roundTimeStartInSeconds = 0
        self.roundTimeEndInSeconds = 0
        self.totalRoundTimeInSeconds = 0

        self.keyInsertTimesString = ["0","0","0","0"]
        self.demoKillTimesString = ["0","0","0","0"]
        self.totalRoundTimeInSecondsString = 0

# Allows for serialization of other class, to convert to Json
class DisruptionJsonEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__ 

# Class used to dump all run times to disk, will be converted to json using the function bellow
class DisruptionRunTimesJson:
    def __init__(self) -> None:
        self.runTimesInSeconds = []
        self.fullRun = None

# Extract all round times, convert class to json and dump to file
def saveTimesAndDumpJson():
    global disruptionRun
    global chartWindow

    if loggingState:
        logging.info("In saveTimesAndDumpJson()")

    jsonClass = DisruptionRunTimesJson()

    # Add all round times to the list
    for roundX in disruptionRun.rounds:
        jsonClass.runTimesInSeconds.append(round(roundX.totalRoundTimeInSeconds, 2))

    # Add full raw run
    jsonClass.fullRun = disruptionRun

    JSONData = json.dumps(jsonClass, indent=4, cls=DisruptionJsonEncoder)

    with open('disruptionFullRunData.json', 'w', encoding='utf-8') as f:
        f.write(JSONData)
        f.close()

    disruptionDataDumpedDisplay.place(relx = .5, rely = lineRelValues[8], anchor = "center")

    # Create new tab for chart, and add chart with times per round
    chartWindow = innerWindowBox.add("Chart")  

    # Get values for x axis. Simultaneously, find highest and lowst run times
    minValue = 9999
    maxValue = 0

    xAxisValues = []
    i = 1
    for x in jsonClass.runTimesInSeconds:
        xAxisValues.append(i)


        if x > maxValue and i > 1:
            maxValue = x

        if x < minValue and i > 1:
            minValue = x

        i += 1
        

    # Create list with min and max values for drawing respective lines on chart
    minList = []
    maxList = []
    i = 1
    for x in jsonClass.runTimesInSeconds:
        i += 1

        minList.append(minValue)
        maxList.append(maxValue)

    # Add line chart. Will fail if no rounds have been completed
    try:
        lineChart = tkchart.LineChart(
                                master = chartWindow,
                                width = app._current_width - 80, 
                                height = app._current_height - 80,
                                axis_size = 2,
                                x_axis_label_count = 6,
                                y_axis_max_value = 240,
                                y_axis_data = "Time",
                                x_axis_data = "Round",
                                x_axis_values = xAxisValues,
                                x_axis_data_position = "side",
                                y_axis_data_position = "side"
                                )
        lineChart.place(relx = .5, rely = 0, anchor = "n")

        # Draw lines, one for time per round, one for max and one for min
        lineToDraw = tkchart.Line(
                    master = lineChart,
                    color = "lightblue",
                    size = 2,
                    style = "line"
                    )
        
        lineToDrawAbove = tkchart.Line(
                    master = lineChart,
                    color = "#326fa8",
                    size = 2,
                    style = "dashed"
                    )
        
        lineToDrawBellow = tkchart.Line(
                    master = lineChart,
                    color = "#326fa8",
                    size = 2,
                    style = "dashed"
                    )


        lineChart.show_data(data = jsonClass.runTimesInSeconds, line = lineToDraw)
        lineChart.show_data(data = maxList, line = lineToDrawAbove)
        lineChart.show_data(data = minList, line = lineToDrawBellow)
    except:
        logging.error("Attempted to draw chart with no finished rounds")



# UI elements for disruption
keyInsertsStringDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.disruptionKeyInsertsStaticString, text_color = textColor, font = ("Arial", 24))
demoKillsStringDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.disruptionDemoKillsString, text_color = textColor, font = ("Arial", 24))
previousRoundTimeStringDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.disruptionPreviousRunAverateString, text_color = textColor, font = ("Arial", 24))
currentAverageStringDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.disruptionCurrentAverateString, text_color = textColor, font = ("Arial", 24))
expectedEndTimeStringDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.disruptionExpectedEndString, text_color = textColor, font = ("Arial", 24))
bestRoundTimeStringDisplay = customtkinter.CTkLabel(analyzerWindow, text = StringConstants.bestRoundTimeString, text_color = textColor, font = ("Arial", 24))

key1Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
key2Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
key3Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
key4Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))

demo1Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
demo2Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
demo3Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
demo4Display = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))

keyDisplays = [key1Display, key2Display, key3Display, key4Display]
demoDisplays = [demo1Display, demo2Display, demo3Display, demo4Display]

previousRoundTimeDisplay = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
currentAverageDisplay = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
expectedEndTimeDisplay = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))
bestRoundTimeDisplay = customtkinter.CTkLabel(analyzerWindow, text = "", text_color = textColor, font = ("Arial", 24))

# UI elements for scrolling through rounds
previousRoundButton = None
nextRoundButton = None
currentRoundShown = -1
currentKeysInserted = 0
currentDemosKilled = 0

# Function called by next round button, changes UI values to next round's
def previousRound():
    global currentRoundShown
    global loggingState
    
    if currentRoundShown > 1:
        currentRoundShown -= 1

    updateDisruptionUIValues(currentRoundShown)

    disruptionRoundInputBox.delete('0.0', 'end')
    disruptionRoundInputBox.insert('end', currentRoundShown)

    if loggingState:
        logging.info("Previous round button pressed, with updated value of " + str(currentRoundShown))


# Function called by previous round button, changes UI values to previous round's
def nextRound():
    global currentRoundShown
    global loggingState 

    if currentRoundShown < len(disruptionRun.rounds):
        currentRoundShown += 1

    updateDisruptionUIValues(currentRoundShown)
        
    disruptionRoundInputBox.delete('0.0', 'end')
    disruptionRoundInputBox.insert('end', currentRoundShown)

    if loggingState:
        logging.info("Next round button pressed, with updated value of " + str(currentRoundShown))


# Function called by the update round button, changes UI values to given round if possible
def updateRoundFromInput():
    global currentRoundShown
    global loggingState 
    
    tempRound = 0
    
    try:
        tempRound = int(disruptionRoundInputBox.get('1.0', "end-1c"))
    except:
        logging.error("Given value is not a valid number (or not a number at all)")

    if tempRound > len(disruptionRun.rounds):
        currentRoundShown = len(disruptionRun.rounds)
    elif tempRound <= 0:
        currentRoundShown = 1
    else:
        currentRoundShown = tempRound

    disruptionRoundInputBox.delete('0.0', 'end')
    disruptionRoundInputBox.insert('end', currentRoundShown)

    updateDisruptionUIValues(currentRoundShown)

    if loggingState:
        logging.info("Updating display round value based on input with value of " + str(currentRoundShown))

# Next/Prev run buttons 
previousRoundButton = customtkinter.CTkButton(
    analyzerWindow,
    text="<",
    font=("Arial", 14),
    width = 20,
    height = 20,
    command = previousRound
)

nextRoundButton = customtkinter.CTkButton(
    analyzerWindow,
    text=">",
    font=("Arial", 14),
    width = 20,
    height = 20,
    command = nextRound
)

# Update button for UI update from input 
updateFromInputButton = customtkinter.CTkButton(
    analyzerWindow,
    text="Update",
    font=("Arial", 14),
    width = 50,
    height = 20,
    command = updateRoundFromInput
)

inputBoxValue = tkinter.StringVar()

# Input box for going to specific round number in disruption run 
disruptionRoundInputBox = customtkinter.CTkTextbox(analyzerWindow, 
                                                   width = 44, 
                                                   height = 20, 
                                                   corner_radius = 4,
                                                   border_width = 1,
                                                   activate_scrollbars = False,
                                                   wrap = "none"
                                                   )


# Update UI to be ready for disruption run logging. Removes most other elements, adds new elements back in
def updateUIForDisruptionLogging():
    global loggingState 

    if loggingState:
        logging.info("In updateUIForDisruptionLogging()")

    # Remove old un-needed elements    
    missionNameDisplay.place_forget()
    foundTileDisplay.place_forget()
    whatIsBeingParsedDisplay.place_forget()
    disruptionDataDumpedDisplay.place_forget()

    # Add new elements
    keyInsertsStringDisplay.place(relx = columnRelValuesDisruption[0], rely = lineRelValuesDisruption[0], anchor = "e")
    demoKillsStringDisplay.place(relx = columnRelValuesDisruption[0], rely = lineRelValuesDisruption[1], anchor = "e")
    
    bestRoundTimeStringDisplay.place(relx = columnRelValuesDisruption[3], rely = lineRelValuesDisruption[2], anchor = "e")
    previousRoundTimeStringDisplay.place(relx = columnRelValuesDisruption[0], rely = lineRelValuesDisruption[2], anchor = "e")
    
    currentAverageStringDisplay.place(relx = columnRelValuesDisruption[0], rely = lineRelValuesDisruption[3], anchor = "e")
    expectedEndTimeStringDisplay.place(relx = columnRelValuesDisruption[3], rely = lineRelValuesDisruption[3], anchor = "e")

    key1Display.place(relx = columnRelValuesDisruption[1], rely = lineRelValuesDisruption[0], anchor = "center")
    key2Display.place(relx = columnRelValuesDisruption[2], rely = lineRelValuesDisruption[0], anchor = "center")
    key3Display.place(relx = columnRelValuesDisruption[3], rely = lineRelValuesDisruption[0], anchor = "center")
    key4Display.place(relx = columnRelValuesDisruption[4], rely = lineRelValuesDisruption[0], anchor = "center")

    demo1Display.place(relx = columnRelValuesDisruption[1], rely = lineRelValuesDisruption[1], anchor = "center")
    demo2Display.place(relx = columnRelValuesDisruption[2], rely = lineRelValuesDisruption[1], anchor = "center")
    demo3Display.place(relx = columnRelValuesDisruption[3], rely = lineRelValuesDisruption[1], anchor = "center")
    demo4Display.place(relx = columnRelValuesDisruption[4], rely = lineRelValuesDisruption[1], anchor = "center")

    previousRoundTimeDisplay.place(relx = columnRelValuesDisruption[1], rely = lineRelValuesDisruption[2], anchor = "center")
    currentAverageDisplay.place(relx = columnRelValuesDisruption[1], rely = lineRelValuesDisruption[3], anchor = "center")
    expectedEndTimeDisplay.place(relx = columnRelValuesDisruption[4], rely = lineRelValuesDisruption[3], anchor = "center")
    bestRoundTimeDisplay.place(relx = columnRelValuesDisruption[4], rely = lineRelValuesDisruption[2], anchor = "center")

    previousRoundButton.place(relx = .43, rely = columnRelValuesDisruption[5], anchor = "c")
    nextRoundButton.place(relx = .46, rely = columnRelValuesDisruption[5], anchor = "c")

    disruptionRoundInputBox.place(relx = .5, rely = columnRelValuesDisruption[5], anchor = "c")
    updateFromInputButton.place(relx = .56, rely = columnRelValuesDisruption[5], anchor = "c")

    app.after(sleepBetweenCalls, scanDisruptionProgress)


# Clean current disruption round values
def cleanDisruptionUI():
    global loggingState 

    if loggingState:
        logging.info("In cleanDisruptionUI()")

    key1Display.configure(text = "", text_color = textColor)
    key2Display.configure(text = "", text_color = textColor)
    key3Display.configure(text = "", text_color = textColor)
    key4Display.configure(text = "", text_color = textColor)

    demo1Display.configure(text = "", text_color = textColor)
    demo2Display.configure(text = "", text_color = textColor)
    demo3Display.configure(text = "", text_color = textColor)
    demo4Display.configure(text = "", text_color = textColor)


# Update disruption UI with values of a given set
def updateDisruptionUIValues(runNumberToDisplay):
    global loggingState 
    
    if loggingState:
        logging.info("In updateDisruptionUIValues()")

    try:
        roundToDisplay = disruptionRun.rounds[runNumberToDisplay - 1]

        key1Display.configure(text = roundToDisplay.keyInsertTimesString[0], text_color = textColor)
        key2Display.configure(text = roundToDisplay.keyInsertTimesString[1], text_color = textColor)
        key3Display.configure(text = roundToDisplay.keyInsertTimesString[2], text_color = textColor)
        key4Display.configure(text = roundToDisplay.keyInsertTimesString[3], text_color = textColor)

        demo1Display.configure(text = roundToDisplay.demoKillTimesString[0], text_color = textColor)
        demo2Display.configure(text = roundToDisplay.demoKillTimesString[1], text_color = textColor)
        demo3Display.configure(text = roundToDisplay.demoKillTimesString[2], text_color = textColor)
        demo4Display.configure(text = roundToDisplay.demoKillTimesString[3], text_color = textColor)

        previousRoundTimeDisplay.configure(text = roundToDisplay.totalRoundTimeInSecondsString, text_color = textColor)
    
    except:
        logging.error("Given run number is out of bounds of the array (too big, or too small)")


# Reset display to default text and colors
def resetDisplay():
    global restartReadingBool
    global loggingState 

    # Logging
    if loggingState:
        logging.info("In resetDisplay()")

    restartReadingBool = False

    foundTileDisplay.configure(text = StringConstants.waitingForMissionStart, text_color = textColor)
    missionNameDisplay.configure(text = StringConstants.replacedByMissionNameString, text_color = textColor)
    app.after(sleepBetweenCalls, scanMissionStart) 


# Start parsing a file from end of file
def startParsing():
    global file
    global fileRollbackPosition
    global fileRollbackPositionSmall
    global loggingState 

    # Logging
    if loggingState:
        logging.info("In startParsing()")

    # Open file if first time going through
    if file == None:
        file = open(filename, 'r', encoding='latin-1')
        
    # Start from end of file
    if parseFromEnd:
        file.seek(0, 2)
    else:
        file.seek(0)

    fileRollbackPosition = file.tell()
    fileRollbackPositionSmall = file.tell()

    app.after(500, scanMissionStart)


# Start scanning for mission start
def scanMissionStart():
    global fileRollbackPositionSmall
    global currentMission
    global disruptionTilesFoundList
    global restartReadingBool
    global loggingState 

    # Logging
    if loggingState:
        logging.info("In scanMissionStart()")

    disruptionTilesFoundList.clear()

    doneHere = False
    scanDisruption = False
    cope = False

    fileRollbackPositionSmall = file.tell()
    line = file.readline()  

    # If read line is faulty, rollback. Othewise, proceed with normal parsing
    if StringConstants.newLineString not in line or line == "":
        file.seek(fileRollbackPositionSmall)
    else:
        while StringConstants.newLineString in line:

            # If mission entry found
            if StringConstants.missionNameString in line:

                # Find the actual mission name and save/display it
                currentMissionTemp = line.split(StringConstants.missionNameString, 1)[1]
                currentMission = currentMissionTemp[1:].rstrip()

                missionNameDisplay.configure(text = currentMission)
                foundTileDisplay.configure(text = StringConstants.searchingTextString)

                # If doing disruption, will go to a different parser function
                if any(x in line for x in StringConstants.disruptionMissionNames):
                    scanDisruption = True
                # elif StringConstants.copernicusLua in line:
                #     cope = True
                else:
                    doneHere = True
                break

            # Save rollback point here. Check next line and decide what to do based on it
            try:
                fileRollbackPositionSmall = file.tell()
                line = file.readline()  
                if StringConstants.newLineString not in line or line == "":
                    file.seek(fileRollbackPositionSmall)
                    break
            except:
                logging.error("Error trying to readline\n")
                file.seek(fileRollbackPosition)
                break
    
    # Move to next parsing step based on previously found conditions
    if restartReadingBool:
        return
    # elif cope:
    #     app.after(sleepBetweenCalls, copeCope) 
    elif doneHere:
        app.after(sleepBetweenCalls, scanMissionLayout) 
    elif scanDisruption:
        app.after(sleepBetweenCalls, scanDisruptionLayout) 
    else:
        app.after(sleepBetweenCalls, scanMissionStart) 


# Start scanning for mission layout. Currently supports Zabala (nano) and Ophelia (poly)
def scanMissionLayout():
    global fileRollbackPosition
    global fileRollbackPositionSmall
    global restartReadingBool
    global loggingState 

    # Logging
    if loggingState:
        logging.info("In scanMissionLayout()")

    orbiterReset = False
    doneHere = False

    fileRollbackPositionSmall = file.tell()
    line = file.readline()  

    # If read line is faulty, rollback. Othewise, proceed with normal parsing
    if StringConstants.newLineString not in line or line == "":
        file.seek(fileRollbackPositionSmall)
    else:
        while StringConstants.newLineString in line:
            # Search for specific tiles
            if any(x in line for x in StringConstants.tileMatchesList):
                foundTileDisplay.configure(text = StringConstants.searchingTextFoundString, text_color = textColorGreen)
                missionNameDisplay.configure(text = StringConstants.appWillResetIn30sString)

                logging.info(line)

                doneHere = True
                break

            # End of mission load, means all the layout has been parsed and found, will simply continue parsing until Orbiter Reset is found
            elif StringConstants.endOfMissionLoadString in line:
                foundTileDisplay.configure(text = StringConstants.searchingTextNotFoundString, text_color = textColorRed)

            # Orbiter reset
            elif StringConstants.orbiterResetString in line:
                # Save rollback point in case of required restart
                fileRollbackPosition = file.tell()

                orbiterReset = True
                
                logging.info("Orbiter reset")
                break

            # Save rollback point here. Check next line and decide what to do based on it
            try:
                fileRollbackPositionSmall = file.tell()
                line = file.readline()  
                if StringConstants.newLineString not in line or line == "":
                    file.seek(fileRollbackPositionSmall)
                    break
            except:
                logging.error("Error trying to readline\n")
                file.seek(fileRollbackPosition)
                break

    # Move to next parsing step based on previously found conditions
    if restartReadingBool:
        return
    elif orbiterReset:
        app.after(sleepBetweenCalls, resetDisplay) 
    elif doneHere:
        app.after(sleepBetweenCalls * 10, resetDisplay)
    else:
        app.after(sleepBetweenCalls, scanMissionLayout) 


# Start scanning for mission layout in Kappa
def scanDisruptionLayout():
    global fileRollbackPosition
    global fileRollbackPositionSmall
    global disruptionTilesFoundList
    global disruptionRun
    global disruptionCurrentRound
    global loggingState
    global restartReadingBool
    global loggingState 

    # Logging
    if loggingState:
        logging.info("In scanDisruptionLayout()")

    orbiterReset = False
    doneHere = False

    fileRollbackPositionSmall = file.tell()
    line = file.readline()  

    currentMissionTileString = ""
    badTileList = None
    
    if StringConstants.kappaSedna in currentMission:
        currentMissionTileString = StringConstants.kappaGrineerIntermediateString
        badTileList = kappaRegBadList
    elif StringConstants.apolloLua in currentMission:
        currentMissionTileString = StringConstants.apolloMoonIntString
        badTileList = apolloRegBadList
    else:
        return

    # If read line is faulty, rollback. Othewise, proceed with normal parsing
    if StringConstants.newLineString not in line or line == "":
        file.seek(fileRollbackPositionSmall)
    else:
        while StringConstants.newLineString in line:

            # Search for tiles, will find the two main rooms of the tileset
            if currentMissionTileString in line:            
                tempLine = line.split(currentMissionTileString, 1)[1]
                tempLine = tempLine.rstrip()
                disruptionTilesFoundList.append(tempLine)

                # print(tempLine)

            # End of mission load, display tiles
            elif StringConstants.endOfMissionLoadString in line:

                tile1 = disruptionTilesFoundList[0].split(StringConstants.dotLevelString, 1)[0]
                tile2 = disruptionTilesFoundList[1].split(StringConstants.dotLevelString, 1)[0]

                foundTileDisplay.configure(text = tile1 + " + " + tile2, text_color = textColor)

                if loggingState:
                    logging.info(disruptionTilesFoundList[0] + " " + disruptionTilesFoundList[1])

                # If any of the selected bad tiles is found, display reset text
                if any(x in badTileList for x in disruptionTilesFoundList):
                    missionNameDisplay.configure(text = StringConstants.kappaShouldResetString, text_color = textColorRed)
                else:
                    missionNameDisplay.configure(text = StringConstants.kappaUsableTileString, text_color = textColorGreen)
                    
                    doneHere = True

                    # Create disruption run that will store all round information
                    disruptionRun = DisruptionRun()

                    # Stop logging, unlikely that anything breaks from here on out
                    loggingCheckBox.deselect()
                    loggingState = False
                    restartReadingText.place_forget()
                    restartReadingButton.place_forget()

                    break

            # Orbiter reset
            elif StringConstants.orbiterResetString in line:
                orbiterReset = True

                # Save rollback point in case of required restart
                fileRollbackPosition = file.tell()

                logging.info("Orbiter reset - " + currentMission)
                break

            # Save rollback point here. Check next line and decide what to do based on it
            try:
                fileRollbackPositionSmall = file.tell()
                line = file.readline()  
                if StringConstants.newLineString not in line or line == "":
                    file.seek(fileRollbackPositionSmall)
                    break
            except:
                logging.error("Error trying to readline\n")
                file.seek(fileRollbackPosition)
                break

    # Move to next parsing step based on previously found conditions
    if restartReadingBool:
        return 
    elif orbiterReset:
        app.after(sleepBetweenCalls, resetDisplay) 
    elif doneHere:
        # app.after(sleepBetweenCalls, updateUIForDisruptionLogging())
        app.after(sleepBetweenCalls * 10, updateUIForDisruptionLogging)
    else:
        app.after(sleepBetweenCalls, scanDisruptionLayout) 


# Start scanning for mission layout in Kappa
def scanDisruptionProgress():
    global fileRollbackPositionSmall
    global disruptionTilesFoundList
    global disruptionRun
    global disruptionCurrentRound
    global currentRoundShown
    global currentKeysInserted
    global currentDemosKilled 
    global loggingState 
    global chartWindow 

    # Logging
    if loggingState:
        logging.info("In scanDisruptionProgress()")

    orbiterReset = False

    fileRollbackPositionSmall = file.tell()
    line = file.readline()  

    # If read line is faulty, rollback. Othewise, proceed with normal parsing
    if StringConstants.newLineString not in line or line == "":
        file.seek(fileRollbackPositionSmall)
    else:
        while StringConstants.newLineString in line:

            # Search for various milestones along each round
            # Run start. Will save start of mission time (after door hack)
            if StringConstants.disruptionIntroDoorUnlockedString in line:
                lineTime = line.split(StringConstants.scriptString, 1)[0]
                trimmedTime = re.sub(r'[^0-9.]', '', lineTime)
                disruptionRun.runTimeStartInSeconds = float(trimmedTime)
            
            # Round begin - create new disruption round
            elif StringConstants.disruptionRoundStartedString in line:            
                lineTime = line.split(StringConstants.scriptString, 1)[0]
                trimmedTime = re.sub(r'[^0-9.]', '', lineTime)
                
                disruptionCurrentRound = DisruptionRound()
                disruptionCurrentRound.roundTimeStartInSeconds = float(trimmedTime)

                currentRoundShown = len(disruptionRun.rounds)

                disruptionRoundInputBox.delete('0.0', 'end')
                disruptionRoundInputBox.insert('end', len(disruptionRun.rounds))

                cleanDisruptionUI()
                currentKeysInserted = 0
                currentDemosKilled = 0

            # Key insert
            elif StringConstants.disruptionKeyInsertString in line:
                lineTime = line.split(StringConstants.scriptString, 1)[0]
                trimmedTime = re.sub(r'[^0-9.]', '', lineTime)

                disruptionCurrentRound.keyInsertTimes[currentKeysInserted] = float(trimmedTime)
                
                realTimeValue = str(datetime.timedelta(seconds = float(trimmedTime) - disruptionCurrentRound.roundTimeStartInSeconds))[2:7]
                disruptionCurrentRound.keyInsertTimesString[currentKeysInserted] = realTimeValue

                keyDisplays[currentKeysInserted].configure(text = realTimeValue)
                currentKeysInserted += 1

            # Defense finished (1 key, not full round)
            elif StringConstants.disruptionDefenseFinishedString in line:
                lineTime = line.split(StringConstants.scriptString, 1)[0]
                trimmedTime = re.sub(r'[^0-9.]', '', lineTime)

                disruptionCurrentRound.demoKillTimes[currentDemosKilled] = float(trimmedTime)
                
                realTimeValue = str(datetime.timedelta(seconds = float(trimmedTime) - disruptionCurrentRound.roundTimeStartInSeconds))[2:7]
                disruptionCurrentRound.demoKillTimesString[currentDemosKilled] = realTimeValue

                demoDisplays[currentDemosKilled].configure(text = realTimeValue)
                currentDemosKilled += 1

            # Defense failed (1 key)
            elif StringConstants.disruptionDefenseFailedString in line:
                lineTime = line.split(StringConstants.scriptString, 1)[0]
                trimmedTime = re.sub(r'[^0-9.]', '', lineTime)

                disruptionCurrentRound.demoKillTimes[currentDemosKilled] = float(trimmedTime)

                realTimeValue = str(datetime.timedelta(seconds = float(trimmedTime) - disruptionCurrentRound.roundTimeStartInSeconds))[2:7]
                disruptionCurrentRound.demoKillTimesString[currentDemosKilled] = realTimeValue

                demoDisplays[currentDemosKilled].configure(text = realTimeValue)
                currentDemosKilled += 1

            # Round finished
            elif StringConstants.disruptionRoundFinishedString in line:
                lineTime = line.split(StringConstants.scriptString, 1)[0]
                trimmedTime = re.sub(r'[^0-9.]', '', lineTime)

                disruptionCurrentRound.roundTimeEndInSeconds = float(trimmedTime)
                disruptionCurrentRound.totalRoundTimeInSeconds = float(trimmedTime) - float(disruptionCurrentRound.roundTimeStartInSeconds)
                disruptionRun.rounds.append(disruptionCurrentRound)
                disruptionRun.sumOfRoundTimesInSeconds += disruptionCurrentRound.totalRoundTimeInSeconds

                realTimeValue = str(datetime.timedelta(seconds = disruptionCurrentRound.totalRoundTimeInSeconds))[2:7]
                disruptionCurrentRound.totalRoundTimeInSecondsString = realTimeValue

                averageRealTimeValueSeconds = disruptionRun.sumOfRoundTimesInSeconds / len(disruptionRun.rounds)
                averageRealTimeValue = str(datetime.timedelta(seconds = averageRealTimeValueSeconds))[2:7]
                currentAverageDisplay.configure(text = averageRealTimeValue)

                previousRoundTimeDisplay.configure(text = realTimeValue)

                # Update expected 46 round end time. Stops updating after 46 reached
                if len(disruptionRun.rounds) < 45: 
                    roundsLeft = 45 - len(disruptionRun.rounds)
                    timeLeftSeconds = roundsLeft * float(float(averageRealTimeValueSeconds) + 20)
                    totalRunTimeExpectedSeconds = float(trimmedTime) - float(disruptionRun.runTimeStartInSeconds) + float(timeLeftSeconds)
                    totalRunTimeExpected = str(datetime.timedelta(seconds = totalRunTimeExpectedSeconds))[0:7]
                    expectedEndTimeDisplay.configure(text = totalRunTimeExpected)

                elif len(disruptionRun.rounds) == 45:
                    # Save 46 run time
                    round45endTimeSeconds = disruptionRun.rounds[44].roundTimeEndInSeconds
                    disruptionRun.round45TimeEndInSeconds = disruptionRun.runTimeStartInSeconds
                    disruptionRun.round45TimeDurationSeconds = round45endTimeSeconds - disruptionRun.runTimeStartInSeconds
                    disruptionRun.round45TimeDurationString = str(datetime.timedelta(seconds = disruptionRun.round45TimeDurationSeconds))[0:7]

                    expectedEndTimeStringDisplay.configure(text = StringConstants.levelCapTimeString)
                    expectedEndTimeDisplay.configure(text = disruptionRun.round45TimeDurationString)

                # Check if round is best overall
                if disruptionCurrentRound.totalRoundTimeInSeconds < disruptionRun.bestRunTime:
                    disruptionRun.bestRunTime = disruptionCurrentRound.totalRoundTimeInSeconds
                    disruptionRun.bestRunTimeString = realTimeValue
                    disruptionRun.bestRunTimeRoundNr = currentRoundShown
                    extraString = " (r" + str(len(disruptionRun.rounds)) + ")"
                    bestRoundTimeDisplay.configure(text = realTimeValue + extraString)

            # Update total keys completed
            elif StringConstants.disruptionTotalKeysCompleted in line:
                nrKeysCompleted = line.split(StringConstants.disruptionTotalKeysCompleted, 1)[1]
                disruptionRun.keysCompleted = nrKeysCompleted

            # Orbiter reset - extracts all round times and dumps to file. Also creates graph in new tab
            elif StringConstants.orbiterResetString in line:
                orbiterReset = True
                
                if loggingState:
                    logging.info("Orbiter reset -  Disruption")

                # Re-enable logging state, incase something breaks while scrolling through rounds
                loggingCheckBox.select()
                loggingState = True

                # Update UI with last round info
                updateDisruptionUIValues(len(disruptionRun.rounds))

                break

            # Save rollback point here. Check next line and decide what to do based on it
            try:
                fileRollbackPositionSmall = file.tell()
                line = file.readline()  
                if StringConstants.newLineString not in line or line == "":
                    file.seek(fileRollbackPositionSmall)
                    break
            except:
                print("Error trying to readline\n")
                file.seek(fileRollbackPosition)
                break

    # Move to next parsing step based on previously found conditions
    if restartReadingBool:
        return
    elif orbiterReset:
        app.after(sleepBetweenCalls, saveTimesAndDumpJson)
    else:
        app.after(sleepBetweenCalls, scanDisruptionProgress) 


# Used to self-close the app in some occasions
def exitApp():
    exit(1)


# Run parser function
app.after(500, startParsing)

# Run app window
app.mainloop()




