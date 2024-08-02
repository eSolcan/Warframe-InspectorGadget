# InspectorGadget

Simple EE.log parser used to search for various mission tilesets, as well as analyze Disruption runs, both real time or post run. Download it from [Releases](https://github.com/eSolcan/Warframe-InspectorGadget/releases/latest) -  InspectorGadget.zip file, .exe contained inside.

## Description

#### Resources tiles
InspectorGadget can be used to simply look for the correct tiles in various missions for farming Nanospores and Polymer:
- Zabala (Eris) - Nano
- Opheli (Uranus) - Poly


#### Disruption
It can also be used to look for specific layouts in some disruption missions, and subsequently analyze a full run, displaying times of key inserts, demolyst kills, expected 45 round time (level cap) based on current round average, amongst other stats. A chart containing time/round is created at the end of the run and all raw data collected is dumped to a file, allowing users to analyze all the data in minute detail.

##### Overlay
A recent new feature allows for the creation of a small overlay window (similar to YATE, for those familiar with Eidolons). In the settings tab, the overlay can be toggled at any time. The window can be positioned anywhere on the screen by simply clicking and dragging it, and the position can be locked by pressing the blue lock button, making it always on top and non-interactable with. Furthermore, the font size can be adjusted at any time in the settings window. 

The overlay will update at the end of each round with the previous round time and expected level cap time.

##### Host-Client Connection
The app also allows for disruption information to be sent to clients. The host must copy the code in the settings tab and share it with the clients, where they must input it in the corresponding box and connect. This will allow for periodic updates on the client side to the main Inspector Analyzer window, as well as on the overlay.

#### Cascade exos
Lastly, InspectorGadget can also parse through Cascade map layout, showing a sequence of numbers which indicate the number of exolizers in each room. Alongside the numbers, the room names will also be shown.

## Using the app
Simply run the .exe file AFTER opening the game (new EE.log sessions are not detected), or directly the InspectorGadget.py file. This will start parsing EE.log from the end of file, and will display relevant information in the Analyzer tab. As mentioned before, make sure to open Warframe before the app, as it only "opens" EE.log once, and doesn't detect game restarts.

If you desire to search for a specific disruption layout combination, select the tiles which you consider bad, and those will be discarded by the app. Once a good layout is found, the analyzer window will automatically switch to disruption analysis mode. As mentioned in the description portion before, after extracting from the disruption run, a graph is created in a new tab, and all collected data is written to disk.

In the **Settings** tab, the general settings allow for the window to be always on top, as well as a "Read from Start" option, which allows a fully completed disruption run to be analyzed.

## Questions about the app
Message *@wtb_username* on Discord for any questions or suggestions regarding the app and its functionalities. A working .exe version is available in the [Releases](https://github.com/eSolcan/Warframe-InspectorGadget/releases/latest) tab in InspectorGadget.zip. Due to being built using pyinstaller and making use of the requests module to check app version, Windows defender usually considers it malicious, so apologies for that.

Alternatively, you can run the python file directly, requiring manual installation of missing modules.

## Preview Images

![SettingsTab](AppImages/SettingsTab.png?)
![AnalyzerTab](AppImages/AnalyzerTab.png?)
![ChartTab](AppImages/ChartTab.png?)
