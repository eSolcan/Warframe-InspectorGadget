# Search String constants
class StringConstants:
    newLineString = "\n"

    # Orbiter reset string
    orbiterResetString = "/Lotus/Levels/Proc/PlayerShip generating layout with segments"

    # Various mission names
    missionNameString = "ThemedSquadOverlay.lua: Mission name:"
    zabalaEris = "Zabala (Eris)"
    nimusEris = "Nimus (Eris)"
    opheliaUranus = "Ophelia (Uranus)"
    kappaSedna = "Kappa (Sedna)"
    apolloLua = "Apollo (Lua)"
    copernicusLua = "Copernicus (Lua)"
    tuvulCommonsZariman = "Tuvul Commons (Zariman)"
    olympusMars = "Olympus (Mars)"

    disruptionMissionNames = [kappaSedna, apolloLua, olympusMars]

    # Tile names for nano and poly farming
    nanoGoodTileString = "/Lotus/Levels/InfestedCorpus/InfestedReactor.level"
    polyGoodTileString = "/Lotus/Levels/GrineerOcean/GrineerOceanIntermediateBotanyLab.level"
    tileMatchesList = [nanoGoodTileString, polyGoodTileString]

    # Kappa strings
    kappaGrineerIntermediateString = "I: /Lotus/Levels/GrineerGalleon/GrnIntermediate"
    kappa1 = "One.level"
    kappa3 = "Three.level"
    kappa4 = "Four.level"
    kappa6 = "Six.level"
    kappa7 = "Seven.level"
    kappa8 = "Eight.level"
    kappaList = [kappa1, kappa3, kappa4, kappa6, kappa7, kappa8]
    kappaListForCheckbox = ["1", "3", "4", "6", "7", "8"]

    # Apollo strings
    apolloMoonIntString = "I: /Lotus/Levels/OrokinMoon/MoonInt"
    apollo1 = "BotGarden.level"
    apollo2 = "Cloister.level"
    apollo3 = "Endurance.level"
    apollo4 = "HallsOfJudgement.level"
    apollo5 = "Power.level"
    apollo6 = "RuinedPiaza.level"
    apollo7 = "Stealth.level"
    apolloList = [apollo1, apollo2, apollo3, apollo4, apollo5, apollo6, apollo7]
    apolloListForCheckbox = ["BotGarden", "Cloister", "Endurance", "HallsOfJudgement", "Power", "RuinedPiaza", "Stealth"]

    # Olympus strings
    olympusCmpString = "I: /Lotus/Levels/GrineerSettlement/Cmp"
    olympus1 = "Intermediate01.level"
    olympus2 = "Intermediate02.level"
    olympus3 = "Intermediate03.level"
    olympus4 = "Intermediate04.level"
    olympus5 = "Intermediate05.level"
    olympus6 = "Intermediate06.level"
    olympus10 = "Intermediate10.level"
    olympus11 = "Intermediate11.level"
    olympusAss = "Assassinate.level"
    olympusConn3 = "Connector03.level"
    olympusList = [olympus1, olympus2, olympus5, olympus6, olympus10, olympus11, olympusAss, olympusConn3]
    olympusListForCheckbox = ["01", "02", "03", "04", "05", "06", "10", "11", "Ass", "Conn"]

    # Cascade strings
    tuvulCommonsIntString = "I: /Lotus/Levels/Zariman/Int"
    
    # 5 - MUST ALWAYS BE THERE
    cascadeShuttleBay = "ShuttleBay.level"
    
    # 4 - x2
    cascadePark = "Park.level"
    cascadePark2 = "Park2.level"
    cascadeParkC = "ParkC.level"
    cascadeSchool = "School.level"
    
    # 3 - passable
    cascadeCellBlockA = "CellBlockA.level"
    cascadeHydroponics = "Hydroponics.level"
    cascadeCargoBay = "CargoBay.level"
    cascadeLivingQuarters = "LivingQuarters.level"
    cascadeIndoctrinationHall = "IndoctrinationHall.level"
    cascadeAmphitheatre = "Amphitheatre.level"
    cascadeLunaroCourt = "LunaroCourt.level"
    cascadeListOf4 = [cascadePark, cascadePark2, cascadeParkC, cascadeSchool]
    cascadeListOf3 = [cascadeCellBlockA, cascadeHydroponics, cascadeCargoBay, cascadeLivingQuarters, cascadeIndoctrinationHall, cascadeAmphitheatre, cascadeLunaroCourt]

    apolloSpeed = "Speed.level"

    dotLevelString = ".level"

    # End of mission load strings
    endOfMissionLoadString = "/Lotus/Levels/Backdrops"
    # endOfMissionLoadString = "Sb: /Lotus/Levels/Backdrops"
    endOfMissionLoadStringKappa = "Cm: /Lotus/Levels/Backdrops/"
    endOfMissionLoadStringCascade = "Cm: /Lotus/Levels/Backdrops/ZarimanRegion.level"

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

    whatIsBeingParsedText = "Parsing:\nKappa & Apollo\nCascade\nZabala - Nano\nOphelia - Poly"

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

    disruptionDataDumpedString = "Run written to file disruptionFullRunData.json and chart created in new tab"

    # Misc strings
    scriptString = "Script"
    sysInfoString = "Sys [Info]"
    netInfoString = "Net [Info]"

    generalSettingsString = "General Settings"

    urlFindMore = "Click for full resolution album (and other map tiles)"

    restartReadingTextString = "(From last orbiter reset)"