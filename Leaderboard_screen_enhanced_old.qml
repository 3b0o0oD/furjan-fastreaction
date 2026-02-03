import QtQuick 2.12

Item {
    id: _leaderboard_screen

    // Flexible resolution support
    property real baseWidth: 1920
    property real baseHeight: 1080
    property real scaleX: width / baseWidth
    property real scaleY: height / baseHeight
    property real scale: Math.min(scaleX, scaleY) // Maintain aspect ratio

    // Palette
    property color palettePrimary: "#A85C4C"
    property color paletteSecondary: "#A47864"
    property color paletteLight: "#E0BFA2"
    property color paletteAccent: "#984421"
    property color paletteDark: "#77202E"

    // Default to 4K resolution
    height: 2160
    width: 3840

    clip: true

    FontLoader {
        id: customFontLoader
        source: "Assets/Fonts/MyriadPro-Regular.otf"
    }
    FontLoader {
        id: customFontLoader2
        source: "Assets/Fonts/Janna-LT-Regular.ttf"
    }

    // Apply scaling transform
    transform: Scale {
        xScale: scale
        yScale: scale
        origin.x: 0
        origin.y: 0
    }

    // Backend property for receiving updates
    property var backend: null

    // Player data properties for binding
    property var playerData: [
        { name: "-", score: 0, weighted_points: 0, rank: 1 },
        { name: "-", score: 0, weighted_points: 0, rank: 2 },
        { name: "-", score: 0, weighted_points: 0, rank: 3 },
        { name: "-", score: 0, weighted_points: 0, rank: 4 },
        { name: "-", score: 0, weighted_points: 0, rank: 5 }
    ]

    // Podium data properties
    property string goldName: "-"
    property string silverName: "-"
    property string bronzeName: "-"
    property int goldScore: 900
    property int silverScore: 850
    property int bronzeScore: 720
    property int goldWeighted: 10080
    property int silverWeighted: 9790
    property int bronzeWeighted: 8520

    // Last player data properties
    property string lastPlayerName: "-"
    property int lastPlayerScore: 0
    property int lastPlayerWeighted: 0
    property int lastPlayerRank: 0

    // Connect backend signals when backend is set
    onBackendChanged: {
        if (backend) {
            console.log("Backend connected to QML")

            // Connect player table signals
            backend.playerTableCellUpdated.connect(updatePlayerTableCell)
            backend.playerTableNameUpdated.connect(updatePlayerTableName)
            backend.playerTableScoreUpdated.connect(updatePlayerTableScore)
            backend.playerTableWeightedUpdated.connect(updatePlayerTableWeighted)
            backend.playerTableRankUpdated.connect(updatePlayerTableRank)

            // Connect podium signals
            backend.podiumUpdated.connect(updatePodium)
            backend.goldPlayerUpdated.connect(updateGoldPlayer)
            backend.silverPlayerUpdated.connect(updateSilverPlayer)
            backend.bronzePlayerUpdated.connect(updateBronzePlayer)

            // Connect last player signals
            backend.lastPlayerUpdated.connect(updateLastPlayer)
            backend.lastPlayerNameUpdated.connect(updateLastPlayerName)
            backend.lastPlayerScoreUpdated.connect(updateLastPlayerScore)
            backend.lastPlayerWeightedUpdated.connect(updateLastPlayerWeighted)
            backend.lastPlayerRankUpdated.connect(updateLastPlayerRank)

            // Connect general signals
            backend.leaderboardUpdated.connect(refreshLeaderboard)
            backend.playerTableUpdated.connect(refreshPlayerTable)
        }
    }

    // Signal handlers for player table updates
    function updatePlayerTableCell(index, name, score, weighted_points, rank) {
        console.log(`Updating player table cell ${index}: ${name}, ${score}, ${weighted_points}, ${rank}`)
        if (index >= 0 && index < playerData.length) {
            playerData[index] = { name: name, score: score, weighted_points: weighted_points, rank: rank }
        }
    }

    function updatePlayerTableName(index, name) {
        console.log(`Updating player table name ${index}: ${name}`)
        if (index >= 0 && index < playerData.length) {
            playerData[index].name = name
        }
    }

    function updatePlayerTableScore(index, score) {
        console.log(`Updating player table score ${index}: ${score}`)
        if (index >= 0 && index < playerData.length) {
            playerData[index].score = score
        }
    }

    function updatePlayerTableWeighted(index, weighted_points) {
        console.log(`Updating player table weighted ${index}: ${weighted_points}`)
        if (index >= 0 && index < playerData.length) {
            playerData[index].weighted_points = weighted_points
        }
    }

    function updatePlayerTableRank(index, rank) {
        console.log(`Updating player table rank ${index}: ${rank}`)
        if (index >= 0 && index < playerData.length) {
            playerData[index].rank = rank
        }
    }

    // Signal handlers for podium updates
    function updatePodium(gold_name, silver_name, bronze_name, gold_score, silver_score, bronze_score, gold_weighted, silver_weighted, bronze_weighted) {
        console.log(`Updating podium: Gold=${gold_name}, Silver=${silver_name}, Bronze=${bronze_name}`)
        goldName = gold_name
        silverName = silver_name
        bronzeName = bronze_name
        goldScore = gold_score
        silverScore = silver_score
        bronzeScore = bronze_score
        goldWeighted = gold_weighted
        silverWeighted = silver_weighted
        bronzeWeighted = bronze_weighted
    }

    function updateGoldPlayer(name, score, weighted_points) {
        console.log(`Updating gold player: ${name}, ${score}, ${weighted_points}`)
        goldName = name
        goldScore = score
        goldWeighted = weighted_points
    }

    function updateSilverPlayer(name, score, weighted_points) {
        console.log(`Updating silver player: ${name}, ${score}, ${weighted_points}`)
        silverName = name
        silverScore = score
        silverWeighted = weighted_points
    }

    function updateBronzePlayer(name, score, weighted_points) {
        console.log(`Updating bronze player: ${name}, ${score}, ${weighted_points}`)
        bronzeName = name
        bronzeScore = score
        bronzeWeighted = weighted_points
    }

    // Signal handlers for last player updates
    function updateLastPlayer(name, score, weighted_points, rank) {
        console.log(`Updating last player: ${name}, ${score}, ${weighted_points}, ${rank}`)
        lastPlayerName = name
        lastPlayerScore = score
        lastPlayerWeighted = weighted_points
        lastPlayerRank = rank
    }

    function updateLastPlayerName(name) {
        console.log(`Updating last player name: ${name}`)
        lastPlayerName = name
    }

    function updateLastPlayerScore(score) {
        console.log(`Updating last player score: ${score}`)
        lastPlayerScore = score
    }

    function updateLastPlayerWeighted(weighted_points) {
        console.log(`Updating last player weighted: ${weighted_points}`)
        lastPlayerWeighted = weighted_points
    }

    function updateLastPlayerRank(rank) {
        console.log(`Updating last player rank: ${rank}`)
        lastPlayerRank = rank
    }

    function refreshLeaderboard() {
        console.log("Refreshing entire leaderboard")
        // Trigger property updates
        playerData = playerData.slice() // Force property change
    }

    function refreshPlayerTable() {
        console.log("Refreshing player table")
        // Trigger property updates
        playerData = playerData.slice() // Force property change
    }

    //-----------------------------------------------------------------
    // Top-left logo area — replaced images with palette-only blocks
    Item {
        id: logo
        x: 745
        y: 920
        height: 110
        width: 441

        Row {
            anchors.fill: parent
            spacing: 18
            Rectangle {
                id: logo_block_1
                width: 120
                anchors.verticalCenter: parent.verticalCenter
                height: parent.height * 0.85
                radius: 8
                color: paletteSecondary
                border.color: paletteDark
                border.width: 2
                Text {
                    anchors.centerIn: parent
                    color: paletteLight
                    font.family: customFontLoader.name
                    font.pixelSize: 20
                    text: "UXE"
                    font.weight: Font.Bold
                }
            }
            Rectangle {
                id: logo_block_2
                width: 120
                anchors.verticalCenter: parent.verticalCenter
                height: parent.height * 0.85
                radius: 8
                color: palettePrimary
                border.color: paletteDark
                border.width: 2
                Text {
                    anchors.centerIn: parent
                    color: paletteLight
                    font.family: customFontLoader.name
                    font.pixelSize: 20
                    text: "SIRA"
                    font.weight: Font.Bold
                }
            }
            Rectangle {
                id: logo_block_3
                width: 160
                anchors.verticalCenter: parent.verticalCenter
                height: parent.height * 0.85
                radius: 8
                color: paletteAccent
                border.color: paletteDark
                border.width: 2
                Text {
                    anchors.centerIn: parent
                    color: paletteLight
                    font.family: customFontLoader.name
                    font.pixelSize: 18
                    text: "EMARAT"
                    font.weight: Font.Bold
                }
            }
        }
    }

    //-----------------------------------------------------------------
    // Popup / main leaderboard card - replaced image backgrounds with rectangles
    Item {
        id: popup
        x: 257
        y: 286
        height: 620
        width: 1406

        // Card background
        Rectangle {
            id: leaderboard_card
            anchors.fill: parent
            radius: 18
            color: paletteDark
            border.color: palettePrimary
            border.width: 3
            opacity: 0.98
        }

        // Inner content area
        Rectangle {
            id: popup_inner
            x: 18
            y: 14
            width: parent.width - 36
            height: parent.height - 28
            radius: 12
            color: paletteSecondary
            border.color: palettePrimary
            border.width: 2
        }

        // Player table area
        Item {
            id: player_table
            x: 64
            y: 138
            height: 432
            width: 1278

            // Reusable row component (implemented inline)
            Component {
                id: rowTemplate
                Rectangle {
                    id: rowRect
                    width: player_table.width
                    height: 60
                    radius: 8
                    color: styleColor
                    border.color: palettePrimary
                    border.width: 1.5

                    property color styleColor: paletteSecondary
                    // Rank circle
                    Rectangle {
                        id: rank
                        x: 20
                        y: 10
                        width: 40
                        height: 40
                        radius: 20
                        color: rankColor
                        border.color: paletteDark
                        border.width: 1
                        property color rankColor: paletteAccent

                        Text {
                            anchors.centerIn: parent
                            color: paletteLight
                            font.family: customFontLoader.name
                            font.pixelSize: 22
                            text: rankText
                            font.weight: Font.Black
                        }
                        property string rankText: "-"
                    }

                    // Team name
                    Text {
                        id: teamName
                        x: 144
                        y: 18
                        color: paletteLight
                        font.family: customFontLoader.name
                        font.pixelSize: 22
                        font.weight: Font.Black
                        text: "-"
                    }

                    // Score
                    Text {
                        id: scoreText
                        x: 918
                        y: 18
                        color: palettePrimary
                        font.family: customFontLoader.name
                        font.pixelSize: 22
                        font.weight: Font.Black
                        horizontalAlignment: Text.AlignHCenter
                        text: "-"
                    }

                    // Weighted points
                    Text {
                        id: weightedText
                        x: 1128
                        y: 18
                        color: palettePrimary
                        font.family: customFontLoader.name
                        font.pixelSize: 22
                        font.weight: Font.Black
                        horizontalAlignment: Text.AlignHCenter
                        text: "-"
                    }
                }
            }

            // Last player row (keeps the same layout and bindings)
            Loader {
                id: lastPlayerRow
                x: 0
                y: 377
                width: player_table.width
                height: 60
                sourceComponent: rowTemplate
                onLoaded: {
                    var item = lastPlayerRow.item
                    item.styleColor = paletteDark
                    item.rankText = lastPlayerRank > 0 ? lastPlayerRank.toString() : "-"
                    item.teamName.text = lastPlayerName
                    item.scoreText.text = lastPlayerScore.toString()
                    item.weightedText.text = lastPlayerWeighted.toString()
                    item.rank.rankColor = paletteAccent
                }
            }

            // Header strip for "Last Played By"
            Rectangle {
                id: nameHeader
                x: 0
                y: 315
                height: 60
                width: player_table.width
                radius: 8
                color: palettePrimary
                border.color: paletteDark
                border.width: 1.5
                Text {
                    anchors.centerIn: parent
                    color: paletteLight
                    font.family: customFontLoader.name
                    font.pixelSize: 30
                    font.letterSpacing: 2.10
                    font.weight: Font.Black
                    text: "Last Played By"
                }
            }

            // Player rows (5 -> indices 0..4). We position them to match original vertical positions.
            // Player 5 (index 4)
            Loader {
                id: player5
                x: 0
                y: 248
                width: player_table.width
                height: 60
                sourceComponent: rowTemplate
                onLoaded: {
                    var it = player5.item
                    it.styleColor = paletteSecondary
                    it.rankText = playerData[4] ? playerData[4].rank.toString() : "5"
                    it.teamName.text = playerData[4] ? playerData[4].name : "-"
                    it.scoreText.text = playerData[4] ? playerData[4].score.toString() : "-"
                    it.weightedText.text = playerData[4] ? playerData[4].weighted_points.toString() : "-"
                    it.rank.rankColor = palettePrimary
                }
            }
            // Player 4 (index 3)
            Loader {
                id: player4
                x: 0
                y: 186
                width: player_table.width
                height: 60
                sourceComponent: rowTemplate
                onLoaded: {
                    var it = player4.item
                    it.styleColor = paletteSecondary
                    it.rankText = playerData[3] ? playerData[3].rank.toString() : "4"
                    it.teamName.text = playerData[3] ? playerData[3].name : "-"
                    it.scoreText.text = playerData[3] ? playerData[3].score.toString() : "-"
                    it.weightedText.text = playerData[3] ? playerData[3].weighted_points.toString() : "-"
                    it.rank.rankColor = palettePrimary
                }
            }
            // Player 3 (index 2) - Bronze style
            Loader {
                id: player3
                x: 0
                y: 124
                width: player_table.width
                height: 60
                sourceComponent: rowTemplate
                onLoaded: {
                    var it = player3.item
                    it.styleColor = paletteDark
                    it.rankText = playerData[2] ? playerData[2].rank.toString() : "3"
                    it.teamName.text = playerData[2] ? playerData[2].name : "-"
                    it.scoreText.text = playerData[2] ? playerData[2].score.toString() : "-"
                    it.weightedText.text = playerData[2] ? playerData[2].weighted_points.toString() : "-"
                    it.rank.rankColor = "#B08B5B" // bronze hue (derived from palette)
                }
            }
            // Player 2 (index 1) - Silver style
            Loader {
                id: player2
                x: 0
                y: 62
                width: player_table.width
                height: 60
                sourceComponent: rowTemplate
                onLoaded: {
                    var it = player2.item
                    it.styleColor = paletteDark
                    it.rankText = playerData[1] ? playerData[1].rank.toString() : "2"
                    it.teamName.text = playerData[1] ? playerData[1].name : "-"
                    it.scoreText.text = playerData[1] ? playerData[1].score.toString() : "-"
                    it.weightedText.text = playerData[1] ? playerData[1].weighted_points.toString() : "-"
                    it.rank.rankColor = "#C0C0C0" // silver hue
                }
            }
            // Player 1 (index 0) - Gold style
            Loader {
                id: player1
                x: 0
                y: 0
                width: player_table.width
                height: 63
                sourceComponent: rowTemplate
                onLoaded: {
                    var it = player1.item
                    it.styleColor = palettePrimary
                    it.rankText = playerData[0] ? playerData[0].rank.toString() : "1"
                    it.teamName.text = playerData[0] ? playerData[0].name : "-"
                    it.scoreText.text = playerData[0] ? playerData[0].score.toString() : "-"
                    it.weightedText.text = playerData[0] ? playerData[0].weighted_points.toString() : "-"
                    it.rank.rankColor = "#FFD166" // gold hue
                }
            }
        }

        // Headers (replacing header images and line)
        Item {
            id: table_headers
            x: 64
            y: 61
            height: 75
            width: parent.width

            // Rank header
            Text {
                id: rank_header_en
                x: 19
                y: 30
                color: paletteAccent
                font.family: customFontLoader2.name
                font.pixelSize: 26
                font.weight: Font.Bold
                text: "Rank"
            }
            // Team name header
            Text {
                id: team_name_header_en
                x: 143
                y: 30
                color: paletteAccent
                font.family: customFontLoader2.name
                font.pixelSize: 26
                font.weight: Font.Bold
                text: "Team name"
            }
            // Score header
            Text {
                id: score_header_en
                x: 914
                y: 30
                color: paletteAccent
                font.family: customFontLoader2.name
                font.pixelSize: 26
                font.weight: Font.Bold
                text: "Score"
            }
            // Weighted points header
            Text {
                id: weighted_Points_header_en
                x: 1042
                y: 30
                color: paletteAccent
                font.family: customFontLoader2.name
                font.pixelSize: 26
                font.weight: Font.Bold
                text: "Weighted Points"
            }

            Rectangle {
                anchors.bottom: parent.bottom
                x: 0
                width: parent.width
                height: 3
                color: palettePrimary
                opacity: 0.9
            }
        }
    }

    //-----------------------------------------------------------------
    // Podium - rebuilt without images, colored using the palette
    Item {
        id: podium
        x: 614
        height: 304
        width: 682

        // Bronze pedestal (right)
        Column {
            id: bronze_cell
            x: 466
            y: 139
            spacing: 6
            width: 216
            height: 165
            Rectangle {
                width: parent.width
                height: 110
                radius: 12
                color: "#B08B5B" // bronze hue
                border.color: paletteDark
                border.width: 2
            }
            Rectangle {
                width: parent.width
                height: 45
                radius: 6
                color: paletteSecondary
                border.color: paletteDark
                border.width: 1.5
                Text {
                    anchors.centerIn: parent
                    color: paletteLight
                    font.family: customFontLoader.name
                    font.pixelSize: 18
                    text: bronzeName
                }
            }
        }

        // Silver pedestal (left)
        Column {
            id: silver_cell
            x: 220
            y: 69
            spacing: 6
            width: 226
            height: 235
            Rectangle {
                width: parent.width
                height: 160
                radius: 12
                color: "#C0C0C0" // silver hue
                border.color: paletteDark
                border.width: 2
            }
            Rectangle {
                width: parent.width
                height: 60
                radius: 6
                color: paletteSecondary
                border.color: paletteDark
                border.width: 1.5
                Text {
                    anchors.centerIn: parent
                    color: paletteLight
                    font.family: customFontLoader.name
                    font.pixelSize: 18
                    text: silverName
                }
            }
        }

        // Gold pedestal (center)
        Column {
            id: gold_cell
            x: 325
            y: 20
            spacing: 6
            width: 246
            height: 304
            Rectangle {
                width: parent.width
                height: 196
                radius: 14
                color: "#FFD166" // gold hue
                border.color: paletteDark
                border.width: 2
            }
            Rectangle {
                width: parent.width
                height: 88
                radius: 6
                color: paletteSecondary
                border.color: paletteDark
                border.width: 1.5
                Text {
                    anchors.centerIn: parent
                    color: paletteLight
                    font.family: customFontLoader.name
                    font.pixelSize: 18
                    text: goldName
                }
            }
        }
    }

    //-----------------------------------------------------------------
    // Game title (right side)
    Item {
        id: game_title
        x: 1504
        y: 55
        height: 80
        width: 367

        Text {
            id: game_title_ar
            x: 66
            y: 45
            height: 35
            width: 301
            color: paletteLight
            font.capitalization: Font.AllUppercase
            font.family: customFontLoader2.name
            font.pixelSize: 50
            font.weight: Font.Bold
            horizontalAlignment: Text.AlignRight
            text: "رد فعل سريع"
            verticalAlignment: Text.AlignVCenter
        }
        Text {
            id: game_title_en
            height: 24
            width: 366
            color: paletteLight
            font.capitalization: Font.AllUppercase
            font.family: customFontLoader.name
            font.pixelSize: 45
            font.weight: Font.Black
            horizontalAlignment: Text.AlignRight
            text: "Fast Reaction"
            verticalAlignment: Text.AlignVCenter
        }
    }
}