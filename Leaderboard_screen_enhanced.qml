import QtQuick 2.12
import QtQuick.Controls 2.12

Item {
    id: _leaderboard_screen
    width: 3840
    height: 2160
    clip: true
    visible: true

    // Palette colors
    property color colorPrimary: "#A85C4C"
    property color colorSecondary: "#A47864"
    property color colorLight: "#E0BFA2"
    property color colorAccent: "#984421"
    property color colorDark: "#77202E"
    property color colorText: "#FFFFFF"
    property color colorBg: "#1a1a1a"

    // Arabic/English toggle (auto)
    property bool isArabic: Qt.locale().textDirection === Qt.RightToLeft

    property var backend: null

    property ListModel playerData: ListModel {
        ListElement { name: "-"; score: 0; weighted_points: 0; rank: 1; org_type: "-" }
        ListElement { name: "-"; score: 0; weighted_points: 0; rank: 2; org_type: "-" }
        ListElement { name: "-"; score: 0; weighted_points: 0; rank: 3; org_type: "-" }
        ListElement { name: "-"; score: 0; weighted_points: 0; rank: 4; org_type: "-" }
        ListElement { name: "-"; score: 0; weighted_points: 0; rank: 5; org_type: "-" }
        ListElement { name: "-"; score: 0; weighted_points: 0; rank: 6; org_type: "-" }
        ListElement { name: "-"; score: 0; weighted_points: 0; rank: 7; org_type: "-" }
    }

    property string goldName: "-"
    property string silverName: "-"
    property string bronzeName: "-"
    property int goldScore: 0
    property int silverScore: 0
    property int bronzeScore: 0
    property int goldWeighted: 0
    property int silverWeighted: 0
    property int bronzeWeighted: 0

    property string lastPlayerName: "-"
    property int lastPlayerScore: 0
    property int lastPlayerWeighted: 0
    property int lastPlayerRank: 0

    onBackendChanged: {
        if (backend) {
            backend.playerTableNameUpdated.connect(updatePlayerTableName)
            backend.playerTableScoreUpdated.connect(updatePlayerTableScore)
            backend.playerTableWeightedUpdated.connect(updatePlayerTableWeighted)
            backend.playerTableRankUpdated.connect(updatePlayerTableRank)
            backend.goldPlayerUpdated.connect(updateGoldPlayer)
            backend.silverPlayerUpdated.connect(updateSilverPlayer)
            backend.bronzePlayerUpdated.connect(updateBronzePlayer)
            backend.lastPlayerNameUpdated.connect(updateLastPlayerName)
            backend.lastPlayerScoreUpdated.connect(updateLastPlayerScore)
            backend.lastPlayerWeightedUpdated.connect(updateLastPlayerWeighted)
            backend.lastPlayerRankUpdated.connect(updateLastPlayerRank)
        }
    }

    function updatePlayerTableName(index, name) {
        if (index >= 0 && index < playerData.count) {
            playerData.setProperty(index, "name", name)
        }
    }
    function updatePlayerTableScore(index, score) {
        if (index >= 0 && index < playerData.count) {
            playerData.setProperty(index, "score", score)
        }
    }
    function updatePlayerTableWeighted(index, weighted_points) {
        if (index >= 0 && index < playerData.count) {
            playerData.setProperty(index, "weighted_points", weighted_points)
        }
    }
    function updatePlayerTableRank(index, rank) {
        if (index >= 0 && index < playerData.count) {
            playerData.setProperty(index, "rank", rank)
        }
    }

    function updateGoldPlayer(name, score, weighted_points) {
        goldName = name
        goldScore = score
        goldWeighted = weighted_points
    }
    function updateSilverPlayer(name, score, weighted_points) {
        silverName = name
        silverScore = score
        silverWeighted = weighted_points
    }
    function updateBronzePlayer(name, score, weighted_points) {
        bronzeName = name
        bronzeScore = score
        bronzeWeighted = weighted_points
    }

    function updateLastPlayerName(name) { lastPlayerName = name }
    function updateLastPlayerScore(score) { lastPlayerScore = score }
    function updateLastPlayerWeighted(weighted_points) { lastPlayerWeighted = weighted_points }
    function updateLastPlayerRank(rank) { lastPlayerRank = rank }

    Image {
        anchors.fill: parent
        source: "Assets/1k/background.gif"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    Item {
        id: stage
        width: 1920
        height: 1080
        anchors.centerIn: parent
        z: 2

        property real scaleFactor: Math.min(_leaderboard_screen.width / 1920, _leaderboard_screen.height / 1080)
        scale: scaleFactor

        Rectangle {
            id: mainContainer
            width: 1280
            height: 760
            anchors.centerIn: parent
            radius: 12
            color: Qt.rgba(30 / 255, 15 / 255, 15 / 255, 0.92)
            border.color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.2)
            border.width: 1

            Row {
                anchors.fill: parent

                // Left panel (Top performers + Recent activity)
                Rectangle {
                    id: leftPanel
                    width: 384
                    height: parent.height
                    border.color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.15)
                    border.width: 1
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: Qt.rgba(119 / 255, 32 / 255, 46 / 255, 0.4) }
                        GradientStop { position: 1.0; color: Qt.rgba(152 / 255, 68 / 255, 33 / 255, 0.2) }
                    }

                    Column {
                        anchors.fill: parent
                        anchors.margins: 32
                        spacing: 16

                        Column {
                            spacing: 8
                            Text {
                                text: "Top Performers"
                                font.family: "Myriad Pro"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.5)
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 2
                            }
                        }

                        Column {
                            spacing: 16

                            // 1st place
                            Rectangle {
                                radius: 10
                                border.color: Qt.rgba(168 / 255, 92 / 255, 76 / 255, 0.4)
                                border.width: 1
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: Qt.rgba(168 / 255, 92 / 255, 76 / 255, 0.3) }
                                    GradientStop { position: 1.0; color: Qt.rgba(119 / 255, 32 / 255, 46 / 255, 0.2) }
                                }
                                height: 78
                                width: parent.width

                                Row {
                                    anchors.fill: parent
                                    anchors.margins: 16
                                    spacing: 16

                                    Rectangle {
                                        width: 45
                                        height: 45
                                        radius: 6
                                        gradient: Gradient {
                                            GradientStop { position: 0.0; color: colorPrimary }
                                            GradientStop { position: 1.0; color: colorDark }
                                        }
                                        Text {
                                            anchors.centerIn: parent
                                            text: "1"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 19
                                            font.weight: Font.Black
                                            color: colorLight
                                        }
                                    }

                                    Column {
                                        spacing: 3
                                        width: parent.width - 70
                                        Text {
                                            text: goldName
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 18
                                            font.weight: Font.Bold
                                            color: colorLight
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            text: goldScore + " points"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 11
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.6)
                                        }
                                    }
                                }
                            }

                            // 2nd place
                            Rectangle {
                                radius: 10
                                border.color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.1)
                                border.width: 1
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.05)
                                height: 70
                                width: parent.width

                                Row {
                                    anchors.fill: parent
                                    anchors.margins: 14
                                    spacing: 13

                                    Rectangle {
                                        width: 38
                                        height: 38
                                        radius: 6
                                        color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.1)
                                        border.color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.2)
                                        border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: "2"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 16
                                            font.weight: Font.Bold
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.7)
                                        }
                                    }

                                    Column {
                                        spacing: 2
                                        width: parent.width - 60
                                        Text {
                                            text: silverName
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 14
                                            font.weight: Font.DemiBold
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.9)
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            text: silverScore + " points"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 10
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.5)
                                        }
                                    }
                                }
                            }

                            // 3rd place
                            Rectangle {
                                radius: 10
                                border.color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.08)
                                border.width: 1
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.03)
                                height: 70
                                width: parent.width

                                Row {
                                    anchors.fill: parent
                                    anchors.margins: 14
                                    spacing: 13

                                    Rectangle {
                                        width: 38
                                        height: 38
                                        radius: 6
                                        color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.05)
                                        border.color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.1)
                                        border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: "3"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 16
                                            font.weight: Font.Bold
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.5)
                                        }
                                    }

                                    Column {
                                        spacing: 2
                                        width: parent.width - 60
                                        Text {
                                            text: bronzeName
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 14
                                            font.weight: Font.DemiBold
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.7)
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            text: bronzeScore + " points"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 10
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4)
                                        }
                                    }
                                }
                            }
                        }

                        Item { width: 1; height: 1 }

                        Column {
                            spacing: 8

                            Rectangle { width: parent.width; height: 1; color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.1) }

                            Text {
                                text: "Recent Activity"
                                font.family: "Myriad Pro"
                                font.pixelSize: 9
                                font.weight: Font.DemiBold
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4)
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 2
                            }

                            Text {
                                text: lastPlayerName
                                font.family: "Myriad Pro"
                                font.pixelSize: 13
                                font.weight: Font.DemiBold
                                color: colorLight
                                elide: Text.ElideRight
                            }

                            Row {
                                spacing: 19

                                Row {
                                    spacing: 4
                                    Text { text: "Score "; font.family: "Myriad Pro"; font.pixelSize: 10; color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4) }
                                    Text { text: lastPlayerScore; font.family: "Myriad Pro"; font.pixelSize: 11; font.weight: Font.DemiBold; color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.8) }
                                }

                                Row {
                                    spacing: 4
                                    Text { text: "Rank "; font.family: "Myriad Pro"; font.pixelSize: 10; color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4) }
                                    Text { text: "#" + lastPlayerRank; font.family: "Myriad Pro"; font.pixelSize: 11; font.weight: Font.DemiBold; color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.8) }
                                }
                            }
                        }
                    }
                }

                // Right panel (Leaderboard table)
                Item {
                    id: rightPanel
                    width: parent.width - leftPanel.width
                    height: parent.height

                    Column {
                        anchors.fill: parent
                        anchors.margins: 38
                        spacing: 16

                        Column {
                            spacing: 10
                            Text {
                                text: "LEADERBOARD"
                                font.family: "Myriad Pro"
                                font.pixelSize: 29
                                font.weight: Font.Black
                                color: colorLight
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 3
                            }
                            Rectangle {
                                width: 48
                                height: 2
                                radius: 2
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: colorPrimary }
                                    GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0) }
                                }
                            }
                        }

                        // Table header
                        Row {
                            width: parent.width
                            height: 32
                            spacing: 17

                            Text {
                                width: 81
                                text: "Rank"
                                font.family: "Myriad Pro"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4)
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 1
                            }
                            Text {
                                width: parent.width - 81 - 141 - 320 - 51
                                text: "Team"
                                font.family: "Myriad Pro"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4)
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 1
                            }
                            Text {
                                width: 141
                                text: "Score"
                                font.family: "Myriad Pro"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4)
                                horizontalAlignment: Text.AlignRight
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 1
                            }
                            Text {
                                width: 320
                                text: "Org Type"
                                font.family: "Myriad Pro"
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4)
                                horizontalAlignment: Text.AlignRight
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 1
                            }
                        }

                        Rectangle { width: parent.width; height: 1; color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.1) }

                        Column {
                            width: parent.width
                            spacing: 0

                            Repeater {
                                model: playerData
                                delegate: Item {
                                    width: parent.width
                                    height: 56

                                    Rectangle {
                                        anchors.fill: parent
                                        color: "transparent"
                                    }

                                    Row {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 17

                                        Text {
                                            width: 81
                                            text: (rank < 10 ? "0" + rank : rank)
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 18
                                            font.weight: rank <= 3 ? Font.Bold : Font.Medium
                                            color: rank <= 3 ? colorLight : Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.5)
                                        }
                                        Text {
                                            width: parent.width - 81 - 141 - 320 - 51
                                            text: name || "-"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 18
                                            font.weight: Font.DemiBold
                                            color: rank <= 3 ? colorLight : Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.7)
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            width: 141
                                            text: score
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 18
                                            font.weight: Font.DemiBold
                                            color: rank <= 3 ? colorPrimary : Qt.rgba(168 / 255, 92 / 255, 76 / 255, 0.6)
                                            horizontalAlignment: Text.AlignRight
                                        }
                                        Text {
                                            width: 320
                                            text: org_type || "-"
                                            font.family: "Myriad Pro"
                                            font.pixelSize: 18
                                            font.weight: Font.Medium
                                            color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.4)
                                            horizontalAlignment: Text.AlignRight
                                            elide: Text.ElideRight
                                        }
                                    }

                                    Rectangle {
                                        width: parent.width
                                        height: 1
                                        color: Qt.rgba(224 / 255, 191 / 255, 162 / 255, 0.05)
                                        anchors.bottom: parent.bottom
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}