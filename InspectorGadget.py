import datetime
import json
import logging
import string
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
from AppUI import AppUI
from playsound import playsound
import requests
import MqttConnection
import random

requestVersionContent = requests.get(StringConstants.versionUrl)

def resource_pathAnnoying(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class FullParser:
    def __init__(self) -> None:
        self.currentVersion = "1.3.7"

        self.currentMissionTileString = None
        self.badTileList = None

        # Logging status
        logging.basicConfig(filename = 'inspectorLog.log', encoding = 'utf-8', filemode='w', level = logging.DEBUG, format='%(asctime)s %(message)s')
        self.loggingState = True

        # Start parsing from end of file onwards
        self.parseFromEnd = True

        # Set the file path for ee.log
        self.filename = os.getenv('LOCALAPPDATA') + r'\Warframe\EE.log'
        self.file = None

        # Rollback positions for parser to return to if incomplete lines are read, or required rollbacks
        self.fileRollbackPosition = None
        self.fileRollbackPositionSmall = None
        self.restartReadingBool = False
        self.playToxinSound = True

        # Time to sleep between each parsing progression, in millis
        self.sleepBetweenCalls = 1000
        self.sleepBetweenCallsMultiplier = 10

        # System Settings
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")
        customtkinter.deactivate_automatic_dpi_awareness()

        def resource_path(relative_path):
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)
    
        appLogo = resource_path("peepoHmm.ico") 

        # App window - Size, Title, icon and always on top setting
        self.app = customtkinter.CTk()
        # self.app.geometry("960x512")
        self.app.geometry("%dx%d+%d+%d" % (960, 512, 1920/4, 1080/4))
        
        self.app.title("InspectorGadget")
        self.app.iconbitmap(appLogo)
        self.app.attributes('-topmost', True)    
        
        self.overlayWindow = None

        # Class that manages all UI elements
        self.appUI = AppUI(self, self.app, self.overlayWindow)
        
        # Misc variables
        self.currentRoundShown = -1
        self.currentKeysInserted = 0
        self.currentDemosKilled = 0

        self.disruptionTilesFoundList = []
        self.disruptionRun = None
        self.disruptionCurrentRound = None

        self.cascadeTilesFound = []
        
        self.missionLoadEndReached = False
        
        # Randomly generated string for clients to connect to
        self.hostCodeLength = 14
        self.hostCodeString = "kappa_" + ''.join(random.choices(string.ascii_letters + string.digits, k = self.hostCodeLength))
        self.appUI.hostCodeActualDisplay.configure(text = self.hostCodeString)
        
        self.selfWarframeUsername = ""
        self.connectedToHostBool = False
        self.connectedToHostString = ""
        
        # New thread to run the mqtt connection
        self.connection = MqttConnection.MqttConnection(self, self.appUI, self.hostCodeString)
        self.connection.startConnection()
        
    # def setClickthrough(self, hwnd):
    #     print("setting window properties")
    #     try:
    #         styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    #         styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    #         win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
    #         win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
    #     except Exception as e:
    #         print(e)
            
        
    # Open url in web browser
    def openInBrowser(url):
        webbrowser.open_new_tab(url)

    # Extract all round times, convert class to json and dump to file
    def saveTimesAndDumpJson(self):
        if self.loggingState:
            logging.info("In saveTimesAndDumpJson()")

        self.currentRoundShown -= 1

        jsonClass = DisruptionRunTimesJson()

        # Add all round times to the list
        for roundX in self.disruptionRun.rounds:
            jsonClass.runTimesInSeconds.append(round(roundX.totalRoundTimeInSeconds, 2))

        # Add full raw run
        jsonClass.fullRun = self.disruptionRun

        JSONData = json.dumps(jsonClass, indent=4, cls=DisruptionJsonEncoder)

        with open('disruptionFullRunData.json', 'w', encoding='utf-8') as f:
            f.write(JSONData)
            f.close()

        self.appUI.disruptionDataDumpedDisplay.place(relx = .5, rely = self.appUI.lineRelValues[8] - 0.05, anchor = "center")

        # Create new tab for chart, and add chart with times per round
        self.appUI.chartWindow = self.appUI.innerWindowBox.add("Chart")  

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
                                    master = self.appUI.chartWindow,
                                    width = self.app._current_width - 80, 
                                    height = self.app._current_height - 80,
                                    axis_size = 2,
                                    x_axis_label_count = 6,
                                    y_axis_max_value = 150,
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

            if self.loggingState:
                logging.info("Data dumped to file and chart drawn. Parsing stopped.")
                logging.info("! ! ! THE END ! ! !")

        except:
            logging.error("Attempted to draw chart with no finished rounds")
            
        # Enable new run button 
        self.appUI.toggleNewRunButton(True)
            
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    #                               Parsing Funcs                                   #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    # Start parsing a file from end of file
    def startParsing(self):
        # Check available version update
        if(requestVersionContent.text != self.currentVersion):
            self.appUI.toggleUpdateAvailableMsg(True)
            
        # Logging
        if self.loggingState:
            logging.info("In startParsing()")

        # Open file if first time going through
        try:
            if self.file == None:
                self.file = open(self.filename, 'r', encoding='latin-1')
        except:
            # If no file, keep trying
            self.app.after(self.sleepBetweenCalls, self.startParsing)
            return
            
        # Get local warframe username
        self.file.seek(0)
        line = self.file.readline()  
        while StringConstants.newLineString in line:
            if StringConstants.loggedInString in line:
                usernameTemp = line.split(StringConstants.loggedInString, 1)[1]
                self.selfWarframeUsername = usernameTemp.split(" (", 1)[0].rstrip()
                self.file.seek(0, 2)
                
                break
    
            line = self.file.readline()  
                
        # Start from end/beginning of file
        if self.parseFromEnd:
            self.file.seek(0, 2)
        else:
            self.file.seek(0)
            if self.loggingState:
                logging.info("In startParsing() + started parsing from start of file")
        
        self.fileRollbackPosition = self.file.tell()
        self.fileRollbackPositionSmall = self.file.tell()

        self.missionLoadEndReached = False

        self.app.after(500, self.scanMissionStart)


    # Start scanning for mission start
    def scanMissionStart(self):
        # Logging
        if self.loggingState:
            logging.info("In scanMissionStart()")

        self.disruptionTilesFoundList.clear()
        self.cascadeTilesFound.clear()

        doneHere = False
        scanDisruption = False
        scanCascade = False

        self.fileRollbackPositionSmall = self.file.tell()
        line = self.file.readline()  
        
        if self.loggingState:
            logging.info(line)
            
        # If read line is faulty, rollback. Othewise, proceed with normal parsing
        if StringConstants.newLineString not in line or line == "":
            self.file.seek(self.fileRollbackPositionSmall)
        else:
            while StringConstants.newLineString in line:

                # If mission entry found
                if StringConstants.missionNameString in line:

                    # Find the actual mission name and save/display it
                    currentMissionTemp = line.split(StringConstants.missionNameString, 1)[1]
                    self.currentMission = currentMissionTemp[1:].rstrip()

                    self.appUI.missionNameDisplay.configure(text = self.currentMission)
                    self.appUI.foundTileDisplay.configure(text = StringConstants.searchingTextString)

                    # If doing disruption, will go to a different parser function
                    if any(x in line for x in StringConstants.disruptionMissionNames):
                        if StringConstants.kappaSedna in self.currentMission or StringConstants.urUranus in self.currentMission:
                            self.currentMissionTileString = StringConstants.kappaGrineerIntermediateString
                            self.badTileList = self.appUI.kappaRegBadList
                        elif StringConstants.apolloLua in self.currentMission:
                            self.currentMissionTileString = StringConstants.apolloMoonIntString
                            self.badTileList = self.appUI.apolloRegBadList
                        elif StringConstants.olympusMars in self.currentMission:
                            self.currentMissionTileString = StringConstants.olympusCmpString
                            self.badTileList = self.appUI.olympusRegBadList
                        else:
                            return

                        scanDisruption = True
                    elif StringConstants.tuvulCommonsZariman in line:
                        scanCascade = True
                    else:
                        doneHere = True

                    if self.loggingState:
                        logging.info("Found mission name in line. Moving to layout parsing. Line: " + line)

                    break

                # Save rollback point here. Check next line and decide what to do based on it
                try:
                    self.fileRollbackPositionSmall = self.file.tell()
                    line = self.file.readline()  
                    if StringConstants.newLineString not in line or line == "":
                        self.file.seek(self.fileRollbackPositionSmall)
                        break
                except:
                    logging.error("Error trying to readline\n")
                    self.file.seek(self.fileRollbackPosition)
                    break
        
        # Move to next parsing step based on previously found conditions
        if self.restartReadingBool:
            return
        elif doneHere:
            self.app.after(self.sleepBetweenCalls, self.scanMissionLayout) 
        elif scanDisruption:
            self.app.after(self.sleepBetweenCalls, self.scanDisruptionLayout) 
        elif scanCascade:
            self.app.after(self.sleepBetweenCalls, self.scanCascadeLayout) 
        else:
            self.app.after(self.sleepBetweenCalls, self.scanMissionStart) 


    # Start scanning for mission layout
    def scanMissionLayout(self):
        # Logging
        if self.loggingState:
            logging.info("In scanMissionLayout()")

        orbiterReset = False
        doneHere = False

        self.fileRollbackPositionSmall = self.file.tell()
        line = self.file.readline()  

        # If read line is faulty, rollback. Othewise, proceed with normal parsing
        if StringConstants.newLineString not in line or line == "":
            self.file.seek(self.fileRollbackPositionSmall)
        else:
            while StringConstants.newLineString in line:
                # Search for specific tiles
                if (any(x in line for x in StringConstants.tileMatchesList) and not self.missionLoadEndReached):
                    self.appUI.foundTileDisplay.configure(text = StringConstants.searchingTextFoundString, text_color = self.appUI.textColorGreen)
                    self.appUI.missionNameDisplay.configure(text = StringConstants.appWillResetIn30sString)

                    if self.loggingState:
                        logging.info("Found specific tile in line for mission " + self.currentMission + ". Line: " + line)

                    self.missionLoadEndReached = True
                    doneHere = True
                    break
                
                elif (StringConstants.assurUranus in self.currentMission and StringConstants.assurGoodTileString in line and not self.missionLoadEndReached):
                    self.appUI.foundTileDisplay.configure(text = StringConstants.searchingTextFoundString, text_color = self.appUI.textColorGreen)
                    self.appUI.missionNameDisplay.configure(text = StringConstants.appWillResetIn30sString)

                    if self.loggingState:
                        logging.info("Found specific tile in line for mission " + self.currentMission + ". Line: " + line)

                    self.missionLoadEndReached = True
                    doneHere = True
                    break

                # End of mission load, means all the layout has been parsed and found, will simply continue parsing until Orbiter Reset is found
                elif (StringConstants.endOfMissionLoadString in line and not self.missionLoadEndReached):
                    if self.loggingState:
                        logging.info("End of mission load found. Will await for mission reset.")

                    self.missionLoadEndReached = True

                    self.appUI.foundTileDisplay.configure(text = StringConstants.searchingTextNotFoundString, text_color = self.appUI.textColorRed)
                    
                    break

                # Orbiter reset
                elif (StringConstants.orbiterResetString in line or 
                      StringConstants.orbiterResetEarthString in line or
                      StringConstants.abortMissionString in line):
                    # Save rollback point in case of required restart
                    self.fileRollbackPosition = self.file.tell()

                    orbiterReset = True
                    
                    if self.loggingState:
                        logging.info("Orbiter reset found. Line: " + line)
                    break

                # Save rollback point here. Check next line and decide what to do based on it
                try:
                    self.fileRollbackPositionSmall = self.file.tell()
                    line = self.file.readline()  
                    if StringConstants.newLineString not in line or line == "":
                        self.file.seek(self.fileRollbackPositionSmall)
                        break
                except:
                    logging.error("Error trying to readline\n")
                    self.file.seek(self.fileRollbackPosition)
                    break

        # Move to next parsing step based on previously found conditions
        if self.restartReadingBool:
            return
        elif orbiterReset:
            self.app.after(self.sleepBetweenCalls, self.appUI.resetDisplay) 
        elif doneHere:
            self.app.after(self.sleepBetweenCalls * self.sleepBetweenCallsMultiplier, self.scanMissionLayout)
        else:
            self.app.after(self.sleepBetweenCalls, self.scanMissionLayout) 


    # Start scanning for mission layout in Kappa
    def scanCascadeLayout(self):
        # Logging
        if self.loggingState:
            logging.info("In scanCascadeLayout()")

        orbiterReset = False
        doneHere = False

        self.fileRollbackPositionSmall = self.file.tell()
        line = self.file.readline()  

        # If read line is faulty, rollback. Othewise, proceed with normal parsing
        if StringConstants.newLineString not in line or line == "":
            self.file.seek(self.fileRollbackPositionSmall)
        else:
            while StringConstants.newLineString in line:
                # Search for tiles, will find the two main rooms of the tileset
                if StringConstants.tuvulCommonsIntString in line:                                
                    tempLine = line.split(StringConstants.tuvulCommonsIntString, 1)[1]
                    tempLine = tempLine.split("/", 1)[0]
                    tempLine = tempLine.rstrip()
                    
                    if(not self.missionLoadEndReached):
                        self.cascadeTilesFound.append(tempLine)

                        if self.loggingState:
                            logging.info("Found cascade tile in Line: " + line)

                # End of mission load, display tiles
                elif StringConstants.endOfMissionLoadString in line:
                    sumOfTiles = ""
                    
                    self.missionLoadEndReached = True
                    tilesString = ""
                    
                    tilesIndex = 0
                    for x in self.cascadeTilesFound:
                        newTileString = ""
                        
                        # Check if layout has 5
                        if x == StringConstants.cascadeShuttleBay: 
                            sumOfTiles = sumOfTiles + "5"
                            newTileString = StringConstants.cascadeShuttleBayDisplay
                        
                        # Check if layout has 4
                        i = 0
                        for y in StringConstants.cascadeListOf4:
                            if(y == x):
                                sumOfTiles = sumOfTiles + "4"
                                newTileString = StringConstants.cascadeListOf4Display[i]
                                break
    
                            i += 1
                            
                        i = 0
                        for y in StringConstants.cascadeListOf3:
                            if(y == x):
                                sumOfTiles = sumOfTiles + "3"
                                newTileString = StringConstants.cascadeListOf3Display[i]
                                break
    
                            i += 1
                            
                        if(tilesIndex < 2):
                            tilesString = tilesString + newTileString + " - "
                        else:
                            tilesString = tilesString + newTileString
                            
                        tilesIndex += 1
                            
                    if len(sumOfTiles) == 3 and "5" in sumOfTiles:
                        self.appUI.missionNameDisplay.configure(text = StringConstants.appWillResetIn30sString)
                        self.appUI.foundTileDisplay.configure(text = sumOfTiles + "\n" + tilesString, text_color = self.appUI.textColorGreen)
                    else:
                        self.appUI.foundTileDisplay.configure(text = sumOfTiles + " - Reset\n" + tilesString, text_color = self.appUI.textColorRed)

                    if self.loggingState:
                        for x in self.cascadeTilesFound:
                            logging.info("Cascade tile found: " + x)

                    break 

                # Orbiter reset
                elif (StringConstants.orbiterResetString in line or 
                      StringConstants.orbiterResetEarthString in line or
                      StringConstants.abortMissionString in line):
                    orbiterReset = True

                    self.cascadeTilesFound.clear()

                    # Save rollback point in case of required restart
                    self.fileRollbackPosition = self.file.tell()

                    if self.loggingState:
                        logging.info("Orbiter reset found in disruption. Line: " + line)
                    break

                # Save rollback point here. Check next line and decide what to do based on it
                try:
                    self.fileRollbackPositionSmall = self.file.tell()
                    line = self.file.readline()  
                    if StringConstants.newLineString not in line or line == "":
                        self.file.seek(self.fileRollbackPositionSmall)
                        break
                except:
                    logging.error("Error trying to readline\n")
                    self.file.seek(self.fileRollbackPosition)
                    break

        # Move to next parsing step based on previously found conditions
        if self.restartReadingBool:
            return 
        elif orbiterReset:
            self.app.after(self.sleepBetweenCalls, self.appUI.resetDisplay) 
        else:
            self.app.after(self.sleepBetweenCalls, self.scanCascadeLayout) 


    # Start scanning for mission layout in Kappa
    def scanDisruptionLayout(self):
        # Logging
        if self.loggingState:
            logging.info("In scanDisruptionLayout()")

        orbiterReset = False
        doneHere = False

        self.fileRollbackPositionSmall = self.file.tell()
        line = self.file.readline()  

        # If read line is faulty, rollback. Othewise, proceed with normal parsing
        if StringConstants.newLineString not in line or line == "":
            self.file.seek(self.fileRollbackPositionSmall)
        else:
            while StringConstants.newLineString in line:
                # Search for tiles, will find the two main rooms of the tileset
                if self.currentMissionTileString in line:            
                    tempLine = line.split(self.currentMissionTileString, 1)[1]
                    tempLine = tempLine.split("/", 1)[0]
                    tempLine = tempLine.rstrip()
                    
                    if(not self.missionLoadEndReached):
                        # Stupid ass olympus got changed in Jade update, need to check all tiles in it
                        if StringConstants.olympusMars in self.currentMission:
                            for x in StringConstants.olympusList:
                                if x in tempLine:
                                    self.disruptionTilesFoundList.append(tempLine) 
                        else:
                            self.disruptionTilesFoundList.append(tempLine)
                        
                        if self.loggingState:
                            logging.info("Found disruption tile in Line: " + line)                    

                # End of mission load, display tiles
                elif StringConstants.endOfMissionLoadString in line:

                    self.missionLoadEndReached = True

                    tile1 = self.disruptionTilesFoundList[0]
                    tile2 = self.disruptionTilesFoundList[1]

                    tileDisplayString = tile1 + " + " + tile2
                    self.appUI.foundTileDisplay.configure(text = tileDisplayString, text_color = self.appUI.textColor)
                    
                    if(self.overlayWindow != None):
                        self.overlayWindow.updateOverlayWithTextRaw(tileDisplayString)
                                        
                    if self.loggingState:
                        logging.info("Disruption tiles found: " + self.disruptionTilesFoundList[0] + " " + self.disruptionTilesFoundList[1])

                    clientDataToSend = DataForClients()

                    # If any of the selected bad tiles is found, display reset text
                    if any(x in self.badTileList for x in self.disruptionTilesFoundList):
                        self.appUI.missionNameDisplay.configure(text = StringConstants.kappaShouldResetString, text_color = self.appUI.textColorRed)
                        clientDataToSend.goodTilesBoolean = False
                    else:
                        self.appUI.missionNameDisplay.configure(text = StringConstants.kappaUsableTileString, text_color = self.appUI.textColorGreen)
                        clientDataToSend.goodTilesBoolean = True
                        
                        doneHere = True
                        # Create disruption run that will store all round information
                        self.disruptionRun = DisruptionRun()      
                        
                    # Client data to send
                    clientDataToSend.missionName = self.currentMission
                    clientDataToSend.tiles = tileDisplayString
                    JSONData = json.dumps(clientDataToSend, indent=4, cls=DisruptionJsonEncoder)
                    self.connection.publishMessage(JSONData)                   
                    
                    break

                # Orbiter reset
                elif (StringConstants.orbiterResetString in line or 
                      StringConstants.orbiterResetEarthString in line or
                      StringConstants.abortMissionString in line):
                    orbiterReset = True

                    clientDataToSend = DataForClients()
                    clientDataToSend.resetToOrbiterBoolean = True

                    # Save rollback point in case of required restart
                    self.fileRollbackPosition = self.file.tell()

                    if self.loggingState:
                        logging.info("Orbiter reset found in disruption. Line: " + line)
                    
                    break

                # Save rollback point here. Check next line and decide what to do based on it
                try:
                    self.fileRollbackPositionSmall = self.file.tell()
                    line = self.file.readline()  
                    if StringConstants.newLineString not in line or line == "":
                        self.file.seek(self.fileRollbackPositionSmall)
                        break
                except:
                    logging.error("Error trying to readline\n")
                    self.file.seek(self.fileRollbackPosition)
                    break

        # Move to next parsing step based on previously found conditions
        if self.restartReadingBool:
            return 
        elif orbiterReset:
            JSONData = json.dumps(clientDataToSend, indent=4, cls=DisruptionJsonEncoder)
            self.connection.publishMessage(JSONData) 
            
            if(self.overlayWindow != None):
                self.overlayWindow.updateOverlayWithTextRaw(StringConstants.orbiterResetOverlayDisplayString)
            
            self.app.after(self.sleepBetweenCalls, self.appUI.resetDisplay) 
        elif doneHere:            
            self.app.after(self.sleepBetweenCalls * self.sleepBetweenCallsMultiplier, self.appUI.updateUIForDisruptionLogging)
        else:
            self.app.after(self.sleepBetweenCalls, self.scanDisruptionLayout) 


    # Start scanning for mission layout in Kappa
    def scanDisruptionProgress(self):
        orbiterReset = False
        toTheStart = False

        self.fileRollbackPositionSmall = self.file.tell()
        line = self.file.readline()  

        # If read line is faulty, rollback. Othewise, proceed with normal parsing
        if StringConstants.newLineString not in line or line == "":
            self.file.seek(self.fileRollbackPositionSmall)
        else:
            while StringConstants.newLineString in line:
                
                # Check for toxin weapons, play sound of true
                # if StringConstants.disruptionToxinPylon in line:
                #     if(self.playToxinSound):
                #         try:
                #             playsound(resource_pathAnnoying(r'soundtoxin.mp3'))
                #         except Exception as error:
                #             logging.error("Broke on trying to play toxin sound: \n")
                #             logging.error(error)
                #             print(error)
                            

                # Search for various milestones along each round
                # Run time start
                if StringConstants.disruptionRunStartString in line:
                    if self.loggingState:
                        logging.info("Disruption run start found in Line: " + line)

                    lineTime = line.split(StringConstants.scriptString, 1)[0]
                    trimmedTime = re.sub(r'[^0-9.]', '', lineTime)
                    self.disruptionRun.runTimeStartInSeconds = float(trimmedTime)

                # Round begin - create new disruption round
                elif StringConstants.disruptionRoundStartedString in line:    
                    if self.loggingState:
                        logging.info("New disruption round found in Line: " + line)

                    lineTime = line.split(StringConstants.scriptString, 1)[0]
                    trimmedTime = re.sub(r'[^0-9.]', '', lineTime)
                    
                    self.disruptionCurrentRound = DisruptionRound()
                    self.disruptionCurrentRound.roundTimeStartInSeconds = float(trimmedTime)
                    self.disruptionRun.rounds.append(self.disruptionCurrentRound)

                    self.currentRoundShown = len(self.disruptionRun.rounds)

                    self.appUI.disruptionRoundInputBox.delete('0.0', 'end')
                    self.appUI.disruptionRoundInputBox.insert('end', len(self.disruptionRun.rounds))

                    self.appUI.cleanDisruptionUI()
                    self.currentKeysInserted = 0
                    self.currentDemosKilled = 0

                # Key insert
                elif StringConstants.disruptionKeyInsertString in line:
                    lineTime = line.split(StringConstants.scriptString, 1)[0]
                    trimmedTime = re.sub(r'[^0-9.]', '', lineTime)

                    self.disruptionCurrentRound.keyInsertTimes[self.currentKeysInserted] = float(trimmedTime)
                    
                    realTimeValue = str(datetime.timedelta(seconds = float(trimmedTime) - self.disruptionCurrentRound.roundTimeStartInSeconds))[2:7]
                    self.disruptionCurrentRound.keyInsertTimesString[self.currentKeysInserted] = realTimeValue

                    self.appUI.keyDisplays[self.currentKeysInserted].configure(text = realTimeValue)
                    self.currentKeysInserted += 1
                    
                # Defense finished (1 key, not full round)
                elif StringConstants.disruptionDefenseFinishedString in line:
                    lineTime = line.split(StringConstants.scriptString, 1)[0]
                    trimmedTime = re.sub(r'[^0-9.]', '', lineTime)

                    self.disruptionCurrentRound.demoKillTimes[self.currentDemosKilled] = float(trimmedTime)
                    
                    realTimeValue = str(datetime.timedelta(seconds = float(trimmedTime) - self.disruptionCurrentRound.roundTimeStartInSeconds))[2:7]
                    self.disruptionCurrentRound.demoKillTimesString[self.currentDemosKilled] = realTimeValue

                    self.appUI.demoDisplays[self.currentDemosKilled].configure(text = realTimeValue)
                    self.currentDemosKilled += 1

                # Defense failed (1 key)
                elif StringConstants.disruptionDefenseFailedString in line:
                    lineTime = line.split(StringConstants.scriptString, 1)[0]
                    trimmedTime = re.sub(r'[^0-9.]', '', lineTime)

                    self.disruptionCurrentRound.demoKillTimes[self.currentDemosKilled] = float(trimmedTime)

                    realTimeValue = str(datetime.timedelta(seconds = float(trimmedTime) - self.disruptionCurrentRound.roundTimeStartInSeconds))[2:7]
                    self.disruptionCurrentRound.demoKillTimesString[self.currentDemosKilled] = realTimeValue

                    self.appUI.demoDisplays[self.currentDemosKilled].configure(text = realTimeValue)
                    self.currentDemosKilled += 1

                # Round finished
                elif StringConstants.disruptionRoundFinishedString in line:
                    lineTime = line.split(StringConstants.scriptString, 1)[0]
                    trimmedTime = re.sub(r'[^0-9.]', '', lineTime)
                    
                    clientDataToSend = DataForClients()

                    self.disruptionCurrentRound.roundTimeEndInSeconds = float(trimmedTime)
                    self.disruptionCurrentRound.totalRoundTimeInSeconds = float(trimmedTime) - float(self.disruptionCurrentRound.roundTimeStartInSeconds)
                    self.disruptionRun.sumOfRoundTimesInSeconds += self.disruptionCurrentRound.totalRoundTimeInSeconds

                    realTimeValue = str(datetime.timedelta(seconds = self.disruptionCurrentRound.totalRoundTimeInSeconds))[2:7]
                    self.disruptionCurrentRound.totalRoundTimeInSecondsString = realTimeValue

                    averageRealTimeValueSeconds = self.disruptionRun.sumOfRoundTimesInSeconds / len(self.disruptionRun.rounds)
                    averageRealTimeValue = str(datetime.timedelta(seconds = averageRealTimeValueSeconds))[2:7]
                    self.appUI.currentAverageDisplay.configure(text = averageRealTimeValue)

                    self.appUI.previousRoundTimeDisplay.configure(text = realTimeValue)

                    timeToDisplayOnOverlay_ExpectedOrEnd = None

                    # Update expected 46 round end time. Stops updating after 46 reached
                    if len(self.disruptionRun.rounds) < 45: 
                        roundsLeft = 45 - len(self.disruptionRun.rounds)
                        timeLeftSeconds = roundsLeft * float(float(averageRealTimeValueSeconds) + 20)
                        totalRunTimeExpectedSeconds = float(trimmedTime) - float(self.disruptionRun.runTimeStartInSeconds) + float(timeLeftSeconds)
                        totalRunTimeExpected = str(datetime.timedelta(seconds = totalRunTimeExpectedSeconds))[0:7]
                        self.appUI.expectedEndTimeDisplay.configure(text = totalRunTimeExpected)

                        clientDataToSend.expectedEnd = totalRunTimeExpected
                        timeToDisplayOnOverlay_ExpectedOrEnd = totalRunTimeExpected

                    elif len(self.disruptionRun.rounds) == 45:
                        if self.loggingState:
                            logging.info("Levelcap reached. Saving relevant information. Levelcap Line: " + line)

                        # Save 46 run time
                        levelcapEndTimeSeconds = self.disruptionRun.rounds[44].roundTimeEndInSeconds
                        self.disruptionRun.levelcapTimeEndInSeconds = levelcapEndTimeSeconds
                        self.disruptionRun.levelcapTimeDurationSeconds = levelcapEndTimeSeconds - self.disruptionRun.runTimeStartInSeconds
                        if self.disruptionRun.levelcapTimeDurationSeconds < 3600:
                            self.disruptionRun.levelcapTimeDurationString = str(datetime.timedelta(seconds = self.disruptionRun.levelcapTimeDurationSeconds))[2:11]
                        else:
                            self.disruptionRun.levelcapTimeDurationString = str(datetime.timedelta(seconds = self.disruptionRun.levelcapTimeDurationSeconds))[0:11]

                        clientDataToSend.expectedEnd = self.disruptionRun.levelcapTimeDurationString
                        clientDataToSend.isLastKappaRound = True
                        timeToDisplayOnOverlay_ExpectedOrEnd = self.disruptionRun.levelcapTimeDurationString
                        
                        self.appUI.expectedEndTimeStringDisplay.configure(text = StringConstants.levelCapTimeString)
                        self.appUI.expectedEndTimeDisplay.configure(text = self.disruptionRun.levelcapTimeDurationString)

                    # Check if round is best overall
                    if self.disruptionCurrentRound.totalRoundTimeInSeconds < self.disruptionRun.bestRunTime:
                        self.disruptionRun.bestRunTime = self.disruptionCurrentRound.totalRoundTimeInSeconds
                        self.disruptionRun.bestRunTimeString = realTimeValue
                        self.disruptionRun.bestRunTimeRoundNr = len(self.disruptionRun.rounds)
                        extraString = " (r" + str(len(self.disruptionRun.rounds)) + ")"
                        self.appUI.bestRoundTimeDisplay.configure(text = realTimeValue + extraString)
                        
                    # Send data to client                    
                    clientDataToSend.keyInsertTimes = self.disruptionCurrentRound.keyInsertTimesString
                    clientDataToSend.demoKillTimes = self.disruptionCurrentRound.demoKillTimesString
                    clientDataToSend.totalRoundTimeInSeconds = self.disruptionCurrentRound.totalRoundTimeInSecondsString
                    clientDataToSend.currentAvg = averageRealTimeValue
                    clientDataToSend.bestRound = self.disruptionRun.bestRunTimeString + " (r" + str(len(self.disruptionRun.rounds)) + ")"
                    
                    if(self.overlayWindow != None):
                        if len(self.disruptionRun.rounds) == 45:
                            self.overlayWindow.updateOverlayWithTextRaw(StringConstants.overlayRoundString + 
                                                                          self.disruptionCurrentRound.totalRoundTimeInSecondsString + 
                                                                          StringConstants.overlaySpaceString + 
                                                                          StringConstants.overlayEndTimeString + 
                                                                          timeToDisplayOnOverlay_ExpectedOrEnd)
                        else:
                            self.overlayWindow.displayDisruptionRoundData(self.disruptionCurrentRound.totalRoundTimeInSecondsString, timeToDisplayOnOverlay_ExpectedOrEnd)
                    
                    JSONData = json.dumps(clientDataToSend, indent=4, cls=DisruptionJsonEncoder)
                    self.connection.publishMessage(JSONData)

                # Update total keys completed
                elif StringConstants.disruptionTotalKeysCompleted in line:
                    nrKeysCompleted = line.split(StringConstants.disruptionTotalKeysCompleted, 1)[1]
                    self.disruptionRun.keysCompleted = nrKeysCompleted

                # Orbiter reset - extracts all round times and dumps to file. Also creates graph in new tab
                elif (StringConstants.orbiterResetString in line or 
                      StringConstants.orbiterResetEarthString in line or
                      StringConstants.abortMissionString in line):
                    
                    if self.loggingState:
                        logging.info("Orbiter reset - Disruption. Line: " + line)

                    if len(self.disruptionRun.rounds) < 5:
                        toTheStart = True
                    else:
                        orbiterReset = True

                        if self.loggingState:
                            logging.info("Last disruption round not finished, removing from list of rounds.")

                        # If last round was not finished, remove it from list of rounds
                        if self.disruptionRun.rounds[len(self.disruptionRun.rounds) - 1].totalRoundTimeInSeconds == 0:
                            self.disruptionRun.rounds.pop()
                            self.currentRoundShown = len(self.disruptionRun.rounds)

                            self.appUI.disruptionRoundInputBox.delete('0.0', 'end')
                            self.appUI.disruptionRoundInputBox.insert('end', len(self.disruptionRun.rounds))

                        # Update UI with last round info
                        self.appUI.updateDisruptionUIValues(len(self.disruptionRun.rounds))

                    break

                # Save rollback point here. Check next line and decide what to do based on it
                try:
                    self.fileRollbackPositionSmall = self.file.tell()
                    line = self.file.readline()  
                    if StringConstants.newLineString not in line or line == "":
                        self.file.seek(self.fileRollbackPositionSmall)
                        break
                except:
                    print("Error trying to readline\n")
                    self.file.seek(self.fileRollbackPosition)
                    break

        # Move to next parsing step based on previously found conditions
        if self.restartReadingBool:
            return
        elif toTheStart:
            clientDataToSend = DataForClients()
            clientDataToSend.resetToOrbiterBoolean = True
            JSONData = json.dumps(clientDataToSend, indent=4, cls=DisruptionJsonEncoder)
            self.connection.publishMessage(JSONData)
            
            if(self.overlayWindow != None):
                self.overlayWindow.updateOverlayWithTextRaw(StringConstants.orbiterResetOverlayDisplayString)
            
            self.app.after(self.sleepBetweenCalls, self.appUI.resetAnalyzerUI)
        elif orbiterReset:
            clientDataToSend = DataForClients()
            clientDataToSend.resetToOrbiterBoolean = True
            JSONData = json.dumps(clientDataToSend, indent=4, cls=DisruptionJsonEncoder)
            self.connection.publishMessage(JSONData)
            
            if(self.overlayWindow != None):
                self.overlayWindow.updateOverlayWithTextRaw(StringConstants.orbiterResetOverlayDisplayString)
            
            self.app.after(self.sleepBetweenCalls, self.saveTimesAndDumpJson)
        else:
            self.app.after(self.sleepBetweenCalls, self.scanDisruptionProgress) 



# Class that stores all disruption run information (rounds, avg, etc)
class DisruptionRun:
    def __init__(self) -> None:
    
        self.rounds = []
        self.runTimeStartInSeconds = 0
        self.levelcapTimeEndInSeconds = 0
        self.levelcapTimeDurationSeconds = 0
        self.levelcapTimeDurationString = ""
        self.sumOfRoundTimesInSeconds = 0
        self.expectedRunTimeInSeconds = 0

        self.keysCompleted = 0

        self.bestRunTime = 99999
        self.bestRunTimeString = 0
        self.bestRunTimeRoundNr = 0

# Class that stores a single disruption round's information
class DisruptionRound:
    def __init__(self) -> None:
    
        # Raw values in seconds
        self.keyInsertTimes = [None, None, None, None]
        self.demoKillTimes = [None, None, None, None]

        self.roundTimeStartInSeconds = 0
        self.roundTimeEndInSeconds = 0
        self.totalRoundTimeInSeconds = 0
        
        # String values
        self.keyInsertTimesString = [None, None, None, None]
        self.demoKillTimesString = [None, None, None, None]
        self.totalRoundTimeInSecondsString = None

# Class to be sent over network to connected clients
class DataForClients:
    def __init__(self) -> None:
        self.keyInsertTimes = []
        self.demoKillTimes = []
        
        self.totalRoundTimeInSeconds = ""
        self.currentAvg = ""
        self.bestRound = ""
        self.expectedEnd = ""
        
        self.missionName = ""
        self.tiles = ""
        self.goodTilesBoolean = False
        self.resetToOrbiterBoolean = False
        
        self.isLastKappaRound = False
        


# Allows for serialization of other class, to convert to Json
class DisruptionJsonEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__ 

# Class used to dump all run times to disk, will be converted to json
class DisruptionRunTimesJson:
    def __init__(self) -> None:
        self.runTimesInSeconds = []
        self.fullRun = None



# # Used to self-close the app in some occasions
# def exitApp():
#     exit(1)


parser = FullParser()

# Run parser function
parser.app.after(500, parser.startParsing)

# Run app window
parser.app.mainloop()




