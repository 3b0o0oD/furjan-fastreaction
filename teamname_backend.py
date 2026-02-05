#!/usr/bin/env python3
"""
Team Name Screen Backend for QML Teamname screen.
Provides signals and slots to update team name and player names/avatars.
"""

import os
import sys
from typing import List, Dict

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, Qt
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout


class TeamNameBackend(QObject):
    """Backend for Team Name screen. Manages team and player data and emits updates to QML."""

    teamNameArUpdated = pyqtSignal(str, arguments=["team_name_ar"])  # Arabic team name
    teamNameEnUpdated = pyqtSignal(str, arguments=["team_name_en"])  # English team name
    playerNameUpdated = pyqtSignal(int, str, arguments=["index", "name"])  # player index 0..3, name
    playerAvatarUpdated = pyqtSignal(int, str, arguments=["index", "avatar_source"])  # player index 0..3, image path
    allPlayersUpdated = pyqtSignal(list, arguments=["players"])  # list of player dicts {name, avatar}

    def __init__(self):
        super().__init__()
        self.team_name_ar: str = "الشغلوبة"
        self.team_name_en: str = "The Shogun"
        # 4 players for the Teamname screen
        self.players: List[Dict[str, str]] = [
            {"name": "Player 1", "avatar": "Assets/avatar_img_1@2x.png"},
            {"name": "Player 2", "avatar": "Assets/avatar_img_2@2x.png"},
            {"name": "Player 3", "avatar": "Assets/avatar_img_3@2x.png"},
            {"name": "Player 4", "avatar": "Assets/avatar_img_4@2x.png"},
        ]

        # self._emit_initial_state()

    def _emit_initial_state(self) -> None:
        # Emit bilingual signals
        self.teamNameArUpdated.emit(self.team_name_ar)
        self.teamNameEnUpdated.emit(self.team_name_en)
        for idx, player in enumerate(self.players):
            self.playerNameUpdated.emit(idx, player["name"])
            self.playerAvatarUpdated.emit(idx, player["avatar"])
        self.allPlayersUpdated.emit(self.players)

    # Slots exposed to QML / Python controllers
    @pyqtSlot(str, str)
    def update_team_name_bilingual(self, team_name_ar: str, team_name_en: str) -> None:
        """Update Arabic and English team names together and emit separate signals."""
        if team_name_ar:
            self.team_name_ar = team_name_ar
            self.teamNameArUpdated.emit(self.team_name_ar)
        if team_name_en:
            self.team_name_en = team_name_en
            self.teamNameEnUpdated.emit(self.team_name_en)
        print(f"Updated team name AR: {self.team_name_ar}, EN: {self.team_name_en}")

    @pyqtSlot(str)
    def update_team_name_ar(self, team_name_ar: str) -> None:
        if not team_name_ar:
            return
        self.team_name_ar = team_name_ar
        self.teamNameArUpdated.emit(self.team_name_ar)
        print(f"Updated team name AR: {self.team_name_ar}")

    @pyqtSlot(str)
    def update_team_name_en(self, team_name_en: str) -> None:
        if not team_name_en:
            return
        self.team_name_en = team_name_en
        self.teamNameEnUpdated.emit(self.team_name_en)
        print(f"Updated team name EN: {self.team_name_en}")

    @pyqtSlot(int, str)
    def update_player_name(self, index: int, name: str) -> None:
        if not (0 <= index < len(self.players)) or not name:
            return
        self.players[index]["name"] = name
        self.playerNameUpdated.emit(index, name)
        print(f"Updated player {index} name: {name}")

    @pyqtSlot(int, str)
    def update_player_avatar(self, index: int, avatar_source: str) -> None:
        if not (0 <= index < len(self.players)) or not avatar_source:
            return
        self.players[index]["avatar"] = avatar_source
        self.playerAvatarUpdated.emit(index, avatar_source)
        print(f"Updated player {index} avatar: {avatar_source}")


class TeamNameDisplay(QWidget):
    """Host widget that loads the Teamname QML and injects the backend object."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team Name Backend - Team & Players")
        self.setGeometry(100, 100, 1920, 1080)

        self.backend = TeamNameBackend()
        self._setup_qml()

    def _setup_qml(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.qml_widget = QQuickWidget()
        self.qml_widget.setClearColor(Qt.transparent)

        fmt = QSurfaceFormat()
        fmt.setAlphaBufferSize(8)
        self.qml_widget.setFormat(fmt)
        self.qml_widget.setAttribute(Qt.WA_TranslucentBackground, True)
        self.qml_widget.setAttribute(Qt.WA_NoSystemBackground, True)
        self.qml_widget.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)

        self._setup_qml_import_paths()

        qml_file = os.path.join(os.path.dirname(__file__), "Teamname_screen_new.ui.qml")
        print(f"Loading QML file: {qml_file}")
        self.qml_widget.setSource(QUrl.fromLocalFile(qml_file))

        if self.qml_widget.quickWindow():
            self.qml_widget.quickWindow().setColor(Qt.transparent)

        root = self.qml_widget.rootObject()
        if root:
            root.setProperty("backend", self.backend)
            print("QML backend connected successfully (Teamname)")
        else:
            print("Error: Failed to get QML root object (Teamname)")

        layout.addWidget(self.qml_widget)
        # self.backend.update_team_name_ar(self.backend.team_name_ar)
        # self.backend.update_team_name_en(self.backend.team_name_en)
        # # self.backend.update_team_name_bilingual(self.backend.team_name_ar, self.backend.team_name_en)
        # self.backend.update_player_name(0, self.backend.players[0]["name"])
        # self.backend.update_player_avatar(0, self.backend.players[0]["avatar"])
        # self.backend.update_player_name(1, self.backend.players[1]["name"])
        # self.backend.update_player_avatar(1, self.backend.players[1]["avatar"])
        # self.backend.update_player_name(2, self.backend.players[2]["name"])
        # self.backend.update_player_avatar(2, self.backend.players[2]["avatar"])
        # self.backend.update_player_name(3, self.backend.players[3]["name"])
        # self.backend.update_player_avatar(3, self.backend.players[3]["avatar"])
        # self.backend.allPlayersUpdated.emit(self.backend.players)
        self.setLayout(layout)

    def _setup_qml_import_paths(self) -> None:
        # Attempt to collect common PyQt5 QML locations
        try:
            import PyQt5  # type: ignore
            pyqt5_path = os.path.dirname(PyQt5.__file__)
            candidates = [
                os.path.join(pyqt5_path, "Qt", "qml"),
                "/usr/lib/qt5/qml",
                "/usr/share/qt5/qml",
                "/usr/lib/python3/dist-packages/PyQt5/Qt/qml",
            ]
            qml_paths = [p for p in candidates if os.path.exists(p)]
            if qml_paths:
                os.environ["QML_IMPORT_PATH"] = ":".join(qml_paths)
                print(f"Set QML_IMPORT_PATH to: {os.environ['QML_IMPORT_PATH']}")
        except Exception:
            pass


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Team Name Backend")
    app.setApplicationVersion("1.0")

    win = TeamNameDisplay()
    win.show()

    print("Team Name Backend started! Use methods to update team/player data.")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


