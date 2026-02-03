import QtQuick 2.12
import QtQuick.Shapes 1.0
import QtGraphicalEffects 1.0

Item {
    id: _Active_screen_FastReaction_2

    // Flexible resolution support
    property real baseWidth: 1920
    property real baseHeight: 1080
    property real scaleX: width / baseWidth
    property real scaleY: height / baseHeight
    property real scale: Math.min(scaleX, scaleY) // Maintain aspect ratio

    // Default to 4K resolution
    height: 2160
    width: 3840

    // Apply scaling transform
    transform: Scale {
        xScale: scale
        yScale: scale
        origin.x: 0
        origin.y: 0
    }

    // Backend property for dynamic updates
    property var backend: null
    property bool backendSettingInProgress: false
    
    // Debug backend connection
    onBackendChanged: {
        if (backendSettingInProgress) {
            console.log("Backend change ignored - setting in progress")
            return
        }
        
        console.log("=== QML DEBUG: Backend changed ===")
        console.log("Backend object:", backend)
        if (backend) {
            console.log("Backend connected successfully")
            console.log("Backend has correctCountChanged signal:", typeof backend.correctCountChanged)
            console.log("Backend has scoreChanged signal:", typeof backend.scoreChanged)
        } else {
            console.log("Backend is null, trying context property...")
            // Try to use context property as fallback
            if (typeof fastreactionBackend !== 'undefined' && fastreactionBackend !== null) {
                console.log("Using context property fastreactionBackend")
                backendSettingInProgress = true
                backend = fastreactionBackend
                backendSettingInProgress = false
            } else {
                console.log("Context property also unavailable")
            }
        }
    }
    
    // Also try to connect to context property on startup
    Component.onCompleted: {
        console.log("=== QML DEBUG: Component completed ===")
        console.log("Context property fastreactionBackend:", typeof fastreactionBackend)
        if (typeof fastreactionBackend !== 'undefined' && !backend) {
            console.log("Setting backend from context property")
            backend = fastreactionBackend
        }
    }
    
    // Timer to prevent infinite backend setting loops
    Timer {
        id: backendRetryTimer
        interval: 1000
        repeat: false
        onTriggered: {
            if (!backend && typeof fastreactionBackend !== 'undefined' && fastreactionBackend !== null) {
                console.log("Retrying backend connection after timeout")
                backendSettingInProgress = true
                backend = fastreactionBackend
                backendSettingInProgress = false
            }
        }
    }
    
    // Properties for dynamic values
    property string currentCorrectCount: "0"
    property string currentWrongCount: "0"
    property string currentMissCount: "0"
    property string currentTime: "02:01"
    property string currentScore: "2300"
    property string currentTeamName: "Team Name"

    
    clip: true

    FontLoader {
        id: customFontLoader
        source: "Assets/Fonts/MyriadPro-Regular.otf"
    }

    
    // mascot left
    Item {
        id: mascot_l

        x: -3
        y: 684.66

        height: 361.34
        width: 314

        Image {
            id: mascot_stand

            y: 306.21

            source: "Assets/mascot_stand_5.png"
        }
        Image {
            id: mascot

            x: 74.31

            source: "Assets/mascot_5.png"
        }
        Image {
            id: stand_light

            x: 19.77
            y: 142.02

            source: "Assets/stand_light_5.png"
        }
    }
    // logo
    Item {
        id: logo

        x: 740
        y: 919

        height: 110
        width: 441

        Image {
            id: uxe_logo

            x: 330
            y: 35

            source: "Assets/uxe_logo_4.png"
        }
        Image {
            id: sira_logo

            x: 161

            source: "Assets/sira_logo_4.png"
        }
        Image {
            id: emarat_alaman_logo

            y: 7

            source: "Assets/emarat_alaman_logo_4.png"
        }
    }
    // team name
    Text {
        id: team_Name
        // increase width but keep it centered in  the screen
        x: 0
        y: 70
        width: 1920
        height: 116

        text: currentTeamName
        color: "#FFFFFF"
        font.family: customFontLoader.name
        font.weight: Font.Black
        font.pixelSize: 80
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        style: Text.Outline
        styleColor: "#091B73"
         layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 6
            verticalOffset: 4
            radius: 4
            samples: 17
            color: "#091B73"
        }
    }
    // time
    Text {
        id: _time

        x: 771.55
        y: 331.16
        width: 380
        height: 116

        text: currentTime
        color: "#FFFFFF"
        font.family: customFontLoader.name
        font.weight: Font.Black
        font.pixelSize: 130
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        style: Text.Outline
        styleColor: "#091B73"
        
        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 6
            verticalOffset: 4
            radius: 4
            samples: 17
            color: "#091B73"
        }

        
    }
    
    // score
    Text {
        id: score

        x: 0
        y: 500
        width: 1920
        height: 100

        text: "Score: " + currentScore
        color: "#FFFFFF"
        font.family: customFontLoader.name
        font.weight: Font.Black
        font.pixelSize: 78
        font.pointSize: 78
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        style: Text.Outline
        styleColor: "#091B73"
         layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 6
            verticalOffset: 4
            radius: 4
            samples: 17
            color: "#091B73"
        }
    }
    // correct button image
    Image{
                id: correct_Button

                x: 513
                y: 704

                height: 166
                width: 218

                source: "Assets/Correct_Button.png"
            }
    // Miss button image
    Image{
                id: miss_Button

                x: 1186
                y: 704

                height: 166
                width: 218

                source: "Assets/Miss_Button.png"
            }
    // Wrong button image
    Image{
                id: wrong_Button

                x: 849
                y: 704

                height: 166
                width: 218
                source: "Assets/Wrong_Button.png"
            }
    Item {
        id: buttons

        x: 513
        y: 631

        height: 288
        width: 896

        Item {
            id: correct

            height: 279.25
            width: 218.30

            Text {
                id: correct_text

                x: 40.74
                y: 236.55

                height: 48.69
                width: 133.17

                color: "#9ff09e"
                font.family: customFontLoader.name
                font.pixelSize: 30
                font.weight: Font.Bold
                horizontalAlignment: Text.Center
                lineHeight: 36
                lineHeightMode: Text.FixedHeight
                text: "Correct"
                verticalAlignment: Text.AlignTop
            }
            Text {
                id: num_of_Correct

                x: 74.53

                height: 48.69
                width: 64.60

                color: "#9ff09e"
                font.family: customFontLoader.name
                font.pixelSize: 45
                font.weight: Font.Bold
                horizontalAlignment: Text.Center
                lineHeight: 36
                lineHeightMode: Text.FixedHeight
                text: currentCorrectCount
                verticalAlignment: Text.AlignTop
            }
        }
        // correct button image
        
        Item {
            id: wrong

            x: 336.08
            y: 0.90

            height: 285.79
            width: 219.20

            Text {
                id: wrong_text

                x: 51.92
                y: 236.10

                height: 49.69
                width: 120.25

                color: "#fba6a8"
                font.family: customFontLoader.name
                font.pixelSize: 30
                font.weight: Font.Bold
                horizontalAlignment: Text.Center
                lineHeight: 36
                lineHeightMode: Text.FixedHeight
                text: "Wrong"
                verticalAlignment: Text.AlignTop
            }
            Text {
                id: num_of_Wrong

                x: 74.53

                height: 49.69
                width: 64.60

                color: "#fba6a8"
                font.family: customFontLoader.name
                font.pixelSize: 45
                font.weight: Font.Bold
                horizontalAlignment: Text.Center
                lineHeight: 36
                lineHeightMode: Text.FixedHeight
                text: currentWrongCount
                verticalAlignment: Text.AlignTop
            }
            
        }
        Item {
            id: miss

            x: 673.13
            y: 1.79

            height: 286.21
            width: 222.87

            Text {
                id: miss_text

                x: 68.57
                y: 236.52

                height: 49.69
                width: 80.50

                color: "#fec476"
                font.family: customFontLoader.name
                font.pixelSize: 30
                font.weight: Font.Bold
                horizontalAlignment: Text.Center
                lineHeight: 36
                lineHeightMode: Text.FixedHeight
                text: "Miss"
                verticalAlignment: Text.AlignTop
            }
            Text {
                id: num_of_Miss

                x: 74.53

                height: 49.69
                width: 69.56

                color: "#fec476"
                font.family: customFontLoader.name
                font.pixelSize: 45
                font.weight: Font.Bold
                horizontalAlignment: Text.Center
                lineHeight: 36
                lineHeightMode: Text.FixedHeight
                text: currentMissCount
                verticalAlignment: Text.AlignTop
            }
            // Item {
            //     id: miss_Button

            //     y: 68.88

            //     height: 169.94
            //     width: 222.87

            //     clip: true

            //     Item {
            //         id: clip_path_group_2

            //         x: 0.23

            //         height: 166.34
            //         width: 218.81

            //         Item {
            //             id: d8ab7edf

            //             height: 166.34
            //             width: 218.81

            //             Shape {
            //                 id: _vector_2

            //                 height: 166.34
            //                 width: 218.81

            //                 ShapePath {
            //                     id: _vector_2_ShapePath0

            //                     fillColor: "#000000"
            //                     fillRule: ShapePath.WindingFill
            //                     strokeColor: "transparent"
            //                     strokeWidth: 1.33

            //                     PathSvg {
            //                         id: _vector_2_ShapePath0_PathSvg0

            //                         path: "M 0 0 L 218.8083038330078 0 L 218.8083038330078 166.34132385253906 L 0 166.34132385253906 L 0 0 Z"
            //                     }
            //                 }
            //             }
            //         }
            //         Item {
            //             id: group_22

            //             x: -71.80
            //             y: -98.65

            //             height: 358.60
            //             width: 359.64

            //             Item {
            //                 id: mask_group_4

            //                 height: 358.60
            //                 width: 359.64

            //                 Item {
            //                     id: group_23

            //                     height: 358.60
            //                     width: 359.64

            //                     Item {
            //                         id: group_24

            //                         height: 358.60
            //                         width: 359.64

            //                         Item {
            //                             id: group_25

            //                             height: 358.60
            //                             width: 359.64

            //                             Image {
            //                                 id: rectangle_8

            //                                 source: "Assets/rectangle_20.png"
            //                             }
            //                         }
            //                     }
            //                 }
            //                 Item {
            //                     id: group_26

            //                     height: 358.60
            //                     width: 359.64

            //                     Item {
            //                         id: group_27

            //                         height: 358.60
            //                         width: 359.64

            //                         Image {
            //                             id: rectangle_9

            //                             source: "Assets/rectangle_21.png"
            //                         }
            //                     }
            //                 }
            //             }
            //             Item {
            //                 id: mask_group_5

            //                 height: 358.60
            //                 width: 359.64

            //                 Item {
            //                     id: group_28

            //                     height: 358.60
            //                     width: 359.64

            //                     Item {
            //                         id: group_29

            //                         height: 358.60
            //                         width: 359.64

            //                         Item {
            //                             id: group_30

            //                             height: 358.60
            //                             width: 359.64

            //                             Image {
            //                                 id: rectangle_10

            //                                 source: "Assets/rectangle_22.png"
            //                             }
            //                         }
            //                     }
            //                 }
            //                 Item {
            //                     id: group_31

            //                     height: 358.60
            //                     width: 359.64

            //                     Item {
            //                         id: group_32

            //                         height: 358.60
            //                         width: 359.64

            //                         Image {
            //                             id: rectangle_11

            //                             source: "Assets/rectangle_23.png"
            //                         }
            //                     }
            //                 }
            //             }
            //         }
            //     }
            // }
        }
    }
    // Connect backend signals to update properties
    Connections {
        target: backend
        enabled: backend !== null
        function onCorrectCountChanged(correctCount) {
            console.log("=== QML DEBUG: correctCountChanged signal received ===")
            console.log("Received correctCount:", correctCount)
            console.log("Current currentCorrectCount:", currentCorrectCount)
            currentCorrectCount = correctCount
            console.log("Updated currentCorrectCount to:", currentCorrectCount)
            console.log("Correct count updated:", correctCount)
        }
        function onWrongCountChanged(wrongCount) {
            console.log("=== QML DEBUG: wrongCountChanged signal received ===")
            console.log("Received wrongCount:", wrongCount)
            currentWrongCount = wrongCount
            console.log("Wrong count updated:", wrongCount)
        }
        function onMissCountChanged(missCount) {
            console.log("=== QML DEBUG: missCountChanged signal received ===")
            console.log("Received missCount:", missCount)
            currentMissCount = missCount
            console.log("Miss count updated:", missCount)
        }
        function onScoreChanged(score) {
            console.log("=== QML DEBUG: scoreChanged signal received ===")
            console.log("Received score:", score)
            console.log("Current currentScore:", currentScore)
            currentScore = score
            console.log("Updated currentScore to:", currentScore)
            console.log("Score updated:", score)
        }
        function onTeamNameChanged(teamName) {
            console.log("=== QML DEBUG: teamNameChanged signal received ===")
            console.log("Received teamName:", teamName)
            currentTeamName = teamName
            console.log("Team name updated:", teamName)
        }
        function onTimeChanged(time) {
            console.log("=== QML DEBUG: timeChanged signal received ===")
            console.log("Received time:", time)
            currentTime = time
            console.log("Time display updated:", time)
        }
        // Timer control signals
        function onTimerValueChanged(seconds, progress) {
            // Update timer display - this ensures QML stays in sync
            console.log(`Timer value changed: ${seconds}s, Progress: ${progress}%`)
            // Force update of time display - use safe method
            if (backend && typeof backend.get_time_value === 'function') {
                var timeValue = backend.get_time_value()
                if (timeValue !== undefined && timeValue !== null) {
                    currentTime = timeValue
                }
            }
        }
        function onCountdownStarted() {
            console.log("Countdown started in QML")
            // Ensure timer display is updated when countdown starts
            if (backend && typeof backend.get_time_value === 'function') {
                var timeValue = backend.get_time_value()
                if (timeValue !== undefined && timeValue !== null) {
                    currentTime = timeValue
                }
            }
        }
        function onCountdownStopped() {
            console.log("Countdown stopped in QML")
        }
    }
}