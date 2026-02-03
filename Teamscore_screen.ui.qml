import QtQuick 2.12

Item {
    id: _teamscore_screen

    // Flexible resolution support
    property real baseWidth: 1920
    property real baseHeight: 1080
    property real scaleX: width / baseWidth
    property real scaleY: height / baseHeight
    property real scale: Math.min(scaleX, scaleY) // Maintain aspect ratio

    // Default to 4K resolution
    height: 2160
    width: 3840

    clip: true

    FontLoader {
        id: customFontLoader
        source: "Assets/Fonts/MyriadPro-Regular.otf"
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

    // Team score data properties for binding
    property string currentTeamName: "Team name"
    property string currentScoreValue: "10080"

    
   
    Item {
        id: logo

        x: 745
        y: 920

        height: 110
        width: 441

        Image {
            id: uxe_logo

            x: 330
            y: 35

            source: "Assets/uxe_logo.png"
        }
        Image {
            id: sira_logo

            x: 161

            source: "Assets/sira_logo.png"
        }
        Image {
            id: emarat_alaman_logo

            y: 7

            source: "Assets/emarat_alaman_logo.png"
        }
    }
    Item {
        id: popup

        x: 360
        y: 378

        height: 454
        width: 1201 

        Item {
            id: score

            x: 249
            y: 242

            height: 212
            width: 702

            Image {
                id: score_bg

                source: "Assets/score_bg.png"
            }
            Image {
                id: score_txt_bg

                x: 1
                y: 101

                source: "Assets/score_txt_bg.png"
            }
            Text {
                id: score_value

                x: 278
                y: 122

                height: 32
                width: 146

                color: "#ffffff"
                font.capitalization: Font.AllUppercase
                font.family: customFontLoader.name
                font.letterSpacing: 1.92
                font.pixelSize: 48
                font.weight: Font.Black
                horizontalAlignment: Text.AlignHCenter
                text: currentScoreValue
                verticalAlignment: Text.AlignVCenter
                
            }
            Image {
                id: element_1

                x: 565
                y: 36
                visible: false
                source: "Assets/element.png"
            }
            
            Image {
                id: score_1

                x: 293
                y: 36

                source: "Assets/score_2.png"
            }
            
        }
        Item {
            id: name

            height: 136
            width: 1201

            Image {
                id: team_name_bg

                source: "Assets/team_name_bg.png"
            }
            Text {
                id: team_name_value

                x: 426
                y: 49

                height: 38
                width: 349

                color: "#ffffff"
                font.capitalization: Font.AllUppercase
                font.family: customFontLoader.name
                font.letterSpacing: 3.92
                font.pixelSize: 56
                font.weight: Font.Black
                horizontalAlignment: Text.AlignHCenter
                text: currentTeamName
                verticalAlignment: Text.AlignVCenter
                // add stroke color 20% opacity outside the text
                style: Text.Outline
                styleColor: "#FFFFFF"
                opacity: 0.8
            }
            
            
        }
    }
    Item {
        id: team_performance

        x: 521
        y: 62

        height: 170
        width: 878

        Text {
            id: element_2

            x: 275

            height: 45
            width: 328
            visible: false
            color: "#fd8c01"
            font.capitalization: Font.AllUppercase
            font.family: customFontLoader.name
            font.letterSpacing: 5.12
            font.pixelSize: 64
            font.weight: Font.Bold
            horizontalAlignment: Text.AlignHCenter
            text: "أداء الفريق"
            verticalAlignment: Text.AlignVCenter
            
        }
        Text {
            id: team_Performance_1

            y: 116

            height: 54
            width: 878

            color: "#ffffff"
            font.capitalization: Font.AllUppercase
            font.family: customFontLoader.name
            font.letterSpacing: 5.60
            font.pixelSize: 80
            font.weight: Font.Black
            horizontalAlignment: Text.AlignHCenter
            text: "Team Performance"
            verticalAlignment: Text.AlignVCenter
            
        }
        
    }
    Item {
        id: mascot

        y: 467

        height: 563
        width: 486

        Image {
            id: mascot_stand

            y: 477

            source: "Assets/mascot_stand.png"
        }
        Image {
            id: mascot_3

            x: 82

            source: "Assets/mascot_3.png"
        }
        Image {
            id: stand_light

            x: 31
            y: 224

            source: "Assets/stand_light.png"
        }
    }

    // Connect backend signals when backend is set (following leaderboard pattern)
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
        console.log(`Updating team name: ${teamName}`)
        currentTeamName = teamName
    }

    function updateScoreValue(scoreValue) {
        console.log(`Updating score value: ${scoreValue}`)
        currentScoreValue = scoreValue
    }

    function updateTeamScore(teamName, scoreValue) {
        console.log(`Updating team score: ${teamName}, ${scoreValue}`)
        currentTeamName = teamName
        currentScoreValue = scoreValue
    }

    function refreshTeamScore() {
        console.log("Refreshing team score display")
        // Force property updates
        currentTeamName = currentTeamName
        currentScoreValue = currentScoreValue
    }
}