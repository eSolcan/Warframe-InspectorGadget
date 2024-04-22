# InspectorGadget

Simple EE.log parser used to search for various mission tilesets, as well as analyze Disruption runs, both real time or post run.

## Description

InspectorGadget can be used to simply look for the correct tiles in various missions for farming Nanospores and Polymer.

It can also be used to look for specific layouts in some disruption missions, and subsequently analyze a full run, displaying times of key inserts, demolyst kills, expected 45 round time (level cap), amongst other stats. A chart containing time/round is created at the end of the run and all raw data collected is dumped to a file, allowing users to analyze all the data in minute detail.

Lastly, InspectorGadget can also parse through Cascade map layout, showing a sequence of numbers which indicate the number of exolizers in each room.

## Using the app
Simply run the InspectorGadget file, or the built .exe file. This will start parsing EE.log from the end of file, and will display relevant information in the Analyzer tab. 

If you desire to search for a specific disruption layout combination, select the tiles which you consider bad, and those will be discarded by the app. Once a good layout is found, the analyzer window will automatically switch to disruption analysis mode. As mentioned in the description portion before, after extracting from the disruption run, a graph is created in a new tab, and all collected data is written to disk.

In the **Settings** tab, the general settings allow for the window to be always on top, as well as an option do log events to a log file. Furthermore, a "Read from Start" option exists, which allows a fully completed disruption run to be analyzed.

## Questions about the app
Message *@wtb_username* on Discord for any questions or suggestions regarding the app and its functionalities. A working .exe version is available in the releases tab. Due to being built using pyinstaller and making use of the requests module to check app version, Windows defender usually considers it malicious, so apologies for that.

Alternatively, you can run the python file directly, requiring manual installation of missing modules.

## Preview Images

![SettingsTab](AppImages/SettingsTab.png?)
![AnalyzerTab](AppImages/AnalyzerTab.png?)
![ChartTab](AppImages/ChartTab.png?)
