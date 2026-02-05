import QtQuick 2.12

Item {
    id: _teamscore_screen

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

    // Backend property for receiving updates
    property var backend: null

    // Team score data properties for binding
    property string currentTeamName: "TEAM NAME"
    property int currentScoreValue: 0

    // Background
    Image {
        anchors.fill: parent
        source: "Assets/1k/dashboard-background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    // Scaled Stage (1920x1080)
    Item {
        id: stage
        width: 1920
        height: 1080
        anchors.centerIn: parent

        property real scaleFactor: {
            var w = _teamscore_screen.width
            var h = _teamscore_screen.height
            if (w <= 0 || h <= 0) return 1
            return Math.min(w / 1920, h / 1080)
        }
        scale: Math.max(0.01, scaleFactor)

        // Content centered vertically
        Column {
            anchors.centerIn: parent
            spacing: 40

            // Header Section
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 16

                // Top decorative line
                Rectangle {
                    width: 400
                    height: 3
                    radius: 2
                    anchors.horizontalCenter: parent.horizontalCenter
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.2; color: colorPrimary }
                        GradientStop { position: 0.5; color: colorDark }
                        GradientStop { position: 0.8; color: colorPrimary }
                        GradientStop { position: 1.0; color: "transparent" }
                    }
                }

                // Title
                Text {
                    text: "TEAM PERFORMANCE"
                    font.family: customFontLoader.name
                    font.pixelSize: 48
                    font.weight: Font.Black
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 8
                    color: colorDark
                    anchors.horizontalCenter: parent.horizontalCenter
                    horizontalAlignment: Text.AlignHCenter
                }

                // Bottom decorative line
                Rectangle {
                    width: 300
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

            // Main Score Card
            Rectangle {
                id: scoreCard
                width: Math.max(500, Math.min(900, teamNameLabel.implicitWidth + 160))
                height: 420
                radius: 32
                anchors.horizontalCenter: parent.horizontalCenter
                border.width: 4
                border.color: colorAccent

                gradient: Gradient {
                    GradientStop { position: 0.0; color: colorLight }
                    GradientStop { position: 1.0; color: colorSecondary }
                }

                Column {
                    anchors.centerIn: parent
                    spacing: 32

                    // Team Name Section
                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 8

                        // "Team" label
                        Text {
                            text: "TEAM"
                            font.family: customFontLoader.name
                            font.pixelSize: 20
                            font.weight: Font.DemiBold
                            font.capitalization: Font.AllUppercase
                            font.letterSpacing: 4
                            color: colorDark
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        // Team Name
                        Text {
                            id: teamNameLabel
                            text: currentTeamName
                            font.family: customFontLoader.name
                            font.pixelSize: currentTeamName.length > 15 ? 48 : 64
                            font.weight: Font.Black
                            font.capitalization: Font.AllUppercase
                            font.letterSpacing: currentTeamName.length > 15 ? 2 : 4
                            color: colorDark
                            anchors.horizontalCenter: parent.horizontalCenter
                            horizontalAlignment: Text.AlignHCenter
                            width: Math.min(implicitWidth, 800)
                            wrapMode: Text.WordWrap
                        }
                    }

                    // Divider
                    Rectangle {
                        width: scoreCard.width - 100
                        height: 3
                        radius: 2
                        anchors.horizontalCenter: parent.horizontalCenter
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 0.2; color: colorAccent }
                            GradientStop { position: 0.5; color: colorDark }
                            GradientStop { position: 0.8; color: colorAccent }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                    }

                    // Score Section
                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 12

                        // "Final Score" label
                        Text {
                            text: "FINAL SCORE"
                            font.family: customFontLoader.name
                            font.pixelSize: 24
                            font.weight: Font.DemiBold
                            font.capitalization: Font.AllUppercase
                            font.letterSpacing: 6
                            color: colorAccent
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        // Score Box
                        Rectangle {
                            width: 280
                            height: 140
                            radius: 24
                            anchors.horizontalCenter: parent.horizontalCenter
                            border.width: 3
                            border.color: colorLight

                            gradient: Gradient {
                                GradientStop { position: 0.0; color: colorDark }
                                GradientStop { position: 1.0; color: colorPrimary }
                            }

                            Text {
                                anchors.centerIn: parent
                                text: currentScoreValue
                                font.family: customFontLoader.name
                                font.pixelSize: 80
                                font.weight: Font.Black
                                font.letterSpacing: 4
                                color: colorLight
                            }
                        }
                    }
                }
            }
        }
    }

    // Connect backend signals when backend is set
    onBackendChanged: {
        if (backend) {
            console.log("Team score backend connected to QML")
            
            // Connect individual signals
            backend.teamNameChanged.connect(updateTeamName)
            backend.scoreValueChanged.connect(updateScoreValue)
            
            // Connect bulk update signal
            backend.teamScoreUpdated.connect(updateTeamScore)
            
            // Connect general signals
            backend.teamScoreDataUpdated.connect(refreshTeamScore)
        }
    }

    // Signal handlers for team score updates
    function updateTeamName(teamName) {
        console.log("Updating team name: " + teamName)
        currentTeamName = teamName
    }

    function updateScoreValue(scoreValue) {
        console.log("Updating score value: " + scoreValue)
        currentScoreValue = scoreValue
    }

    function updateTeamScore(teamName, scoreValue) {
        console.log("Updating team score: " + teamName + ", " + scoreValue)
        currentTeamName = teamName
        currentScoreValue = scoreValue
    }

    function refreshTeamScore() {
        console.log("Refreshing team score display")
        currentTeamName = currentTeamName
        currentScoreValue = currentScoreValue
    }
}