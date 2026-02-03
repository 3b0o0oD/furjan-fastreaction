"""
FastReaction Backend for updating game elements in QML.
This backend provides methods to dynamically update:
- correct_count (correct count)
- wrong_count (wrong count)
- miss_count (miss count)
- time_value (timer display)
- score_value (game score)
- team_name (team name)
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat

class FastReactionBackend(QObject):
    """
    Backend class that manages game element updates for the FastReaction screen.
    Controls: correct_count, wrong_count, miss_count, time_value, score_value, team_name
    """

    # Signals to update QML elements
    # correct count
    correctCountChanged = pyqtSignal(str, arguments=['correctCount'])
    # wrong count
    wrongCountChanged = pyqtSignal(str, arguments=['wrongCount'])
    # miss count
    missCountChanged = pyqtSignal(str, arguments=['missCount'])
    # time value
    timeChanged = pyqtSignal(str, arguments=['timeValue'])
    # score value
    scoreChanged = pyqtSignal(str, arguments=['scoreValue'])
    # team name
    teamNameChanged = pyqtSignal(str, arguments=['teamName'])
    
    # Timer control signals (for CircularTimer_enhanced.qml)
    timerValueChanged = pyqtSignal(int, float, arguments=['seconds', 'progress'])
    countdownStarted = pyqtSignal()
    countdownStopped = pyqtSignal()
    timerPaused = pyqtSignal()
    timerResumed = pyqtSignal()
    

    def __init__(self):
        super().__init__()
        
        # Initialize default values
        self.correct_count = "0"
        self.wrong_count = "0"
        self.miss_count = "0"
        self.time_value = "02:01"
        self.score_value = "2300"
        self.team_name = "Team Name"
        
        # Timer properties
        self.timer_seconds = 121  # 2:01 in seconds
        self.timer_running = False
        self.total_time = 121
        
        # Timer for countdown
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # 1 second intervals

    @pyqtSlot(str)
    def set_correct_count(self, correct_count):
        """Set the correct count and emit signal to update QML."""
        try:
            # Validate input
            count = str(correct_count).strip()
            if not count.isdigit() and count != "":
                print(f"Warning: Invalid correct count format: {correct_count}")
                return
            
            self.correct_count = count
            print(f"Emitting correctCountChanged signal with value: {self.correct_count}")
            self.correctCountChanged.emit(self.correct_count)
            print(f"Correct count updated to: {self.correct_count}")
        except Exception as e:
            print(f"Error updating correct count: {e}")

    @pyqtSlot(str)
    def set_wrong_count(self, wrong_count):
        """Set the wrong count and emit signal to update QML."""
        try:
            # Validate input
            count = str(wrong_count).strip()
            if not count.isdigit() and count != "":
                print(f"Warning: Invalid wrong count format: {wrong_count}")
                return
            
            self.wrong_count = count
            print(f"Emitting wrongCountChanged signal with value: {self.wrong_count}")
            self.wrongCountChanged.emit(self.wrong_count)
            print(f"Wrong count updated to: {self.wrong_count}")
        except Exception as e:
            print(f"Error updating wrong count: {e}")
    
    @pyqtSlot(str)
    def set_miss_count(self, miss_count):
        """Set the miss count and emit signal to update QML."""
        try:
            # Validate input
            count = str(miss_count).strip()
            if not count.isdigit() and count != "":
                print(f"Warning: Invalid miss count format: {miss_count}")
                return
            
            self.miss_count = count
            self.missCountChanged.emit(self.miss_count)
            print(f"Miss count updated to: {self.miss_count}")
        except Exception as e:
            print(f"Error updating miss count: {e}")

    @pyqtSlot(str)
    def set_time_value(self, time_value):
        """Set the time display value and emit signal to update QML."""
        try:
            # Validate time format (MM:SS)
            time_str = str(time_value).strip()
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    self.time_value = time_str
                    print(f"Emitting timeChanged signal with value: {self.time_value}")
                    self.timeChanged.emit(self.time_value)
                    print(f"Time display updated to: {self.time_value}")
                else:
                    print(f"Warning: Invalid time format: {time_value}")
            else:
                print(f"Warning: Time format should be MM:SS, got: {time_value}")
        except Exception as e:
            print(f"Error updating time value: {e}")

    @pyqtSlot(str)
    def set_score_value(self, score_value):
        """Set the score value and emit signal to update QML."""
        try:
            # Validate score input
            score_str = str(score_value).strip()
            if not score_str.isdigit() and score_str != "":
                print(f"Warning: Invalid score format: {score_value}")
                return
            
            self.score_value = score_str
            print(f"Emitting scoreChanged signal with value: {self.score_value}")
            self.scoreChanged.emit(self.score_value)
            print(f"Score updated to: {self.score_value}")
        except Exception as e:
            print(f"Error updating score: {e}")

    @pyqtSlot(int)
    def set_score_int(self, score_value):
        """Set the score value as integer and emit signal to update QML."""
        self.set_score_value(str(score_value))

    @pyqtSlot(str)
    def set_team_name(self, team_name):
        """Set the team name and emit signal to update QML."""
        try:
            # Validate team name
            name = str(team_name).strip()
            
            
            self.team_name = name
            self.teamNameChanged.emit(self.team_name)
            print(f"Team name updated to: {self.team_name}")
        except Exception as e:
            print(f"Error updating team name: {e}")

    # Timer control methods
    @pyqtSlot(int)
    def set_timer_seconds(self, seconds):
        """Set timer in seconds and update display."""
        try:
            # Validate input
            if not isinstance(seconds, int) or seconds < 0:
                print(f"Warning: Invalid timer seconds: {seconds}. Must be non-negative integer.")
                return
            
            self.timer_seconds = seconds
            self.total_time = seconds
            
            # Format time as MM:SS
            minutes = self.timer_seconds // 60
            secs = self.timer_seconds % 60
            time_str = f"{minutes:02d}:{secs:02d}"
            
            self.set_time_value(time_str)
            self.timerValueChanged.emit(self.timer_seconds, 0.0)
            print(f"Timer set to: {time_str} ({seconds} seconds)")
        except Exception as e:
            print(f"Error setting timer seconds: {e}")

    @pyqtSlot()
    def start_countdown(self):
        """Start the countdown timer."""
        if not self.timer_running:
            self.timer_running = True
            self.timer.start()
            self.countdownStarted.emit()
            # Emit initial timer value to sync QML
            progress = ((self.total_time - self.timer_seconds) / self.total_time) * 100
            self.timerValueChanged.emit(self.timer_seconds, progress)
            print(f"Countdown started - Timer: {self.timer_seconds}s, Progress: {progress:.1f}%")

    @pyqtSlot()
    def stop_countdown(self):
        """Stop the countdown timer."""
        if self.timer_running:
            self.timer_running = False
            self.timer.stop()
            self.countdownStopped.emit()
            print("Countdown stopped")

    @pyqtSlot()
    def reset_timer(self):
        """Reset timer to initial value."""
        self.set_timer_seconds(self.total_time)
        self.stop_countdown()
        print("Timer reset")

    def update_timer(self):
        """Internal method to update timer countdown."""
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            progress = ((self.total_time - self.timer_seconds) / self.total_time) * 100
            
            # Format time as MM:SS
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Update display
            self.set_time_value(time_str)
            self.timerValueChanged.emit(self.timer_seconds, progress)
            
            print(f"Timer: {time_str} ({self.timer_seconds}s, {progress:.1f}%)")
        else:
            # Timer finished
            self.stop_countdown()
            print("Timer finished!")
    
    @pyqtSlot(int)
    def update_timer_countdown(self, seconds_remaining):
        """Update timer countdown from external source."""
        try:
            self.timer_seconds = seconds_remaining
            progress = ((self.total_time - self.timer_seconds) / self.total_time) * 100
            
            # Format time as MM:SS
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Update display
            self.set_time_value(time_str)
            self.timerValueChanged.emit(self.timer_seconds, progress)
            
            print(f"External timer update: {time_str} ({self.timer_seconds}s, {progress:.1f}%)")
        except Exception as e:
            print(f"Error updating timer countdown: {e}")

    @pyqtSlot(int, bool)
    def sync_timer_state(self, seconds_remaining, is_running):
        """Synchronize timer state with external source (game timer)."""
        try:
            self.timer_seconds = seconds_remaining
            
            # Update internal timer state
            if is_running and not self.timer_running:
                self.timer_running = True
                self.timer.start()
                self.countdownStarted.emit()
            elif not is_running and self.timer_running:
                self.timer_running = False
                self.timer.stop()
                self.countdownStopped.emit()
            
            # Calculate progress
            progress = ((self.total_time - self.timer_seconds) / self.total_time) * 100
            
            # Format time as MM:SS
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Update display
            self.set_time_value(time_str)
            self.timerValueChanged.emit(self.timer_seconds, progress)
            
            print(f"Timer synced: {time_str} ({self.timer_seconds}s, {progress:.1f}%, running: {is_running})")
        except Exception as e:
            print(f"Error syncing timer state: {e}")

    # Getter methods
    @pyqtSlot()
    def get_correct_count(self):
        """Get current correct count."""
        return self.correct_count
    @pyqtSlot()
    def get_wrong_count(self):
        """Get current wrong count."""
        return self.wrong_count
    @pyqtSlot()
    def get_miss_count(self):
        """Get current miss count."""
        return self.miss_count

    @pyqtSlot()
    def get_time_value(self):
        """Get current time value."""
        return self.time_value

    @pyqtSlot()
    def get_score_value(self):
        """Get current score value."""
        return self.score_value

    @pyqtSlot()
    def get_team_name(self):
        """Get current team name."""
        return self.team_name

    @pyqtSlot()
    def get_timer_seconds(self):
        """Get current timer seconds."""
        return self.timer_seconds

    @pyqtSlot()
    def is_timer_running(self):
        """Check if timer is running."""
        return self.timer_running

    @pyqtSlot()
    def reset_to_defaults(self):
        """Reset all values to defaults."""
        self.set_correct_count("0")
        self.set_wrong_count("0")
        self.set_miss_count("0")
        self.set_score_value("2300")
        self.set_team_name("Team Name")
        self.set_timer_seconds(121)
        self.stop_countdown()
        print("Reset to default values")

    @pyqtSlot()
    def force_timer_sync(self):
        """Force synchronization of timer display with current state."""
        try:
            # Emit current timer state
            progress = ((self.total_time - self.timer_seconds) / self.total_time) * 100 if self.total_time > 0 else 0
            
            # Format time as MM:SS
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Update display
            self.set_time_value(time_str)
            self.timerValueChanged.emit(self.timer_seconds, progress)
            
            print(f"Timer sync forced: {time_str} ({self.timer_seconds}s, {progress:.1f}%, running: {self.timer_running})")
        except Exception as e:
            print(f"Error forcing timer sync: {e}")

    @pyqtSlot()
    def get_game_state(self):
        """Get current game state as dictionary."""
        return {
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'miss_count': self.miss_count,
            'time_value': self.time_value,
            'score_value': self.score_value,
            'team_name': self.team_name,
            'timer_seconds': self.timer_seconds,
            'timer_running': self.timer_running
        }

    @pyqtSlot()
    def force_qml_refresh(self):
        """Force QML to refresh all displayed values by re-emitting all signals."""
        try:
            print("Forcing QML refresh - re-emitting all signals...")
            self.correctCountChanged.emit(self.correct_count)
            self.wrongCountChanged.emit(self.wrong_count)
            self.missCountChanged.emit(self.miss_count)
            self.timeChanged.emit(self.time_value)
            self.scoreChanged.emit(self.score_value)
            self.teamNameChanged.emit(self.team_name)
            
            # Also emit timer signals
            progress = ((self.total_time - self.timer_seconds) / self.total_time) * 100 if self.total_time > 0 else 0
            self.timerValueChanged.emit(self.timer_seconds, progress)
            
            print("QML refresh signals emitted successfully")
        except Exception as e:
            print(f"Error forcing QML refresh: {e}")

    @pyqtSlot('QVariant')
    def set_game_state(self, state_dict):
        """Set complete game state from dictionary."""
        if 'correct_count' in state_dict:
            self.set_correct_count(state_dict['correct_count'])
        if 'wrong_count' in state_dict:
            self.set_wrong_count(state_dict['wrong_count'])
        if 'miss_count' in state_dict:
            self.set_miss_count(state_dict['miss_count'])
        if 'score_value' in state_dict:
            self.set_score_value(state_dict['score_value'])
        if 'team_name' in state_dict:
            self.set_team_name(state_dict['team_name'])
        if 'timer_seconds' in state_dict:
            self.set_timer_seconds(state_dict['timer_seconds'])
        if 'timer_running' in state_dict and state_dict['timer_running']:
            self.start_countdown()
        elif 'timer_running' in state_dict and not state_dict['timer_running']:
            self.stop_countdown()
        
        print("Game state updated from dictionary")

