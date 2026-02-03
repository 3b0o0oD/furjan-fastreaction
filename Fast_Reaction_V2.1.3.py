'''
Updates on 15/10/2025:
- Integrated New GUI

'''


import csv
from datetime import datetime
from re import T
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import ConnectionError, Timeout, RequestException
import time   
import numpy as np
import json
from PyQt5.QtGui import QPainter, QColor, QFont,QFontDatabase ,QImage, QPixmap,QPen, QPainterPath , QPolygonF, QBrush, QRadialGradient, QLinearGradient, QSurfaceFormat, QMovie
from PyQt5.QtCore import QTimer,Qt, pyqtSignal, pyqtSlot ,QThread , QTime,QSize,QRectF,QPointF, QUrl, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget ,QGridLayout,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QTableWidget,QTableWidgetItem,QHeaderView,QFrame
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQml import qmlRegisterType
import math 
import requests , os ,time

from PyQt5 import QtCore, QtGui, QtWidgets
import paho.mqtt.client as mqtt
# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# import New Sound Service
from utils.audio_service import AudioPlayer
from utils.audio_service import AudioService
from utils.audio_service import AudioServiceThread

from leaderboard_enhanced_backend import EnhancedLeaderboardBackend
from teamscore_backend import TeamScoreBackend
from Active_screen_FastReaction import FastReactionBackend

# Register the FastReactionBackend class as a QML type
qmlRegisterType(FastReactionBackend, "FastReactionBackend", 1, 0, "FastReactionBackend")

import sys

# Import our new API and configuration system
from api.game_api import GameAPI
from config import config
from utils.logger import get_logger

# Setup logging
logger = get_logger(__name__)

# Load configuration
game_config = config.settings.game
ui_config = config.settings.ui



# Initialize global variables
final_screen_timer_idle = game_config.final_screen_timer
count = 0
TimerValue = game_config.timer_value
global scaled
scaled = 1
scored = 0
correct_count = 0
miss_count = 0
wrong_count = 0
last_team_name = ""
last_score = 0

# Global variables for last player data
last_player_name = ""
last_player_score = 0
last_player_weighted_points = 0
last_player_rank = 0

serial_scoring_active = False
list_players_name = []
list_players_score = [0,0,0,0,0]
list_players_id = []
list_top5_FastReaction = []
RemainingTime = 0
teamName = ""
homeOpened = False

import numpy as np
gamefinished = False
gameStarted = False
firstDetected = False

response = None


class SimpleSerialThread(QThread):
    """
    Enhanced Serial Thread for Fast Reaction Game
    Reads simple data lines from serial port with automatic reconnection
    """
    # Qt signals for thread communication
    data_received = pyqtSignal(str)  # Emitted when data is received
    # connection_status_changed = pyqtSignal(bool)  # Emitted when connection status changes
    # error_occurred = pyqtSignal(str)  # Emitted when an error occurs
    # 
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.port = config.port
        self.baudrate = config.baudrate
        self.timeout = config.timeout
        self.auto_reconnect = config.auto_reconnect
        self.reconnect_interval = config.reconnect_interval
        self.max_reconnect_attempts = config.max_reconnect_attempts
        
        self.serial_connection = None
        self.is_monitoring = False
        self.connected = False
        self.should_stop = False
        self.reconnect_attempts = 0
        
        logger.info(f" SimpleSerial initialized for port: {self.port} (baudrate: {self.baudrate})")
    
    def connect(self) -> bool:
        """Establish serial connection"""
        try:
            import serial
            
            # Close existing connection if any
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connected = True
            self.reconnect_attempts = 0  # Reset reconnect attempts on successful connection
            # self.connection_status_changed.emit(True)
            logger.info(f" Serial connected to {self.port}")
            return True
        except Exception as e:
            self.connected = False
            # self.connection_status_changed.emit(False)
            error_msg = f" Failed to connect to {self.port}: {e}"
            logger.error(error_msg)
            # self.error_occurred.emit(error_msg)
            return False
    
    def disconnect(self):
        """Close serial connection"""
        self.is_monitoring = False
        self.should_stop = True  # Signal thread to stop
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                self.connected = False
                # self.connection_status_changed.emit(False)
                logger.info(f" Serial disconnected from {self.port}")
            except Exception as e:
                logger.warning(f"Error disconnecting serial: {e}")
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to serial port"""
        if self.should_stop:
            return False
            
        self.reconnect_attempts += 1
        max_attempts = self.max_reconnect_attempts
        
        if max_attempts > 0 and self.reconnect_attempts > max_attempts:
            logger.error(f" Maximum reconnection attempts ({max_attempts}) reached for {self.port}")
            # self.error_occurred.emit(f"Maximum reconnection attempts reached")
            return False
        
        logger.info(f" Attempting to reconnect to {self.port} (attempt {self.reconnect_attempts})")
        return self.connect()
    
    def force_reconnect(self) -> bool:
        """Force a reconnection by resetting attempt counter"""
        self.reconnect_attempts = 0
        return self.reconnect()
    
    from typing import Optional

    def read_line(self) -> Optional[str]:

        """Read a single line from serial port - BIDIRECTIONAL"""
        if not self.serial_connection or not self.serial_connection.is_open:
            return None
        
        try:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    logger.debug(f"[BIDIRECTIONAL] RECEIVED: {line}")
                return line if line else None
        except Exception as e:
            logger.warning(f"️  Error reading serial data: {e}")
            return None
        
        return None
    
    def send_data(self, data: str) -> bool:
        """Send data via serial port - BIDIRECTIONAL COMMUNICATION"""
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.warning("️  Cannot send data: serial connection not open")
            return False
        
        try:
            # BIDIRECTIONAL: Send data while still able to receive
            # logger.info()
            # self.serial_connection.write(data.encode("utf-8"))
            data_bytes = bytearray(data, 'utf-8')
            self.serial_connection.write(data_bytes)
            self.serial_connection.flush()  # Ensure data is sent immediately
            
            logger.debug(f"📤 [BIDIRECTIONAL] SENT: {data.strip()}")
            return True
            
        except Exception as e:
            logger.error(f" Error sending serial data: {e}")
            return False
    
    def start_monitoring(self):
        """Start monitoring serial data and send start signal - WAIT FOR OK RESPONSE"""
        self.is_monitoring = True
        
        # BIDIRECTIONAL: Send "Start" signal via serial and wait for OK response
        if self.send_data("Start\n"):
            logger.info("📤 Serial monitoring started - sent 'Start' signal, waiting for 'OK' response...")
            
            # Wait for OK response for up to 5 seconds
            import time
            start_time = time.time()
            ok_received = False
            
            
            if self.serial_connection and self.serial_connection.in_waiting > 0:
                try:
                    response = self.serial_connection.readline().strip()
                    if response:
                        logger.info(f"📥 Received response: '{response}'")
                        if response.upper() == "OK":
                            ok_received = True
                            logger.info("✅ Received 'OK' - serial communication confirmed!")
                            
                        else:
                            logger.warning(f"⚠️ Expected 'OK' but received: '{response}'")
                except Exception as e:
                    logger.error(f"❌ Error reading OK response: {e}")
                        
                
            
            if not ok_received:
                logger.warning("⚠️ Did not receive 'OK' response within 5 seconds - continuing anyway")
        else:
            logger.warning("️❌ Serial monitoring started but failed to send start signal")
        
        logger.info("🚀 Serial monitoring started (BIDIRECTIONAL) - ready to receive scores and events")
    
    def stop_monitoring(self):
        """Stop monitoring serial data and send stop signal - WAIT FOR OK RESPONSE"""
        self.is_monitoring = False
        
        # BIDIRECTIONAL: Send "Stop" signal via serial and wait for OK response
        if self.send_data("Stop\n\n"):
            logger.info("📤 Serial monitoring stopped - sent 'Stop' signal, waiting for 'OK' response...")
            
            # Wait for OK response for up to 3 seconds
            import time
            start_time = time.time()
            ok_received = False
            
            while time.time() - start_time < .1 and not ok_received:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    try:
                        response = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                        if response:
                            logger.info(f"📥 Received response: '{response}'")
                            if response.upper() == "OK":
                                ok_received = True
                                logger.info("✅ Received 'OK' - stop confirmed!")
                                break
                            else:
                                logger.warning(f"⚠️ Expected 'OK' but received: '{response}'")
                    except Exception as e:
                        logger.error(f"❌ Error reading OK response: {e}")
                        break
                time.sleep(0.1)
            
            if not ok_received:
                logger.warning("⚠️ Did not receive 'OK' response for stop within 3 seconds")
        else:
            logger.warning("️❌ Serial monitoring stopped but failed to send stop signal")
        
        logger.info("🛑 Serial monitoring stopped (BIDIRECTIONAL)")
    
    def run(self):
        """Main thread loop for reading serial data with automatic reconnection"""
        logger.info(" SimpleSerial thread started")
        
        # Try initial connection
        if not self.connect():
            if self.auto_reconnect:
                logger.info(" Initial connection failed, will attempt reconnection")
            else:
                logger.error(" Initial connection failed and auto-reconnect is disabled")
                return
        
        while not self.should_stop:
            try:
                if self.connected and self.is_monitoring:
                    data = self.read_line()
                    # data expected:
                    # Sc{score}\n
                    # Mstk\n
                    # Ok\n
                    # Crct\n
                    # Miss\n
                    if data:
                        logger.info(f" Serial data received: {data}")
                        if data.lower().startswith("mstk"):
                            
                            global wrong_count
                            wrong_count += 1
                           
                                
                        elif data.lower().startswith("crct"):
                            
                            global correct_count
                            correct_count += 1
                            
                        elif data.lower().startswith("miss"):
                           
                            global miss_count
                            miss_count += 1        
                        
                        self.data_received.emit(data)
                elif not self.connected and self.auto_reconnect:
                    # Attempt reconnection
                    logger.debug(f" Connection lost, waiting {self.reconnect_interval}s before reconnection attempt")
                    self.msleep(self.reconnect_interval * 1000)  # Convert to milliseconds
                    
                    if not self.should_stop:  # Check again after sleep
                        if not self.reconnect():
                            # If reconnect failed and we've exceeded max attempts, stop trying
                            if (self.max_reconnect_attempts > 0 and 
                                self.reconnect_attempts >= self.max_reconnect_attempts):
                                logger.error(" Giving up on reconnection attempts")
                                break
                
                # Adaptive delay to prevent excessive CPU usage while maintaining responsiveness
                # Reduce delay when actively receiving data to minimize sound latency
                # if self.connected and self.is_monitoring:
                #     # Check if we have data waiting - if so, use shorter delay
                #     if self.serial_connection and self.serial_connection.in_waiting > 0:
                #         self.msleep(5)  # Very short delay when data is available
                #     else:
                #         self.msleep(20)  # Slightly longer delay when no data
                # else:
                #     self.msleep(50)  # Normal delay when not monitoring
                
            except Exception as e:
                logger.error(f" Error in serial thread loop: {e}")
                # self.error_occurred.emit(str(e))
                self.connected = False
                # self.connection_status_changed.emit(False)
                
                # If auto-reconnect is disabled, break the loop
                if not self.auto_reconnect:
                    break
        
        # Cleanup
        self.disconnect()
        logger.info(" SimpleSerial thread stopped")
    
    def stop(self):
        """Safely stop the serial thread"""
        logger.debug(" Stopping SimpleSerial thread...")
        
        self.should_stop = True
        self.is_monitoring = False
        self.connected = False
        
        # Close serial connection
        self.disconnect()
        
        # Wait for thread to finish
        if self.isRunning():
            if not self.wait(3000):  # Wait 3 seconds
                logger.warning("️  SimpleSerial thread did not finish gracefully")
                self.terminate()
                self.wait()
        
        logger.debug(" SimpleSerial thread stopped successfully")
    
    def send_score_update(self, score: int) -> bool:
        """Send score update via serial - BIDIRECTIONAL"""
        return self.send_data(f"Sc{score}")
    
    def send_game_event(self, event: str) -> bool:
        """Send game event (Miss, Ok, Crct, Mstk) via serial - BIDIRECTIONAL"""
        return self.send_data(event)
    
    def get_status(self) -> dict:
        """Get current connection status and configuration"""
        return {
            'connected': self.connected,
            'monitoring': self.is_monitoring,
            'port': self.port,
            'baudrate': self.baudrate,
            'auto_reconnect': self.auto_reconnect,
            'reconnect_attempts': self.reconnect_attempts,
            'max_reconnect_attempts': self.max_reconnect_attempts,
            'should_stop': self.should_stop
        }
    
    

class MqttThread(QThread):
    message_signal = pyqtSignal(str)
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    restart_signal = pyqtSignal()
    activate_signal = pyqtSignal()
    deactivate_signal = pyqtSignal()

    def __init__(self, broker='localhost', port=1883):
        super().__init__()
        mqtt_config = config.settings.mqtt
        self.data_topics = mqtt_config.data_topics
        self.control_topics = mqtt_config.control_topics
        self.broker = mqtt_config.broker
        self.port = mqtt_config.port
        # Fix MQTT deprecation warning by using callback_api_version
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.subscribed = False

    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        for topic in self.control_topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg, properties=None):
        print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")

        if msg.topic == "FastReaction/game/start":
            self.handle_start()
        elif msg.topic == "FastReaction/game/Activate":
            self.handle_Activate()
        elif msg.topic == "FastReaction/game/Deactivate":
            self.deactivate_signal.emit()
        elif msg.topic == "FastReaction/game/stop":
            if msg.payload.decode() == "0":
                self.handle_stop()
            elif msg.payload.decode() == "1":
                self.unsubscribe_from_data_topics()
        elif msg.topic == "FastReaction/game/restart":
            print("Game restarted")
            self.handle_restart()
        elif msg.topic == "FastReaction/game/timer":
            global TimerValue
            TimerValue = int(msg.payload.decode())*1000
            print(TimerValue)
            with open("file2.txt", "w") as file:
                file.write(f"{TimerValue}\n")
        elif msg.topic == "FastReaction/game/timerfinal":
            global final_screen_timer_idle
            final_screen_timer_idle = int(msg.payload.decode())*1000
            print(final_screen_timer_idle)
            with open("file.txt", "w") as file:
                file.write(f"{final_screen_timer_idle}\n")
        else:
            if self.subscribed:
                self.handle_data_message(msg)

    def handle_data_message(self, msg):
        data = msg.payload.decode()
        self.message_signal.emit(data)

    def handle_restart(self):
        print("Game restarted")
        self.subscribe_to_data_topics()
        self.restart_signal.emit()     

    def handle_start(self):
        print("Game started")
        self.subscribe_to_data_topics()
        self.start_signal.emit()

    def handle_Activate(self):
        print("Game Activated")
        self.activate_signal.emit()

    def handle_stop(self):
        print("Game stopped")
        self.unsubscribe_from_data_topics()
        self.stop_signal.emit()
   
    def subscribe_to_data_topics(self):
        if not self.subscribed:
            for topic in self.data_topics:
                self.client.subscribe(topic)
            self.subscribed = True

    def unsubscribe_from_data_topics(self):
        if self.subscribed:
            for topic in self.data_topics:
                self.client.unsubscribe(topic)
            self.subscribed = False
    
    def stop(self):
        """Safely stop the MQTT thread and cleanup resources"""
        logger.debug(" Stopping MqttThread...")
        
        try:
            # Unsubscribe from all topics first
            if hasattr(self, 'client') and self.client:
                try:
                    # Unsubscribe from data topics
                    if self.subscribed:
                        for topic in self.data_topics:
                            self.client.unsubscribe(topic)
                        self.subscribed = False
                    
                    # Unsubscribe from control topics
                    for topic in self.control_topics:
                        self.client.unsubscribe(topic)
                    
                    logger.debug(" Unsubscribed from all MQTT topics")
                except Exception as e:
                    logger.warning(f"️  Error unsubscribing from topics: {e}")
                
                try:
                    # Disconnect the MQTT client gracefully
                    self.client.loop_stop()  # Stop the network loop
                    self.client.disconnect()  # Disconnect from broker
                    logger.debug(" MQTT client disconnected")
                except Exception as e:
                    logger.warning(f"️  Error disconnecting MQTT client: {e}")
                
                self.client = None
        
        except Exception as e:
            logger.warning(f"️  Error in MQTT cleanup: {e}")
        
        # Wait for thread to finish gracefully
        if self.isRunning():
            if not self.wait(3000):  # Wait 3 seconds
                logger.warning("️  MqttThread did not finish gracefully")
                # Only terminate as last resort
                self.terminate()
                self.wait()
        
        logger.debug(" MqttThread stopped successfully")
    
    def run(self):
        """Run MQTT client with proper error handling and cleanup support"""
        try:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.connect(self.broker, self.port)
            self.client.loop_forever()  # This will run until loop_stop() is called
        except Exception as e:
            logger.error(f" MQTT thread error: {e}")
        finally:
            logger.debug(" MQTT thread run() method exiting")


class GameManager(QThread):
    """
    Updated GameManager that uses the new GameAPI
    Handles the complete game flow:
    1. Authentication with API
    2. Poll for game initialization 
    3. Poll for game start
    4. Submit final scores
    """
    init_signal = pyqtSignal()
    start_signal = pyqtSignal()
    cancel_signal = pyqtSignal()
    submit_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        logger.info(" GameManager initializing...")
        
        # Initialize the GameAPI
        try:
            self.api = GameAPI()
            logger.info(" GameAPI initialized successfully")
        except Exception as e:
            logger.error(f" Failed to initialize GameAPI: {e}")
            raise
            
        # Game state
        self.game_result_id = None
        self.submit_score_flag = False
        self.playStatus = True
        self.started_flag = False
        self.cancel_flag = False
        self.game_done = True
        
        logger.info(" GameManager initialized successfully")
        
    def run(self):
        """Main game loop following the proper API flow"""
        logger.info(" GameManager starting main loop...")
        
        while self.playStatus:
            try:
                # Step 1: Authenticate
                logger.info(" Step 1: Authenticating...")
                if not hasattr(self, 'api') or self.api is None:
                    logger.error(" GameAPI not initialized")
                    time.sleep(5)
                    continue
                    
                if not self.api.authenticate():
                    logger.error(" Authentication failed, retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                
                # Step 2: Poll for game initialization
                logger.info(" Step 2: Polling for game initialization...")
                if not self._poll_initialization():
                    continue
                
                # Step 3: Poll for game start
                logger.info(" Step 3: Polling for game start...")
                if not self._poll_game_start():
                    continue
                
                # Step 4: Wait for game completion and submit scores
                logger.info(" Step 4: Waiting for game completion...")
                if not self._wait_and_submit_scores():
                    continue
                    
            except Exception as e:
                logger.error(f" Error in game loop: {e}")
                time.sleep(5)
                continue
    
    def _poll_initialization(self) -> bool:
        """Poll for game initialization"""
        while self.playStatus:
            try:
                if not hasattr(self, 'api') or self.api is None:
                    logger.error(" GameAPI not available for initialization polling")
                    return False
                    
                game_data = self.api.poll_game_initialization()
                if game_data:
                    self.game_result_id = game_data.get('id')
                    
                    # Extract team and player information
                    global teamName, list_players_name, list_players_id
                    teamName = game_data.get('name', 'Unknown Team')
                    
                    # Extract player info from nodeIDs
                    node_ids = game_data.get('nodeIDs', [])
                    list_players_name = [player.get('name', f'Player {i+1}') for i, player in enumerate(node_ids)]
                    list_players_id = [player.get('userID', f'user_{i+1}') for i, player in enumerate(node_ids)]
                    
                    logger.info(f" Game initialized: {self.game_result_id}")
                    logger.info(f" Team: {teamName}")
                    logger.info(f" Players: {list_players_name}")
                    
                    # Check if home screen is ready
                    global homeOpened
                    if homeOpened:
                        logger.info(" Home screen ready, emitting init signal")
                        homeOpened = False
                        self.init_signal.emit()
                        return True
                    else:
                        logger.info("⏳ Waiting for home screen to be ready...")
                
                time.sleep(3)  # Poll every 3 seconds
                
            except Exception as e:
                logger.error(f" Error polling initialization: {e}")
                time.sleep(5)
                
        return False
    
    def _poll_game_start(self) -> bool:
        """Poll for game start and continue monitoring during gameplay - Like CAGE_Game.py"""
        if not self.game_result_id:
            logger.error(" No game result ID available")
            return False
        
        logger.info(f" Starting polling with started_flag={self.started_flag}, cancel_flag={self.cancel_flag}")
        logger.info(" Starting continuous polling for game start...")
        
        # Create a simple reference object to avoid lambda timing issues
        class FlagRef:
            def __init__(self, manager):
                self.manager = manager
            def __call__(self, value=None):
                if value is not None:
                    self.manager.started_flag = value
                return self.manager.started_flag
        
        flag_ref = FlagRef(self)
        
        try:
            # Check API availability
            if not hasattr(self, 'api') or self.api is None:
                logger.error(" GameAPI not available for game start polling")
                return False
                
            # Phase 1: Wait for game to start using continuous polling like CAGE
            game_data = self.api.poll_game_start_continuous(
                game_result_id=self.game_result_id,
                submit_score_flag_ref=lambda: self.submit_score_flag,
                started_flag_ref=flag_ref,
                cancel_flag_ref=lambda x: setattr(self, 'cancel_flag', x)
            )
            
            if game_data:
                status = game_data.get('status')
                
                if status == 'playing' and not self.started_flag:
                    logger.info(" Game start signal received!")
                    self.start_signal.emit()
                    self.started_flag = True
                    
                    logger.info(" Start signal emitted successfully!")
                    logger.info(" Now subsequent 'playing' responses will be ignored")
                    
                    # Phase 2: Continue monitoring during gameplay
                    logger.info(" Game started - continuing to monitor for cancellation...")
                    return self._monitor_during_gameplay()
                    
                elif status == 'cancel' or game_data.get('cancelled'):
                    logger.warning("️  Game cancelled before starting")
                    self.cancel_flag = True
                    # CRITICAL: Reset started_flag IMMEDIATELY before emitting cancel
                    self.started_flag = False
                    logger.warning(f" started_flag reset to False before cancel: {self.started_flag}")
                    self.cancel_signal.emit()
                    # Manual reset of essential flags only
                    self.game_result_id = None
                    self.submit_score_flag = False
                    return False
                elif status == 'submit_triggered':
                    logger.info(" Score submission triggered before game start")
                    return True
                else:
                    logger.warning(f"️  Unexpected status: {status}")
                    return False
            else:
                logger.warning("️  No game data returned from continuous polling")
                return False
                
        except Exception as e:
            logger.error(f" Error in game start polling: {e}")
            return False
    
    def _monitor_during_gameplay(self) -> bool:
        """Continue monitoring for cancellation during active gameplay (from CAGE)"""
        logger.info(" Monitoring for cancellation during gameplay...")
        
        try:
            # Create a callback to check if game has stopped
            def game_stopped_check():
                # Only check if game has stopped AFTER it has actually started
                # This prevents race condition where polling starts before UI sets gameStarted=True
                global gameStarted
                
                # First, give the UI thread time to process the start signal
                # Only check for stop if we're confident the game was actually running
                import time
                current_time = time.time()
                if not hasattr(game_stopped_check, 'start_time'):
                    game_stopped_check.start_time = current_time
                
                # Only start checking for game stop after 2 seconds of polling
                if current_time - game_stopped_check.start_time < 2.0:
                    return False
                
                # Now check if game has actually stopped (timers stopped)
                if not gameStarted:
                    logger.info(" Game timers stopped (gameStarted=False) - stopping API polling")
                    return True
                    
                return False
            
            # Check API availability
            if not hasattr(self, 'api') or self.api is None:
                logger.error(" GameAPI not available for gameplay monitoring")
                return False
                
            # Continue continuous polling during gameplay with stop check - Like CAGE
            game_data = self.api.poll_game_start_continuous(
                game_result_id=self.game_result_id,
                submit_score_flag_ref=lambda: self.submit_score_flag,
                started_flag_ref=lambda: self.started_flag,
                cancel_flag_ref=lambda x: setattr(self, 'cancel_flag', x),
                game_stopped_check=game_stopped_check
            )
            
            if game_data:
                status = game_data.get('status')
                logger.info(f" Gameplay monitoring completed with status: {status}")
                
                if status == 'cancel' or game_data.get('cancelled'):
                    logger.warning("️  Game cancelled during gameplay")
                    self.cancel_flag = True
                    # CRITICAL: Reset started_flag IMMEDIATELY before emitting cancel
                    self.started_flag = False
                    logger.warning(f" started_flag reset to False during gameplay cancel: {self.started_flag}")
                    self.cancel_signal.emit()
                    # Manual reset of essential flags only
                    self.game_result_id = None
                    self.submit_score_flag = False
                    return False
                elif status == 'submit_triggered':
                    logger.info(" Score submission triggered during gameplay")
                    return True
                else:
                    logger.info(f" Gameplay monitoring completed with status: {status}")
                    return True
            else:
                logger.warning("️  No game data returned during gameplay monitoring")
                return False
                
        except Exception as e:
            logger.error(f" Error monitoring during gameplay: {e}")
            return False
    
    def _wait_and_submit_scores(self) -> bool:
        """Wait for game completion and submit scores"""
        while self.playStatus and not self.cancel_flag:
            if self.submit_score_flag:
                try:
                    # Prepare individual scores
                    global scored, list_players_id
                    individual_scores = self._prepare_individual_scores(scored, list_players_id)
                    
                    #  SAVE PLAYER DATA TO CSV FIRST (before API submission)
                    logger.info(" Saving FastReaction player data to CSV before API submission...")
                    self._save_individual_players_csv(self.game_result_id, individual_scores, None)  # None = pre-submission
                    self._save_pre_submission_log(self.game_result_id, individual_scores)
                    logger.info(" FastReaction player data saved locally before submission")
                     # SAVE TEAM DATA AND BACKEND PAYLOAD TO JSON (before API submission)
                    global teamName
                    logger.info("Saving team data and backend payload to JSON...")
                    self.save_team_and_payload_to_json(teamName, individual_scores, self.game_result_id)
                    logger.info(" Team data and backend payload saved to JSON")
                    
                    # Submit scores with API safety check
                    if not hasattr(self, 'api') or self.api is None:
                        logger.error(" GameAPI not available for score submission")
                        return False
                    
                    # Submit scores using original method (keep as main submitter)
                    logger.info(" Now submitting FastReaction scores to API...")
                    success = self.api.submit_final_scores(self.game_result_id, individual_scores)
                    
                    # Save player CSV with final submission status (after API submission)
                    self._save_individual_players_csv(self.game_result_id, individual_scores, success)
                    
                    if success:
                        logger.info(" Scores submitted successfully")
                        # Get updated leaderboard
                        self._update_leaderboard()
                        self.submit_signal.emit()
                        self._reset_game_state()
                        return True
                    else:
                        logger.error(" Failed to submit scores")
                        time.sleep(5)
                        
                except Exception as e:
                    logger.error(f" Error submitting scores: {e}")
                    time.sleep(5)
            else:
                time.sleep(1)  # Check every second for score submission flag
                
        return False
    def save_team_and_payload_to_json(self, team_name, individual_scores, game_result_id):
        """Save team data and backend payload in one JSON file"""
        try:
            # Create teams directory if it doesn't exist
            teams_dir = "teams"
            if not os.path.exists(teams_dir):
                os.makedirs(teams_dir)
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create safe filename from team name
            safe_team_name = "".join(c for c in team_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_team_name = safe_team_name.replace(' ', '_')
            
            # Create JSON filename
            json_filename = f"{timestamp}_{safe_team_name}.json"
            json_file_path = os.path.join(teams_dir, json_filename)
            
            # Prepare the exact backend payload structure
            backend_payload = {
                "gameResultID": game_result_id,
                "individualScore": individual_scores
            }
            
            # Combine team data and backend payload in one JSON
            combined_data = {
                "team_name": team_name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_score": sum(score_data.get('score', 0) for score_data in individual_scores),
                "backend_payload": backend_payload
                
            }
            
            # Save to JSON file
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(combined_data, json_file, indent=2, ensure_ascii=False)
            
            print(f"Team data and backend payload saved to JSON: {json_file_path}")
            logger.info(f"Team data and backend payload saved to JSON: {json_file_path}")
            
        except Exception as e:
            print(f"An error occurred while saving team data and payload to JSON: {e}")
            logger.error(f"Error saving team data and payload to JSON: {e}")
   
    def _prepare_individual_scores(self, total_score: int, player_ids: list) -> list:
        """Prepare individual scores in the required format"""
        if not player_ids:
            logger.warning("️  No player IDs available, using default")
            player_ids = ["default_user"]
        
        # Distribute score among players (first player gets any remainder)
        base_score = total_score // len(player_ids)
        remainder = total_score % len(player_ids)
        
        individual_scores = []
        for i, user_id in enumerate(player_ids):
            score = base_score + (remainder if i == 0 else 0)
            individual_scores.append({
                "userID": user_id,
                "nodeID": i + 1,
                "score": score
            })
        
        logger.info(f" Prepared scores for {len(individual_scores)} players")
        return individual_scores
    
    def _save_individual_players_csv(self, game_result_id: str, individual_scores: list, success: bool):
        """Save individual player scores for database revision"""
        try:
            csv_filename = "FastReaction_Individual_Players_Log.csv"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(csv_filename)
            
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'game_result_id', 'user_id', 'node_id', 
                    'individual_score', 'submission_success', 'status'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    logger.info(f" Created new individual players log file: {csv_filename}")
                
                # Determine status based on success parameter
                if success is None:
                    status = "pre_submission"
                elif success:
                    status = "submitted_success"
                else:
                    status = "submitted_failed"
                
                # Write one row per player
                for score_data in individual_scores:
                    writer.writerow({
                        'timestamp': timestamp,
                        'game_result_id': game_result_id,
                        'user_id': score_data.get('userID', 'Unknown'),
                        'node_id': score_data.get('nodeID', 'N/A'),
                        'individual_score': score_data.get('score', 0),
                        'submission_success': success,
                        'status': status
                    })
                
            if success is None:
                logger.info(f" Player data saved to {csv_filename} BEFORE API submission")
            else:
                logger.info(f" Player data status updated in {csv_filename} AFTER API submission")
            
        except Exception as e:
            logger.error(f" Error saving individual players log to CSV: {e}")
            # Don't let CSV errors break the game flow
    
    def _save_pre_submission_log(self, game_result_id: str, individual_scores: list):
        """Save a pre-submission log entry for safety"""
        try:
            csv_filename = "FastReaction_Pre_Submission_Backup.csv"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(csv_filename)
            
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'game_result_id', 'total_players', 'total_score', 
                    'player_ids', 'individual_scores_json', 'status'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    logger.info(f" Created new pre-submission backup file: {csv_filename}")
                
                # Calculate totals
                total_players = len(individual_scores)
                total_score = sum(score_data.get('score', 0) for score_data in individual_scores)
                
                # Create player IDs list
                player_ids = [score_data.get('userID', 'Unknown') for score_data in individual_scores]
                player_ids_str = " | ".join(player_ids)
                
                # Convert individual scores to JSON string for complete backup
                individual_scores_json = json.dumps(individual_scores)
                
                writer.writerow({
                    'timestamp': timestamp,
                    'game_result_id': game_result_id,
                    'total_players': total_players,
                    'total_score': total_score,
                    'player_ids': player_ids_str,
                    'individual_scores_json': individual_scores_json,
                    'status': 'saved_before_submission'
                })
                
            logger.info(f" Pre-submission backup saved to {csv_filename}")
            logger.info(f"    Game ID: {game_result_id}")
            logger.info(f"    Players: {total_players}")
            logger.info(f"    Total Score: {total_score}")
            
        except Exception as e:
            logger.error(f" Error saving pre-submission backup: {e}")
            # Don't let CSV errors break the game flow
    
    def _update_leaderboard(self):
        """Update the leaderboard data"""
        try:
            global list_top5_FastReaction ,lastplayed_score,lastplayed_weighted_points,lastplayed_rank
            leaderboard , lastplayed = self.api.get_leaderboard()
            if lastplayed is not None:
                lastplayed_score = lastplayed.get('total_score', 0)
                lastplayed_weighted_points = lastplayed.get('weighted_points', 0)
                lastplayed_rank = lastplayed.get('rank', 0)
            list_top5_FastReaction.clear()
            list_top5_FastReaction.extend(leaderboard)

            logger.info(f" Leaderboard updated with {len(leaderboard)} entries")
        except Exception as e:
            logger.error(f" Error updating leaderboard: {e}")
    
    def _reset_game_state(self):
        """Reset game state for next round"""
        logger.info(" Resetting game state for next round")
        self.game_result_id = None
        self.submit_score_flag = False
        self.started_flag = False
        self.cancel_flag = False
        
        # Reset global game variables
        global scored, serial_scoring_active
        # scored = 0
        serial_scoring_active = False
    
    def trigger_score_submission(self):
        """Trigger score submission (called when game ends)"""
        logger.info(" Score submission triggered")
        self.submit_score_flag = True
    
    def stop_manager(self):
        """Stop the game manager with comprehensive cleanup"""
        logger.info(" Stopping GameManager...")
        
        try:
            # Stop the game loop
            self.playStatus = False
            
            # Disconnect all signals
            try:
                self.init_signal.disconnect()
                self.start_signal.disconnect()
                self.cancel_signal.disconnect()
                self.submit_signal.disconnect()
                logger.debug(" GameManager signals disconnected")
            except Exception as e:
                logger.warning(f"️  Error disconnecting signals: {e}")
            
            # Clean up API object
            if hasattr(self, 'api') and self.api:
                try:
                    # The GameAPI object doesn't have explicit cleanup,
                    # but we can clear the reference
                    self.api = None
                    logger.debug(" GameAPI reference cleared")
                except Exception as e:
                    logger.warning(f"️  Error cleaning API: {e}")
            
            # Reset game state
            try:
                self._reset_game_state()
                logger.debug(" Game state reset")
            except Exception as e:
                logger.warning(f"️  Error resetting game state: {e}")
        
        except Exception as e:
            logger.warning(f"️  Error in GameManager cleanup: {e}")
        
        # Stop the thread gracefully
        try:
            self.quit()
            if not self.wait(5000):  # Wait up to 5 seconds
                logger.warning("️  GameManager thread did not finish gracefully")
                # Don't use terminate() unless absolutely necessary
            logger.debug(" GameManager stopped successfully")
        except Exception as e:
            logger.warning(f"️  Error stopping GameManager thread: {e}")


class Final_Screen(QtWidgets.QMainWindow):
    """Complete Final Screen implementation"""
    
    def setupUi(self, Home):
        Home.setObjectName("Home")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        Home.setLayoutDirection(QtCore.Qt.LeftToRight)
        Home.setAutoFillBackground(False)
        
        self.centralwidget = QtWidgets.QWidget(Home)
        Home.setGeometry(0, 0, QtWidgets.QDesktopWidget().screenGeometry().width(), QtWidgets.QDesktopWidget().screenGeometry().height())
        print(Home.geometry().width())

        if Home.geometry().width() > 1920:
            self.scale = 2
            background_gif_path = "Assets/1k/background.gif"
        else:
            self.scale = 1
            background_gif_path = "Assets/1k/background.gif"
        
        self.Background = QtWidgets.QLabel(self.centralwidget)
        self.Background.setScaledContents(True)
        self.Background.setGeometry(0, 0, Home.geometry().width(), Home.geometry().height())
        self.Background.setText("")
        
        # Initialize background_movie as None for safety
        self.background_movie = None
        
        # Safe movie creation and assignment
        try:
            self.background_movie = QMovie(background_gif_path)
            if self.background_movie.isValid():
                self.background_movie.setCacheMode(QMovie.CacheAll)
                # Set speed to normal (100% speed)
                self.background_movie.setSpeed(100)
                try:
                    self.background_movie.jumpToFrame(0)
                except Exception:
                    pass
                try:
                    self.Background.setPixmap(self.background_movie.currentPixmap())
                except Exception:
                    pass
                self.Background.setMovie(self.background_movie)
                self.background_movie.start()
            else:
                logger.warning(f"Invalid GIF file: {background_gif_path}")
        except Exception as e:
            logger.error(f"Error loading background movie: {e}")
            self.background_movie = None
            
        self.Background.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        

        self.teamscore_qml = QQuickWidget(self.centralwidget)
        self.teamscore_qml.setClearColor(QtCore.Qt.transparent)
        fmt = QSurfaceFormat()
        fmt.setAlphaBufferSize(8)
        self.teamscore_qml.setFormat(fmt)
        self.teamscore_qml.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.teamscore_qml.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.teamscore_qml.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
        self.teamscore_qml.setAttribute(QtCore.Qt.WA_AlwaysStackOnTop, True)
        self.teamscore_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)

        import os
        qml_path = os.path.join(os.path.dirname(__file__),"Teamscore_screen.ui.qml")
        self.teamscore_qml.setSource(QUrl.fromLocalFile(qml_path))

        # Geometry full screen (1920x1080 base, scale adapt if needed)
        self.teamscore_qml.setGeometry(QtCore.QRect(0, 0, Home.geometry().width(), Home.geometry().height()))

        # Seed initial data from list_top5_FastReaction
        try:
            root_obj = self.teamscore_qml.rootObject()
            if root_obj:
                # Create and attach backend
                self.teamscore_backend = TeamScoreBackend()
                root_obj.setProperty('backend', self.teamscore_backend)
                # Seed initial data from API list
                self.teamscore_backend.set_team_name(str(teamName))
                self.teamscore_backend.set_score_value(str(scored))
        except Exception:
            pass
        self.teamscore_qml.raise_()
        Home.setCentralWidget(self.centralwidget)
        self.retranslateUi(Home)
        QtCore.QMetaObject.connectSlotsByName(Home)
    
    def retranslateUi(self, Home):
        _translate = QtCore.QCoreApplication.translate
        Home.setWindowTitle(_translate("Home", "MainWindow"))
       

    def closeEvent(self, event):
        """Enhanced cleanup for Final_Screen with comprehensive resource management"""
        logger.info("Final screen closing with enhanced cleanup...")
        
        # 1. Stop all timers first to prevent any ongoing operations
        self._cleanup_timers()
        
        # 2. Clean up QML components with proper signal disconnection
        self._cleanup_qml_components()
        
        # 3. Clean up media and background resources
        self._cleanup_media_resources()
        
        # 4. Clean up UI widgets with safe Qt object handling
        self._cleanup_ui_widgets()
        
        # 5. Clean up layout and central widget
        self._cleanup_layout_components()
        
        # 6. Final cleanup of any remaining references
        self._final_cleanup()
        
        event.accept()
        logger.info("Final screen closed successfully with comprehensive cleanup")
        super().closeEvent(event)
    
    def _cleanup_timers(self):
        """Clean up all timers with proper signal disconnection"""
        timer_attrs = ['timer', 'timer2']
        for timer_attr in timer_attrs:
            if hasattr(self, timer_attr):
                timer = getattr(self, timer_attr)
                if timer is not None:
                    try:
                        timer.stop()
                        # Disconnect all signals safely
                        try:
                            timer.timeout.disconnect()
                        except (TypeError, RuntimeError):
                            pass  # Signal not connected or already disconnected
                        setattr(self, timer_attr, None)
                        logger.debug(f" {timer_attr} cleaned up")
                    except Exception as e:
                        logger.warning(f"Error cleaning up {timer_attr}: {e}")
                        setattr(self, timer_attr, None)
    
    def _cleanup_qml_components(self):
        """Clean up QML widgets and backends with proper signal disconnection"""
        # Clean up QML widget
        if hasattr(self, 'teamscore_qml') and self.teamscore_qml:
            try:
                # Test if widget is still valid
                self.teamscore_qml.isVisible()
                logger.debug("Cleaning up TeamScore QML widget...")
                
                # Disconnect all signals before deletion
                signal_methods = ['statusChanged', 'sceneGraphError', 'statusChanged', 'sceneGraphError']
                for signal_method in signal_methods:
                    try:
                        signal = getattr(self.teamscore_qml, signal_method)
                        signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass  # Signal not connected or doesn't exist
                
                self.teamscore_qml.deleteLater()
                logger.debug("TeamScore QML widget cleaned up")
            except RuntimeError:
                logger.debug("TeamScore QML widget was already deleted")
            except Exception as e:
                logger.warning(f"Error cleaning up TeamScore QML widget: {e}")
            finally:
                self.teamscore_qml = None

        # Clean up QML backend
        if hasattr(self, 'teamscore_backend') and self.teamscore_backend:
            try:
                # Stop any running operations in backend
                if hasattr(self.teamscore_backend, 'stop'):
                    self.teamscore_backend.stop()
                self.teamscore_backend = None
                logger.debug("TeamScore backend cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up TeamScore backend: {e}")
    
    def _cleanup_media_resources(self):
        """Clean up media resources including movies and pixmaps"""
        # Clean up background movie
        if hasattr(self, 'background_movie') and self.background_movie:
            try:
                self.background_movie.stop()
                self.background_movie.setCacheMode(QMovie.CacheNone)
                # Disconnect all signals
                signal_methods = ['frameChanged', 'finished']
                for signal_method in signal_methods:
                    try:
                        signal = getattr(self.background_movie, signal_method)
                        signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                self.background_movie.deleteLater()
                logger.debug("Background movie cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background movie: {e}")
            finally:
                self.background_movie = None
        
        # Clean up background pixmap
        if hasattr(self, 'background_pixmap') and self.background_pixmap:
            try:
                self.background_pixmap = None
                logger.debug("Background pixmap cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background pixmap: {e}")
    
    def _cleanup_ui_widgets(self):
        """Clean up UI widgets with safe Qt object handling"""
        
        
        # Clean up labels
        label_names = ['Label2', 'Label_team_name', 'Label', 'Countdown']
        for label_name in label_names:
            if hasattr(self, label_name):
                label_obj = getattr(self, label_name)
                if label_obj is not None:
                    try:
                        label_obj.hide()
                        label_obj.deleteLater()
                        logger.debug(f"{label_name} cleaned up")
                    except (RuntimeError, AttributeError):
                        logger.debug(f"{label_name} already deleted by Qt, skipping cleanup")
                    finally:
                        setattr(self, label_name, None)
        
        # Clean up background widget and movie
        if hasattr(self, 'background_movie') and self.background_movie is not None:
            try:
                self.background_movie.stop()
                # Disconnect all signals before deletion
                try:
                    self.background_movie.frameChanged.disconnect()
                    self.background_movie.finished.disconnect()
                except (AttributeError, TypeError, RuntimeError):
                    pass
                self.background_movie.deleteLater()
                logger.debug("Background movie cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background movie: {e}")
            finally:
                self.background_movie = None
                
        if hasattr(self, 'Background') and self.Background is not None:
            try:
                self.Background.clear()
                self.Background.setMovie(None)
                self.Background.deleteLater()
                logger.debug("Background widget cleaned up")
            except (RuntimeError, AttributeError):
                logger.debug("Background already deleted by Qt, skipping cleanup")
            finally:
                self.Background = None
    
    def _cleanup_layout_components(self):
        """Clean up layout and central widget components"""
        if hasattr(self, 'centralwidget') and self.centralwidget is not None:
            try:
                # Clean up all child widgets recursively
                children = self.centralwidget.findChildren(QtCore.QObject)
                for child in children:
                    try:
                        child.deleteLater()
                    except (RuntimeError, AttributeError):
                        pass
                
                self.centralwidget.deleteLater()
                logger.debug("Central widget and children cleaned up")
            except (RuntimeError, AttributeError):
                logger.debug("Central widget already deleted by Qt, skipping cleanup")
            finally:
                self.centralwidget = None
    
    def _final_cleanup(self):
        """Final cleanup of any remaining references"""
        # Clear any remaining object references
        cleanup_attrs = ['background_pixmap', 'teamscore_qml', 'teamscore_backend']
        for attr in cleanup_attrs:
            if hasattr(self, attr):
                setattr(self, attr, None)
        
        logger.debug("Final cleanup completed")

class Active_screen(QWidget):
    """Complete Active Screen implementation"""
    # signals for Miss OK Crct Mstk
    miss_signal = pyqtSignal()
    ok_signal = pyqtSignal()
    crct_signal = pyqtSignal()
    mstk_signal = pyqtSignal()
    def __init__(self, serial_thread=None):
        super().__init__()
        
        # Audio signal debouncing to prevent rapid-fire sound issues
        self.last_audio_signal_time = {}
        self.audio_debounce_interval = 100  # Minimum 100ms between same audio signals
        
        # Initialize MQTT thread
        self.mqtt_thread = MqttThread('localhost')
        self.mqtt_thread.start_signal.connect(self.start_game)
        self.mqtt_thread.stop_signal.connect(self.stop_game)
        self.mqtt_thread.restart_signal.connect(self.restart_game)
        self.mqtt_thread.start()
        
        # Store reference to serial thread (managed by MainApp)
        self.serial_thread = serial_thread
        if self.serial_thread:
            # Connect to serial signals
            try:
                self.serial_thread.data_received.connect(self.on_serial_data_received)
                # self.serial_thread.connection_status_changed.connect(self.on_serial_connection_status_changed)
                # self.serial_thread.error_occurred.connect(self.on_serial_error)
                logger.info(" Serial signals connected to Active_screen")
            except Exception as e:
                logger.warning(f"️  Failed to connect serial signals: {e}")
        
        
        
        
        # Initialize FastReaction backend for QML integration
        self.fastreaction_backend = FastReactionBackend()
        
        # Track QML widget initialization state
        self.qml_widget_initialized = False
        
        # Track direct signal connections for proper cleanup
        self.direct_signal_connections = []
        
    def _should_emit_audio_signal(self, signal_type: str) -> bool:
        """Check if enough time has passed since last audio signal to prevent rapid-fire sounds"""
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        
        if signal_type not in self.last_audio_signal_time:
            self.last_audio_signal_time[signal_type] = 0
            
        time_since_last = current_time - self.last_audio_signal_time[signal_type]
        
        if time_since_last >= self.audio_debounce_interval:
            self.last_audio_signal_time[signal_type] = current_time
            return True
        else:
            logger.debug(f"Audio signal {signal_type} debounced (last: {time_since_last:.1f}ms ago)")
            return False

    def _ensure_backend_connection(self) -> bool:
        """Ensure QML backend is properly connected and reinitialize if needed"""
        try:
            # Check if backend exists and QML widget is initialized
            if not hasattr(self, 'fastreaction_backend') or self.fastreaction_backend is None:
                logger.warning("FastReaction backend is None, recreating...")
                self.fastreaction_backend = FastReactionBackend()
            
            if not hasattr(self, 'qml_widget') or self.qml_widget is None:
                logger.warning("QML widget is None, cannot ensure backend connection")
                return False
            
            # Check if QML widget is initialized
            if not getattr(self, 'qml_widget_initialized', False):
                logger.warning("QML widget not initialized, attempting to initialize...")
                return self.init_qml_widget(self)
            
            # Verify backend is connected to QML root object
            root_object = self.qml_widget.rootObject()
            if root_object is None:
                logger.warning("QML root object is None, attempting to reconnect backend...")
                root_object.setProperty('backend', self.fastreaction_backend)
                return True
            
            # Test if backend property is set correctly
            backend_property = root_object.property('backend')
            if backend_property is None or backend_property != self.fastreaction_backend:
                logger.warning("Backend property not set correctly, reconnecting...")
                root_object.setProperty('backend', self.fastreaction_backend)
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring backend connection: {e}")
            return False

    def _manual_qml_refresh(self):
        """Manual QML refresh by directly calling backend methods"""
        try:
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend:
                logger.info("Performing manual QML refresh...")
                # Re-emit all signals by calling the setter methods
                global teamName, scored, correct_count, wrong_count, miss_count
                
                self.fastreaction_backend.set_team_name(teamName)
                self.fastreaction_backend.set_score_value(str(scored))
                self.fastreaction_backend.set_correct_count(str(correct_count))
                self.fastreaction_backend.set_wrong_count(str(wrong_count))
                self.fastreaction_backend.set_miss_count(str(miss_count))
                
                # Update timer display
                minutes = self.countdown_time // 60
                seconds = self.countdown_time % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                self.fastreaction_backend.set_time_value(time_str)
                
                logger.info("Manual QML refresh completed")
        except Exception as e:
            logger.error(f"Error in manual QML refresh: {e}")

    def _connect_backend_signals_directly(self):
        """Connect backend signals directly to QML properties as a fallback"""
        try:
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend and hasattr(self, 'qml_widget'):
                root_object = self.qml_widget.rootObject()
                if root_object:
                    logger.info("Connecting backend signals directly to QML properties...")
                    
                    # Create safe wrapper functions that check if object still exists
                    def safe_set_property(prop_name):
                        def wrapper(value):
                            try:
                                if hasattr(self, 'qml_widget') and self.qml_widget:
                                    root_obj = self.qml_widget.rootObject()
                                    if root_obj:
                                        root_obj.setProperty(prop_name, value)
                                    else:
                                        logger.debug(f"QML root object is None, skipping {prop_name} update")
                                else:
                                    logger.debug(f"QML widget not available, skipping {prop_name} update")
                            except RuntimeError as e:
                                if "deleted" in str(e):
                                    logger.debug(f"QML object deleted, disconnecting {prop_name} signal")
                                    # Disconnect this specific signal to prevent further errors
                                    if prop_name == 'currentScore':
                                        self.fastreaction_backend.scoreChanged.disconnect(wrapper)
                                    elif prop_name == 'currentCorrectCount':
                                        self.fastreaction_backend.correctCountChanged.disconnect(wrapper)
                                    elif prop_name == 'currentWrongCount':
                                        self.fastreaction_backend.wrongCountChanged.disconnect(wrapper)
                                    elif prop_name == 'currentMissCount':
                                        self.fastreaction_backend.missCountChanged.disconnect(wrapper)
                                    elif prop_name == 'currentTime':
                                        self.fastreaction_backend.timeChanged.disconnect(wrapper)
                                    elif prop_name == 'currentTeamName':
                                        self.fastreaction_backend.teamNameChanged.disconnect(wrapper)
                                else:
                                    logger.warning(f"Error setting QML property {prop_name}: {e}")
                            except Exception as e:
                                logger.warning(f"Unexpected error setting QML property {prop_name}: {e}")
                        return wrapper
                    
                    # Connect each signal to update QML properties directly with safe wrappers
                    # Store connections for proper cleanup
                    connections = [
                        self.fastreaction_backend.scoreChanged.connect(safe_set_property('currentScore')),
                        self.fastreaction_backend.correctCountChanged.connect(safe_set_property('currentCorrectCount')),
                        self.fastreaction_backend.wrongCountChanged.connect(safe_set_property('currentWrongCount')),
                        self.fastreaction_backend.missCountChanged.connect(safe_set_property('currentMissCount')),
                        self.fastreaction_backend.timeChanged.connect(safe_set_property('currentTime')),
                        self.fastreaction_backend.teamNameChanged.connect(safe_set_property('currentTeamName'))
                    ]
                    self.direct_signal_connections.extend(connections)
                    
                    logger.info("Direct signal connections established successfully")
        except Exception as e:
            logger.error(f"Error connecting backend signals directly: {e}")
        
    def init_mqtt_thread(self):
        """Initialize or reinitialize MQTT thread if needed"""
        try:
            if not hasattr(self, 'mqtt_thread') or self.mqtt_thread is None:
                logger.info(" Initializing MQTT thread...")
                self.mqtt_thread = MqttThread('localhost')
                self.mqtt_thread.start_signal.connect(self.start_game)
                self.mqtt_thread.stop_signal.connect(self.stop_game)
                self.mqtt_thread.restart_signal.connect(self.restart_game)
                self.mqtt_thread.start()
                logger.info(" MQTT thread initialized successfully")
            elif not self.mqtt_thread.isRunning():
                logger.info(" Starting existing MQTT thread...")
                self.mqtt_thread.start()
                logger.info(" MQTT thread started successfully")
            else:
                logger.debug(" MQTT thread already running")
        except Exception as e:
            logger.error(f" Error initializing MQTT thread: {e}")
    
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
   
    def init_qml_widget(self, parent_widget):
        """Initialize or reinitialize the QML widget safely"""
        try:
            # Always recreate the widget - don't try to reuse deleted widgets
            logger.debug("Initializing QML widget...")
            
            # Clean up any existing widget first (it might be deleted already)
            if hasattr(self, 'qml_widget') and self.qml_widget:
                try:
                    # Test if the widget is still valid
                    self.qml_widget.isVisible()
                    logger.debug("Existing QML widget found, cleaning up...")
                    # Disconnect all signals before deletion
                    try:
                        self.qml_widget.statusChanged.disconnect()
                        self.qml_widget.sceneGraphError.disconnect()
                    except:
                        pass
                    self.qml_widget.deleteLater()
                except RuntimeError:
                    # Widget was already deleted
                    logger.debug("Existing QML widget was already deleted")
                finally:
                    self.qml_widget = None
            
            # Reset initialization flag
            self.qml_widget_initialized = False
            
            # Create new QML widget
            self.qml_widget = QQuickWidget(parent_widget)
            self.qml_widget.setClearColor(Qt.transparent)
            
            # Configure QML widget for transparency (same settings as other QML widgets)
            fmt = QSurfaceFormat()
            fmt.setAlphaBufferSize(8)
            self.qml_widget.setFormat(fmt)
            self.qml_widget.setAttribute(Qt.WA_TranslucentBackground, True)
            self.qml_widget.setAttribute(Qt.WA_NoSystemBackground, True)
            self.qml_widget.setAttribute(Qt.WA_OpaquePaintEvent, False)
            self.qml_widget.setAttribute(Qt.WA_AlwaysStackOnTop, True)
            self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
            # Add black background to mask loading delays (same as other QML widgets)
            self.qml_widget.setStyleSheet("background-color: black;")
            
            # Set the widget to cover the entire screen
            self.qml_widget.setGeometry(QtCore.QRect(0, 0, 1920*self.scale, 1080*self.scale))
            
            # Load the Active_screen_FastReaction QML file
            qml_file_path = os.path.join(os.path.dirname(__file__), 'Active_screen_FastReaction.ui.qml')
            logger.info(f"QML file path: {qml_file_path}")
            logger.info(f"QML file exists: {os.path.exists(qml_file_path)}")
            
            if not os.path.exists(qml_file_path):
                logger.error(f"QML file not found: {qml_file_path}")
                return False
                
            self.qml_widget.setSource(QUrl.fromLocalFile(qml_file_path))
            logger.info(f"QML file loaded successfully")
            
            # Register backend as context property for QML access
            from PyQt5.QtQml import qmlRegisterType
            qmlRegisterType(FastReactionBackend, "FastReactionBackend", 1, 0, "FastReactionBackend")
            
            # Also set as context property for global access
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend:
                self.qml_widget.rootContext().setContextProperty("fastreactionBackend", self.fastreaction_backend)
            
            # Set up the backend connection
            root_object = self.qml_widget.rootObject()
            if root_object:
                # Ensure backend exists (recreate if it was cleaned up)
                if not hasattr(self, 'fastreaction_backend') or self.fastreaction_backend is None:
                    logger.debug("Recreating FastReaction backend...")
                    self.fastreaction_backend = FastReactionBackend()
                
                root_object.setProperty('backend', self.fastreaction_backend)
                logger.info(f"Backend connected to QML root object: {root_object}")
                
                # Also connect signals directly to ensure they work
                self._connect_backend_signals_directly()
                
                # Set initial values
                global teamName, scored
                logger.info(f"Setting initial values - Team: {teamName}, Score: {scored}")
                self.fastreaction_backend.set_team_name(teamName)
                self.fastreaction_backend.set_score_value(str(scored))
                self.fastreaction_backend.set_correct_count("0")
                self.fastreaction_backend.set_wrong_count("0")
                self.fastreaction_backend.set_miss_count("0")
                self.fastreaction_backend.set_timer_seconds(TimerValue // 1000)
                
                # Force initial timer sync to ensure QML displays correct values
                self.fastreaction_backend.force_timer_sync()
                logger.info("QML backend initialization completed with initial values")
                
                self.qml_widget_initialized = True
                logger.debug(" QML widget initialized successfully")
                return True
            else:
                logger.error(" Failed to get QML root object")
                return False
                
        except Exception as e:
            logger.error(f" Error initializing QML widget: {e}")
            return False
    
    def reset_qml_widget(self):
        """Reset QML widget state without recreating widget"""
        try:
            # Ensure backend exists (recreate if it was cleaned up)
            if not hasattr(self, 'fastreaction_backend') or self.fastreaction_backend is None:
                logger.debug("Recreating FastReaction backend for reset...")
                self.fastreaction_backend = FastReactionBackend()
            
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend:
                # Stop any running countdown
                self.fastreaction_backend.stop_countdown()
                
                # Reset to initial values
                global teamName, scored
                self.fastreaction_backend.set_team_name(teamName)
                self.fastreaction_backend.set_score_value(str(scored))
                self.fastreaction_backend.set_correct_count("0")
                self.fastreaction_backend.set_wrong_count("0")
                self.fastreaction_backend.set_miss_count("0")
                self.fastreaction_backend.set_timer_seconds(TimerValue // 1000)
                
                # Force timer sync after reset
                self.fastreaction_backend.force_timer_sync()
                
                # CRITICAL: Update QML backend property if widget exists
                if hasattr(self, 'qml_widget') and self.qml_widget:
                    root_object = self.qml_widget.rootObject()
                    if root_object:
                        logger.debug("Updating QML backend property after reset...")
                        root_object.setProperty('backend', self.fastreaction_backend)
                        # Also reconnect direct signals
                        self._connect_backend_signals_directly()
                        logger.debug("QML backend property updated after reset")
                
                logger.debug(" QML widget reset successfully")
        except Exception as e:
            logger.error(f" Error resetting QML widget: {e}")
        
    # def play_audio(self):
    #     """Load and play the audio file with safety checks."""
    #     try:
    #         # Ensure player is initialized
    #         if not hasattr(self, 'player') or self.player is None:
    #             logger.warning("️  MediaPlayer not initialized, creating new one")
    #             self.player = QMediaPlayer()
            
    #         audio_file = "Assets/mp3/2066.wav"
    #         absolute_path = os.path.abspath(audio_file)
    #         print("Absolute path:", absolute_path)
            
    #         # Check if file exists
    #         if not os.path.exists(absolute_path):
    #             logger.error(f" Audio file not found: {absolute_path}")
    #             return
                
    #         self.player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(absolute_path)))
    #         self.player.setVolume(100)
    #         self.player.play()
            
    #         # Safely connect signal (disconnect first to avoid multiple connections)
    #         try:
    #             self.player.mediaStatusChanged.disconnect()
    #         except:
    #             pass  # No existing connection
    #         self.player.mediaStatusChanged.connect(self.check_media_status)
            
    #         logger.debug(" Audio playback started successfully")
            
    #     except Exception as e:
    #         logger.error(f" Error playing audio: {e}")
    
    # def play_audio_2(self):
    #     """Load and play the audio file with safety checks."""
    #     try:
    #         # Ensure player is initialized
    #         if not hasattr(self, 'player') or self.player is None:
    #             logger.warning("️  MediaPlayer not initialized, creating new one")
    #             self.player = QMediaPlayer()
            
    #         audio_file = "Assets/mp3/2066.wav"
    #         absolute_path = os.path.abspath(audio_file)
    #         print("Absolute path:", absolute_path)
            
    #         # Check if file exists
    #         if not os.path.exists(absolute_path):
    #             logger.error(f" Audio file not found: {absolute_path}")
    #             return
                
    #         self.player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(absolute_path)))
    #         self.player.setVolume(100)
    #         self.player.play()
            
    #         # Safely connect signal (disconnect first to avoid multiple connections)
    #         try:
    #             self.player.mediaStatusChanged.disconnect()
    #         except:
    #             pass  # No existing connection
    #         self.player.mediaStatusChanged.connect(self.check_media_status)
            
    #         logger.debug(" Audio playback started successfully")
            
    #     except Exception as e:
    #         logger.error(f" Error playing audio: {e}")
        
    # def check_media_status(self, status):
    #     """Check media status and stop playback if finished."""
    #     if status == QMediaPlayer.MediaStatus.EndOfMedia:
    #         self.player.stop()
    
    @pyqtSlot(str)
    def on_serial_data_received(self, data):
        """Handle serial data received from device"""
        try:
            logger.debug(f" Serial data received: {data}")
            
            # Ensure QML backend is properly connected before processing updates
            if not self._ensure_backend_connection():
                logger.warning("Backend connection lost, skipping update")
                return
            
            # Process the serial data based on your game logic
            # Example: if data contains score information
             # data expected:
                    # Sc{score}\n
                    # Mstk\n
                    # Ok\n
                    # Crct\n
                    # Miss\n

            global scored, serial_scoring_active, gameStarted
            
            # Debug logging for edge device troubleshooting
            logger.info(f"QML widget initialized: {getattr(self, 'qml_widget_initialized', False)}")
            logger.info(f"Backend exists: {hasattr(self, 'fastreaction_backend') and self.fastreaction_backend is not None}")
            logger.info(f"Game started: {gameStarted}")
            
            if gameStarted:  # Only update score if game is active
                if data.lower().startswith("sc"):
                    scored = int(data.split("Sc")[1])
                    serial_scoring_active = True
                    logger.info(f"Score updated via serial: +{data} (total: {scored})")
                    
                    # Update the score display if the label exists
                    # if hasattr(self, 'label_Score'):
                    # self.label_Score.setText(f"Score: {scored}")
                    logger.info(f"Updating backend score: {scored}")
                    self.fastreaction_backend.set_score_value(str(scored))
                    # Force QML refresh to ensure immediate update
                    self.fastreaction_backend.force_qml_refresh()
                    logger.info(f"Backend score updated successfully")

                    # BIDIRECTIONAL: Send acknowledgment back
                    # if self.serial_thread:
                    #     self.serial_thread.send_data("ScoreReceived")
                        
                elif data.lower().startswith("mstk"):
                    serial_scoring_active = True
                    logger.info(f"Mstk updated via serial")
                    # Use debouncing to prevent rapid-fire audio signals
                    if self._should_emit_audio_signal("mstk"):
                        logger.info("Emitting mstk_signal")
                        global wrong_count
                        # wrong_count += 1
                        logger.info(f"Updating backend wrong count: {wrong_count}")
                        self.fastreaction_backend.set_wrong_count(str(wrong_count))
                        # Force QML refresh to ensure immediate update
                        self.fastreaction_backend.force_qml_refresh()
                        logger.info(f"Backend wrong count updated successfully")
                        self.mstk_signal.emit()
                    else:
                        logger.debug("Mstk signal debounced (too soon)")
                    # BIDIRECTIONAL: Send acknowledgment back
                    # if self.serial_thread:
                    #     self.serial_thread.send_data("MstkReceived")
                        
                elif data.lower().startswith("ok"):
                    serial_scoring_active = True
                    logger.info(f"Ok updated via serial")
                    # Use debouncing to prevent rapid-fire audio signals
                    if self._should_emit_audio_signal("ok"):
                        self.ok_signal.emit()
                    # BIDIRECTIONAL: Send acknowledgment back
                    # if self.serial_thread:
                    #     self.serial_thread.send_data("OkReceived")
                        
                elif data.lower().startswith("crct"):
                    serial_scoring_active = True
                    logger.info(f"Crct updated via serial")
                    # Use debouncing to prevent rapid-fire audio signals
                    if self._should_emit_audio_signal("crct"):
                        logger.info("Emitting crct_signal")
                        global correct_count
                        # correct_count += 1
                        logger.info(f"Updating backend correct count: {correct_count}")
                        self.fastreaction_backend.set_correct_count(str(correct_count))
                        # Force QML refresh to ensure immediate update
                        self.fastreaction_backend.force_qml_refresh()
                        logger.info(f"Backend correct count updated successfully")
                        self.crct_signal.emit()
                        
                    else:
                        logger.debug("Crct signal debounced (too soon)")
                    # BIDIRECTIONAL: Send acknowledgment back
                    # if self.serial_thread:
                    #     self.serial_thread.send_data("CrctReceived")
                        
                elif data.lower().startswith("miss"):
                    serial_scoring_active = True
                    logger.info(f"Miss updated via serial")
                    # Use debouncing to prevent rapid-fire audio signals
                    if self._should_emit_audio_signal("miss"):
                        global miss_count
                        # miss_count += 1
                        logger.info(f"Updating backend miss count: {miss_count}")
                        self.fastreaction_backend.set_miss_count(str(miss_count))
                        # Force QML refresh to ensure immediate update
                        self.fastreaction_backend.force_qml_refresh()
                        logger.info(f"Backend miss count updated successfully")
                        self.miss_signal.emit()
                    # BIDIRECTIONAL: Send acknowledgment back
                    # if self.serial_thread:
                    #     self.serial_thread.send_data("MissReceived")
                        
                else:
                    logger.debug(f"📥 Custom serial data: {data}")
                    # BIDIRECTIONAL: Send acknowledgment for unknown data
                    # if self.serial_thread:
                    #     self.serial_thread.send_data(f"DataReceived:{data}")
                # if data.isdigit():
                #     # Simple numeric data - could be score increment
                    
                #     scored = int(data)
                #     serial_scoring_active = True
                #     logger.info(f" Score updated via serial: +{data} (total: {scored})")
                    
                #     # Update the score display if the label exists
                #     if hasattr(self, 'label_Score'):
                #         self.label_Score.setText(f"Score: {scored}")
                
                # elif data.lower() == "win":
                #     # Game win condition received via serial
                #     global gamefinished
                #     gamefinished = True
                #     serial_scoring_active = True
                #     logger.info(" Win condition received via serial")
                    
                # elif data.lower() == "hit" or data.lower() == "point":
                #     # Hit/point detected
                #     scored += 1
                #     serial_scoring_active = True
                #     logger.info(f" Hit detected via serial! Score: {scored}")
                    
                #     # Update the score display
                #     if hasattr(self, 'label_Score'):
                #         self.label_Score.setText(f"Score: {scored}")
                # else:
                #     # Custom data processing - you can extend this based on your needs
                #     logger.debug(f" Custom serial data: {data}")
            else:
                logger.debug(f" Serial data received but game not active: {data}")
                
        except Exception as e:
            logger.error(f" Error processing serial data: {e}")
    
    @pyqtSlot(bool)
    def on_serial_connection_status_changed(self, connected):
        """Handle serial connection status changes"""
        if connected:
            logger.info(" Serial device connected")
        else:
            logger.warning("️  Serial device disconnected")
    
    @pyqtSlot(str)
    def on_serial_error(self, error_message):
        """Handle serial communication errors"""
        logger.error(f" Serial error: {error_message}")
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        print(MainWindow.geometry().width())

        if MainWindow.geometry().width() > 1920:
            self.movie = QMovie("Assets/1k/background.gif")
            print("1")
            self.scale = 2
        else:
            self.movie = QMovie("Assets/1k/background.gif")
            print("2")
            self.scale = 1
        
        global TimerValue
        try:
            with open("file2.txt", "r") as file:
                lines = file.readlines()
                if lines:
                    TimerValue = int(lines[-1].strip())
        except FileNotFoundError:
            print("file2.txt not found. Using default timer value.")
            TimerValue = 30000

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        
        MainWindow.setCentralWidget(self.centralwidget)

        
        # Load fonts
        self.font_family = self.load_custom_font("Assets/Fonts/GOTHIC.TTF")
        self.font_family_good = self.load_custom_font("Assets/Fonts/good_times_rg.ttf")
        
        # Background
        self.Background = QtWidgets.QLabel(self.centralwidget)
        self.Background.setGeometry(QtCore.QRect(0, 0, 1920*self.scale, 1080*self.scale))
        self.Background.setText("")
        self.Background.setScaledContents(True)
        self.Background.setMovie(self.movie)
        self.movie.start()
       
        

        self.setup_qml_import_paths()
        # Initialize QML widget
        try:
            if self.init_qml_widget(self.centralwidget):
                logger.info(" QML widget successfully initialized")
                # Show the QML widget
                self.qml_widget.show()
            else:
                logger.warning("️  Failed to initialize QML widget")
        except Exception as e:
            logger.error(f" Error setting up QML widget: {e}")
        
        
        
        
        # Game timer
        self.TimerGame = QTimer(MainWindow)
        self.TimerGame.setSingleShot(True)
        self.TimerGame.setTimerType(QtCore.Qt.PreciseTimer)
        self.TimerGame.timeout.connect(self.stop_game)
       
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update_timer)
        self.countdown_time = TimerValue//1000

        # Raise elements to proper layer order
        self.Background.setObjectName("Background")
        self.Background.raise_()
        
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
    
    # def set_timer_text(self, value):
    #     """Set the timer text to the given value in MM:SS format"""
    #     minutes = value // 60
    #     seconds = value % 60
    #     timer_text = f"{minutes:02d}:{seconds:02d}"
    #     self.label_timer.setText(timer_text)
        
    def update_timer(self):
        global RemainingTime
        # if self.serial_thread.connected:
        #     self.label_serial_connection.setText("Serial Connection: Connected")
        # else:
        #     self.label_serial_connection.setText("Serial Connection: Disconnected")
        
        self.countdown_time -= 1
        if gamefinished == True:
            global scored, serial_scoring_active
            
            # No bonuses applied regardless of serial communication status
            if serial_scoring_active:
                print(f"Game finished! Final Score: {scored} (serial score)")
            else:
                print(f"Game finished! Final Score: {scored} (no bonuses applied)")
            
            self.stop_game()
        
        if self.countdown_time == 0:
            self.timer.stop()
            # self.set_timer_text(0)
            # Change timer color to red when time's up
            # self.label_timer.setStyleSheet("color: rgb(244,28,23);")
        
        # Update QML backend with current values
        try:
            # Ensure backend connection before updating
            if not self._ensure_backend_connection():
                logger.warning("Backend connection not available, skipping QML update")
                return
                
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend and self.qml_widget_initialized:
                # Force QML refresh to ensure all values are displayed
                try:
                    if hasattr(self.fastreaction_backend, 'force_qml_refresh'):
                        self.fastreaction_backend.force_qml_refresh()
                    else:
                        # Fallback: manually emit signals if method doesn't exist
                        logger.warning("force_qml_refresh method not available, using fallback")
                        self._manual_qml_refresh()
                except Exception as e:
                    logger.error(f"Error forcing QML refresh: {e}")
                    self._manual_qml_refresh()
                # Update score
                self.fastreaction_backend.set_score_value(str(scored))
                self.fastreaction_backend.set_correct_count(str(correct_count))
                self.fastreaction_backend.set_miss_count(str(miss_count))
                self.fastreaction_backend.set_wrong_count(str(wrong_count))
                
                # Update timer display
                minutes = self.countdown_time // 60
                seconds = self.countdown_time % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                self.fastreaction_backend.set_time_value(time_str)
                
                # Sync timer state with game timer
                is_timer_running = self.timer.isActive() if hasattr(self, 'timer') else False
                self.fastreaction_backend.sync_timer_state(self.countdown_time, is_timer_running)
                
                # Additional validation: ensure QML timer is in sync
                if self.countdown_time <= 0 and self.fastreaction_backend.is_timer_running():
                    self.fastreaction_backend.stop_countdown()
                    logger.debug(" QML timer stopped due to countdown reaching zero")
        except Exception as e:
            logger.error(f" Error updating QML backend: {e}")
        
        RemainingTime = self.countdown_time
    
    @pyqtSlot()
    def start_game(self):
        global gameStarted, firstDetected
        gameStarted = True
        
        # Start serial monitoring if available
        if self.serial_thread:
            self.serial_thread.start_monitoring()
            
            logger.info(" Serial monitoring started for game")
        
        # Start QML timer and sync state
        try:
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend and self.qml_widget_initialized:
                # Ensure timer is properly initialized
                self.fastreaction_backend.set_timer_seconds(self.countdown_time)
                # Sync timer state before starting
                self.fastreaction_backend.sync_timer_state(self.countdown_time, True)
                self.fastreaction_backend.start_countdown()
                logger.info(f" QML timer started - Time: {self.countdown_time}s")
        except Exception as e:
            logger.error(f" Error starting QML timer: {e}")
        
        self.timer.start(1000)
        self.TimerGame.start(TimerValue)
        print("start")
        # self.play_audio()

    @pyqtSlot()
    def stop_game(self):
        global teamName, scored, gameStarted, firstDetected, gamefinished, serial_scoring_active
        
        # Cancel any existing deactivate timer first to prevent multiple timers
        if hasattr(self, 'deactivate_timer') and self.deactivate_timer:
            self.deactivate_timer.stop()
            self.deactivate_timer = None
        
        # Stop serial monitoring if available
        if self.serial_thread:
            self.serial_thread.stop_monitoring()
            logger.info(" Serial monitoring stopped for game")
        
        # Stop QML timer and sync state
        try:
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend and self.qml_widget_initialized:
                # Sync timer state before stopping
                self.fastreaction_backend.sync_timer_state(self.countdown_time, False)
                self.fastreaction_backend.stop_countdown()
                logger.debug(" QML timer stopped")
        except Exception as e:
            logger.error(f" Error stopping QML timer: {e}")
        self.TimerGame.stop()
        self.timer.stop()
        self.save_final_score_to_csv(teamName, scored)

        # self.play_audio_2()
        gameStarted = False
        firstDetected = False
        gamefinished = False
        
        # Emit deactivate signal directly after 5 seconds to trigger score submission
        def emit_deactivate_signal():
            if self.mqtt_thread and hasattr(self.mqtt_thread, 'deactivate_signal'):
                self.mqtt_thread.deactivate_signal.emit()
                print("deactivate signal emitted")
            else:
                print("mqtt_thread is None, deactivate signal not emitted")
            # Clear the timer reference after execution
            self.deactivate_timer = None
        
        # Store timer reference so it can be cancelled during cleanup
        self.deactivate_timer = QtCore.QTimer()
        self.deactivate_timer.setSingleShot(True)
        self.deactivate_timer.timeout.connect(emit_deactivate_signal)
        self.deactivate_timer.start(5000)
        
        # # Deactivate after 5 seconds
        # QtCore.QTimer.singleShot(5000, lambda: (
        #     self.mqtt_thread.client.publish("FastReaction/game/Deactivate", 1),
        #     print("deactivate")
        # ))
        
        print("stop")
    
    def save_final_score_to_csv(self, team_name, final_score):
        """Save final score to CSV file"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        csv_file_path = "Fast_Reaction.csv"
        
        try:
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([team_name, final_score, current_time])
            print("Score saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving the score to CSV: {e}")
    
    @pyqtSlot()
    def restart_game(self):
        # Reset QML timer
        try:
            if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend:
                self.reset_qml_widget()
                logger.debug(" QML timer reset for restart")
        except Exception as e:
            logger.error(f" Error resetting QML timer for restart: {e}")
        
        self.TimerGame.start(TimerValue)
        print("restart")
        
        self.TimerGame.stop()
        
    def load_custom_font(self, font_path):
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_path}")
            return "Default"
        font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            return font_families[0]
        return "Default"

    def closeEvent(self, event):
        """Enhanced cleanup for Active_screen with comprehensive resource management"""
        logger.info("Active screen closing with enhanced cleanup...")
        
        # 1. Stop all timers first to prevent any ongoing operations
        self._cleanup_timers()
        
        
        # 3. Clean up QML components
        self._cleanup_qml_components()
        
        # 4. Clean up threading components (MQTT, Serial)
        self._cleanup_threading_components()
        
        # 5. Clean up audio signals and game state
        self._cleanup_audio_and_game_state()
        
        # 6. Clean up UI widgets and layout
        self._cleanup_ui_components()
        
        # 7. Final cleanup
        self._final_cleanup()
        
        event.accept()
        logger.info("Active screen closed successfully with comprehensive cleanup")
        super().closeEvent(event)
    
    def _cleanup_timers(self):
        """Clean up all timers with proper signal disconnection"""
        timer_attrs = ['timer', 'TimerGame', 'deactivate_timer']
        for timer_attr in timer_attrs:
            if hasattr(self, timer_attr):
                timer = getattr(self, timer_attr)
                if timer is not None:
                    try:
                        timer.stop()
                        # Disconnect all signals safely
                        try:
                            timer.timeout.disconnect()
                        except (TypeError, RuntimeError):
                            pass  # Signal not connected or already disconnected
                        setattr(self, timer_attr, None)
                        logger.debug(f"{timer_attr} cleaned up")
                    except Exception as e:
                        logger.warning(f"Error cleaning up {timer_attr}: {e}")
                        setattr(self, timer_attr, None)
    
    
    def _cleanup_qml_components(self):
        """Clean up QML widget and backend"""
        # Clean up QML widget
        if hasattr(self, 'qml_widget') and self.qml_widget:
            try:
                # Test if widget is still valid
                self.qml_widget.isVisible()
                logger.debug("Cleaning up QML widget...")
                
                # Disconnect all signals before deletion
                signal_methods = ['statusChanged', 'sceneGraphError']
                for signal_method in signal_methods:
                    try:
                        signal = getattr(self.qml_widget, signal_method)
                        signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                
                self.qml_widget.deleteLater()
                logger.debug("QML widget cleaned up")
            except RuntimeError:
                logger.debug("QML widget was already deleted")
            except Exception as e:
                logger.warning(f"Error cleaning up QML widget: {e}")
            finally:
                self.qml_widget = None
                self.qml_widget_initialized = False

        # Clean up QML backend
        if hasattr(self, 'fastreaction_backend') and self.fastreaction_backend:
            try:
                # Disconnect tracked direct signal connections first
                if hasattr(self, 'direct_signal_connections'):
                    for connection in self.direct_signal_connections:
                        try:
                            connection.disconnect()
                        except Exception:
                            pass
                    self.direct_signal_connections.clear()
                
                # Also try to disconnect all signals as fallback
                try:
                    self.fastreaction_backend.scoreChanged.disconnect()
                except Exception:
                    pass
                try:
                    self.fastreaction_backend.correctCountChanged.disconnect()
                except Exception:
                    pass
                try:
                    self.fastreaction_backend.wrongCountChanged.disconnect()
                except Exception:
                    pass
                try:
                    self.fastreaction_backend.missCountChanged.disconnect()
                except Exception:
                    pass
                try:
                    self.fastreaction_backend.timeChanged.disconnect()
                except Exception:
                    pass
                try:
                    self.fastreaction_backend.teamNameChanged.disconnect()
                except Exception:
                    pass
                
                self.fastreaction_backend.stop_countdown()
                self.fastreaction_backend = None
                logger.debug("FastReaction backend cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up FastReaction backend: {e}")
    
    def _cleanup_threading_components(self):
        """Clean up MQTT and Serial threading components"""
        # Clean up MQTT thread
        if hasattr(self, 'mqtt_thread') and self.mqtt_thread:
            try:
                # Disconnect all signals first
                signal_methods = ['start_signal', 'stop_signal', 'restart_signal', 
                                'deactivate_signal', 'activate_signal', 'message_signal']
                for signal_method in signal_methods:
                    try:
                        if hasattr(self.mqtt_thread, signal_method):
                            signal = getattr(self.mqtt_thread, signal_method)
                            signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                
                # Stop the thread gracefully
                self.mqtt_thread.stop()
                self.mqtt_thread = None
                logger.debug("MQTT thread cleaned up")
            except Exception as e:
                logger.warning(f"Error stopping MQTT thread: {e}")
        
        # Disconnect serial signals (but don't stop the thread - it's managed by MainApp)
        if hasattr(self, 'serial_thread') and self.serial_thread:
            try:
                # Disconnect signals only
                try:
                    self.serial_thread.data_received.disconnect(self.on_serial_data_received)
                    logger.debug("Serial signals disconnected")
                except (TypeError, RuntimeError):
                    pass  # Signal not connected or already disconnected
                # Don't set to None or stop - it's managed by MainApp
            except Exception as e:
                logger.warning(f"Error disconnecting Serial signals: {e}")
    
    def _cleanup_audio_and_game_state(self):
        """Clean up audio signals and reset game state"""
        # Disconnect audio signals
        audio_signals = ['crct_signal', 'mstk_signal']
        for signal_name in audio_signals:
            if hasattr(self, signal_name):
                try:
                    signal = getattr(self, signal_name)
                    signal.disconnect()
                    logger.debug(f"{signal_name} disconnected")
                except (TypeError, RuntimeError):
                    pass  # Signal not connected or already disconnected
        
        # Reset global game state
        global gameStarted
        gameStarted = False
        logger.debug("Game state reset")
    
    def _cleanup_ui_components(self):
        """Clean up UI widgets and layout components"""
        # Clean up background widget and movie
        if hasattr(self, 'background_movie') and self.background_movie is not None:
            try:
                self.background_movie.stop()
                # Disconnect all signals before deletion
                try:
                    self.background_movie.frameChanged.disconnect()
                    self.background_movie.finished.disconnect()
                except (AttributeError, TypeError, RuntimeError):
                    pass
                self.background_movie.deleteLater()
                logger.debug("Background movie cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background movie: {e}")
            finally:
                self.background_movie = None
                
        # Also clean up legacy movie used in Active_screen
        if hasattr(self, 'movie') and self.movie is not None:
            try:
                self.movie.stop()
                # Disconnect all signals before deletion (if any)
                try:
                    self.movie.frameChanged.disconnect()
                    self.movie.finished.disconnect()
                except (AttributeError, TypeError, RuntimeError):
                    pass
                self.movie.deleteLater()
                logger.debug("Legacy movie cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up legacy movie: {e}")
            finally:
                self.movie = None
                
        if hasattr(self, 'Background') and self.Background is not None:
            try:
                self.Background.clear()
                self.Background.deleteLater()
                self.Background = None
                logger.debug("Background widget cleaned up")
            except Exception as e:
                logger.warning(f"Error clearing background: {e}")
        
        # Clean up central widget and all children
        if hasattr(self, 'centralwidget') and self.centralwidget:
            try:
                # Clean up all child widgets recursively
                children = self.centralwidget.findChildren(QtCore.QObject)
                for child in children:
                    try:
                        child.deleteLater()
                    except (RuntimeError, AttributeError):
                        pass
                self.centralwidget = None
                logger.debug("Central widget and children cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning central widget: {e}")
    
    def _final_cleanup(self):
        """Final cleanup of any remaining references"""
        # Clear any remaining object references
        cleanup_attrs = ['qml_widget', 'fastreaction_backend', 'mqtt_thread', 
                        'Background', 'centralwidget']
        for attr in cleanup_attrs:
            if hasattr(self, attr):
                setattr(self, attr, None)
        
        logger.debug("Final cleanup completed")



class TeamMember_screen(QtWidgets.QMainWindow):
    """Complete TeamMember Screen implementation"""
    
    def load_custom_font(self, font_path):
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_path}")
            return "Default"
        font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            return font_families[0]
        return "Default"

    # def play_audio(self):
    #     """Load and play the audio file."""
    #     audio_file = "Assets/mp3/2066.wav"
    #     absolute_path = os.path.abspath(audio_file)
    #     print("Absolute path:", absolute_path)
    #     self.player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(absolute_path)))
    #     self.player.setVolume(100)
    #     self.player.play()
    #     self.player.mediaStatusChanged.connect(self.check_media_status)
    
    # def check_media_status(self, status):
    #     """Check media status and stop playback if finished."""
    #     if status == QMediaPlayer.MediaStatus.EndOfMedia:
    #         self.player.stop()
        
    def setupUi(self, Home):
        Home.setObjectName("Home")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        Home.setLayoutDirection(QtCore.Qt.LeftToRight)
        Home.setAutoFillBackground(False)

        self.centralwidget = QtWidgets.QWidget(Home)
        self.centralwidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        print(Home.geometry().width())
        self.font_family = self.load_custom_font("Assets/Fonts/GOTHIC.TTF")
        self.font_family_good = self.load_custom_font("Assets/Fonts/good_times_rg.ttf")
        
        if Home.geometry().width() > 1920:
            background_gif_path = "Assets/1k/background.gif"
            self.scale = 2
            global scaled
            scaled = 2
        else:
            background_gif_path = "Assets/1k/background.gif"
            self.scale = 1  
            scaled = 1
        
        self.Background = QtWidgets.QLabel(self.centralwidget)
        self.Background.setScaledContents(True)
        self.Background.setGeometry(0, 0, Home.geometry().width(), Home.geometry().height())
        self.Background.setText("")
        # Add black background to mask loading delays
        self.Background.setStyleSheet("background-color: black;")
        
        # Initialize background_movie as None for safety
        self.background_movie = None
        
        # Safe movie creation and assignment
        try:
            self.background_movie = QMovie(background_gif_path)
            if self.background_movie.isValid():
                self.background_movie.setCacheMode(QMovie.CacheAll)
                # Set speed to normal (100% speed)
                self.background_movie.setSpeed(100)
                try:
                    self.background_movie.jumpToFrame(0)
                except Exception:
                    pass
                try:
                    self.Background.setPixmap(self.background_movie.currentPixmap())
                except Exception:
                    pass
                self.Background.setMovie(self.background_movie)
                self.background_movie.start()
            else:
                logger.warning(f"Invalid GIF file: {background_gif_path}")
        except Exception as e:
            logger.error(f"Error loading background movie: {e}")
            self.background_movie = None
            
        self.Background.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        

        Home.setCentralWidget(self.centralwidget)
        
        # Add QML TeamName overlay (after central widget is set)
        try:
            from PyQt5.QtQuickWidgets import QQuickWidget
            self.teamname_qml = QQuickWidget(self.centralwidget)
            self.teamname_qml.setClearColor(QtCore.Qt.transparent)
            fmt = QSurfaceFormat()
            fmt.setAlphaBufferSize(8)
            self.teamname_qml.setFormat(fmt)
            self.teamname_qml.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.teamname_qml.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
            self.teamname_qml.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
            self.teamname_qml.setAttribute(QtCore.Qt.WA_AlwaysStackOnTop, True)
            self.teamname_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
            # Add black background to mask loading delays
            self.teamname_qml.setStyleSheet("background-color: black;")

            # Load Teamname QML
            qml_path = os.path.join(os.path.dirname(__file__), "Teamname_screen_new.ui.qml")
            print(f"TeamMember QML path: {qml_path}")
            self.teamname_qml.setSource(QUrl.fromLocalFile(qml_path))
            print(f"TeamMember QML geometry: {self.teamname_qml.geometry()}")

            # Size full screen
            self.teamname_qml.setGeometry(QtCore.QRect(0, 0, Home.geometry().width(), Home.geometry().height()))

            # Wire backend
            
            from teamname_backend import TeamNameBackend as TeamNameBackendCube
            
            self.team_backend = TeamNameBackendCube()
            root_obj = self.teamname_qml.rootObject()
            print(f"TeamMember QML root object: {root_obj}")
            if root_obj:
                root_obj.setProperty('backend', self.team_backend)
                print("TeamMember QML backend set successfully")
                # Seed initial data from API (global state)
                # Split team name into AR/EN if available; fallback to EN only
                self.team_backend.update_team_name_en(teamName)
                # Players: fill first 4
                for idx in range(4):
                    if idx < len(list_players_name):
                        self.team_backend.update_player_name(idx, list_players_name[idx])
                # Emit all for QML refresh
                self.team_backend.allPlayersUpdated.emit(self.team_backend.players)
            
            # Preload QML to avoid white flash (similar to GIF first frame preloading)
            try:
                # Force QML to render immediately
                self.teamname_qml.setVisible(True)
                self.teamname_qml.update()
                # Small delay to ensure QML is rendered
                QtCore.QTimer.singleShot(50, lambda: self.teamname_qml.raise_())
            except Exception:
                pass
        except Exception as e:
            logger.error(f" Error setting Teamname QML overlay: {e}")
        
        # Background is already set with pixmap
        
        self.retranslateUi(Home)
        # self.play_audio()
        self.UpdateTable()
        
        QtCore.QMetaObject.connectSlotsByName(Home)
    
    def retranslateUi(self, Home):
        _translate = QtCore.QCoreApplication.translate
        Home.setWindowTitle(_translate("Home", "MainWindow"))
    
    
    
    def UpdateTable(self):
        """Update table with team member names"""
        global teamName
        # self.Label_team_name.setText(teamName)  # Traditional label hidden, QML overlay handles display
        # self.Label_team_name.show()
        global list_players_name
        # Also push updates to QML backend so overlay mirrors the table/API
        try:
            if hasattr(self, 'team_backend') and self.team_backend:
                # Update team name (English) and optionally Arabic if you have it
                self.team_backend.update_team_name_en(teamName)
                # Update player names
                for idx in range(4):
                    if idx < len(list_players_name):
                        self.team_backend.update_player_name(idx, list_players_name[idx])
                # Trigger a bulk refresh
                self.team_backend.allPlayersUpdated.emit(self.team_backend.players)
        except Exception as e:
            logger.warning(f"️  Failed to sync TeamMember QML backend: {e}")
    
    def closeEvent(self, event):
        """Enhanced cleanup for TeamMember_screen with comprehensive resource management"""
        logger.info("TeamMember screen closing with enhanced cleanup...")
        
        # 1. Stop all timers first to prevent any ongoing operations
        self._cleanup_timers()
        
        # 2. Clean up QML components
        self._cleanup_qml_components()
        
        # 3. Clean up media and background resources
        self._cleanup_media_resources()
        
        # 4. Clean up UI widgets and layout
        self._cleanup_ui_components()
        
        # 5. Final cleanup
        self._final_cleanup()
        
        event.accept()
        logger.info("TeamMember screen closed successfully with comprehensive cleanup")
        super().closeEvent(event)
    
    def _cleanup_timers(self):
        """Clean up all timers with proper signal disconnection"""
        if hasattr(self, 'timer') and self.timer:
            try:
                self.timer.stop()
                # Disconnect all signals safely
                try:
                    self.timer.timeout.disconnect()
                except (TypeError, RuntimeError):
                    pass  # Signal not connected or already disconnected
                self.timer = None
                logger.debug("Timer cleaned up")
            except Exception as e:
                logger.warning(f"Error stopping timer: {e}")
    
    def _cleanup_qml_components(self):
        """Clean up QML widget and backend"""
        # Clean up QML widget
        if hasattr(self, 'teamname_qml') and self.teamname_qml:
            try:
                # Test if widget is still valid
                self.teamname_qml.isVisible()
                logger.debug("Cleaning up TeamName QML widget...")
                
                # Disconnect all signals before deletion
                signal_methods = ['statusChanged', 'sceneGraphError']
                for signal_method in signal_methods:
                    try:
                        signal = getattr(self.teamname_qml, signal_method)
                        signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                
                self.teamname_qml.deleteLater()
                logger.debug("TeamName QML widget cleaned up")
            except RuntimeError:
                logger.debug("TeamName QML widget was already deleted")
            except Exception as e:
                logger.warning(f"Error cleaning up TeamName QML widget: {e}")
            finally:
                self.teamname_qml = None

        # Clean up QML backend
        if hasattr(self, 'team_backend') and self.team_backend:
            try:
                # Stop any running operations in backend
                if hasattr(self.team_backend, 'stop'):
                    self.team_backend.stop()
                self.team_backend = None
                logger.debug("Team backend cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up team backend: {e}")
    
    def _cleanup_media_resources(self):
        """Clean up media resources including movies and pixmaps"""
        # Clean up background movie
        if hasattr(self, 'background_movie') and self.background_movie:
            try:
                self.background_movie.stop()
                self.background_movie.setCacheMode(QMovie.CacheNone)
                # Disconnect all signals
                signal_methods = ['frameChanged', 'finished']
                for signal_method in signal_methods:
                    try:
                        signal = getattr(self.background_movie, signal_method)
                        signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                self.background_movie.deleteLater()
                logger.debug("Background movie cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background movie: {e}")
            finally:
                self.background_movie = None
        
        # Clean up background pixmap
        if hasattr(self, 'background_pixmap') and self.background_pixmap:
            try:
                self.background_pixmap = None
                logger.debug("Background pixmap cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background pixmap: {e}")
    
    def _cleanup_ui_components(self):
        """Clean up UI widgets and layout components"""
        # Clean up background widget
        if hasattr(self, 'Background') and self.Background:
            try:
                self.Background.clear()
                self.Background.deleteLater()
                self.Background = None
                logger.debug("Background widget cleaned up")
            except Exception as e:
                logger.warning(f"Error clearing background: {e}")
        
        # Clean up central widget and all children
        if hasattr(self, 'centralwidget') and self.centralwidget:
            try:
                # Clean up all child widgets recursively
                children = self.centralwidget.findChildren(QtCore.QObject)
                for child in children:
                    try:
                        child.deleteLater()
                    except (RuntimeError, AttributeError):
                        pass
                self.centralwidget.deleteLater()
                self.centralwidget = None
                logger.debug("Central widget and children cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning central widget: {e}")
    
    def _final_cleanup(self):
        """Final cleanup of any remaining references"""
        # Clear any remaining object references
        cleanup_attrs = ['teamname_qml', 'team_backend', 'background_pixmap', 
                        'background_movie', 'Background', 'centralwidget']
        for attr in cleanup_attrs:
            if hasattr(self, attr):
                setattr(self, attr, None)
        
        logger.debug("Final cleanup completed")


class Home_screen(QtWidgets.QMainWindow):
    """Complete Home Screen implementation"""
    
    def load_custom_font(self, font_path):
        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_path}")
            return "Default"
        font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            return font_families[0]
        return "Default"

    # def play_audio(self):
    #     """Load and play the audio file."""
    #     audio_file = "Assets/mp3/2066.wav"
    #     absolute_path = os.path.abspath(audio_file)
    #     print("Absolute path:", absolute_path)
    #     self.player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(absolute_path)))
    #     self.player.setVolume(100)
    #     self.player.play()
    #     self.player.mediaStatusChanged.connect(self.check_media_status)
    
    # def check_media_status(self, status):
    #     """Check media status and stop playback if finished."""
    #     if status == QMediaPlayer.MediaStatus.EndOfMedia:
    #         self.player.stop()
        
    def setupUi(self, Home):
        Home.setObjectName("Home")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        Home.setLayoutDirection(QtCore.Qt.LeftToRight)
        Home.setAutoFillBackground(False)

        self.centralwidget = QtWidgets.QWidget(Home)
        self.centralwidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        print(Home.geometry().width())
        self.font_family = self.load_custom_font("Assets/Fonts/GOTHIC.TTF")
        self.font_family_good = self.load_custom_font("Assets/Fonts/good_times_rg.ttf")
        
        if Home.geometry().width() > 1920:
            background_gif_path = "Assets/1k/Fast_Reaction.gif"
            self.scale = 2
            global scaled
            scaled = 2
        else:
            background_gif_path = "Assets/1k/Fast_Reaction.gif"
            self.scale = 1  
            scaled = 1
        
        self.Background = QtWidgets.QLabel(self.centralwidget)
        self.Background.setScaledContents(True)
        self.Background.setGeometry(0, 0, Home.geometry().width(), Home.geometry().height())
        self.Background.setText("")
        
        # Initialize background_movie as None for safety
        self.background_movie = None
        
        # Safe movie creation and assignment with performance optimizations
        try:
            self.background_movie = QMovie(background_gif_path)
            if self.background_movie.isValid():
                # Use CacheNone for better performance with large GIFs
                self.background_movie.setCacheMode(QMovie.CacheNone)
                # Set speed to normal (100% speed)
                self.background_movie.setSpeed(100)
                
                # Preload first frame to prevent white flash
                try:
                    self.background_movie.jumpToFrame(0)
                    # Set first frame immediately to prevent lag
                    first_frame = self.background_movie.currentPixmap()
                    if not first_frame.isNull():
                        self.Background.setPixmap(first_frame)
                except Exception:
                    pass
                
                # Connect frame update signal for optimized playback
                try:
                    self.background_movie.frameChanged.connect(self._update_background_frame)
                except Exception:
                    pass
                
                self.Background.setMovie(self.background_movie)
                self.background_movie.start()
                
                logger.debug(f"Home screen background GIF loaded successfully: {background_gif_path}")
            else:
                logger.warning(f"Invalid GIF file: {background_gif_path}")
        except Exception as e:
            logger.error(f"Error loading background movie: {e}")
            self.background_movie = None
            
        self.Background.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        # QML Leaderboard (transparent, 1920x1080)
        try:
            self.leaderboard_qml = QQuickWidget(self.centralwidget)
            self.leaderboard_qml.setClearColor(QtCore.Qt.transparent)
            fmt = QSurfaceFormat()
            fmt.setAlphaBufferSize(8)
            self.leaderboard_qml.setFormat(fmt)
            self.leaderboard_qml.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.leaderboard_qml.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
            self.leaderboard_qml.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
            self.leaderboard_qml.setAttribute(QtCore.Qt.WA_AlwaysStackOnTop, True)
            self.leaderboard_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)

            import os
            qml_path = os.path.join(os.path.dirname(__file__),"Leaderboard_screen_enhanced.qml")
            self.leaderboard_qml.setSource(QUrl.fromLocalFile(qml_path))

            global lastplayed_score, lastplayed_weighted_points, lastplayed_rank
            leaderboard , lastplayed = api.get_leaderboard()
            if lastplayed is not None:
                lastplayed_score = lastplayed.get('total_score', 0)
                lastplayed_weighted_points = lastplayed.get('weighted_points', 0)
                lastplayed_rank = lastplayed.get('rank', 0)
            list_top5_FastReaction.clear()
            list_top5_FastReaction.extend(leaderboard)
            # Geometry full screen (1920x1080 base, scale adapt if needed)
            self.leaderboard_qml.setGeometry(QtCore.QRect(0, 0, Home.geometry().width(), Home.geometry().height()))

            # Seed initial data from list_top5_FastReaction
            try:
                root_obj = self.leaderboard_qml.rootObject()
                if root_obj:
                    # Create and attach backend
                    self.leaderboard_backend = EnhancedLeaderboardBackend()
                    root_obj.setProperty('backend', self.leaderboard_backend)
                    # Seed initial data from API list
                    sorted_data = sorted(list_top5_FastReaction, key=lambda it: it[2], reverse=True)[:3]
                    for idx, item in enumerate(sorted_data):
                        team, score, weighted_points = item[0], item[1], item[2]
                        self.leaderboard_backend.update_player_table_name(idx, str(team))
                        self.leaderboard_backend.update_player_table_score(idx, int(score))
                        self.leaderboard_backend.update_player_table_weighted_points(idx, int(weighted_points))
                        self.leaderboard_backend.update_player_table_rank(idx, int(idx + 1))
                    if lastplayed is not None:
                        self.leaderboard_backend.update_last_player_name(str(lastplayed.get('name', 'Unknown')))
                        self.leaderboard_backend.update_last_player_score(int(lastplayed.get('total_score', 0)))
                        self.leaderboard_backend.update_last_player_weighted_points(int(lastplayed.get('weighted_points', 0)))
                        self.leaderboard_backend.update_last_player_rank(int(lastplayed.get('rank', 0)))
            except Exception:
                pass

            self.leaderboard_qml.hide()
            self.leaderboard_qml.raise_()
        except Exception:
            self.leaderboard_qml = None

        # Remove legacy table entirely
        self.frame_2 = None
        self.gridLayout = None
        self.LeaderboardTable = None
        Home.setCentralWidget(self.centralwidget)
        
        # Timers for showing table and switching to inactive
        self.timer = QTimer(Home)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.Inactive)
        self.timer.start(10000)
        
        # Background pixmap is already set
        
       
        
        self.timer3 = QTimer(Home)
        self.timer3.setTimerType(Qt.PreciseTimer)
        self.timer3.timeout.connect(self.looping)
        
        # No legacy table headers to translate
        # self.play_audio()
        
        QtCore.QMetaObject.connectSlotsByName(Home)
    
    def retranslateUi(self, Home):
        _translate = QtCore.QCoreApplication.translate
        Home.setWindowTitle(_translate("Home", "MainWindow"))
        # No legacy table content
    
    def showTable(self):
        try:
            if hasattr(self, 'leaderboard_qml') and self.leaderboard_qml:
                self.leaderboard_qml.show()
                self.leaderboard_qml.raise_()
        except Exception:
            pass
        
    def hideTable(self):
        try:
            if hasattr(self, 'leaderboard_qml') and self.leaderboard_qml:
                self.leaderboard_qml.hide()
        except Exception:
            pass
    
    def UpdateTable(self):
        global list_top5_FastReaction
        # Update QML via backend signals
        try:
            if hasattr(self, 'leaderboard_backend') and self.leaderboard_backend:
                sorted_data = sorted(list_top5_FastReaction, key=lambda it: it[2], reverse=True)[:3]
                for idx, item in enumerate(sorted_data):
                    print(item)
                    team, score, weighted_points = item[0], item[1], item[2]
                    self.leaderboard_backend.update_player_table_name(idx, str(team))
                    self.leaderboard_backend.update_player_table_score(idx, int(score))
                    self.leaderboard_backend.update_player_table_weighted_points(idx, int(weighted_points))
                    self.leaderboard_backend.update_player_table_rank(idx, int(idx + 1))
                if lastplayed is not None:
                    self.leaderboard_backend.update_last_player_name(str(lastplayed.get('name', 'Unknown')))
                    self.leaderboard_backend.update_last_player_score(int(lastplayed.get('total_score', 0)))
                    self.leaderboard_backend.update_last_player_weighted_points(int(lastplayed.get('weighted_points', 0)))
                    self.leaderboard_backend.update_last_player_rank(int(lastplayed.get('rank', 0)))
        except Exception:
            pass

    def Inactive(self):
        self.timer.stop()
        self.timer3.start(9000)
        if scaled == 1:
            background_gif_path = "Assets/1k/background.gif"
        else:
            background_gif_path = "Assets/1k/background.gif"
        # swap movie
        # Use safe movie replacement method
        self._safe_replace_background_movie(background_gif_path)
        # Show QML leaderboard during inactive
        try:
            self.showTable()
            self.UpdateTable()
        except Exception:
            pass
        global homeOpened
        homeOpened = True
    
    def _safe_replace_background_movie(self, gif_path):
        """Safely replace background movie with proper cleanup"""
        try:
            # Clean up existing movie first
            if hasattr(self, 'background_movie') and self.background_movie is not None:
                try:
                    self.background_movie.stop()
                    # Disconnect all signals before deletion
                    try:
                        self.background_movie.frameChanged.disconnect()
                        self.background_movie.finished.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                    self.background_movie.deleteLater()
                except Exception as e:
                    logger.warning(f"Error cleaning up old background movie: {e}")
                finally:
                    self.background_movie = None
            
            # Clear the background label before setting new movie
            if hasattr(self, 'Background') and self.Background is not None:
                self.Background.setMovie(None)
                
            # Create new movie
            self.background_movie = QMovie(gif_path)
            if self.background_movie.isValid():
                self.background_movie.setCacheMode(QMovie.CacheAll)
                # Set speed to normal (100% speed)
                self.background_movie.setSpeed(100)
                
                # Only set movie if Background still exists
                if hasattr(self, 'Background') and self.Background is not None:
                    self.Background.setMovie(self.background_movie)
                    self.background_movie.start()
                    logger.debug("Background movie replaced successfully")
                    return True
                else:
                    logger.warning("Background label no longer exists, skipping movie assignment")
                    return False
            else:
                logger.warning(f"Invalid GIF file: {gif_path}")
                self.background_movie = None
                return False
                
        except Exception as e:
            logger.error(f"Error replacing background movie: {e}")
            self.background_movie = None
            return False

    def _update_background_frame(self, frame_number):
        """Optimized frame update for smooth GIF playback"""
        try:
            if hasattr(self, 'background_movie') and self.background_movie and self.background_movie.isValid():
                # Only update every few frames to reduce CPU usage
                if frame_number % 2 == 0:  # Update every 2nd frame
                    current_frame = self.background_movie.currentPixmap()
                    if not current_frame.isNull() and hasattr(self, 'Background') and self.Background:
                        self.Background.setPixmap(current_frame)
        except Exception:
            pass

    def looping(self):
        """Enhanced looping function with improved safety (from game2)"""
        logger.debug("Starting looping cycle")
        global lastplayed_score, lastplayed_weighted_points, lastplayed_rank
        leaderboard , lastplayed = api.get_leaderboard()
        if lastplayed is not None:
            lastplayed_score = lastplayed.get('total_score', 0)
            lastplayed_weighted_points = lastplayed.get('weighted_points', 0)
            lastplayed_rank = lastplayed.get('rank', 0)
        list_top5_FastReaction.clear()
        list_top5_FastReaction.extend(leaderboard)
        # Safe timer stop
        try:
            if hasattr(self, 'timer3') and self.timer3:
                self.timer3.stop()
        except (RuntimeError, AttributeError):
            pass

        # Hide QML leaderboard when looping back
        try:
            self.hideTable()
        except Exception:
            pass
            
        # Load intro image with proper scaling
        if scaled == 1:
            background_gif_path = "Assets/1k/Fast_Reaction.gif"
        else:
            background_gif_path = "Assets/1k/Fast_Reaction.gif"
            
        # Safe background and pixmap operations
        # Use safe movie replacement method
        self._safe_replace_background_movie(background_gif_path)
            
        # Safe timer restart with proper error handling
        try:
            if hasattr(self, 'timer') and self.timer:
                self.timer.start(10000)
                logger.debug("⏰ Timer restarted for 11 seconds")
        except (RuntimeError, AttributeError):
            logger.debug("Timer already deleted, skipping start()")
            
        # Set homeOpened flag for game manager detection
        global homeOpened
        homeOpened = True
        logger.debug(" Looping cycle completed successfully")
    
    def closeEvent(self, event):
        """Enhanced cleanup for Home_screen with comprehensive resource management"""
        logger.info("Home screen closing with enhanced cleanup...")
        
        # 1. Stop all timers first to prevent any ongoing operations
        self._cleanup_timers()
        
        # 2. Clean up QML components
        self._cleanup_qml_components()
        
        # 3. Clean up media and background resources
        self._cleanup_media_resources()
        
        # 4. Clean up UI widgets and layout
        self._cleanup_ui_components()
        
        # 5. Final cleanup
        self._final_cleanup()
        
        event.accept()
        logger.info("Home screen closed successfully with comprehensive cleanup")
        super().closeEvent(event)
    
    def _cleanup_timers(self):
        """Clean up all timers with proper signal disconnection"""
        timer_attrs = ['timer', 'timer3']
        for timer_attr in timer_attrs:
            if hasattr(self, timer_attr):
                timer = getattr(self, timer_attr)
                if timer is not None:
                    try:
                        timer.stop()
                        # Disconnect all signals safely
                        try:
                            timer.timeout.disconnect()
                        except (TypeError, RuntimeError):
                            pass  # Signal not connected or already disconnected
                        setattr(self, timer_attr, None)
                        logger.debug(f"{timer_attr} cleaned up")
                    except Exception as e:
                        logger.warning(f"Error cleaning up {timer_attr}: {e}")
                        setattr(self, timer_attr, None)
    
    def _cleanup_qml_components(self):
        """Clean up QML widgets and backends"""
        # Clean up leaderboard QML widget
        if hasattr(self, 'leaderboard_qml') and self.leaderboard_qml:
            try:
                # Test if widget is still valid
                self.leaderboard_qml.isVisible()
                logger.debug("Cleaning up Leaderboard QML widget...")
                
                # Disconnect all signals before deletion
                signal_methods = ['statusChanged', 'sceneGraphError']
                for signal_method in signal_methods:
                    try:
                        signal = getattr(self.leaderboard_qml, signal_method)
                        signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                
                self.leaderboard_qml.deleteLater()
                logger.debug("Leaderboard QML widget cleaned up")
            except RuntimeError:
                logger.debug("Leaderboard QML widget was already deleted")
            except Exception as e:
                logger.warning(f"Error cleaning up Leaderboard QML widget: {e}")
            finally:
                self.leaderboard_qml = None

        # Clean up QML backend
        if hasattr(self, 'leaderboard_backend') and self.leaderboard_backend:
            try:
                # Stop any running operations in backend
                if hasattr(self.leaderboard_backend, 'stop'):
                    self.leaderboard_backend.stop()
                self.leaderboard_backend = None
                logger.debug("Leaderboard backend cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up leaderboard backend: {e}")
    
    def _cleanup_media_resources(self):
        """Clean up media resources including movies and pixmaps"""
        # Clean up background movie
        if hasattr(self, 'background_movie') and self.background_movie:
            try:
                self.background_movie.stop()
                self.background_movie.setCacheMode(QMovie.CacheNone)
                # Disconnect all signals
                signal_methods = ['frameChanged', 'finished']
                for signal_method in signal_methods:
                    try:
                        signal = getattr(self.background_movie, signal_method)
                        signal.disconnect()
                    except (AttributeError, TypeError, RuntimeError):
                        pass
                self.background_movie.deleteLater()
                logger.debug("Background movie cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background movie: {e}")
            finally:
                self.background_movie = None
        
        # Clean up background pixmap
        if hasattr(self, 'background_pixmap') and self.background_pixmap:
            try:
                self.background_pixmap = None
                logger.debug("Background pixmap cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background pixmap: {e}")
    
    def _cleanup_ui_components(self):
        """Clean up UI widgets and layout components"""
        
        # Clean up background widget
        if hasattr(self, 'Background') and self.Background is not None:
            try:
                self.Background.clear()
                try:
                    self.Background.setMovie(None)
                except Exception:
                    pass
                self.Background.deleteLater()
                logger.debug("Background widget cleaned up")
            except (RuntimeError, AttributeError):
                logger.debug("Background widget already deleted by Qt, skipping cleanup")
            finally:
                self.Background = None
        
        # Clean up background movie
        if hasattr(self, 'background_movie') and self.background_movie is not None:
            try:
                self.background_movie.stop()
                # Disconnect frame update signal
                try:
                    self.background_movie.frameChanged.disconnect()
                except (AttributeError, TypeError, RuntimeError):
                    pass
                # Disconnect all signals before deletion
                try:
                    self.background_movie.finished.disconnect()
                except (AttributeError, TypeError, RuntimeError):
                    pass
                self.background_movie.deleteLater()
                logger.debug("Background movie cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background movie: {e}")
            finally:
                self.background_movie = None
        
        
        # Clean up central widget and all children
        if hasattr(self, 'centralwidget') and self.centralwidget is not None:
            try:
                # Clean up all child widgets recursively
                children = self.centralwidget.findChildren(QtCore.QObject)
                for child in children:
                    try:
                        child.deleteLater()
                    except (RuntimeError, AttributeError):
                        pass
                self.centralwidget.deleteLater()
                logger.debug("Central widget and children cleaned up")
            except (RuntimeError, AttributeError):
                logger.debug("Central widget already deleted by Qt, skipping cleanup")
            finally:
                self.centralwidget = None
    
    def _final_cleanup(self):
        """Final cleanup of any remaining references"""
        # Clear any remaining object references
        cleanup_attrs = ['leaderboard_qml', 'leaderboard_backend', 'background_pixmap', 
                        'background_movie', 'Background', 'centralwidget']
        for attr in cleanup_attrs:
            if hasattr(self, attr):
                setattr(self, attr, None)
        
        logger.debug("Final cleanup completed")

class MainApp(QtWidgets.QMainWindow):
    """Complete Main Application with all screens and new API integration"""
    
    def __init__(self):
        super().__init__()
        logger.info(" MainApp initializing with complete UI and new API...")
        
        # Initialize Serial thread from config
        self.serial_thread = None
        serial_config = config.settings.serial
        
        if serial_config.enabled:
            try:
                self.serial_thread = SimpleSerialThread(serial_config)
                self.serial_thread.start()
                logger.info(f" Serial thread initialized for port: {serial_config.port}")
                logger.info(f" Serial config: baudrate={serial_config.baudrate}, auto_reconnect={serial_config.auto_reconnect}")
            except Exception as e:
                logger.warning(f"️  Failed to initialize serial thread: {e}")
                self.serial_thread = None
        else:
            logger.info(" Serial communication disabled in config")
        
        # Setup mainWindow and screens
        self.sized = QtWidgets.QDesktopWidget().screenGeometry()
        self.ui_final = Final_Screen()
        self.ui_home = Home_screen()
        self.ui_active = Active_screen(serial_thread=self.serial_thread)    
        self.ui_team_member = TeamMember_screen()
        
        self.mainWindow = QtWidgets.QMainWindow()

        self.mainWindow.setObjectName("Home")
        self.mainWindow.setWindowTitle("Fast Reaction Game - Complete")
        self.mainWindow.setFixedSize(self.sized.width(), self.sized.height())
        # self.mainWindow.setFixedSize(3840, 2160)
        print(self.sized.width(), self.sized.height())
        self.mainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        # Set default background color immediately to prevent white screen flashes
        self._set_background_image("Assets/imgSeq_0.jpg")
        
        # Initialize GameManager with new API
        try:
            self.game_manager = GameManager()
            logger.info(" GameManager initialized with new API")
        except Exception as e:
            logger.error(f" Failed to initialize GameManager: {e}")
            raise
            
        # Connection signals for the game manager with safety checks
        if hasattr(self, 'game_manager') and self.game_manager:
            # 1. init_signal: Triggered when the game manager is initialized
            self.game_manager.init_signal.connect(self.start_TeamMember_screen)
            # 2. start_signal: Triggered when the game manager starts
            self.game_manager.start_signal.connect(lambda: (
                self.start_Active_screen(),
                self._safe_mqtt_subscribe(),
                self.ui_active.start_game() if hasattr(self, 'ui_active') and self.ui_active else None
            ))
            # 3. cancel_signal: Triggered when the game manager is cancelled
            self.game_manager.cancel_signal.connect(self._handle_game_cancellation)
            # 4. submit_signal: Triggered when the game manager is submitted
            self.game_manager.submit_signal.connect(self.start_final_screen)
            logger.debug(" GameManager signals connected successfully")
            
            # Connect deactivate signal to trigger score submission (with enhanced safety checks)
            if (hasattr(self, 'ui_active') and self.ui_active and 
                hasattr(self.ui_active, 'mqtt_thread') and self.ui_active.mqtt_thread and
                hasattr(self.ui_active.mqtt_thread, 'deactivate_signal')):
                try:
                    self.ui_active.mqtt_thread.deactivate_signal.connect(
                        self.game_manager.trigger_score_submission
                    )
                    logger.debug(" Deactivate signal connected to GameManager")
                except Exception as e:
                    logger.warning(f"️  Error connecting deactivate signal: {e}")
            else:
                logger.warning("️  MQTT thread or deactivate signal not properly initialized")
        else:
            logger.error(" GameManager not available for signal connections")
        # ------------------------------
        audio_files = {
            'continuous': 'Assets/mp3/2066.wav',
            'inactive_game': 'Assets/mp3/game-music-loop-inactive.mp3',
            # correct.mp3
# correct_2.mp3
# miss.mp3
# wrong-answer.mp3
# wrong-answer_2.mp3
            'active_game': 'Assets/mp3/game-music-loop-active.mp3',
            'miss_sound': 'Assets/mp3/miss.mp3',
            'ok_sound': 'Assets/mp3/game-music-loop-active.mp3',
            'crct_sound': 'Assets/mp3/correct.mp3',
            'mstk_sound': 'Assets/mp3/wrong-answer.mp3'
        }
        
        self.audio_thread = AudioServiceThread(audio_files)
        
        # Connect signals - use service_ready to play audio only when ready
        self.audio_thread.service_ready.connect(self._on_audio_service_ready)
        # self.audio_thread.service_error.connect(lambda error: print(f"Audio service error: {error}"))
        # self.audio_thread.player_state_changed.connect(
        #     lambda name, state: print(f"Player {name} state: {state}")
        # )
# Connect audio signals for sound effects (optional - game continues even if this fails)
        if not self._connect_active_screen_audio_signals():
            logger.warning("️  Some or all active screen audio signals could not be connected")
        
        self.start_Home_screen()

        # Start the thread (audio will play when service_ready signal is emitted)
        self.audio_thread.start()
        print("🚀 Starting audio service thread...")
    
    def _on_audio_service_ready(self):
        """Called when audio service is fully initialized and ready"""
        logger.info("✅ Audio service ready - starting inactive game sound")
        # Now it's safe to play audio
        self.audio_thread.play_inactive_game_sound()

        """
        @comment: keep this for testing the game manager
        """
        # ------------------------------
        # self.start_Active_screen()
        # self.serial_thread.start_monitoring()
        # self.serial_thread.serial_connection.write("Start\n".encode('utf-8'))
        # self.ui_active.start_game()
        # ------------------------------
        # self.start_final_screen()

        # Start game manager after delay 
        QtCore.QTimer.singleShot(5000, self.game_manager.start)
        
        self.mainWindow.showFullScreen()
        logger.info(" MainApp initialization complete")
                
    def start_Home_screen(self):
        logger.info(" Starting Home Screen")
        
        # Set background image immediately to prevent white screen flashes
        self._set_background_image("Assets/imgSeq_0.jpg")
        QApplication.processEvents()  # Force immediate UI update
        
        # Force stop all timers before transition
        self._force_stop_all_timers()
        
        # Clean up previous screens (this now includes stopping all audio)
        self._cleanup_previous_screens()
        
        # Small delay to ensure audio cleanup is complete, then start inactive sound
        QTimer.singleShot(100, self._start_inactive_audio_for_home)

        # Reset global game state
        global list_players_score, list_players_name, scored, serial_scoring_active ,correct_count, miss_count, wrong_count, last_player_name, last_player_score, last_player_weighted_points, last_player_rank
        list_players_score = [0,0,0,0,0]
        list_players_name.clear()
        scored = 0
        serial_scoring_active = False
        correct_count = 0
        miss_count = 0
        wrong_count = 0
        last_player_name = ""
        last_player_score = 0
        last_player_weighted_points = 0
        last_player_rank = 0
        
        # Initialize home screen with error handling
        if hasattr(self, 'ui_home') and self.ui_home:
            try:
                self.ui_home.setupUi(self.mainWindow)
                logger.info(" Home screen initialized successfully")
                
                # Set homeOpened flag so game manager can detect home screen is ready
                global homeOpened
                homeOpened = True
                logger.info(" Home screen is now ready for game initialization")
                
            except Exception as e:
                logger.error(f" Error setting up home screen: {e}")
                return
        else:
            logger.error(" ui_home not properly initialized")
            return
       
        quit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('q'), self.mainWindow)
        quit_shortcut.activated.connect(self.close_application)
        
    def start_TeamMember_screen(self):
        logger.info(" Starting TeamMember Screen")
        
        # Set background image immediately to prevent white screen flashes
        self._set_background_image("Assets/imgSeq_0.jpg")
        QApplication.processEvents()  # Force immediate UI update
        
        # Clean up previous screens (this now includes stopping all audio)
        self._cleanup_previous_screens()
        
        # Small delay to ensure audio cleanup is complete, then start inactive sound
        QTimer.singleShot(100, self._start_inactive_audio_for_teammember)
        
        # Initialize team member screen with error handling
        if hasattr(self, 'ui_team_member') and self.ui_team_member:
            try:
                self.ui_team_member.setupUi(self.mainWindow)
                logger.info(" TeamMember screen initialized successfully")
            except Exception as e:
                logger.error(f" Error setting up team member screen: {e}")
                return
        else:
            logger.error(" ui_team_member not properly initialized")
            return
       
        quit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('q'), self.mainWindow)
        quit_shortcut.activated.connect(self.close_application)
    
    def _handle_game_cancellation(self):
        """Robust handler for game cancellation that works regardless of current screen state (improved from CAGE)"""
        logger.warning("" + "=" * 50)
        logger.warning(" GAME CANCELLATION DETECTED")
        logger.warning("" + "=" * 50)
        
        try:
            # Safely cleanup active screen components
            if hasattr(self, 'ui_active') and self.ui_active:
                try:
                    if hasattr(self.ui_active, 'TimerGame') and self.ui_active.TimerGame:
                        self.ui_active.TimerGame.stop()
                        logger.debug(" TimerGame stopped")
                except Exception as e:
                    logger.warning(f"️  Error stopping TimerGame: {e}")
                
                try:
                    if hasattr(self.ui_active, 'timer') and self.ui_active.timer:
                        self.ui_active.timer.stop()
                        logger.debug(" Timer stopped")
                except Exception as e:
                    logger.warning(f"️  Error stopping timer: {e}")
                
                
                try:
                    if hasattr(self.ui_active, 'mqtt_thread') and self.ui_active.mqtt_thread:
                        self.ui_active.mqtt_thread.unsubscribe_from_data_topics()
                        logger.debug(" MQTT unsubscribed")
                except Exception as e:
                    logger.warning(f"️  Error unsubscribing MQTT: {e}")
                
                try:
                    # Check if ui_active is still valid before closing
                    try:
                        self.ui_active.objectName()  # Test if object is still valid
                        self.ui_active.close()
                        logger.debug(" Active screen closed")
                    except RuntimeError:
                        logger.debug(" Active screen was already deleted by Qt")
                except Exception as e:
                    logger.warning(f"️  Error closing active screen: {e}")
                
                # CRITICAL: Reset the Active_screen state instead of recreating it
                try:
                    logger.info(" Resetting Active_screen state after cancellation...")
                    self._reset_active_screen_state()
                    logger.info(" Active_screen state reset successfully")
                    
                except Exception as e:
                    logger.error(f" Error resetting Active_screen state: {e}")
            
            # Force manual reset of essential flags only
            if hasattr(self, 'game_manager') and self.game_manager:
                self.game_manager.game_result_id = None
                self.game_manager.submit_score_flag = False
                self.game_manager.started_flag = False  # CRITICAL: Reset like CAGE_Game.py
                self.game_manager.cancel_flag = False
                logger.debug(f" GameManager flags reset: started_flag={self.game_manager.started_flag}")
            
        except Exception as e:
            logger.error(f" Error during cancellation cleanup: {e}")
        
        # Always try to go to home screen, regardless of cleanup errors
        try:
            logger.info(" Moving to home screen after cancellation...")
            
            # CRITICAL: Clean up ALL screen GIF resources to prevent lagging
            screens_to_cleanup = [
                ('ui_home', 'Homescreen'),
                ('ui_team_member', 'TeamMember screen'),
                ('ui_active', 'Active screen'),
                ('ui_final', 'Final screen')
            ]
            
            for screen_attr, screen_name in screens_to_cleanup:
                if hasattr(self, screen_attr):
                    screen = getattr(self, screen_attr)
                    if screen:
                        try:
                            # Stop timers
                            for timer_name in ['timer', 'timer2', 'timer3', 'TimerGame']:
                                if hasattr(screen, timer_name):
                                    timer = getattr(screen, timer_name)
                                    if timer:
                                        timer.stop()
                            
                            # Clean up QML widgets with proper hide + delete pattern
                            for qml_attr in ['teamname_qml', 'qml_widget', 'teamscore_qml', 'leaderboard_qml']:
                                if hasattr(screen, qml_attr):
                                    qml_widget = getattr(screen, qml_attr)
                                    if qml_widget:
                                        try:
                                            # Hide first to prevent black background flash
                                            qml_widget.hide()
                                            qml_widget.deleteLater()
                                            setattr(screen, qml_attr, None)
                                            logger.debug(f" {screen_name} {qml_attr} cleaned up")
                                        except RuntimeError as e:
                                            if "deleted" in str(e):
                                                logger.debug(f" {screen_name} {qml_attr} already deleted by Qt")
                                            else:
                                                logger.warning(f" Runtime error cleaning up {screen_name} {qml_attr}: {e}")
                                        except Exception as e:
                                            logger.warning(f" Error cleaning up {screen_name} {qml_attr}: {e}")
                            
                            # Clean up backends
                            for backend_attr in ['team_backend', 'teamscore_backend', 'leaderboard_backend', 'fastreaction_backend']:
                                if hasattr(screen, backend_attr):
                                    backend = getattr(screen, backend_attr)
                                    if backend:
                                        try:
                                            if hasattr(backend, 'stop'):
                                                backend.stop()
                                            elif hasattr(backend, 'stop_countdown'):
                                                backend.stop_countdown()
                                            setattr(screen, backend_attr, None)
                                            logger.debug(f" {screen_name} {backend_attr} cleaned up")
                                        except Exception as e:
                                            logger.warning(f" Error cleaning up {screen_name} {backend_attr}: {e}")
                            
                            # Background cleanup is handled by _cleanup_previous_screens() in start_Home_screen()
                            
                            logger.debug(f" {screen_name} resources cleaned up")
                        except RuntimeError as runtime_error:
                            # Silently ignore Qt object deletion errors - these are normal
                            if "deleted" in str(runtime_error):
                                logger.debug(f" {screen_name} resources already deleted by Qt")
                            else:
                                logger.warning(f" Runtime error cleaning up {screen_name}: {runtime_error}")
                        except Exception as cleanup_error:
                            logger.warning(f" Error cleaning up {screen_name} resources: {cleanup_error}")
            
            # Set background image to prevent black screen during transition
            self._set_background_image("Assets/imgSeq_0.jpg")
            
            self.start_Home_screen()
            logger.info(" Successfully moved to home screen after cancellation")
        except Exception as e:
            logger.error(f" Error moving to home screen after cancellation: {e}")
            # Last resort - try basic home screen setup
            try:
                if hasattr(self, 'ui_home') and self.ui_home:
                    self.ui_home.setupUi(self.mainWindow)
                    self.mainWindow.show()
                    logger.info(" Last resort home screen setup successful")
            except Exception as last_resort_error:
                logger.error(f" Last resort home screen setup failed: {last_resort_error}")

        if self.serial_thread:
            self.serial_thread.stop_monitoring()
            logger.info(" Serial monitoring stopped for game")
        
    def _reset_active_screen_state(self):
        """Reset Active_screen state without recreating objects to avoid resource conflicts (from CAGE)"""
        try:
            if not hasattr(self, 'ui_active') or not self.ui_active:
                logger.warning("️  ui_active not available for state reset")
                return
            
            logger.info(" Resetting Active_screen state without object recreation...")
            
            # Reset game state variables specific to Fast Reaction
            global gameStarted, firstDetected, scored, serial_scoring_active
            global list_players_score, list_players_name
            
            gameStarted = False
            firstDetected = False
            scored = 0
            serial_scoring_active = False
            global correct_count, miss_count, wrong_count
            correct_count = 0
            miss_count = 0
            wrong_count = 0
            
            # Reset score tracking
            list_players_score = [0,0,0,0,0]
            list_players_name.clear()
            
            logger.debug(" Global game state variables reset")
            
            # Reset MediaPlayer state (reuse existing player) - Fast Reaction doesn't use MediaPlayer
            # Skip MediaPlayer reset for Fast Reaction
            
            # Reset MQTT thread state (reuse existing connection if available)
            if hasattr(self.ui_active, 'mqtt_thread') and self.ui_active.mqtt_thread:
                try:
                    # Check if MQTT is still connected
                    if (hasattr(self.ui_active.mqtt_thread, 'connected') and 
                        self.ui_active.mqtt_thread.connected and
                        hasattr(self.ui_active.mqtt_thread, 'client') and
                        self.ui_active.mqtt_thread.client):
                        logger.debug(" MQTT thread still connected, reusing existing connection")
                    else:
                        logger.debug(" MQTT thread disconnected, will reconnect on next game start")
                except Exception as e:
                    logger.warning(f"️  Error checking MQTT state: {e}")
            
            # Reset UI state if needed
            try:
                # Reset any timers (but don't recreate them)
                if hasattr(self.ui_active, 'timer') and self.ui_active.timer:
                    self.ui_active.timer.stop()
                
                if hasattr(self.ui_active, 'TimerGame') and self.ui_active.TimerGame:
                    self.ui_active.TimerGame.stop()
                
                # Reset QML widget state
                if hasattr(self.ui_active, 'reset_qml_widget'):
                    try:
                        self.ui_active.reset_qml_widget()
                        logger.debug(" QML widget state reset")
                    except Exception as e:
                        logger.warning(f"️  Error resetting QML widget state: {e}")
                
                logger.debug(" UI state reset completed")
                
            except Exception as e:
                logger.warning(f"️  Error resetting UI state: {e}")
            
            # Reconnect audio signals after reset
            try:
                logger.info("Reconnecting audio signals after reset...")
                if self._connect_active_screen_audio_signals():
                    logger.info(" Audio signals reconnected successfully")
                else:
                    logger.warning("️  Failed to reconnect some audio signals")
            except Exception as e:
                logger.error(f" Error reconnecting audio signals: {e}")
                
            logger.info(" Active_screen state reset completed without object recreation")
            
        except Exception as e:
            logger.error(f" Error in _reset_active_screen_state: {e}")

    def _safe_mqtt_subscribe(self):
        """Safely subscribe to MQTT data topics"""
        try:
            if hasattr(self, 'ui_active') and self.ui_active:
                if hasattr(self.ui_active, 'mqtt_thread') and self.ui_active.mqtt_thread:
                    self.ui_active.mqtt_thread.subscribe_to_data_topics()
                    logger.debug(" MQTT subscribed to data topics")
                else:
                    logger.warning("️  MQTT thread not available for subscription")
        except Exception as e:
            logger.warning(f"️  Error subscribing to MQTT: {e}")
    
    def _safe_mqtt_unsubscribe(self):
        """Safely unsubscribe from MQTT data topics"""
        try:
            if hasattr(self, 'ui_active') and self.ui_active:
                if hasattr(self.ui_active, 'mqtt_thread') and self.ui_active.mqtt_thread:
                    self.ui_active.mqtt_thread.unsubscribe_from_data_topics()
                    logger.debug(" MQTT unsubscribed from data topics")
                else:
                    logger.warning("️  MQTT thread not available for unsubscription")
        except Exception as e:
            logger.warning(f"️  Error unsubscribing from MQTT: {e}")
    
    def _ensure_background_label(self):
        """Ensure background label exists and is properly initialized"""
        if not hasattr(self, 'background_label') or self.background_label is None:
            try:
                self.background_label = QtWidgets.QLabel(self.mainWindow)
                self.background_label.setGeometry(0, 0, self.mainWindow.width(), self.mainWindow.height())
                self.background_label.lower()  # Send to back
                self.background_label.setScaledContents(True)
                self.background_label.setStyleSheet("border: none;")
                logger.debug("Background label created/recreated")
                return True
            except Exception as e:
                logger.error(f"Error creating background label: {e}")
                return False
        return True

    def _set_background_image(self, image_path):
        """Set background image with proper scaling and error handling using Qt-compatible method"""
        try:
            # Check if image file exists
            if os.path.exists(image_path):
                # Method 1: Try using QLabel as background (Qt-compatible scaling)
                try:
                    # Ensure background label exists
                    if not self._ensure_background_label():
                        raise Exception("Failed to create background label")
                    
                    # Verify the label is still valid before using it
                    if self.background_label is not None:
                        # Load and set the image
                        pixmap = QtGui.QPixmap(image_path)
                        if not pixmap.isNull():
                            # Scale to fill entire window
                            scaled_pixmap = pixmap.scaled(
                                self.mainWindow.size(), 
                                QtCore.Qt.IgnoreAspectRatio, 
                                QtCore.Qt.SmoothTransformation
                            )
                            self.background_label.setPixmap(scaled_pixmap)
                            self.background_label.setGeometry(0, 0, self.mainWindow.width(), self.mainWindow.height())
                            self.background_label.lower()  # Ensure it stays in background
                            self.background_label.show()
                            logger.info(f"Background image set via QLabel: {image_path}")
                        else:
                            raise Exception("Failed to load image")
                    else:
                        raise Exception("Background label is None")
                        
                except Exception as label_error:
                    logger.warning(f"QLabel method failed: {label_error}, trying CSS method")
                    
                    # Method 2: Fallback to CSS method (without background-size)
                    stylesheet = f"""
                    QMainWindow {{
                        background-image: url({image_path});
                        background-repeat: no-repeat;
                        background-position: center;
                    }}
                    """
                    self.mainWindow.setStyleSheet(stylesheet)
                    logger.info(f"Background image set via CSS: {image_path}")
                
                # Force immediate repaint to prevent white screen
                self.mainWindow.repaint()
            else:
                logger.warning(f"Background image not found: {image_path}")
                # Fallback to solid color
                self.mainWindow.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")
                self.mainWindow.repaint()
        except Exception as e:
            logger.error(f"Error setting background image: {e}")
            # Fallback to solid color
            self.mainWindow.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")
            self.mainWindow.repaint()
    
    def _cleanup_previous_screens(self):
        """Enhanced cleanup for previous screen resources with comprehensive resource management"""
        logger.info("Cleaning up previous screens with enhanced resource management...")
        
        # 1. Stop all audio first to prevent overlapping sounds
        self._stop_all_audio()
        
        # 2. Clean up background resources
        self._cleanup_background_resources()


        
        # 3. Clean up all screen instances with proper resource management
        self._cleanup_screen_instances()
        
        # 4. Force stop all timers across all screens
        self._force_stop_all_timers()
        
        logger.info("Previous screens cleaned up successfully with comprehensive resource management")
    
    def _cleanup_background_resources(self):
        """Clean up background label and related resources"""
        if hasattr(self, 'background_label') and self.background_label:
            try:
                # Only hide the background label, don't delete it yet as it might be reused
                self.background_label.hide()
                logger.debug("Background label hidden")
            except Exception as e:
                logger.warning(f"Error hiding background label: {e}")
    
    def _cleanup_background_resources_final(self):
        """Final cleanup of background resources when application is closing"""
        if hasattr(self, 'background_label') and self.background_label:
            try:
                self.background_label.hide()
                self.background_label.deleteLater()
                self.background_label = None
                logger.debug("Background label cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up background label: {e}")
    
    def _cleanup_screen_instances(self):
        """Clean up all screen instances with enhanced resource management"""
        screen_configs = [
            ('ui_active', ['timer', 'TimerGame'], ['qml_widget'], ['fastreaction_backend'], ['background_movie', 'movie']),
            ('ui_final', ['timer', 'timer2'], ['teamscore_qml'], ['teamscore_backend'], ['background_movie']),
            ('ui_home', ['timer', 'timer3'], ['leaderboard_qml'], ['leaderboard_backend'], ['background_movie']),
            ('ui_team_member', ['timer'], ['teamname_qml'], ['team_backend'], ['background_movie'])
        ]
        
        for screen_attr, timer_attrs, qml_attrs, backend_attrs, movie_attrs in screen_configs:
            if hasattr(self, screen_attr):
                screen = getattr(self, screen_attr)
                if screen:
                    try:
                        # Stop timers
                        for timer_attr in timer_attrs:
                            if hasattr(screen, timer_attr):
                                timer = getattr(screen, timer_attr)
                                if timer:
                                    try:
                                        timer.stop()
                                        logger.debug(f"{screen_attr} {timer_attr} stopped")
                                    except Exception as e:
                                        logger.warning(f"Error stopping {screen_attr} {timer_attr}: {e}")
                        
                        # Clean up QML widgets - hide first to prevent black background flash
                        for qml_attr in qml_attrs:
                            if hasattr(screen, qml_attr):
                                qml_widget = getattr(screen, qml_attr)
                                if qml_widget:
                                    try:
                                        # Test if object is still valid before accessing
                                        qml_widget.isVisible()
                                        # Hide the widget first to prevent black background flash
                                        qml_widget.hide()
                                        qml_widget.deleteLater()
                                        setattr(screen, qml_attr, None)
                                        logger.debug(f"{screen_attr} {qml_attr} cleaned up")
                                    except RuntimeError as e:
                                        # Object already deleted by Qt - this is normal, just log as debug
                                        if "deleted" in str(e):
                                            logger.debug(f"{screen_attr} {qml_attr} already deleted by Qt")
                                        else:
                                            logger.warning(f"Runtime error cleaning up {screen_attr} {qml_attr}: {e}")
                                    except Exception as e:
                                        logger.warning(f"Error cleaning up {screen_attr} {qml_attr}: {e}")
                        
                        # Clean up backends
                        for backend_attr in backend_attrs:
                            if hasattr(screen, backend_attr):
                                backend = getattr(screen, backend_attr)
                                if backend:
                                    try:
                                        # Stop any running operations in backend
                                        if hasattr(backend, 'stop'):
                                            backend.stop()
                                        elif hasattr(backend, 'stop_countdown'):
                                            backend.stop_countdown()
                                        setattr(screen, backend_attr, None)
                                        logger.debug(f"{screen_attr} {backend_attr} cleaned up")
                                    except Exception as e:
                                        logger.warning(f"Error cleaning up {screen_attr} {backend_attr}: {e}")
                        
                        # Clean up background movies (CRITICAL for preventing lag)
                        for movie_attr in movie_attrs:
                            if hasattr(screen, movie_attr):
                                movie = getattr(screen, movie_attr)
                                if movie:
                                    try:
                                        movie.stop()
                                        # Disconnect all signals
                                        try:
                                            movie.frameChanged.disconnect()
                                            movie.finished.disconnect()
                                        except (AttributeError, TypeError, RuntimeError):
                                            pass
                                        movie.deleteLater()
                                        setattr(screen, movie_attr, None)
                                        logger.debug(f"{screen_attr} {movie_attr} cleaned up")
                                    except Exception as e:
                                        logger.warning(f"Error cleaning up {screen_attr} {movie_attr}: {e}")
                        
                        # Clean up Background labels with safety check for already-deleted Qt objects
                        if hasattr(screen, 'Background') and screen.Background:
                            try:
                                # Test if object is still valid before accessing
                                screen.Background.isVisible()
                                screen.Background.setMovie(None)
                                screen.Background.clear()
                                logger.debug(f"{screen_attr} Background label cleared")
                            except RuntimeError as e:
                                # Object already deleted by Qt - this is normal, just log as debug
                                if "deleted" in str(e):
                                    logger.debug(f"{screen_attr} Background already deleted by Qt")
                                else:
                                    logger.warning(f"Runtime error clearing {screen_attr} Background: {e}")
                            except Exception as e:
                                logger.warning(f"Error clearing {screen_attr} Background: {e}")
                        
                    except Exception as e:
                        logger.warning(f"Error cleaning up {screen_attr}: {e}")
    
    def _stop_all_audio(self):
        """Stop all audio to prevent overlapping sounds during screen transitions"""
        try:
            logger.info("🔇 Stopping all audio to prevent overlaps...")
            self.audio_thread.stop_all_sounds()
            logger.info("✅ All audio stopped successfully")
        except Exception as e:
            logger.warning(f"⚠️ Error stopping audio: {e}")
    
    def _start_inactive_audio_for_teammember(self):
        """Start inactive audio specifically for team member screen"""
        try:
            logger.info("🎵 Starting inactive audio for team member screen...")
            self.audio_thread.play_inactive_game_sound()
            logger.info("✅ Inactive audio started for team member screen")
        except Exception as e:
            logger.warning(f"⚠️ Error starting inactive audio: {e}")
    
    def _start_inactive_audio_for_home(self):
        """Start inactive audio specifically for home screen"""
        try:
            logger.info("🎵 Starting inactive audio for home screen...")
            self.audio_thread.play_inactive_game_sound()
            logger.info("✅ Inactive audio started for home screen")
        except Exception as e:
            logger.warning(f"⚠️ Error starting inactive audio: {e}")
    
    def _start_inactive_audio_for_final(self):
        """Start inactive audio specifically for final screen"""
        try:
            logger.info("🎵 Starting inactive audio for final screen...")
            self.audio_thread.play_inactive_game_sound()
            logger.info("✅ Inactive audio started for final screen")
        except Exception as e:
            logger.warning(f"⚠️ Error starting inactive audio: {e}")
    
    def _start_active_audio_for_game(self):
        """Start active audio specifically for active game screen"""
        try:
            logger.info("🎵 Starting active audio for game screen...")
            self.audio_thread.play_active_game_sound()
            logger.info("✅ Active audio started for game screen")
        except Exception as e:
            logger.warning(f"⚠️ Error starting active audio: {e}")
    
    # def _active_screen_miss_signal_sound(self):
    #     # self.audio_thread.play_miss_sound()
    #     print("miss")
    # def _active_screen_ok_signal_sound(self):
    #     # self.audio_thread.play_ok_sound()
    #     print("Played ok sound")
    def _active_screen_crct_signal_sound(self):
        logger.info("🔊 CRCT signal received - playing correct sound")
        self.audio_thread.play_crct_sound()
    def _active_screen_mstk_signal_sound(self):
        logger.info("🔊 MSTK signal received - playing mistake sound")
        self.audio_thread.play_mstk_sound()
    
    def _connect_active_screen_audio_signals(self):
        """Connect audio signals from Active_screen to MainApp audio handlers with proper disconnect-first pattern"""
        connected_count = 0
        
        if not hasattr(self, 'ui_active') or not self.ui_active:
            logger.warning("️  ui_active not available for audio signal connections")
            return False
        
        # Try to connect crct_signal (correct sound)
        if hasattr(self.ui_active, 'crct_signal'):
            try:
                self.ui_active.crct_signal.disconnect(self._active_screen_crct_signal_sound)
            except:
                pass  # Ignore if not connected
            
            try:
                self.ui_active.crct_signal.connect(self._active_screen_crct_signal_sound)
                connected_count += 1
                logger.debug(" Connected crct_signal for correct sound")
            except Exception as e:
                logger.warning(f"️  Could not connect crct_signal: {e}")
        else:
            logger.debug(" crct_signal not available on ui_active")
        
        # Try to connect mstk_signal (mistake sound)
        if hasattr(self.ui_active, 'mstk_signal'):
            try:
                self.ui_active.mstk_signal.disconnect(self._active_screen_mstk_signal_sound)
            except:
                pass  # Ignore if not connected
            
            try:
                self.ui_active.mstk_signal.connect(self._active_screen_mstk_signal_sound)
                connected_count += 1
                logger.debug(" Connected mstk_signal for mistake sound")
            except Exception as e:
                logger.warning(f"️  Could not connect mstk_signal: {e}")
        else:
            logger.debug(" mstk_signal not available on ui_active")
        
        if connected_count > 0:
            logger.info(f" Active screen audio signals connected ({connected_count} signals)")
            return True
        else:
            logger.warning("️  No active screen audio signals were connected")
            return False

    def start_Active_screen(self):
        logger.info(" Starting Active Screen")
        
        # Set background image immediately to prevent white screen flashes
        self._set_background_image("Assets/imgSeq_0.jpg")
        QApplication.processEvents()  # Force immediate UI update
        
        # Reconnect audio signals to ensure they work after cancellation
        try:
            logger.info("Reconnecting audio signals for Active screen...")
            if self._connect_active_screen_audio_signals():
                logger.info(" Audio signals reconnected successfully")
            else:
                logger.warning("️  Failed to reconnect some audio signals")
        except Exception as e:
            logger.error(f" Error reconnecting audio signals: {e}")
        
        # Check if critical audio players are ready (non-blocking check)
        if hasattr(self, 'audio_thread') and self.audio_thread:
            if not self.audio_thread.are_critical_players_ready():
                logger.warning("⚠️ Critical audio players not fully ready yet, proceeding anyway")
            else:
                logger.info("✅ All critical audio players are ready")
        
        # Initialize active screen with error handling
        if hasattr(self, 'ui_active') and self.ui_active:
            try:
                # Reinitialize mqtt thread
                self.ui_active.setupUi(self.mainWindow)
# Safely close home screen
                
                # Stop all audio first, then start active game sound after delay
                self._stop_all_audio()
                QTimer.singleShot(50, self._start_active_audio_for_game)
                
                
                self.ui_active.init_mqtt_thread()
                
                # Ensure QML widget is properly initialized for new game
                if hasattr(self.ui_active, 'centralwidget') and hasattr(self.ui_active, 'init_qml_widget'):
                    try:
                        if self.ui_active.init_qml_widget(self.ui_active.centralwidget):
                            logger.info(" QML widget re-initialized for new game")
                            self.ui_active.qml_widget.show()
                        else:
                            logger.warning("️  Failed to re-initialize QML widget")
                    except Exception as e:
                        logger.error(f" Error re-initializing QML widget: {e}")
                
                # Connect deactivate signal to trigger score submission
                if (hasattr(self.ui_active, 'mqtt_thread') and self.ui_active.mqtt_thread and 
                    hasattr(self.ui_active.mqtt_thread, 'deactivate_signal')):
                    try:
                        self.ui_active.mqtt_thread.deactivate_signal.connect(
                            self.game_manager.trigger_score_submission
                        )
                        logger.debug(" Deactivate signal connected to GameManager")
                    except Exception as e:
                        logger.warning(f"️  Error connecting deactivate signal: {e}")
                else:
                    logger.warning("️  MQTT thread or deactivate signal not properly initialized")
                # Ensure serial thread is properly set up
                if hasattr(self, 'serial_thread') and self.serial_thread:
                    try:
                        # Update the serial thread reference in ui_active
                        self.ui_active.serial_thread = self.serial_thread
                        
                        # Ensure serial thread is ready (but don't start monitoring yet - that happens in start_game)
                        if hasattr(self.serial_thread, 'connect') and not self.serial_thread.connected:
                            self.serial_thread.connect()
                            logger.debug(" Serial connection established")
                        else:
                            logger.debug(" Serial thread ready")
                        
                        # Ensure signals are connected (disconnect first to avoid duplicates, then reconnect)
                        try:
                            # Safely disconnect existing serial connections
                            self.serial_thread.data_received.disconnect(self.ui_active.on_serial_data_received)
                        except:
                            pass  # Ignore if not connected
                        
                        # try:
                        #     self.serial_thread.connection_status_changed.disconnect(self.ui_active.on_serial_connection_status_changed)
                        # except:
                        #     pass  # Ignore if not connected
                        
                        # try:
                        #     self.serial_thread.error_occurred.disconnect(self.ui_active.on_serial_error)
                        # except:
                        #     pass  # Ignore if not connected
                        
                        # Reconnect serial signals
                        self.serial_thread.data_received.connect(self.ui_active.on_serial_data_received)
                        # self.serial_thread.connection_status_changed.connect(self.ui_active.on_serial_connection_status_changed)
                        # self.serial_thread.error_occurred.connect(self.ui_active.on_serial_error)
                        logger.debug(" Serial and audio signals ensured connected")
                        
                        logger.debug(" Serial thread properly configured for Active_screen")
                    except Exception as e:
                        logger.warning(f"️  Error configuring serial thread: {e}")
                else:
                    logger.info("ℹ️  Serial thread not available (disabled in config or failed to initialize)")
                
                
                # Setup and show the active screen
                # self.mainWindow.show()
                logger.debug(" Active screen started successfully")
            except Exception as e:
                logger.error(f" Error setting up active screen: {e}")
                return
        else:
            logger.error(" ui_active not properly initialized")
            return

        if hasattr(self, 'ui_home') and self.ui_home:
            try:
                self.ui_home.close()
            except Exception as e:
                logger.warning(f"️  Error closing home screen: {e}")
        
        quit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('q'), self.mainWindow)
        quit_shortcut.activated.connect(self.close_application)

    def start_final_screen(self):
        """Start Final Screen with comprehensive error handling (improved from game2)"""
        logger.info(" Starting Final Screen")
        
        # Set background image immediately to prevent white screen flashes
        self._set_background_image("Assets/imgSeq_0.jpg")
        QApplication.processEvents()  # Force immediate UI update
        try:
            # Close any current screens safely
            self._close_current_screen()
            
            # Stop all audio first, then start inactive after delay
            self._stop_all_audio()
            QTimer.singleShot(100, self._start_inactive_audio_for_final)
            # Setup and show final screen
            self.ui_final.setupUi(self.mainWindow)
            self.mainWindow.show()
            logger.debug(" Final screen started successfully")
            
            # Read timer value from file with fallback
            try:
                with open("file.txt", "r") as file:
                    lines = file.readlines()
                    if lines:
                        final_screen_timer_idle = int(lines[-1].strip())
                    else:
                        final_screen_timer_idle = game_config.final_screen_timer
            except FileNotFoundError:
                logger.info("file.txt not found. Using default timer value.")
                final_screen_timer_idle = game_config.final_screen_timer
            except (ValueError, IndexError) as e:
                logger.warning(f"️  Error reading timer value: {e}. Using default.")
                final_screen_timer_idle = game_config.final_screen_timer
            
            # Override with default for consistency
            final_screen_timer_idle = 15000
            
            # Set up automatic transition back to home screen after final_screen_timer_idle (improved from game2)
            logger.info(f"⏰ Setting final screen auto-transition timer: {final_screen_timer_idle}ms")
            QtCore.QTimer.singleShot(final_screen_timer_idle, lambda: (
                self.ui_final.close() if hasattr(self, 'ui_final') and self.ui_final is not None and self.ui_final.isVisible() else None,
                self.start_Home_screen() if hasattr(self, 'ui_final') and self.ui_final is not None and not self.ui_final.isVisible() else None
            ))
            
        except Exception as e:
            logger.error(f" Error starting final screen: {e}")

        quit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('q'), self.mainWindow)
        quit_shortcut.activated.connect(self.close_application)

    def _close_current_screen(self):
        """Safely close any currently active screen (improved from game2)"""
        try:
            # Clear central widget content
            central_widget = self.mainWindow.centralWidget()
            if central_widget:
                # Get all child widgets
                for child in central_widget.findChildren(QtWidgets.QWidget):
                    try:
                        child.hide()
                        child.deleteLater()
                    except RuntimeError:
                        # Widget already deleted
                        pass
                
                # Clear the central widget
                central_widget.deleteLater()
                self.mainWindow.setCentralWidget(None)
                
            logger.debug(" Current screen closed successfully")
        except Exception as e:
            logger.warning(f"️  Error closing current screen: {e}")

    def close_application(self):
        """Comprehensive application cleanup and shutdown"""
        logger.info(" Closing application with comprehensive cleanup...")
        
        try:
            # Stop GameManager thread first
            if hasattr(self, 'game_manager') and self.game_manager:
                try:
                    self.game_manager.stop_manager()
                    logger.debug(" GameManager stopped")
                except Exception as e:
                    logger.warning(f"️  Error stopping GameManager: {e}")
            
            # Stop Serial thread
            if hasattr(self, 'serial_thread') and self.serial_thread:
                try:
                    self.serial_thread.stop()
                    self.serial_thread = None
                    logger.debug(" Serial thread stopped")
                except Exception as e:
                    logger.warning(f"️  Error stopping Serial thread: {e}")
            
            # Clean up all UI screens
            self._cleanup_all_screens()
            
            # Close main window
            if hasattr(self, 'mainWindow') and self.mainWindow:
                try:
                    self.mainWindow.close()
                    logger.debug(" Main window closed")
                except Exception as e:
                    logger.warning(f"️  Error closing main window: {e}")
            
        except Exception as e:
            logger.error(f" Error during application cleanup: {e}")
        
        # Quit the application
        QtWidgets.QApplication.quit()
        logger.info(" Application shutdown complete")
    
    def closeEvent(self, event):
        """Handle application close event with comprehensive cleanup"""
        logger.info(" MainApp closeEvent triggered...")
        
        try:
            # Perform the same cleanup as close_application
            if hasattr(self, 'game_manager') and self.game_manager:
                self.game_manager.stop_manager()
            
            # Stop Serial thread
            if hasattr(self, 'serial_thread') and self.serial_thread:
                try:
                    self.serial_thread.stop()
                    self.serial_thread = None
                    logger.debug(" Serial thread stopped in closeEvent")
                except Exception as e:
                    logger.warning(f"️  Error stopping Serial thread in closeEvent: {e}")
            
            self._cleanup_all_screens()
            
        except Exception as e:
            logger.error(f" Error in MainApp closeEvent: {e}")
        
        event.accept()
        logger.info(" MainApp closeEvent completed")
        super().closeEvent(event)
    
    def _cleanup_all_screens(self):
        """Enhanced cleanup for all screen instances with comprehensive resource management"""
        logger.info("Cleaning up all screens with enhanced resource management...")
        
        # 1. Stop all audio first to prevent overlapping sounds
        self._stop_all_audio()
        
        # 2. Clean up all screen instances with proper resource management
        self._cleanup_all_screen_instances()
        
        # 3. Force stop all timers across all screens
        self._force_stop_all_timers()
        
        # 4. Clean up background resources (final cleanup)
        self._cleanup_background_resources_final()
        
        logger.info("All screens cleaned up successfully with comprehensive resource management")
    
    def _cleanup_all_screen_instances(self):
        """Clean up all screen instances with enhanced resource management"""
        screen_attrs = ['ui_active', 'ui_final', 'ui_home', 'ui_team_member']
        
        for screen_attr in screen_attrs:
            if hasattr(self, screen_attr):
                screen = getattr(self, screen_attr)
                if screen:
                    try:
                        # Close the screen (this will trigger the enhanced closeEvent methods)
                        screen.close()
                        logger.debug(f"{screen_attr} closed successfully")
                    except Exception as e:
                        logger.warning(f"Error closing {screen_attr}: {e}")
                        # Force cleanup if close() fails
                        try:
                            if hasattr(screen, '_final_cleanup'):
                                screen._final_cleanup()
                        except Exception as cleanup_error:
                            logger.warning(f"Error in final cleanup for {screen_attr}: {cleanup_error}")
                    
                    # Clear the reference
                    setattr(self, screen_attr, None)
    
    def _force_stop_all_timers(self):
        """Force stop all timers across all screens for safe shutdown"""
        logger.info(" Force stopping all application timers")
        
        # Stop timers in all screen instances
        screen_attrs = ['ui_home', 'ui_active', 'ui_final', 'ui_team_member']
        for screen_attr in screen_attrs:
            if hasattr(self, screen_attr):
                screen = getattr(self, screen_attr)
                if screen:
                    # Check for common timer names and stop them
                    timer_names = ['timer', 'timer2', 'timer3', 'TimerGame', 'traverse_Timer']
                    for timer_name in timer_names:
                        if hasattr(screen, timer_name):
                            timer_obj = getattr(screen, timer_name)
                            if timer_obj:
                                try:
                                    if hasattr(timer_obj, 'stop'):
                                        timer_obj.stop()
                                        logger.debug(f" {screen_attr}.{timer_name} stopped")
                                except (RuntimeError, AttributeError):
                                    logger.debug(f"️  {screen_attr}.{timer_name} already deleted or invalid")
                                except Exception as e:
                                    logger.warning(f"️  Error stopping {screen_attr}.{timer_name}: {e}")
        
        logger.info(" All application timers forcibly stopped")


if __name__ == "__main__":
    # Initialize logging
    from utils.logger import setup_root_logger
    setup_root_logger("INFO")
    
    logger.info("" + "=" * 60)
    logger.info(" STARTING CAGE GAME WITH COMPLETE UI AND NEW API")
    logger.info("" + "=" * 60)
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Initialize leaderboard
    try:
        api = GameAPI()
        if api.authenticate():
            logger.info(" API authentication successful")
            # TODO: Uncomment when leaderboard is needed
            leaderboard , lastplayed = api.get_leaderboard()
            if lastplayed is not None:
                lastplayed_score = lastplayed.get('total_score', 0)
                lastplayed_weighted_points = lastplayed.get('weighted_points', 0)
                lastplayed_rank = lastplayed.get('rank', 0)
            list_top5_FastReaction.extend(leaderboard)
            # print(list_top5_FastReaction)
            logger.info(f" Initial leaderboard loaded: {len(leaderboard)} entries")
        else:
            logger.warning("️  Failed to authenticate for initial leaderboard")
    except Exception as e:
        logger.error(f" Error loading initial leaderboard: {e}")
    
    # Start main application
    try:
        main_app = MainApp()
        logger.info(" Application started successfully!")
        
        # Log serial configuration status
        serial_config = config.settings.serial
        if serial_config.enabled:
            logger.info(f" Serial communication enabled: {serial_config.port}")
        else:
            logger.info(" Serial communication disabled (MQTT only mode)")
            logger.info(" To enable serial: Set FAST_REACTION_SERIAL_ENABLED=true and FAST_REACTION_SERIAL_PORT=/dev/ttyUSB0")
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f" Application failed to start: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
