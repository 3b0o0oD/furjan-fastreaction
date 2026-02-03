#!/usr/bin/env python3
"""
Enhanced Leaderboard Backend for QML Leaderboard Screen.
Provides complete control over player_table cells and podium top 3 updates.
"""

import sys
import os
# Disable hardware OpenGL before importing Qt
os.environ.setdefault("QT_OPENGL", "software")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_XCB_GL_INTEGRATION", "xcb_egl")
os.environ.setdefault("LIBGL_ALWAYS_INDIRECT", "1")
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QSpinBox, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
                             QTextEdit, QScrollArea, QFrame, QGridLayout)
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, pyqtSlot, QUrl, Qt
from PyQt5.QtGui import QSurfaceFormat, QFont

class EnhancedLeaderboardBackend(QObject):
    """
    Enhanced backend class that manages player_table cells and podium updates.
    """

    # Signals for player table cell updates
    playerTableCellUpdated = pyqtSignal(int, str, int, int, int, arguments=['index', 'name', 'score', 'weighted_points', 'rank'])
    playerTableNameUpdated = pyqtSignal(int, str, arguments=['index', 'name'])
    playerTableScoreUpdated = pyqtSignal(int, int, arguments=['index', 'score'])
    playerTableWeightedUpdated = pyqtSignal(int, int, arguments=['index', 'weighted_points'])
    playerTableRankUpdated = pyqtSignal(int, int, arguments=['index', 'rank'])
    
    # Signals for podium updates (top 3)
    podiumUpdated = pyqtSignal(str, str, str, int, int, int, int, int, int, 
                              arguments=['gold_name', 'silver_name', 'bronze_name',
                                       'gold_score', 'silver_score', 'bronze_score',
                                       'gold_weighted', 'silver_weighted', 'bronze_weighted'])
    
    # Individual podium signals
    goldPlayerUpdated = pyqtSignal(str, int, int, arguments=['name', 'score', 'weighted_points'])
    silverPlayerUpdated = pyqtSignal(str, int, int, arguments=['name', 'score', 'weighted_points'])
    bronzePlayerUpdated = pyqtSignal(str, int, int, arguments=['name', 'score', 'weighted_points'])
    
    # Last player signals
    lastPlayerUpdated = pyqtSignal(str, int, int, int, arguments=['name', 'score', 'weighted_points', 'rank'])
    lastPlayerNameUpdated = pyqtSignal(str, arguments=['name'])
    lastPlayerScoreUpdated = pyqtSignal(int, arguments=['score'])
    lastPlayerWeightedUpdated = pyqtSignal(int, arguments=['weighted_points'])
    lastPlayerRankUpdated = pyqtSignal(int, arguments=['rank'])
    
    # General signals
    leaderboardUpdated = pyqtSignal()
    playerTableUpdated = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        # Initialize player data (5 players total - ranks 1-5)
        self.players = [
            {
                "name": "Amjad Ali", 
                "score": 900, 
                "weighted_points": 10080,
                "rank": 1, 
                "team": "Team Eta",
                "position": "player_table_item_1"
            },
            {
                "name": "Andri raffaelo", 
                "score": 850, 
                "weighted_points": 9790,
                "rank": 2, 
                "team": "Team Zeta",
                "position": "player_table_item_2"
            },
            {
                "name": "Krishna karate", 
                "score": 720, 
                "weighted_points": 8520,
                "rank": 3, 
                "team": "Team Epsilon",
                "position": "player_table_item_3"
            },
            {
                "name": "-", 
                "score": 630, 
                "weighted_points": 6970,
                "rank": 4, 
                "team": "Team Delta",
                "position": "player_table_item_4"
            },
            {
                "name": "-", 
                "score": 510, 
                "weighted_points": 5750,
                "rank": 5, 
                "team": "Team Gamma",
                "position": "player_table_item_5"
            }
        ]
        
        # Initialize last player data
        self.last_player = {
            "name": "Aayan afzal khan", 
            "score": 320, 
            "weighted_points": 3750,
            "rank": 34, 
            "team": "Team Alpha"
        }
        
        # Emit initial data
        self.emit_initial_data()

    def emit_initial_data(self):
        """Emit initial player data to QML."""
        # Emit all player table data (5 players)
        for i, player in enumerate(self.players):
            self.playerTableCellUpdated.emit(i, player["name"], player["score"], 
                                           player["weighted_points"], player["rank"])
        
        # Emit initial podium data (top 3)
        self.update_podium()
        
        # Emit initial last player data
        self.lastPlayerUpdated.emit(self.last_player["name"], self.last_player["score"], 
                                  self.last_player["weighted_points"], self.last_player["rank"])

    @pyqtSlot(int, str)
    def update_player_table_name(self, index, name):
        """Update player name in player table at given index."""
        if 0 <= index < len(self.players):
            self.players[index]["name"] = name
            player = self.players[index]
            
            # Emit cell update
            self.playerTableCellUpdated.emit(index, name, player["score"], 
                                           player["weighted_points"], player["rank"])
            self.playerTableNameUpdated.emit(index, name)
            self.playerTableUpdated.emit()
            
            # Update podium if this affects top 3
            if index < 3:
                self.update_podium()
            
            print(f"Updated player table {index} name to: {name}")

    @pyqtSlot(int, int)
    def update_player_table_score(self, index, score):
        """Update player score in player table at given index."""
        if 0 <= index < len(self.players):
            self.players[index]["score"] = score
            player = self.players[index]
            
            # Emit cell update
            self.playerTableCellUpdated.emit(index, player["name"], score, 
                                           player["weighted_points"], player["rank"])
            self.playerTableScoreUpdated.emit(index, score)
            self.playerTableUpdated.emit()
            
            # Update podium if this affects top 3
            if index < 3:
                self.update_podium()
            
            print(f"Updated player table {index} score to: {score}")

    @pyqtSlot(int, int)
    def update_player_table_weighted_points(self, index, weighted_points):
        """Update player weighted points in player table at given index."""
        if 0 <= index < len(self.players):
            self.players[index]["weighted_points"] = weighted_points
            player = self.players[index]
            
            # Emit cell update
            self.playerTableCellUpdated.emit(index, player["name"], player["score"], 
                                           weighted_points, player["rank"])
            self.playerTableWeightedUpdated.emit(index, weighted_points)
            self.playerTableUpdated.emit()
            
            # Update podium if this affects top 3
            if index < 3:
                self.update_podium()
            
            print(f"Updated player table {index} weighted points to: {weighted_points}")

    @pyqtSlot(int, int)
    def update_player_table_rank(self, index, rank):
        """Update player rank in player table at given index."""
        if 0 <= index < len(self.players):
            self.players[index]["rank"] = rank
            player = self.players[index]
            
            # Emit cell update
            self.playerTableCellUpdated.emit(index, player["name"], player["score"], 
                                           player["weighted_points"], rank)
            self.playerTableRankUpdated.emit(index, rank)
            self.playerTableUpdated.emit()
            
            print(f"Updated player table {index} rank to: {rank}")

    @pyqtSlot(str)
    def update_last_player_name(self, name):
        """Update last player name."""
        self.last_player["name"] = name
        self.lastPlayerUpdated.emit(name, self.last_player["score"], 
                                  self.last_player["weighted_points"], self.last_player["rank"])
        self.lastPlayerNameUpdated.emit(name)
        print(f"Updated last player name to: {name}")

    @pyqtSlot(int)
    def update_last_player_score(self, score):
        """Update last player score."""
        self.last_player["score"] = score
        self.lastPlayerUpdated.emit(self.last_player["name"], score, 
                                  self.last_player["weighted_points"], self.last_player["rank"])
        self.lastPlayerScoreUpdated.emit(score)
        print(f"Updated last player score to: {score}")

    @pyqtSlot(int)
    def update_last_player_weighted_points(self, weighted_points):
        """Update last player weighted points."""
        self.last_player["weighted_points"] = weighted_points
        self.lastPlayerUpdated.emit(self.last_player["name"], self.last_player["score"], 
                                  weighted_points, self.last_player["rank"])
        self.lastPlayerWeightedUpdated.emit(weighted_points)
        print(f"Updated last player weighted points to: {weighted_points}")

    @pyqtSlot(int)
    def update_last_player_rank(self, rank):
        """Update last player rank."""
        self.last_player["rank"] = rank
        self.lastPlayerUpdated.emit(self.last_player["name"], self.last_player["score"], 
                                  self.last_player["weighted_points"], rank)
        self.lastPlayerRankUpdated.emit(rank)
        print(f"Updated last player rank to: {rank}")

    @pyqtSlot(str, int, int, int)
    def update_last_player(self, name, score, weighted_points, rank):
        """Update all last player data at once."""
        self.last_player["name"] = name
        self.last_player["score"] = score
        self.last_player["weighted_points"] = weighted_points
        self.last_player["rank"] = rank
        self.lastPlayerUpdated.emit(name, score, weighted_points, rank)
        print(f"Updated last player: {name}, {score}, {weighted_points}, {rank}")

    @pyqtSlot()
    def update_podium(self):
        """Update podium with top 3 players."""
        if len(self.players) >= 3:
            # Get top 3 players (sorted by rank)
            top_3 = sorted(self.players, key=lambda x: x["rank"])[:3]
            
            gold = top_3[0] if len(top_3) > 0 else {"name": "", "score": 0, "weighted_points": 0}
            silver = top_3[1] if len(top_3) > 1 else {"name": "", "score": 0, "weighted_points": 0}
            bronze = top_3[2] if len(top_3) > 2 else {"name": "", "score": 0, "weighted_points": 0}
            
            # Emit podium update
            self.podiumUpdated.emit(
                gold["name"], silver["name"], bronze["name"],
                gold["score"], silver["score"], bronze["score"],
                gold["weighted_points"], silver["weighted_points"], bronze["weighted_points"]
            )
            
            # Emit individual podium updates
            self.goldPlayerUpdated.emit(gold["name"], gold["score"], gold["weighted_points"])
            self.silverPlayerUpdated.emit(silver["name"], silver["score"], silver["weighted_points"])
            self.bronzePlayerUpdated.emit(bronze["name"], bronze["score"], bronze["weighted_points"])
            
            print(f"Updated podium: Gold={gold['name']}, Silver={silver['name']}, Bronze={bronze['name']}")

    @pyqtSlot()
    def sort_leaderboard_by_score(self):
        """Sort leaderboard by score and update ranks."""
        self.players.sort(key=lambda x: x["score"], reverse=True)
        
        # Update ranks
        for i, player in enumerate(self.players):
            player["rank"] = i + 1
        
        # Emit all updates
        for i, player in enumerate(self.players):
            self.playerTableCellUpdated.emit(i, player["name"], player["score"], 
                                           player["weighted_points"], player["rank"])
        
        # Update podium
        self.update_podium()
        self.leaderboardUpdated.emit()
        print("Leaderboard sorted by score")

    @pyqtSlot()
    def reset_leaderboard(self):
        """Reset leaderboard to default values."""
        self.players = [
            {
                "name": "Amjad Ali", 
                "score": 900, 
                "weighted_points": 10080,
                "rank": 1, 
                "team": "Team Eta",
                "position": "player_table_item_1"
            },
            {
                "name": "Andri raffaelo", 
                "score": 850, 
                "weighted_points": 9790,
                "rank": 2, 
                "team": "Team Zeta",
                "position": "player_table_item_2"
            },
            {
                "name": "Krishna karate", 
                "score": 720, 
                "weighted_points": 8520,
                "rank": 3, 
                "team": "Team Epsilon",
                "position": "player_table_item_3"
            },
            {
                "name": "khurram khan", 
                "score": 630, 
                "weighted_points": 6970,
                "rank": 4, 
                "team": "Team Delta",
                "position": "player_table_item_4"
            },
            {
                "name": "Swapnil patil", 
                "score": 510, 
                "weighted_points": 5750,
                "rank": 5, 
                "team": "Team Gamma",
                "position": "player_table_item_5"
            }
        ]
        
        # Reset last player data
        self.last_player = {
            "name": "Aayan afzal khan", 
            "score": 320, 
            "weighted_points": 3750,
            "rank": 34, 
            "team": "Team Alpha"
        }
        
        self.emit_initial_data()
        print("Leaderboard reset to default values")

    def get_player_data(self, index):
        """Get player data at given index."""
        if 0 <= index < len(self.players):
            return self.players[index]
        return None

    def get_leaderboard_data(self):
        """Get all leaderboard data."""
        return self.players

    def get_podium_data(self):
        """Get top 3 players for podium."""
        if len(self.players) >= 3:
            return sorted(self.players, key=lambda x: x["rank"])[:3]
        return []

    def get_last_player_data(self):
        """Get last player data."""
        return self.last_player

    @pyqtSlot(list)
    def update_leaderboard_table(self, players=None):
        """Update leaderboard table with new player data or emit current data."""
        if players is None:
            # Emit all current player data
            for i, player in enumerate(self.players):
                self.playerTableCellUpdated.emit(i, player["name"], player["score"], 
                                               player["weighted_points"], player["rank"])
            self.playerTableUpdated.emit()
            print("Leaderboard table updated")
        else:
            # Update with new player data
            if players and len(players) <= len(self.players):
                for i, player_data in enumerate(players):
                    if i < len(self.players):
                        self.players[i].update(player_data)
                        self.playerTableCellUpdated.emit(i, self.players[i]["name"], 
                                                       self.players[i]["score"], 
                                                       self.players[i]["weighted_points"], 
                                                       self.players[i]["rank"])
                self.playerTableUpdated.emit()
                print(f"Leaderboard table updated with {len(players)} players")


class EnhancedLeaderboardDisplay(QWidget):
    """
    Enhanced leaderboard display with controls for player table and podium.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Leaderboard Backend - Player Table & Podium Control")
        
        # Set window properties
        self.setGeometry(100, 100, 1800, 1000)
        self.setStyleSheet("""
            QWidget {
                background: #1a1a1a;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4574AD;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create the backend
        self.backend = EnhancedLeaderboardBackend()
        
        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the enhanced UI with player table and podium controls."""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left side - Controls
        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setMaximumWidth(400)  # Limit width of controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(15)
        
        # Title
        title = QLabel("Enhanced Leaderboard Controls")
        title.setStyleSheet("""
            QLabel {
                color: #4574AD;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background: #2a2a2a;
                border-radius: 8px;
                border: 2px solid #4574AD;
            }
        """)
        controls_layout.addWidget(title)
        
       

        # Right side - QML Display
        self.setup_qml_widget()
        main_layout.addWidget(self.qml_widget)
        # Test updates with new structure (5 players + last player)
        self.update_player_name(4,"Test Player")
        self.update_player_score(4,10000)
        self.update_weighted_points(4,10000)
        self.update_last_player("New Last Player", 500, 6000, 25)
        self.sort_leaderboard_by_score()
        
        self.setLayout(main_layout)

   
    
   

    def setup_qml_widget(self):
        """Setup the QML widget with leaderboard."""
        # Create QML widget
        self.qml_widget = QQuickWidget()
        self.qml_widget.setClearColor(Qt.transparent)
        
        # Set format for transparency and software rendering
        fmt = QSurfaceFormat()
        fmt.setAlphaBufferSize(8)
        fmt.setVersion(2, 0)
        fmt.setRenderableType(QSurfaceFormat.OpenGL)
        fmt.setProfile(QSurfaceFormat.NoProfile)
        fmt.setSwapBehavior(QSurfaceFormat.SingleBuffer)
        self.qml_widget.setFormat(fmt)
        
        # Set attributes for transparency
        self.qml_widget.setAttribute(Qt.WA_TranslucentBackground, True)
        self.qml_widget.setAttribute(Qt.WA_NoSystemBackground, True)
        self.qml_widget.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.qml_widget.setAttribute(Qt.WA_AlwaysStackOnTop, True)
        self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        
        # Set QML import paths
        self.setup_qml_import_paths()
        
        # Load QML file
        qml_file_path = os.path.join(os.path.dirname(__file__), 'Leaderboard_screen_enhanced.qml')
        if not os.path.exists(qml_file_path):
            # Fallback to original version
            qml_file_path = os.path.join(os.path.dirname(__file__), 'Leaderboard_screen.ui.qml')
        print(f"Loading QML file: {qml_file_path}")
        self.qml_widget.setSource(QUrl.fromLocalFile(qml_file_path))
        
        # Set transparent background for quick window
        if self.qml_widget.quickWindow():
            self.qml_widget.quickWindow().setColor(Qt.transparent)
        
        # Connect backend to QML
        self.setup_qml_backend()

    def setup_qml_import_paths(self):
        """Setup QML import paths for better compatibility."""
        import PyQt5
        
        # Multiple QML import paths for better compatibility
        qml_paths = []
        
        # PyQt5 QML path
        pyqt5_path = os.path.dirname(PyQt5.__file__)
        pyqt5_qml = os.path.join(pyqt5_path, 'Qt', 'qml')
        if os.path.exists(pyqt5_qml):
            qml_paths.append(pyqt5_qml)
        
        # System QML paths
        system_paths = [
            '/usr/lib/aarch64-linux-gnu/qt5/qml',
            '/usr/lib/qt5/qml',
            '/usr/share/qt5/qml',
            '/usr/lib/python3/dist-packages/PyQt5/Qt/qml'
        ]
        
        for path in system_paths:
            if os.path.exists(path):
                qml_paths.append(path)
        
        # Set QML_IMPORT_PATH with all found paths
        if qml_paths:
            qml_import_path = ':'.join(qml_paths)
            os.environ['QML_IMPORT_PATH'] = qml_import_path
            print(f"Set QML_IMPORT_PATH to: {qml_import_path}")

    def setup_qml_backend(self):
        """Connect the backend to the QML component."""
        root_object = self.qml_widget.rootObject()
        if root_object:
            root_object.setProperty('backend', self.backend)
            print("QML backend connected successfully")
        else:
            print("Error: Failed to get QML root object")

    def update_player_name(self):
        """Update player name from controls."""
        index = self.player_index.value()
        name = self.player_name_input.text()
        
        if name:
            self.backend.update_player_table_name(index, name)
            self.update_leaderboard_table()
    def update_player_name(self, index, name):
        """Update player name from controls."""
        if name:
            self.backend.update_player_table_name(index, name)
            

    def update_player_score(self):
        """Update player score from controls."""
        index = self.player_index.value()
        score = self.score_input.value()
        
        self.backend.update_player_table_score(index, score)
        self.update_leaderboard_table()
    def update_player_score(self, index, score):
        """Update player score from controls."""
        if score:
            self.backend.update_player_table_score(index, score)
            

    def update_weighted_points(self):
        """Update weighted points from controls."""
        index = self.player_index.value()
        weighted_points = self.weighted_input.value()
        self.backend.update_player_table_weighted_points(index, weighted_points)
        self.update_leaderboard_table()
    def update_weighted_points(self, index, weighted_points):
        """Update weighted points from controls."""
        if weighted_points:
            self.backend.update_player_table_weighted_points(index, weighted_points)
            
    def update_rank(self):
        """Update rank from controls."""
        index = self.player_index.value()
        rank = self.rank_input.value()
        
        self.backend.update_player_table_rank(index, rank)
        self.update_leaderboard_table()
    def update_rank(self, index, rank):
        """Update rank from controls."""
        if rank:
            self.backend.update_player_table_rank(index, rank)
            

    def update_podium(self):
        """Update podium from controls."""
        gold_name = self.gold_name_input.text()
        silver_name = self.silver_name_input.text()
        bronze_name = self.bronze_name_input.text()
        
        if gold_name:
            # Update first player (gold)
            self.backend.update_player_table_name(0, gold_name)
        if silver_name:
            # Update second player (silver)
            self.backend.update_player_table_name(1, silver_name)
        if bronze_name:
            # Update third player (bronze)
            self.backend.update_player_table_name(2, bronze_name)
        
        self.update_leaderboard_table()
    def update_podium(self, gold_name, silver_name, bronze_name):
        """Update podium from controls."""
        if gold_name:
            self.backend.update_player_table_name(0, gold_name)
        if silver_name:
            self.backend.update_player_table_name(1, silver_name)
        if bronze_name:
            self.backend.update_player_table_name(2, bronze_name)
        
    def sort_leaderboard_by_score(self):
        """Sort leaderboard by score."""
        self.backend.sort_leaderboard_by_score()
    def sort_leaderboard_by_weighted_points(self):
        """Sort leaderboard by weighted points."""
        self.backend.sort_leaderboard_by_weighted_points()
    def reset_leaderboard(self):
        """Reset leaderboard."""
        self.backend.reset_leaderboard()
    def update_leaderboard_table(self, players=None):
        """Update leaderboard table."""
        if players is None:
            self.backend.update_leaderboard_table()
        else:
            self.backend.update_leaderboard_table(players)
    
    def update_last_player(self, name, score, weighted_points, rank):
        """Update last player data."""
        self.backend.update_last_player(name, score, weighted_points, rank)
    
    def update_last_player_name(self, name):
        """Update last player name."""
        self.backend.update_last_player_name(name)
    
    def update_last_player_score(self, score):
        """Update last player score."""
        self.backend.update_last_player_score(score)
    
    def update_last_player_weighted_points(self, weighted_points):
        """Update last player weighted points."""
        self.backend.update_last_player_weighted_points(weighted_points)
    
    def update_last_player_rank(self, rank):
        """Update last player rank."""
        self.backend.update_last_player_rank(rank)
    

def main():
    """Main function to run the enhanced leaderboard display."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Leaderboard Backend")
    app.setApplicationVersion("1.0")
    
    # Create and show the window
    window = EnhancedLeaderboardDisplay()
    window.show()
    
    print("Enhanced Leaderboard Backend started!")
    print("This backend controls:")
    print("- Player table cells (5 players - ranks 1-5)")
    print("- Podium top 3 players")
    print("- Last player section")
    print("- Individual cell updates")
    print("Use the controls to update any element.")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
