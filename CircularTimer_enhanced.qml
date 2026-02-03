// CircularTimer_qt212_full.qml
import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12

Item {
    id: root
    width: 600
    height: 600
    focus: true

    /* ------------------------------------------------------------
       CONFIG: enable demoMode = true to see animations without backend
       Set demoMode = false when you attach a backend from Python.
       ------------------------------------------------------------ */
    property bool demoMode: false
    property int timerSeconds: 60
    property real progressValue: 0.0
    property bool isRunning: false
    property QtObject backend
    property int previousSeconds: 60

    property real baseSize: 400
    property real scaleFactor: Math.min(width / baseSize, height / baseSize)
    property real timerSize: Math.min(width * 0.75, height * 0.75)

    // safe screenWidth fallback
    property int screenWidth: (typeof Screen !== "undefined" && Screen.width) ? Screen.width : 1920
    property real screenScale: {
        if (screenWidth >= 3840) return 1.3
        else if (screenWidth >= 2560) return 1.2
        else if (screenWidth >= 1920) return 1.0
        else return 0.8
    }

    readonly property color oxfordBlue: "#0C1936"
    readonly property color uclaBlue: "#4574AD"
    readonly property color oxfordBlue2: "#1B2437"
    readonly property color oxfordBlue3: "#0D1D3C"
    readonly property color yinmnBlue: "#48536D"
    readonly property color lightBlue: "#b3dcff"
    readonly property color urgencyRed: "#bd4e45"

    // FontLoader (optional - safe if file missing)
    FontLoader {
        id: customFontLoader
        source: "Assets/Fonts/good_times_rg.ttf"
    }

    // --- Backend connections ---
    Connections {
        target: backend
        onTimerValueChanged: function(seconds, progress) {
            // only update if backend triggers it
            previousSeconds = timerSeconds;
            timerSeconds = seconds;
            progressValue = progress;
            // trigger animations
            if (isRunning && seconds !== previousSeconds) {
                numberAnimation.start();
                rippleEffect.start();
                if (seconds <= 10 && seconds > 0) warningPulse.start();
                if (seconds === 0) gameOverEffect.start();
            }
        }
        onCountdownStarted: function() {
            isRunning = true;
            startAnimation.start();
            // ensure canvas repaints
            gradientAnimationTimer.running = true;
        }
        onCountdownStopped: function() {
            isRunning = false;
            stopAnimation.start();
            // stop canvas repaints if not demo
            if (!demoMode) gradientAnimationTimer.running = false;
        }
    }

    Component.onCompleted: {
        // If demoMode enabled, start a fake countdown so you can see everything
        if (demoMode) {
            timerSeconds = 15; // short demo
            progressValue = 0;
            isRunning = true;
            fakeCountdown.start();
            gradientAnimationTimer.running = true;
            startAnimation.start();
        } else {
            // if there's a backend, ask it to start (safe-call)
            if (backend && backend.start_countdown) {
                // don't force-start; backend will control lifecycle
            }
        }
    }

    Keys.onPressed: {
        if (event.key === Qt.Key_S) {
            if (isRunning) {
                isRunning = false;
                if (backend && backend.stop_countdown) backend.stop_countdown();
                stopAnimation.start();
                if (!demoMode) gradientAnimationTimer.running = false;
            } else {
                isRunning = true;
                if (backend && backend.start_countdown) backend.start_countdown();
                startAnimation.start();
                gradientAnimationTimer.running = true;
            }
            event.accepted = true;
        }
    }

    // --- MAIN TIMER CONTAINER ---
    Rectangle {
        id: timerContainer
        width: timerSize
        height: timerSize
        anchors.centerIn: parent
        color: "transparent"
        radius: width / 2

        transform: [
            Scale { id: containerScale; origin.x: timerContainer.width/2; origin.y: timerContainer.height/2; xScale:1.0; yScale:1.0 },
            Translate { id: containerShake; x:0; y:0 }
        ]

        // Background ring
        Rectangle {
            anchors.fill: parent
            radius: width / 2
            color: "transparent"
            border.color: timerSeconds <= 10 ? urgencyRed : uclaBlue
            border.width: Math.max(4, 6 * scaleFactor)
            opacity: 0.3
            Behavior on border.color { ColorAnimation { duration: 300 } }
        }

        // Ripples
        Rectangle { id: ripple1; anchors.centerIn: parent; width:0; height:0; radius: width/2;
                   color: "transparent"; border.width: Math.max(2,3*scaleFactor); opacity:0;
                   border.color: timerSeconds <= 10 ? urgencyRed : uclaBlue;
                   Behavior on border.color { ColorAnimation { duration: 300 } } }
        Rectangle { id: ripple2; anchors.centerIn: parent; width:0; height:0; radius: width/2;
                   color: "transparent"; border.width: Math.max(2,3*scaleFactor); opacity:0;
                   border.color: timerSeconds <= 10 ? Qt.lighter(urgencyRed,1.2) : yinmnBlue;
                   Behavior on border.color { ColorAnimation { duration: 300 } } }
        Rectangle { id: ripple3; anchors.centerIn: parent; width:0; height:0; radius: width/2;
                   color: "transparent"; border.width: Math.max(2,3*scaleFactor); opacity:0;
                   border.color: timerSeconds <= 10 ? Qt.darker(urgencyRed,1.1) : oxfordBlue2;
                   Behavior on border.color { ColorAnimation { duration: 300 } } }

        // Canvas for progress + gradients
        Canvas {
            id: progressCanvas
            anchors.fill: parent

            property real glowIntensity: isRunning ? 0.6 : 0.3
            property real pulseScale: 1.0

            transform: [
                Rotation { id: canvasRotation; origin.x: progressCanvas.width/2; origin.y: progressCanvas.height/2; angle:0 },
                Scale { id: canvasPulse; origin.x: progressCanvas.width/2; origin.y: progressCanvas.height/2; xScale: progressCanvas.pulseScale; yScale: progressCanvas.pulseScale }
            ]

            // pulse animation manually started/stopped by isRunning
            SequentialAnimation on pulseScale {
                loops: Animation.Infinite
                running: isRunning
                NumberAnimation { from:1.0; to:1.03; duration:1500; easing.type: Easing.InOutSine }
                NumberAnimation { from:1.03; to:1.0; duration:1500; easing.type: Easing.InOutSine }
            }

            Behavior on glowIntensity { NumberAnimation { duration: 500; easing.type: Easing.InOutQuad } }

            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0,0,width,height);

                var centerX = width/2;
                var centerY = height/2;
                var radius = (width - (20 * scaleFactor)) / 2;
                var startAngle = -Math.PI/2;
                var progressAngle = (progressValue / 100) * 2 * Math.PI;

                // Background track
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, 0, 2*Math.PI);
                ctx.lineWidth = Math.max(8, 12*scaleFactor);
                ctx.strokeStyle = Qt.rgba(0.1,0.1,0.2,0.3);
                ctx.stroke();

                // Outer glow
                if (glowIntensity > 0) {
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, radius + (4*scaleFactor), startAngle, startAngle + progressAngle);
                    ctx.lineWidth = Math.max(6, 8*scaleFactor);
                    ctx.strokeStyle = Qt.rgba(0.27,0.45,0.68, glowIntensity * 0.4);
                    ctx.stroke();
                }

                // Gradient
                var gradient = ctx.createLinearGradient(centerX - radius, centerY - radius, centerX + radius, centerY + radius);
                var time = Date.now() * 0.001;
                var gradientOffset = (time * 0.8) % 1.0;
                var baseColor, lighterColor, darkerColor, midColor;

                if (timerSeconds <= 10) {
                    baseColor = urgencyRed;
                    lighterColor = Qt.lighter(baseColor,1.4);
                    darkerColor = Qt.darker(baseColor,1.3);
                    midColor = Qt.lighter(baseColor,1.1);
                } else {
                    baseColor = uclaBlue;
                    lighterColor = Qt.lighter(baseColor,1.4);
                    darkerColor = Qt.darker(baseColor,1.3);
                    midColor = Qt.lighter(baseColor,1.1);
                }

                gradient.addColorStop((gradientOffset + 0.0) % 1.0, lighterColor);
                gradient.addColorStop((gradientOffset + 0.2) % 1.0, baseColor);
                gradient.addColorStop((gradientOffset + 0.4) % 1.0, midColor);
                gradient.addColorStop((gradientOffset + 0.6) % 1.0, darkerColor);
                gradient.addColorStop((gradientOffset + 0.8) % 1.0, baseColor);
                gradient.addColorStop((gradientOffset + 1.0) % 1.0, lighterColor);

                // Main progress arc
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, startAngle, startAngle + progressAngle);
                ctx.lineWidth = Math.max(12, 18 * scaleFactor);
                ctx.strokeStyle = gradient;
                ctx.lineCap = "round";
                ctx.stroke();

                // Inner highlight gradient
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, startAngle, startAngle + progressAngle);
                ctx.lineWidth = Math.max(4, 6 * scaleFactor);
                var highlightGradient = ctx.createLinearGradient(centerX - radius, centerY - radius, centerX + radius, centerY + radius);
                var highlightOffset = (time * 1.2) % 1.0;
                var highlightBaseColor, highlightLighterColor, highlightDarkerColor;
                if (timerSeconds <= 10) {
                    highlightBaseColor = Qt.lighter(urgencyRed,1.6);
                    highlightLighterColor = Qt.lighter(highlightBaseColor,1.3);
                    highlightDarkerColor = Qt.darker(highlightBaseColor,1.2);
                } else {
                    highlightBaseColor = Qt.lighter(uclaBlue,1.6);
                    highlightLighterColor = Qt.lighter(highlightBaseColor,1.3);
                    highlightDarkerColor = Qt.darker(highlightBaseColor,1.2);
                }
                highlightGradient.addColorStop((highlightOffset + 0.0) % 1.0, highlightLighterColor);
                highlightGradient.addColorStop((highlightOffset + 0.3) % 1.0, highlightBaseColor);
                highlightGradient.addColorStop((highlightOffset + 0.6) % 1.0, highlightDarkerColor);
                highlightGradient.addColorStop((highlightOffset + 0.9) % 1.0, highlightBaseColor);
                ctx.strokeStyle = highlightGradient;
                ctx.lineCap = "round";
                ctx.stroke();

                // Progress indicator dot
                if (progressAngle > 0.1) {
                    var dotX = centerX + radius * Math.cos(startAngle + progressAngle);
                    var dotY = centerY + radius * Math.sin(startAngle + progressAngle);
                    var dotGradient = ctx.createRadialGradient(dotX - Math.max(2,3*scaleFactor), dotY - Math.max(2,3*scaleFactor), 0, dotX, dotY, Math.max(4,6*scaleFactor));
                    var dotOffset = (time * 1.5) % 1.0;
                    var dotBaseColor, dotLighterColor, dotDarkerColor, dotCenterColor;
                    if (timerSeconds <= 10) {
                        dotBaseColor = urgencyRed;
                        dotLighterColor = Qt.lighter(dotBaseColor,1.5);
                        dotDarkerColor = Qt.darker(dotBaseColor,1.3);
                        dotCenterColor = Qt.lighter(dotBaseColor,1.2);
                    } else {
                        dotBaseColor = uclaBlue;
                        dotLighterColor = Qt.lighter(dotBaseColor,1.5);
                        dotDarkerColor = Qt.darker(dotBaseColor,1.3);
                        dotCenterColor = Qt.lighter(dotBaseColor,1.2);
                    }
                    dotGradient.addColorStop(0.0, dotLighterColor);
                    dotGradient.addColorStop(0.3, dotCenterColor);
                    dotGradient.addColorStop(0.7, dotBaseColor);
                    dotGradient.addColorStop(1.0, dotDarkerColor);

                    ctx.beginPath();
                    ctx.arc(dotX, dotY, Math.max(4,6*scaleFactor), 0, 2*Math.PI);
                    ctx.fillStyle = dotGradient;
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(dotX, dotY, Math.max(2,3*scaleFactor), 0, 2*Math.PI);
                    ctx.fillStyle = Qt.lighter(dotBaseColor,1.4);
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(dotX - Math.max(1,1.5*scaleFactor), dotY - Math.max(1,1.5*scaleFactor), Math.max(1,1.5*scaleFactor), 0, 2*Math.PI);
                    ctx.fillStyle = Qt.rgba(1,1,1,0.8);
                    ctx.fill();
                }
            }
        }

        // Force repaint timer for Canvas - runs when isRunning or demoMode
        Timer {
            id: gradientAnimationTimer
            interval: 50
            running: isRunning || demoMode
            repeat: true
            onTriggered: progressCanvas.requestPaint()
        }

        // Timer text
        Text {
            id: timerText
            text: formatTime(timerSeconds)
            font.family: customFontLoader.name
            font.pixelSize: Math.max(24, 48 * scaleFactor)
            font.bold: true
            color: timerSeconds <= 10 ? urgencyRed : Qt.lighter(uclaBlue, 1.5)
            anchors.centerIn: parent
            renderType: Text.NativeRendering
            antialiasing: true

            transform: [
                Scale { id: textScale; origin.x: timerText.width/2; origin.y: timerText.height/2; xScale:1.0; yScale:1.0 },
                Rotation { id: textRotation; origin.x: timerText.width/2; origin.y: timerText.height/2; angle:0 }
            ]

            Behavior on color { ColorAnimation { duration: 300 } }
        }
    } // timerContainer

    // =========== ANIMATIONS ===========

    ParallelAnimation {
        id: numberAnimation
        SequentialAnimation {
            NumberAnimation { target: textScale; properties: "xScale,yScale"; from:1.0; to:1.2; duration:150; easing.type: Easing.OutQuad }
            NumberAnimation { target: textScale; properties: "xScale,yScale"; to:1.0; duration:250; easing.type: Easing.OutElastic }
        }
        SequentialAnimation {
            ColorAnimation { target: timerText; property: "color"; from: "white"; to: uclaBlue; duration:80 }
            ColorAnimation { target: timerText; property: "color"; to: "white"; duration:150 }
        }
        SequentialAnimation {
            NumberAnimation { target: textRotation; property: "angle"; from:0; to:3; duration:100 }
            NumberAnimation { target: textRotation; property: "angle"; to:0; duration:200; easing.type: Easing.OutElastic }
        }
    }

    ParallelAnimation {
        id: rippleEffect
        SequentialAnimation {
            PauseAnimation { duration:0 }
            ParallelAnimation {
                NumberAnimation { target: ripple1; properties: "width,height"; from:0; to: timerSize * 1.0; duration:800; easing.type: Easing.OutCubic }
                NumberAnimation { target: ripple1; property: "opacity"; from:0.7; to:0; duration:800; easing.type: Easing.OutQuad }
            }
            PropertyAction { target: ripple1; properties: "width,height,opacity"; value: 0 }
        }
        SequentialAnimation {
            PauseAnimation { duration:120 }
            ParallelAnimation {
                NumberAnimation { target: ripple2; properties: "width,height"; from:0; to: timerSize * 1.15; duration:800; easing.type: Easing.OutCubic }
                NumberAnimation { target: ripple2; property: "opacity"; from:0.7; to:0; duration:800; easing.type: Easing.OutQuad }
            }
            PropertyAction { target: ripple2; properties: "width,height,opacity"; value: 0 }
        }
        SequentialAnimation {
            PauseAnimation { duration:240 }
            ParallelAnimation {
                NumberAnimation { target: ripple3; properties: "width,height"; from:0; to: timerSize * 1.3; duration:800; easing.type: Easing.OutCubic }
                NumberAnimation { target: ripple3; property: "opacity"; from:0.7; to:0; duration:800; easing.type: Easing.OutQuad }
            }
            PropertyAction { target: ripple3; properties: "width,height,opacity"; value: 0 }
        }
    }

    SequentialAnimation {
        id: warningPulse
        loops: 2
        ParallelAnimation {
            NumberAnimation { target: containerScale; properties: "xScale,yScale"; from:1.0; to:1.04; duration:120 }
            NumberAnimation { target: timerContainer; property: "opacity"; from:1.0; to:0.8; duration:120 }
        }
        ParallelAnimation {
            NumberAnimation { target: containerScale; properties: "xScale,yScale"; from:1.04; to:1.0; duration:120 }
            NumberAnimation { target: timerContainer; property: "opacity"; from:0.8; to:1.0; duration:120 }
        }
    }

    ParallelAnimation {
        id: gameOverEffect
        SequentialAnimation {
            NumberAnimation { target: canvasRotation; property: "angle"; from:0; to:720; duration:900; easing.type: Easing.OutQuad }
            PropertyAction { target: canvasRotation; property: "angle"; value: 0 }
        }
        SequentialAnimation {
            PauseAnimation { duration:100 }
            ParallelAnimation {
                SequentialAnimation {
                    PauseAnimation { duration:0 }
                    ParallelAnimation {
                        NumberAnimation { target: ripple1; properties: "width,height"; from:0; to: timerSize * 2.0; duration:1000; easing.type: Easing.OutQuad }
                        NumberAnimation { target: ripple1; property: "opacity"; from:1.0; to:0; duration:1000; easing.type: Easing.OutQuad }
                    }
                }
                SequentialAnimation {
                    PauseAnimation { duration:150 }
                    ParallelAnimation {
                        NumberAnimation { target: ripple2; properties: "width,height"; from:0; to: timerSize * 2.5; duration:1200; easing.type: Easing.OutQuad }
                        NumberAnimation { target: ripple2; property: "opacity"; from:1.0; to:0; duration:1200; easing.type: Easing.OutQuad }
                    }
                }
                SequentialAnimation {
                    PauseAnimation { duration:300 }
                    ParallelAnimation {
                        NumberAnimation { target: ripple3; properties: "width,height"; from:0; to: timerSize * 3.0; duration:1400; easing.type: Easing.OutQuad }
                        NumberAnimation { target: ripple3; property: "opacity"; from:1.0; to:0; duration:1400; easing.type: Easing.OutQuad }
                    }
                }
            }
        }
    }

    ParallelAnimation {
        id: startAnimation
        NumberAnimation { target: timerContainer; property: "opacity"; from:0.3; to:1.0; duration:500; easing.type: Easing.OutQuad }
        NumberAnimation { target: containerScale; properties: "xScale,yScale"; from:0.8; to:1.0; duration:500; easing.type: Easing.OutBack }
    }

    NumberAnimation {
        id: stopAnimation
        target: timerContainer
        property: "opacity"
        from: 1.0; to: 0.7
        duration: 300
        easing.type: Easing.InQuad
    }

    // ---------- Demo countdown (only when demoMode true) ----------
    Timer {
        id: fakeCountdown
        interval: 1000
        repeat: true
        running: demoMode && isRunning
        onTriggered: {
            if (timerSeconds > 0) {
                timerSeconds = timerSeconds - 1
                progressValue = Math.round((( ( (demoMode ? 15 : 60) - timerSeconds) / (demoMode ? 15 : 60) ) * 100) * 100) / 100
                // trigger animations
                numberAnimation.start()
                rippleEffect.start()
                if (timerSeconds <= 10 && timerSeconds > 0) warningPulse.start()
                if (timerSeconds === 0) {
                    gameOverEffect.start()
                    isRunning = false
                }
            } else {
                fakeCountdown.stop()
                gradientAnimationTimer.running = false
            }
        }
    }

    function formatTime(seconds) {
        var mins = Math.floor(seconds / 60);
        var secs = seconds % 60;
        return (mins < 10 ? "0" : "") + mins + ":" + (secs < 10 ? "0" : "") + secs;
    }

    // ensure canvas repaints when progress changed
    onProgressValueChanged: progressCanvas.requestPaint()
}
