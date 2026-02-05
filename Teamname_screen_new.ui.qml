import QtQuick 2.12

Item {
    id: _teamname_screen_new

    implicitWidth: 1920
    implicitHeight: 1080
    clip: true

    // Palette colors (matching React)
    property color colorPrimary: "#A85C4C"
    property color colorSecondary: "#A47864"
    property color colorLight: "#E0BFA2"
    property color colorDark: "#77202E"
    property color colorAccent: "#984421"

    FontLoader {
        id: customFontLoader
        source: "Assets/Fonts/MyriadPro-Regular.otf"
    }

    // Backend property for receiving updates (set from Python)
    property var backend: null

    // Local player state (names and avatar sources)
    property var players: [
        { name: "Player 1", avatar: "Assets/avatar_img_1@2x.png" },
        { name: "Player 2", avatar: "Assets/avatar_img_2@2x.png" },
        { name: "Player 3", avatar: "Assets/avatar_img_3@2x.png" },
        { name: "Player 4", avatar: "Assets/avatar_img_4@2x.png" }
    ]

    property string teamNameText: "TEAM NAME"

    // Update handlers bound to backend signals
    onBackendChanged: {
        if (backend) {
            console.log("Teamname backend connected to QML")
            if (backend.teamNameArUpdated)
                backend.teamNameArUpdated.connect(function(team_name_ar) { /* Arabic support if needed */ })
            if (backend.teamNameEnUpdated)
                backend.teamNameEnUpdated.connect(function(team_name_en) { teamNameText = team_name_en })
            backend.playerNameUpdated.connect(function(index, name) {
                if (index >= 0 && index < players.length) {
                    players[index].name = name
                    refreshPlayers()
                }
            })
            backend.playerAvatarUpdated.connect(function(index, avatar_source) {
                if (index >= 0 && index < players.length) {
                    players[index].avatar = avatar_source
                    refreshPlayers()
                }
            })
            backend.allPlayersUpdated.connect(function(p) {
                if (p && p.length === 4) {
                    players = p
                    refreshPlayers()
                }
            })
        }
    }

    function refreshPlayers() {
        players = players.slice()
    }

    // Background is handled by Python (QMovie GIF), so no need for QML background image
    // This prevents duplicate background loading

    // Scaled Stage (1920x1080)
    Item {
        id: stage
        width: 1920
        height: 1080
        anchors.centerIn: parent

        property real scaleFactor: {
            var w = _teamname_screen_new.width
            var h = _teamname_screen_new.height
            if (w <= 0 || h <= 0) return 1
            return Math.min(w / 1920, h / 1080)
        }
        scale: Math.max(0.01, scaleFactor)

        // Team Name Header Section (top: 334px - lowered by 5% screen height)
        Item {
            id: teamNameHeader
            width: parent.width
            height: 200
            y: 334
            
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 16

                // Top decorative line
                // Rectangle {
                //     width: 600
                //     height: 3
                //     radius: 2
                //     anchors.horizontalCenter: parent.horizontalCenter
                //     gradient: Gradient {
                //         orientation: Gradient.Horizontal
                //         GradientStop { position: 0.0; color: "transparent" }
                //         GradientStop { position: 0.2; color: colorPrimary }
                //         GradientStop { position: 0.5; color: colorDark }
                //         GradientStop { position: 0.8; color: colorPrimary }
                //         GradientStop { position: 1.0; color: "transparent" }
                //     }
                // }

                // Team Name
                Text {
                    id: teamNameLabel
                    text: teamNameText
                    font.family: customFontLoader.name
                    font.pixelSize: 72
                    font.weight: Font.Black
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 8
                    color: colorDark
                    anchors.horizontalCenter: parent.horizontalCenter
                    horizontalAlignment: Text.AlignHCenter
                    
                    style: Text.Outline
                    styleColor: colorAccent
                }

                // Subtitle "Players"
                Text {
                    text: "PLAYERS"
                    font.family: customFontLoader.name
                    font.pixelSize: 24
                    font.weight: Font.DemiBold
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 6
                    color: colorSecondary
                    anchors.horizontalCenter: parent.horizontalCenter
                    horizontalAlignment: Text.AlignHCenter
                }

                // Bottom decorative line
                Rectangle {
                    width: 400
                    height: 2
                    radius: 2
                    anchors.horizontalCenter: parent.horizontalCenter
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.3; color: colorSecondary }
                        GradientStop { position: 0.7; color: colorSecondary }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }
            }
        }

        // Player Cards Container (top: 540px)
        Item {
            id: playerCardsContainer
            width: parent.width
            height: 400
            y: 540

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 40

                Repeater {
                    model: 4

                    // Player Card
                    Rectangle {
                        id: playerCard
                        width: 260
                        height: 280
                        radius: 24
                        // border.width: 3
                        // border.color: colorAccent

                        gradient: Gradient {
                            GradientStop { position: 0.0; color: colorLight }
                            GradientStop { position: 1.0; color: colorSecondary }
                        }

                        Column {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 24
                            spacing: 0

                            // Avatar with ring
                            Item {
                                width: 140
                                height: 140
                                anchors.horizontalCenter: parent.horizontalCenter

                                // Outer gradient ring
                                Rectangle {
                                    anchors.fill: parent
                                    radius: 70
                                    gradient: Gradient {
                                        GradientStop { position: 0.0; color: colorDark }
                                        GradientStop { position: 0.5; color: colorPrimary }
                                        GradientStop { position: 1.0; color: colorDark }
                                    }

                                    // Inner border
                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 130
                                        height: 130
                                        radius: 65
                                        color: "transparent"
                                        border.width: 3
                                        border.color: colorLight

                                        // Avatar image container
                                        Rectangle {
                                            anchors.fill: parent
                                            anchors.margins: 3
                                            radius: 62
                                            clip: true
                                            color: "#333"

                                            Image {
                                                anchors.fill: parent
                                                source: players[index] ? players[index].avatar : ("Assets/avatar_img_" + (index + 1) + "@2x.png")
                                                fillMode: Image.PreserveAspectCrop
                                                asynchronous: true
                                            }
                                        }
                                    }
                                }
                            }

                            // Spacer
                            Item { width: 1; height: 20 }

                            // Divider
                            Rectangle {
                                width: 208
                                height: 2
                                radius: 1
                                anchors.horizontalCenter: parent.horizontalCenter
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: "transparent" }
                                    GradientStop { position: 0.5; color: colorAccent }
                                    GradientStop { position: 1.0; color: "transparent" }
                                }
                            }

                            // Spacer
                            Item { width: 1; height: 16 }

                            // Player Name
                            Text {
                                width: 220
                                text: players[index] ? players[index].name : ("Player " + (index + 1))
                                font.family: customFontLoader.name
                                font.pixelSize: 24
                                font.weight: Font.Black
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 1.5
                                color: colorDark
                                horizontalAlignment: Text.AlignHCenter
                                anchors.horizontalCenter: parent.horizontalCenter
                                elide: Text.ElideRight
                            }
                        }

                        // Player Number Badge (top-right corner)
                        Rectangle {
                            width: 36
                            height: 36
                            radius: 18
                            color: colorDark
                            border.width: 2
                            border.color: colorLight
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.rightMargin: 8
                            anchors.topMargin: 8

                            Text {
                                anchors.centerIn: parent
                                text: (index + 1)
                                font.family: customFontLoader.name
                                font.pixelSize: 18
                                font.weight: Font.Black
                                color: colorLight
                            }
                        }
                    }
                }
            }
        }
    }
}