import paho.mqtt.client as mqtt
import json
from json import JSONDecoder, JSONEncoder

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
        self.mqttClient.connect(self.mqttBroker, 1883, 60)
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
            elif(receivedDataJson["missionName"] != ""):
                self.appUi.displayMissionAndTiles(receivedDataJson["missionName"], receivedDataJson["tiles"], receivedDataJson["goodTilesBoolean"])
            elif(receivedDataJson["totalRoundTimeInSeconds"] != ""):
                self.appUi.displayDisruptionRoundFromHostData(receivedDataJson)
            
        
        
        
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
        self.goodTilesBoolean = None
        self.resetToOrbiterBoolean = None
