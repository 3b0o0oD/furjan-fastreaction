import QtQuick 2.12

Item {
    id: _teamname_screen_new

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
    // Backend property for receiving updates (set from Python)
    property var backend: null
    // Local player state (names and avatar sources)
    property var players: [
        { name: "Name 1", avatar: "Assets/avatar_img_13.png" },
        { name: "Name 2", avatar: "Assets/avatar_img_14.png" },
        { name: "Name 3", avatar: "Assets/avatar_img_15.png" },
        { name: "Name 4", avatar: "Assets/avatar_img_16.png" }
    ]
    // Update handlers bound to backend signals
    onBackendChanged: {
        if (backend) {
            console.log("Teamname backend connected to QML")
            // bilingual updates only
            if (backend.teamNameArUpdated)
                backend.teamNameArUpdated.connect(function(team_name_ar) { team_Name_ar.text = team_name_ar })
            if (backend.teamNameEnUpdated)
                backend.teamNameEnUpdated.connect(function(team_name_en) { team_Name_en.text = team_name_en })
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
        // Force property updates for Text/Image bindings
        players = players.slice()
    }

    // Item {
    //     id: background

    //     x: -1
    //     y: -155

    //     height: 1336
    //     width: 1991

    //     Image {
    //         id: base_blue_bg

    //         x: 1
    //         y: 155

    //         source: "Assets/base_blue_bg_7.png"
    //     }
    //     Image {
    //         id: center_round

    //         x: 390

    //         source: "Assets/center_round_7.png"
    //     }
    //     Image {
    //         id: btm_shape

    //         x: 1
    //         y: 975

    //         source: "Assets/btm_shape_7.png"
    //     }
    //     Item {
    //         id: right_shapes

    //         x: 1510
    //         y: 87

    //         height: 870
    //         width: 381

    //         Image {
    //             id: right_shape_1

    //             source: "Assets/right_shape_50.png"
    //         }
    //         Image {
    //             id: right_shape_2

    //             x: 321
    //             y: 38

    //             source: "Assets/right_shape_51.png"
    //         }
    //         Image {
    //             id: right_shape_3

    //             x: 193
    //             y: 126

    //             source: "Assets/right_shape_52.png"
    //         }
    //         Image {
    //             id: right_shape_4

    //             x: 150
    //             y: 321

    //             source: "Assets/right_shape_53.png"
    //         }
    //         Image {
    //             id: right_shape_5

    //             x: 299
    //             y: 279

    //             source: "Assets/right_shape_54.png"
    //         }
    //         Image {
    //             id: right_shape_6

    //             x: 224
    //             y: 516

    //             source: "Assets/right_shape_55.png"
    //         }
    //         Image {
    //             id: right_shape_7

    //             x: 152
    //             y: 682

    //             source: "Assets/right_shape_56.png"
    //         }
    //     }
    //     Item {
    //         id: left_shapes

    //         x: 52
    //         y: 185

    //         height: 801
    //         width: 290

    //         Image {
    //             id: left_shape_1

    //             x: 93

    //             source: "Assets/left_shape_43.png"
    //         }
    //         Image {
    //             id: left_shape_2

    //             x: 246
    //             y: 32

    //             source: "Assets/left_shape_44.png"
    //         }
    //         Image {
    //             id: left_shape_3

    //             y: 187

    //             source: "Assets/left_shape_45.png"
    //         }
    //         Image {
    //             id: left_shape_4

    //             x: 122
    //             y: 363

    //             source: "Assets/left_shape_46.png"
    //         }
    //         Image {
    //             id: left_shape_5

    //             x: 129
    //             y: 525

    //             source: "Assets/left_shape_47.png"
    //         }
    //         Image {
    //             id: left_shape_6

    //             x: 4
    //             y: 701

    //             source: "Assets/left_shape_48.png"
    //         }
    //     }
    //     Image {
    //         id: rounds

    //         x: 1
    //         y: 126

    //         source: "Assets/rounds_7.png"
    //     }
    //     Image {
    //         id: shadow

    //         x: 1
    //         y: 155

    //         source: "Assets/shadow_8.png"
    //     }
    //     Image {
    //         id: check_pattern

    //         y: 54

    //         source: "Assets/check_pattern_7.png"
    //     }
    //     Image {
    //         id: light

    //         x: 23
    //         y: 360

    //         source: "Assets/light_7.png"
    //     }
    //     Item {
    //         id: assets

    //         x: 18
    //         y: 125

    //         height: 1093
    //         width: 1973

    //         Image {
    //             id: right_light

    //             x: 1385
    //             y: 67

    //             source: "Assets/right_light_7.png"
    //         }
    //         Image {
    //             id: right_triangle

    //             x: 1489
    //             y: 320

    //             source: "Assets/right_triangle_7.png"
    //         }
    //         Image {
    //             id: left_light

    //             y: 126

    //             source: "Assets/left_light_7.png"
    //         }
    //         Image {
    //             id: left_triangle

    //             x: 409

    //             source: "Assets/left_triangle_7.png"
    //         }
    //         Image {
    //             id: polygon

    //             x: 1602
    //             y: 831

    //             source: "Assets/polygon_7.png"
    //         }
    //         Image {
    //             id: triangle

    //             x: 105
    //             y: 113

    //             source: "Assets/triangle_7.png"
    //         }
    //         Item {
    //             id: lines

    //             x: 600
    //             y: 57

    //             height: 770
    //             width: 1217

    //             Image {
    //                 id: line_1

    //                 x: 118

    //                 source: "Assets/line_29.png"
    //             }
    //             Image {
    //                 id: line_2

    //                 x: 1096
    //                 y: 204

    //                 source: "Assets/line_30.png"
    //             }
    //             Image {
    //                 id: line_3

    //                 y: 694

    //                 source: "Assets/line_31.png"
    //             }
    //             Image {
    //                 id: line_4

    //                 x: 747
    //                 y: 654

    //                 source: "Assets/line_32.png"
    //             }
    //         }
    //     }
    // }
    
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

            source: "Assets/uxe_logo_7.png"
        }
        Image {
            id: sira_logo

            x: 161

            source: "Assets/sira_logo_7.png"
        }
        Image {
            id: emarat_alaman_logo

            y: 7

            source: "Assets/emarat_alaman_logo_7.png"
        }
    }
    
    Item {
        id: avatars

        x: 439
        y: 313

        height: 504
        width: 1044

        Item {
            id: avatar_1

            x: 510
            y: 255

            height: 249
            width: 534

            Item {
                id: name_1

                y: 95

                height: 154
                width: 534

                Image {
                    id: player_name_bg_1

                    source: "Assets/player_name_bg_12.png"
                }
                Text {
                    id: name_1_text

                    x: 227
                    y: 65

                    height: 20
                    width: 247

                    color: "#ffffff"
                    font.capitalization: Font.AllUppercase
                    font.family: customFontLoader.name
                    font.letterSpacing: 1.20
                    font.pixelSize: 30
                    font.weight: Font.Black
                    horizontalAlignment: Text.AlignLeft
                    text: players[0] ? players[0].name : "Name 1"
                    verticalAlignment: Text.AlignVCenter
                    
                }
            }
            Item {
                id: avatar_bg_1

                x: 14

                height: 234
                width: 234

                Image {
                    id: avatar_border_bg1_1

                    x: 41
                    y: 41

                    source: "Assets/avatar_border_bg1_12.png"
                }
                Image {
                    id: avatar_border_bg2_1

                    source: "Assets/avatar_border_bg2_12.png"
                }
            }
            Image {
                id: avatar_img_1

                x: 57
                y: 43

                source: "Assets/avatar_img_13.png"
            }
        }
        Item {
            id: avatar_2

            y: 255

            height: 249
            width: 534

            Item {
                id: name_2

                y: 95

                height: 154
                width: 534

                Image {
                    id: player_name_bg_2

                    source: "Assets/player_name_bg_13.png"
                }
                Text {
                    id: name_2_text

                    x: 227
                    y: 65

                    height: 20
                    width: 259

                    color: "#ffffff"
                    font.capitalization: Font.AllUppercase
                    font.family: customFontLoader.name
                    font.letterSpacing: 1.20
                    font.pixelSize: 30
                    font.weight: Font.Black
                    horizontalAlignment: Text.AlignLeft
                    text: players[1] ? players[1].name : "Name 2"
                    verticalAlignment: Text.AlignVCenter
                    
                }
            }
            Item {
                id: avatar_bg_2

                x: 14

                height: 234
                width: 234

                Image {
                    id: avatar_border_bg1_2

                    x: 41
                    y: 41

                    source: "Assets/avatar_border_bg1_13.png"
                }
                Image {
                    id: avatar_border_bg2_2

                    source: "Assets/avatar_border_bg2_13.png"
                }
            }
            Image {
                id: avatar_img_2

                x: 57
                y: 43

                source: "Assets/avatar_img_14.png"
            }
        }
        Item {
            id: avatar_3

            x: 510

            height: 249
            width: 534

            Item {
                id: name_3

                y: 95

                height: 154
                width: 534

                Image {
                    id: player_name_bg_3

                    source: "Assets/player_name_bg_14.png"
                }
                Text {
                    id: name_3_text

                    x: 227
                    y: 65

                    height: 20
                    width: 256

                    color: "#ffffff"
                    font.capitalization: Font.AllUppercase
                    font.family: customFontLoader.name
                    font.letterSpacing: 1.20
                    font.pixelSize: 30
                    font.weight: Font.Black
                    horizontalAlignment: Text.AlignLeft
                    text: players[2] ? players[2].name : "Name 3"
                    verticalAlignment: Text.AlignVCenter
                    
                }
            }
            Item {
                id: avatar_bg_3

                x: 14

                height: 234
                width: 234

                Image {
                    id: avatar_border_bg1_3

                    x: 41
                    y: 41

                    source: "Assets/avatar_border_bg1_14.png"
                }
                Image {
                    id: avatar_border_bg2_3

                    source: "Assets/avatar_border_bg2_14.png"
                }
            }
            Image {
                id: avatar_img_3

                x: 57
                y: 43

                source:"Assets/avatar_img_15.png"
            }
        }
        Item {
            id: avatar_4

            height: 249
            width: 534

            Item {
                id: name_4

                y: 95

                height: 154
                width: 534

                Image {
                    id: player_name_bg_4

                    source: "Assets/player_name_bg_15.png"
                }
                Text {
                    id: name_4_text

                    x: 227
                    y: 65

                    height: 20
                    width: 162

                    color: "#ffffff"
                    font.capitalization: Font.AllUppercase
                    font.family: customFontLoader.name
                    font.letterSpacing: 1.20
                    font.pixelSize: 30
                    font.weight: Font.Black
                    horizontalAlignment: Text.AlignLeft
                    text: players[3] ? players[3].name : "Name 4"
                    verticalAlignment: Text.AlignVCenter
                    
                }
            }
            Item {
                id: avatar_bg_4

                x: 14

                height: 234
                width: 234

                Image {
                    id: avatar_border_bg1_4

                    x: 41
                    y: 41

                    source: "Assets/avatar_border_bg1_15.png"
                }
                Image {
                    id: avatar_border_bg2_4

                    source: "Assets/avatar_border_bg2_15.png"
                }
            }
            Image {
                id: avatar_img_4

                x: 57
                y: 43

                source: "Assets/avatar_img_16.png"
            }
        }
    }
    Item {
        id: team_name

        x: 711
        y: 62

        height: 170
        width: 498

        Text {
            id: team_Name_ar

            x: 71

            height: 45
            width: 357
            visible: false
            color: "#fd8c01"
            font.capitalization: Font.AllUppercase
            font.family: customFontLoader.name
            font.letterSpacing: 5.12
            font.pixelSize: 64
            font.weight: Font.Bold
            horizontalAlignment: Text.AlignHCenter
            text: "اسم الفريق"
            verticalAlignment: Text.AlignVCenter
            
        }
        Text {
            id: team_Name_en

            y: 116

            height: 54
            width: 498

            color: "#ffffff"
            font.capitalization: Font.AllUppercase
            font.family: customFontLoader.name
            font.letterSpacing: 5.60
            font.pixelSize: 80
            font.weight: Font.Black
            horizontalAlignment: Text.AlignHCenter
            text: "Team Name"
            verticalAlignment: Text.AlignVCenter
            
        }
        
    }
    // Item {
    //     id: mascot

    //     y: 466

    //     height: 564
    //     width: 486

    //     Image {
    //         id: mascot_stand

    //         y: 478

    //         source: "Assets/mascot_stand_9.png"
    //     }
    //     Image {
    //         id: mascot_2

    //         x: 80

    //         source: "Assets/mascot_9.png"
    //     }
    //     Image {
    //         id: stand_light

    //         x: 31
    //         y: 225

    //         source: "Assets/stand_light_9.png"
    //     }
    // }
}