#!/usr/bin/env python3
"""
Enhanced Team Score Backend for updating team name and score values in QML.
This backend provides methods to dynamically update the team_name_value and score_value elements.
Follows the same pattern as the leaderboard backend for consistency.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat

class TeamScoreBackend(QObject):
    """
    Enhanced backend class that manages team name and score updates for the team score screen.
    Follows the same pattern as the leaderboard backend for consistency.
    """

    # Individual signals for team name and score updates
    teamNameChanged = pyqtSignal(str, arguments=['teamName'])
    scoreValueChanged = pyqtSignal(str, arguments=['scoreValue'])
    
    # Bulk update signal for both values
    teamScoreUpdated = pyqtSignal(str, str, arguments=['teamName', 'scoreValue'])
    
    # General signals
    teamScoreDataUpdated = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        # Initialize team score data
        self.team_data = {
            "name": "Team Alpha",
            "score": "0"
        }
        
        # Emit initial data
        self.emit_initial_data()
        
    def emit_initial_data(self):
        """Emit initial team score data to QML."""
        self.teamNameChanged.emit(self.team_data["name"])
        self.scoreValueChanged.emit(self.team_data["score"])
        self.teamScoreUpdated.emit(self.team_data["name"], self.team_data["score"])
        self.teamScoreDataUpdated.emit()
        print(f"Initial data emitted: {self.team_data['name']}, {self.team_data['score']}")

    @pyqtSlot(str)
    def set_team_name(self, team_name):
        """Set the team name and emit signal to update QML."""
        self.team_data["name"] = team_name
        self.teamNameChanged.emit(team_name)
        self.teamScoreDataUpdated.emit()
        print(f"Team name updated to: {team_name}")

    @pyqtSlot(str)
    def set_score_value(self, score_value):
        """Set the score value and emit signal to update QML."""
        self.team_data["score"] = score_value
        self.scoreValueChanged.emit(score_value)
        self.teamScoreDataUpdated.emit()
        print(f"Score updated to: {score_value}")

    @pyqtSlot(str, str)
    def set_team_score(self, team_name, score_value):
        """Set both team name and score value at once."""
        self.team_data["name"] = team_name
        self.team_data["score"] = score_value
        self.teamNameChanged.emit(team_name)
        self.scoreValueChanged.emit(score_value)
        self.teamScoreUpdated.emit(team_name, score_value)
        self.teamScoreDataUpdated.emit()
        print(f"Team score updated: {team_name}, {score_value}")

    @pyqtSlot(int)
    def set_score_int(self, score_value):
        """Set the score value as integer and emit signal to update QML."""
        score_str = str(score_value)
        self.set_score_value(score_str)

    @pyqtSlot()
    def get_team_name(self):
        """Get current team name."""
        return self.team_data["name"]

    @pyqtSlot()
    def get_score_value(self):
        """Get current score value."""
        return self.team_data["score"]

    @pyqtSlot()
    def get_team_data(self):
        """Get current team data."""
        return self.team_data

    @pyqtSlot()
    def reset_to_defaults(self):
        """Reset to default values."""
        self.set_team_score("Team Alpha", "0")
        print("Reset to default values")

    @pyqtSlot()
    def refresh_team_score(self):
        """Refresh team score display with current data."""
        self.emit_initial_data()
        print("Team score refreshed")

