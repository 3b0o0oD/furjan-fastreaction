"""
Audio Service for Game Applications
Provides threaded audio playback using pygame.mixer with multiple sound interfaces
Optimized for low-latency game audio on embedded systems (Jetson)
"""

import os
import sys
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
import pygame.mixer

from .logger import get_logger


class AudioPlayer:
    """
    Individual audio player that wraps pygame.mixer for instant playback
    Sounds are pre-loaded into RAM for zero-latency playback
    """
    
    def __init__(self, audio_file: str, loop: bool = False, volume: float = 1.0):
        self.logger = get_logger(f"{__name__}.AudioPlayer")
        
        self.audio_file = audio_file
        self.loop = loop
        self.volume = max(0.0, min(1.0, volume / 100.0))  # Convert 0-100 to 0.0-1.0
        self.should_loop = loop
        
        # pygame.mixer Sound object (pre-loaded in RAM)
        self.sound = None
        self.channel = None  # Dedicated channel for this sound
        
        # Load audio file into memory
        self._load_audio_file()
        
    def _load_audio_file(self):
        """Load the audio file into RAM for instant playback"""
        # Convert to absolute path if it's relative
        if not os.path.isabs(self.audio_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            game_dir = os.path.dirname(script_dir)
            self.audio_file = os.path.join(game_dir, self.audio_file)
            
        if not os.path.exists(self.audio_file):
            self.logger.error(f"Audio file not found: {self.audio_file}")
            return
            
        try:
            # Load sound into memory (instant playback later)
            self.sound = pygame.mixer.Sound(self.audio_file)
            self.sound.set_volume(self.volume)
            self.logger.debug(f"Loaded audio into RAM: {self.audio_file}")
        except Exception as e:
            self.logger.error(f"Failed to load audio file {self.audio_file}: {e}")
            
    def play(self):
        """Start playback (instant, no buffering needed)"""
        if not self.sound:
            self.logger.warning(f"Cannot play - sound not loaded: {self.audio_file}")
            return
            
        try:
            # Play with loop count: -1 = infinite loop, 0 = play once
            loops = -1 if self.should_loop else 0
            self.channel = self.sound.play(loops=loops)
            self.logger.debug(f"Playing: {self.audio_file} (loop: {self.should_loop})")
        except Exception as e:
            self.logger.error(f"Error playing sound: {e}")
            
    def stop(self):
        """Stop playback"""
        if self.sound:
            self.sound.stop()
            self.logger.debug(f"Stopped: {self.audio_file}")
            
    def pause(self):
        """Pause playback"""
        if self.channel:
            self.channel.pause()
            
    def unpause(self):
        """Resume playback"""
        if self.channel:
            self.channel.unpause()
            
    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        self.volume = max(0.0, min(1.0, volume / 100.0))
        if self.sound:
            self.sound.set_volume(self.volume)
            self.logger.debug(f"Set volume to {volume}% for: {self.audio_file}")
            
    def is_playing(self) -> bool:
        """Check if currently playing"""
        if self.channel:
            return self.channel.get_busy()
        return False
        
    def set_loop(self, loop: bool):
        """Enable or disable looping"""
        self.loop = loop
        self.should_loop = loop
        # If currently playing, restart with new loop setting
        if self.is_playing():
            self.stop()
            self.play()
        self.logger.debug(f"Set loop to {loop} for: {self.audio_file}")


class AudioService(QObject):
    """
    Audio Service that manages multiple audio players using pygame.mixer
    All sounds are pre-loaded into RAM for instant, zero-latency playback
    """
    
    # Signals
    service_ready = pyqtSignal()
    service_error = pyqtSignal(str)
    
    def __init__(self, audio_files: Optional[Dict[str, str]] = None):
        super().__init__()
        self.logger = get_logger(f"{__name__}.AudioService")
        
        # Default audio files
        self.audio_files = audio_files or {
            'continuous': 'Assets/mp3/2066.wav',
            'inactive_game': 'Assets/mp3/game-music-loop-inactive.mp3',
            'active_game': 'Assets/mp3/game-music-loop-active.mp3',
            'miss_sound': 'Assets/mp3/miss.mp3',
            'ok_sound': 'Assets/mp3/game-music-loop-active.mp3',
            'crct_sound': 'Assets/mp3/correct.mp3',
            'mstk_sound': 'Assets/mp3/2066.wav'
        }
        
        # Convert relative paths to absolute paths
        self.audio_files = self._resolve_audio_paths(self.audio_files)
        
        # Audio players
        self.players: Dict[str, AudioPlayer] = {}
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        # Initialize pygame.mixer
        self._initialize_pygame()
        
        # Initialize players
        self._initialize_players()
        
    def _initialize_pygame(self):
        """Initialize pygame.mixer with optimal settings for low latency"""
        try:
            # Initialize pygame.mixer with optimal settings
            # frequency=44100, size=-16 (16-bit signed), channels=2 (stereo), buffer=512 (low latency)
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            # Set number of mixing channels (max simultaneous sounds)
            pygame.mixer.set_num_channels(16)
            
            self.logger.info("🎵 pygame.mixer initialized (44.1kHz, 16-bit, stereo, 512-byte buffer)")
        except Exception as e:
            error_msg = f"Failed to initialize pygame.mixer: {e}"
            self.logger.error(error_msg)
            self.service_error.emit(error_msg)
            raise
            
    def _resolve_audio_paths(self, audio_files: Dict[str, str]) -> Dict[str, str]:
        """Convert relative paths to absolute paths"""
        resolved_files = {}
        for name, file_path in audio_files.items():
            if not os.path.isabs(file_path):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                game_dir = os.path.dirname(script_dir)
                resolved_files[name] = os.path.join(game_dir, file_path)
            else:
                resolved_files[name] = file_path
        return resolved_files
        
    def _initialize_players(self):
        """Initialize all audio players (pre-load sounds into RAM)"""
        try:
            # Continuous sound player (looped)
            if 'continuous' in self.audio_files:
                self.players['continuous'] = AudioPlayer(
                    self.audio_files['continuous'],
                    loop=True,
                    volume=50
                )
                
            # Inactive game sound player
            if 'inactive_game' in self.audio_files:
                self.players['inactive_game'] = AudioPlayer(
                    self.audio_files['inactive_game'],
                    loop=True,
                    volume=70
                )
                
            # Active game sound player
            if 'active_game' in self.audio_files:
                self.players['active_game'] = AudioPlayer(
                    self.audio_files['active_game'],
                    loop=True,
                    volume=80
                )
            
            # One-shot sound effect players (no loop)
            if 'miss_sound' in self.audio_files:
                self.players['miss_sound'] = AudioPlayer(
                    self.audio_files['miss_sound'],
                    loop=False,
                    volume=90
                )
                
            if 'ok_sound' in self.audio_files:
                self.players['ok_sound'] = AudioPlayer(
                    self.audio_files['ok_sound'],
                    loop=False,
                    volume=85
                )
                
            if 'crct_sound' in self.audio_files:
                self.players['crct_sound'] = AudioPlayer(
                    self.audio_files['crct_sound'],
                    loop=False,
                    volume=85
                )
                
            if 'mstk_sound' in self.audio_files:
                self.players['mstk_sound'] = AudioPlayer(
                    self.audio_files['mstk_sound'],
                    loop=False,
                    volume=90
                )
                
            self.is_initialized = True
            self.logger.info(f"✅ Audio service initialized - {len(self.players)} sounds pre-loaded into RAM")
            self.service_ready.emit()
            
        except Exception as e:
            error_msg = f"Failed to initialize audio service: {e}"
            self.logger.error(error_msg)
            self.service_error.emit(error_msg)
            
    # Public API Methods
    
    def start_service(self):
        """Start the audio service"""
        if not self.is_initialized:
            self.logger.error("Cannot start service: not initialized")
            return False
            
        self.is_running = True
        self.logger.info("Audio service started")
        return True
        
    def stop_service(self):
        """Stop the audio service and all players"""
        self.is_running = False
        
        # Stop all players
        for name, player in self.players.items():
            player.stop()
            
        self.logger.info("Audio service stopped")
        
    # Continuous Sound Interface
    
    @pyqtSlot()
    def play_continuous_sound(self):
        """Start playing continuous background sound"""
        if 'continuous' in self.players:
            self.players['continuous'].play()
            self.logger.info("Started continuous sound")
        else:
            self.logger.warning("Continuous sound player not available")
    
    @pyqtSlot()
    def stop_continuous_sound(self):
        """Stop continuous background sound"""
        if 'continuous' in self.players:
            self.players['continuous'].stop()
            self.logger.info("Stopped continuous sound")
    
    @pyqtSlot(int)
    def set_continuous_volume(self, volume: int):
        """Set volume for continuous sound (0-100)"""
        if 'continuous' in self.players:
            self.players['continuous'].set_volume(volume)
            
    # Inactive Game Sound Interface
    
    @pyqtSlot()
    def play_inactive_game_sound(self):
        """Play sound for inactive game state (instant, pre-loaded)"""
        if 'inactive_game' in self.players:
            self.players['inactive_game'].play()
            self.logger.info("Started inactive game sound")
        else:
            self.logger.warning("Inactive game sound player not available")
    
    @pyqtSlot()
    def stop_inactive_game_sound(self):
        """Stop inactive game sound"""
        if 'inactive_game' in self.players:
            self.players['inactive_game'].stop()
            self.logger.info("Stopped inactive game sound")
    
    @pyqtSlot(int)
    def set_inactive_game_volume(self, volume: int):
        """Set volume for inactive game sound (0-100)"""
        if 'inactive_game' in self.players:
            self.players['inactive_game'].set_volume(volume)
            
    # Active Game Sound Interface
    
    @pyqtSlot()
    def play_active_game_sound(self):
        """Play sound for active game state (instant, pre-loaded)"""
        if 'active_game' in self.players:
            self.players['active_game'].play()
            self.logger.info("Started active game sound")
        else:
            self.logger.warning("Active game sound player not available")
    
    @pyqtSlot()
    def stop_active_game_sound(self):
        """Stop active game sound"""
        if 'active_game' in self.players:
            self.players['active_game'].stop()
            self.logger.info("Stopped active game sound")
    
    @pyqtSlot(int)
    def set_active_game_volume(self, volume: int):
        """Set volume for active game sound (0-100)"""
        if 'active_game' in self.players:
            self.players['active_game'].set_volume(volume)
    
    # One-Shot Sound Effects Interface
    
    @pyqtSlot()
    def play_miss_sound(self):
        """Play miss sound effect (instant, pre-loaded)"""
        if 'miss_sound' in self.players:
            self.players['miss_sound'].play()
            self.logger.info("Played miss sound effect")
        else:
            self.logger.warning("Miss sound player not available")
    
    @pyqtSlot()
    def play_ok_sound(self):
        """Play OK sound effect (instant, pre-loaded)"""
        if 'ok_sound' in self.players:
            self.players['ok_sound'].play()
            self.logger.info("Played OK sound effect")
        else:
            self.logger.warning("OK sound player not available")
    
    @pyqtSlot()
    def play_crct_sound(self):
        """Play correct sound effect (instant, pre-loaded)"""
        if 'crct_sound' in self.players:
            self.players['crct_sound'].play()
            self.logger.info("✅ Played correct sound effect")
        else:
            self.logger.error("❌ Correct sound player not available")
    
    @pyqtSlot()
    def play_mstk_sound(self):
        """Play mistake sound effect (instant, pre-loaded)"""
        if 'mstk_sound' in self.players:
            self.players['mstk_sound'].play()
            self.logger.info("✅ Played mistake sound effect")
        else:
            self.logger.error("❌ Mistake sound player not available")
            
    # General Control Methods
    
    @pyqtSlot()
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        for name, player in self.players.items():
            player.stop()
        self.logger.info("Stopped all sounds")
    
    @pyqtSlot()
    def pause_all_sounds(self):
        """Pause all currently playing sounds"""
        for name, player in self.players.items():
            player.pause()
        self.logger.info("Paused all sounds")
        
    def is_player_playing(self, player_name: str) -> bool:
        """Check if a specific player is currently playing"""
        if player_name in self.players:
            return self.players[player_name].is_playing()
        return False
        
    def get_available_players(self) -> list:
        """Get list of available player names"""
        return list(self.players.keys())
        
    @pyqtSlot(str, str)
    def update_audio_file(self, player_name: str, audio_file: str):
        """Update the audio file for a specific player"""
        resolved_audio_file = self._resolve_audio_paths({player_name: audio_file})[player_name]
        
        if player_name in self.players and os.path.exists(resolved_audio_file):
            # Stop current player
            self.players[player_name].stop()
            
            # Create new player with new file
            self.players[player_name] = AudioPlayer(
                resolved_audio_file,
                loop=(player_name in ['continuous', 'inactive_game', 'active_game']),
                volume=self.players[player_name].volume * 100
            )
            
            self.logger.info(f"Updated audio file for {player_name}: {resolved_audio_file}")
        else:
            self.logger.warning(f"Cannot update audio file for {player_name}: file not found or player not available")
    
    @pyqtSlot(str, bool)
    def set_player_loop(self, player_name: str, loop: bool):
        """Enable or disable looping for a specific player"""
        if player_name in self.players:
            self.players[player_name].set_loop(loop)
            self.logger.info(f"Set loop to {loop} for player: {player_name}")
        else:
            self.logger.warning(f"Player not found: {player_name}")
            
    def get_player_loop(self, player_name: str) -> bool:
        """Get the loop setting for a specific player"""
        if player_name in self.players:
            return self.players[player_name].loop
        return False


class AudioServiceThread(QThread):
    """
    Thread wrapper for AudioService to run in background
    Note: pygame.mixer is thread-safe, simpler than QMediaPlayer
    """
    
    # Signals
    service_ready = pyqtSignal()
    service_error = pyqtSignal(str)
    
    def __init__(self, audio_files: Optional[Dict[str, str]] = None):
        super().__init__()
        self.audio_files = audio_files
        self.audio_service = None
        
    def run(self):
        """Thread entry point - create audio service in this thread"""
        # Create audio service in the thread context
        self.audio_service = AudioService(self.audio_files)
        
        # Connect service signals to thread signals
        self.audio_service.service_ready.connect(self.service_ready.emit)
        self.audio_service.service_error.connect(self.service_error.emit)
        
        # Start the audio service
        self.audio_service.start_service()
        
        # Emit ready signal
        self.service_ready.emit()
        
        # Keep thread alive
        self.exec_()
        
    def stop(self):
        """Stop the audio service and thread"""
        if self.audio_service:
            self.audio_service.stop_service()
        self.quit()
        self.wait()
        
    # Delegate methods to audio service with THREAD-SAFE Qt meta-object calls
    def play_continuous_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "play_continuous_sound", Qt.QueuedConnection)
        
    def stop_continuous_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "stop_continuous_sound", Qt.QueuedConnection)
        
    def set_continuous_volume(self, volume: int):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(self.audio_service, "set_continuous_volume", Qt.QueuedConnection, Q_ARG(int, volume))
        
    def play_inactive_game_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "play_inactive_game_sound", Qt.QueuedConnection)
        
    def stop_inactive_game_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "stop_inactive_game_sound", Qt.QueuedConnection)
        
    def set_inactive_game_volume(self, volume: int):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(self.audio_service, "set_inactive_game_volume", Qt.QueuedConnection, Q_ARG(int, volume))
        
    def play_active_game_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "play_active_game_sound", Qt.QueuedConnection)
        
    def stop_active_game_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "stop_active_game_sound", Qt.QueuedConnection)
        
    def set_active_game_volume(self, volume: int):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(self.audio_service, "set_active_game_volume", Qt.QueuedConnection, Q_ARG(int, volume))
    
    # One-shot sound effects delegate methods (THREAD-SAFE)
    def play_miss_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "play_miss_sound", Qt.QueuedConnection)
        
    def play_ok_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "play_ok_sound", Qt.QueuedConnection)
        
    def play_crct_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "play_crct_sound", Qt.QueuedConnection)
        
    def play_mstk_sound(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "play_mstk_sound", Qt.QueuedConnection)
        
    def stop_all_sounds(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "stop_all_sounds", Qt.QueuedConnection)
        
    def pause_all_sounds(self):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self.audio_service, "pause_all_sounds", Qt.QueuedConnection)
        
    def is_player_playing(self, player_name: str):
        # Read-only method - safe to call directly
        if self.audio_service:
            return self.audio_service.is_player_playing(player_name)
        return False
        
    def get_available_players(self):
        # Read-only method - safe to call directly
        if self.audio_service:
            return self.audio_service.get_available_players()
        return []
        
    def update_audio_file(self, player_name: str, audio_file: str):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(self.audio_service, "update_audio_file", Qt.QueuedConnection, 
                                    Q_ARG(str, player_name), Q_ARG(str, audio_file))
        
    def set_player_loop(self, player_name: str, loop: bool):
        if self.audio_service:
            from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(self.audio_service, "set_player_loop", Qt.QueuedConnection,
                                    Q_ARG(str, player_name), Q_ARG(bool, loop))
        
    def get_player_loop(self, player_name: str):
        # Read-only method - safe to call directly
        if self.audio_service:
            return self.audio_service.get_player_loop(player_name)
        return False
    
    def are_critical_players_ready(self):
        """Check if all critical audio players are ready for playback"""
        # With pygame.mixer, sounds are pre-loaded in RAM, always ready
        return True if self.audio_service else False


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    
    app = QApplication(sys.argv)
    
    # Create audio service thread
    audio_files = {
        'continuous': 'Assets/mp3/2066.wav',
        'inactive_game': 'Assets/mp3/game-music-loop-inactive.mp3',
        'active_game': 'Assets/mp3/game-music-loop-active.mp3',
        'crct_sound': 'Assets/mp3/correct.mp3',
        'mstk_sound': 'Assets/mp3/2066.wav'
    }
    
    audio_thread = AudioServiceThread(audio_files)
    
    # Connect signals
    audio_thread.service_ready.connect(lambda: print("✅ Audio service ready!"))
    audio_thread.service_error.connect(lambda error: print(f"❌ Audio service error: {error}"))
    
    # Start the thread
    audio_thread.start()
    print("🚀 Starting audio service thread...")
    
    # Test sounds after a delay using QTimer
    QTimer.singleShot(1000, audio_thread.play_inactive_game_sound)
    QTimer.singleShot(3000, audio_thread.play_active_game_sound)
    QTimer.singleShot(4000, audio_thread.play_crct_sound)
    QTimer.singleShot(5000, audio_thread.play_mstk_sound)
    QTimer.singleShot(7000, audio_thread.stop_all_sounds)
    QTimer.singleShot(8000, app.quit)
    
    sys.exit(app.exec_())
