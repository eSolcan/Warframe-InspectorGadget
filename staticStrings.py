# Search String constants
class StringConstants:
    versionUrl = "https://raw.githubusercontent.com/eSolcan/Warframe_InspectorGadget/main/version.txt"
    updateUrl = "https://github.com/eSolcan/Warframe-InspectorGadget/releases/latest"
    
    newLineString = "\n"

    loggedInString = "Logged in "

    updateAvailableString = "Update available"
    updateAvailableHyperlinkString = "Download"
    
    hostCodeDisplayString = "Host/Client Connect (Disruption)"
    
    openOverlayString = "Open Overlay"
    closeOverlayString = "Close Overlay"
    orbiterResetOverlayDisplayString = "Orbiter Reset"

    # Orbiter reset string
    orbiterResetString = "/Lotus/Levels/Proc/PlayerShip generating layout with segments"
    orbiterResetEarthString = "/Lotus/Levels/Proc/TheNewWar/PartTwo/TNWDrifterCampMain generating layout with segments"
    abortMissionString = "Script [Info]: TopMenu.lua: Abort: host/no session"

    # Various mission names
    missionNameString = "ThemedSquadOverlay.lua: Mission name:"
    missionSolNodeHostLoadinString = "ThemedSquadOverlay.lua: Host loading"
    
    copernicusLua = "Copernicus (Lua)"
    assurUranus = "ClanNode17"
    opheliaUranus = "SolNode69"
    
    kappaSedna = "SolNode177"
    apolloLua = "SolNode308"
    urUranus = "ClanNode16"
    olympusMars = "SolNode30"
    tuvulCommonsZariman = "SolNode232"
    
    disruptionMissionNames = [kappaSedna, apolloLua, olympusMars, urUranus]
    
    # assurUranus = "Assur (Uranus)"
    # copernicusLua = "Copernicus (Lua)"
    
    # opheliaUranus = "Ophelia (Uranus)"
    # kappaSedna = "Kappa (Sedna)"
    # apolloLua = "Apollo (Lua)"
    # urUranus = "Ur (Uranus)"
    # olympusMars = "Olympus (Mars)"
    # tuvulCommonsZariman = "Tuvul Commons (Zariman)"
    
    # kappaSednaRussian = "Kappa (Седна)"
    # apolloLuaRussian = "Apollo (Луа)"
    # olympusMarsRussian = "Olympus (Марс)"
    # urUranusRussian = "Ur (Уран)"
    # tuvulCommonsZarimanRussian = "Палаты Тувула (Зариман)"

    # disruptionMissionNamesRussian = [kappaSednaRussian, apolloLuaRussian, olympusMarsRussian, urUranusRussian]

    # Tile names for nano and poly farming
    nanoGoodTileString = "Layer /Lotus/Levels/InfestedCorpus/InfestedReactor"
    polyGoodTileString = "Layer /Lotus/Levels/GrineerOcean/GrineerOceanIntermediateBotanyLab"
    assurGoodTileString = "Layer /Lotus/Levels/GrineerGalleon/GrnConnectorFour"
    tileMatchesList = [nanoGoodTileString, polyGoodTileString]

    # Disruption toxin
    disruptionToxinPylon = "SentientArtifactMission.lua: Disruption: Level aura 15"

    # Kappa strings
    kappaGrineerIntermediateString = "Layer /Lotus/Levels/GrineerGalleon/GrnIntermediate"
    kappa1 = "One"
    kappa3 = "Three"
    kappa4 = "Four"
    kappa6 = "Six"
    kappa7 = "Seven"
    kappa8 = "Eight"
    kappaList = [kappa1, kappa3, kappa4, kappa6, kappa7, kappa8]
    kappaListForCheckbox = ["1", "3", "4", "6", "7", "8"]
    
    overlayRoundString = "Round - "
    overlaySpaceString = "     "
    overlayExpectedString = "Expected - "
    overlayEndTimeString = "End Time - "

    # Apollo strings
    apolloMoonIntString = "Layer /Lotus/Levels/OrokinMoon/MoonInt"
    apollo1 = "BotGarden"
    apollo2 = "Cloister"
    apollo3 = "Endurance"
    apollo4 = "HallsOfJudgement"
    apollo5 = "Power"
    apollo6 = "RuinedPiaza"
    apollo7 = "Stealth"
    apolloList = [apollo1, apollo2, apollo3, apollo4, apollo5, apollo6, apollo7]
    apolloListForCheckbox = ["BotGarden", "Cloister", "Endurance", "HallsOfJ", "Power", "RuinedPiaza", "Stealth"]

    # Olympus strings
    olympusCmpString = "Layer /Lotus/Levels/GrineerSettlement/Cmp"
    olympus1 = "Intermediate01"
    olympus2 = "Intermediate02"
    olympus3 = "Intermediate03"
    olympus4 = "Intermediate04"
    olympus5 = "Intermediate05"
    olympus6 = "Intermediate06"
    olympus10 = "Intermediate10"
    olympus11 = "Intermediate11"
    olympusAss = "Assassinate"
    olympusConn3 = "Connector03"
    olympusList = [olympus1, olympus2, olympus3, olympus4, olympus5, olympus6, olympus10, olympus11, olympusAss, olympusConn3]
    olympusListForCheckbox = ["01", "02", "03", "04", "05", "06", "10", "11", "Ass", "Conn"]

    # Cascade strings
    tuvulCommonsIntString = "Layer /Lotus/Levels/Zariman/Int"
    
    # 5 - MUST ALWAYS BE THERE
    cascadeShuttleBay = "ShuttleBay"
    
    cascadeShuttleBayDisplay = "Hangar"
    
    # 4 - x2
    cascadePark = "Park"
    cascadeParkB = "ParkB"
    cascadeParkC = "ParkC"
    cascadeSchool = "School"
    
    cascadeParkDisplay = "Park"
    cascadeParkBDisplay = "Serenity"
    cascadeParkCDisplay = "Roost"
    cascadeSchoolDisplay = "Schoolyard"
    
    # 3 - passable
    cascadeCellBlockA = "CellBlockA"
    cascadeHydroponics = "Hydroponics"
    cascadeCargoBay = "CargoBay"
    cascadeLivingQuarters = "LivingQuarters"
    cascadeIndoctrinationHall = "IndoctrinationHall"
    cascadeAmphitheatre = "Amphitheatre"
    cascadeLunaroCourt = "LunaroCourt"
    
    cascadeCellBlockADisplay = "Brig"
    cascadeHydroponicsDisplay = "Garden"
    cascadeCargoBayDisplay = "Cargo"
    cascadeLivingQuartersDisplay = "Habitat"
    cascadeIndoctrinationHallDisplay = "Hall"
    cascadeAmphitheatreDisplay = "Theatre"
    cascadeLunaroCourtDisplay = "Lunaro"
    
    cascadeListOf4 = [cascadePark, cascadeParkB, cascadeParkC, cascadeSchool]
    cascadeListOf3 = [cascadeCellBlockA, cascadeHydroponics, cascadeCargoBay, cascadeLivingQuarters, cascadeIndoctrinationHall, cascadeAmphitheatre, cascadeLunaroCourt]
    
    cascadeListOf4Display = [cascadeParkDisplay, cascadeParkBDisplay, cascadeParkCDisplay, cascadeSchoolDisplay]
    cascadeListOf3Display = [cascadeCellBlockADisplay, cascadeHydroponicsDisplay, cascadeCargoBayDisplay, cascadeLivingQuartersDisplay, cascadeIndoctrinationHallDisplay, cascadeAmphitheatreDisplay, cascadeLunaroCourtDisplay]

    # Dent
    apolloSpeed = "Speed"

    # End of mission load strings
    endOfMissionLoadString = "Layer /Lotus/Levels/Backdrops"
    # endOfMissionLoadString = "Sb: /Lotus/Levels/Backdrops"
    endOfMissionLoadStringKappa = "Layer /Lotus/Levels/Backdrops/"
    endOfMissionLoadStringCascade = "Layer /Lotus/Levels/Backdrops/ZarimanRegion"

    # Various analyzer related strings
    replacedByMissionNameString = "(This will be replaced by mission name)"
    waitingForMissionStart = "(Waiting for mission load)"
    searchingTextString = "Parsing tileset"
    searchingTextFoundString = "Found"
    searchingTextNotFoundString = "Not Found"
    kappaShouldResetString = "Bad tiles found - Reset"
    kappaUsableTileString = "No bad tiles found\nWill begin analyzing in 10s"
    
    # Cascade related strings
    cascade544Yes = "544 Found"
    cascade544No = "544 Not Found"
    cascadeResetString = "No 544 found - Should reset"
    cascadeGoodToGoString = "544 found\nWill continue in 10s, close app if you want"

    appWillResetIn30sString = "Will continue in 10s, close app if you want"

    # Bad tiles strings
    selectBadTilesKappaString = "Bad tiles (Kappa):"
    selectBadTilesApolloString = "Bad tiles (Apollo):"
    selectBadTilesOlympusString = "Bad tiles (Olympus):"

    whatIsBeingParsedText = "Parsing:\nDisruption\nCascade\nOphelia - Poly\nAssur - Poly"

    discordTagString = "@wtb_username"

    # Disruption related strings
    disruptionIntroDoorUnlockedString = "Script [Info]: SentientArtifactMission.lua: Disruption: Intro door"
    disruptionKeyInsertString = "SentientArtifactMission.lua: Disruption: Starting defense for artifact"
    disruptionDefenseFinishedString = "SentientArtifactMission.lua: Disruption: Completed defense for artifact"
    disruptionDefenseFailedString = "SentientArtifactMission.lua: Disruption: Failed defense for artifact"
    disruptionTotalKeysCompleted = "SentientArtifactMission.lua: Disruption: Total artifacts complete so far this mission:"
    # disruptionRunStartString = "Net [Info]: **** Starting session on HOST"
    disruptionRunStartString = "Script [Info]: NemesisMission.lua: NemesisGenerator::InitMission"

    disruptionRoundStartedString = "SentientArtifactMission.lua: ModeState = 3"
    disruptionRoundFinishedString = "SentientArtifactMission.lua: ModeState = 4"

    disruptionKeyInsertsStaticString = "Key inserts:"
    disruptionDemoKillsString = "Demo kills:"
    disruptionPreviousRunAverateString = "Round time:"
    disruptionCurrentAverateString = "Current AVG:"
    disruptionExpectedEndString = "Expected end:"
    bestRoundTimeString = "Best round:"
    levelCapTimeString = "LvlCap time:"

    disruptionDataDumpedString = "Run written to disk and Chart created in new Tab"

    # Misc strings
    scriptString = "Script"
    sysInfoString = "Sys [Info]"
    netInfoString = "Net [Info]"

    generalSettingsString = "General Settings"

    urlFindMore = "Click for full resolution album (and other map tiles)"

    restartReadingTextString = "(From last orbiter reset)"