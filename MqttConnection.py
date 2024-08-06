import paho.mqtt.client as mqtt
import json
from json import JSONDecoder, JSONEncoder
from staticStrings import StringConstants

class MqttConnection:

    def __init__(self, parser, appUi, topic) -> None:
        self.fullParser = parser
        self.appUi = appUi
        
        self.mqttBroker = 'mqtt.eclipseprojects.io'

        self.mqttTopic = topic

        self.mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.mqttClient.on_connect = self.onConnect
        self.mqttClient.on_message = self.onMessage


    def startConnection(self):
        self.mqttClient.connect(self.mqttBroker, 1883, 30)
        self.mqttClient.loop_start()
        
    def stopConnection(self):
        self.mqttClient.disconnect()
        self.mqttClient.loop_stop()

    def publishMessage(self, message):
        self.mqttClient.publish(self.mqttTopic, message)

    # The callback for when the client receives a CONNACK response from the server.
    def onConnect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f'Failed to connect: {reason_code}, retrying...')
        else:
            print(f'Connected with <{reason_code}> code to topic {self.mqttTopic}')

            self.mqttClient.subscribe(topic = self.mqttTopic)
                                

    # The callback for when a PUBLISH message is received from the server.
    # Currently will only receive JSON -> dict, so take care of it like that.
    # All logic done here and sent to UI/main parser
    # receivedDataJson["varId"] to access things
    def onMessage(self, client, userdata, msg):
                
        if(self.fullParser.connectedToHostBool):
        
            receivedDataJson = json.loads(msg.payload)
            
            if(receivedDataJson["resetToOrbiterBoolean"]):
                self.appUi.resetAnalyzerUI()
                self.appUi.resetDisplay()
                if(self.fullParser.overlayWindow != None):
                    self.fullParser.overlayWindow.updateOverlayWithTextRaw(StringConstants.orbiterResetOverlayDisplayString)
            
            if(receivedDataJson["missionName"] != ""):
                self.appUi.displayMissionAndTiles(receivedDataJson["missionName"], receivedDataJson["tiles"], receivedDataJson["goodTilesBoolean"])
                if(self.fullParser.overlayWindow != None):
                    self.fullParser.overlayWindow.updateOverlayWithTextRaw(receivedDataJson["tiles"])
            
            if(receivedDataJson["totalRoundTimeInSeconds"] != ""):
                if(not self.appUi.displayInKappaMode):
                    self.fullParser.app.after(50, self.appUi.updateUIForDisruptionLogging)
                
                self.appUi.displayDisruptionRoundFromHostData(receivedDataJson)
                if(self.fullParser.overlayWindow != None):
                    if(receivedDataJson["isLastKappaRound"]):
                        self.fullParser.overlayWindow.updateOverlayWithTextRaw(StringConstants.overlayRoundString + 
                                                                          receivedDataJson["totalRoundTimeInSeconds"] + 
                                                                          StringConstants.overlaySpaceString + 
                                                                          StringConstants.overlayEndTimeString + 
                                                                          receivedDataJson["expectedEnd"])
                    else:
                        self.fullParser.overlayWindow.displayDisruptionRoundData(receivedDataJson["totalRoundTimeInSeconds"], receivedDataJson["expectedEnd"])
            
            if(receivedDataJson["isToxin"]):
                self.fullParser.appUI.updateInterfaceForToxin(True)
        