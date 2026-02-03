"""
Configuration Management for Fast Reaction Game
Handles all configuration settings for the game application

Serial Configuration Usage:
===========================
To enable serial communication, set environment variables:

Linux/macOS:
    export FAST_REACTION_SERIAL_ENABLED=true
    export FAST_REACTION_SERIAL_PORT=/dev/ttyUSB0

Windows:
    set FAST_REACTION_SERIAL_ENABLED=true
    set FAST_REACTION_SERIAL_PORT=COM3

Or modify the SerialConfig class defaults directly.

Serial Data Format:
==================
The game expects simple text commands:
- Numeric values: "5" (adds 5 to score)
- "hit" or "point": adds 1 to score
- "win": triggers game end
- Custom commands can be added in on_serial_data_received()
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class APIConfig:
    """API configuration settings"""
    # base_url: str = "https://dev-eaa25-api-hpfyfcbshkabezeh.uaenorth-01.azurewebsites.net/"
    # email: str = "eaa25admin@gmail.com"
    # password: str = "qhv#1kGI$"
    # game_id: str = "73a92ae9-995d-4eed-a60d-217b7ce54643" 
    game_name: str = "Fast Reaction"
    
    # Production API
    base_url: str = "https://dev-ferjan-api.azurewebsites.net/"
    email: str = "eaa25admin@gmail.com"
    password: str = "qhv#1kGI$" 
    game_id: str = "73a92ae9-995d-4eed-a60d-217b7ce54643"  
    
    
        
    # Timeout settings (in seconds)
    auth_timeout: int = 30
    game_status_timeout: int = 8
    submit_score_timeout: int = 20
    leaderboard_timeout: int = 12


@dataclass
class GameConfig:
    """Game configuration settings"""
    timer_value: int = 180300  # Default timer value in milliseconds
    final_screen_timer: int = 15000  # Final screen display time
    

    time_bonus_multiplier: int = 10


@dataclass
class UIConfig:
    """UI configuration settings"""
    scale_factor: int = 1  # Will be set based on screen resolution
    fonts_path: str = "Assets/Fonts/"
    assets_path: str = "Assets/"
    audio_path: str = "Assets/mp3/"


@dataclass
class SerialConfig:
    """Serial communication configuration settings"""
    enabled: bool = False  # Enable/disable serial communication
    # port: str = "/dev/pts/11"  # Default serial port (Linux)
    port: str = "/dev/ttyUSB0"
    baudrate: int = 115200  # Communication speed
    timeout: int = 1  # Read timeout in seconds
    auto_reconnect: bool = True  # Enable automatic reconnection
    reconnect_interval: int = 5  # Seconds between reconnection attempts
    max_reconnect_attempts: int = 10  # Maximum reconnection attempts (-1 for infinite)


@dataclass
class MQTTConfig:
    """MQTT configuration settings"""
    broker: str = "localhost"
    port: int = 1883
    data_topics: list = None
    control_topics: list = None
    
    def __post_init__(self):
        if self.data_topics is None:
            self.data_topics = [
                "FastReaction/score/Pub",
            ]
        
        if self.control_topics is None:
            self.control_topics = [
                "FastReaction/game/start",
                "FastReaction/game/stop", 
                "FastReaction/game/restart",
                "FastReaction/game/timer",
                "FastReaction/game/Activate",
                "FastReaction/game/Deactivate",
                "FastReaction/game/timerfinal"
            ]


@dataclass
class Settings:
    """Main settings container"""
    api: APIConfig
    game: GameConfig
    ui: UIConfig
    serial: SerialConfig
    mqtt: MQTTConfig
    
    @classmethod
    def load(cls, config_file: Optional[str] = None) -> 'Settings':
        """Load settings from environment variables or config file"""
        
        # Load API settings from environment or defaults
        api_config = APIConfig(
            base_url=os.getenv('FAST_REACTION_API_BASE_URL', APIConfig.base_url),
            email=os.getenv('FAST_REACTION_API_EMAIL', APIConfig.email),
            password=os.getenv('FAST_REACTION_API_PASSWORD', APIConfig.password),
            game_id=os.getenv('FAST_REACTION_GAME_ID', APIConfig.game_id),
            game_name=os.getenv('FAST_REACTION_GAME_NAME', APIConfig.game_name),
        )
        
        # Load game settings
        game_config = GameConfig(
            timer_value=int(os.getenv('FAST_REACTION_TIMER_VALUE', GameConfig.timer_value)),
            final_screen_timer=int(os.getenv('FAST_REACTION_FINAL_TIMER', GameConfig.final_screen_timer)),
        )
        
        # Load UI settings
        ui_config = UIConfig(
            fonts_path=os.getenv('FAST_REACTION_FONTS_PATH', UIConfig.fonts_path),
            assets_path=os.getenv('FAST_REACTION_ASSETS_PATH', UIConfig.assets_path),
            audio_path=os.getenv('FAST_REACTION_AUDIO_PATH', UIConfig.audio_path),
        )
        
        # Load Serial settings
        serial_config = SerialConfig(
            enabled=os.getenv('FAST_REACTION_SERIAL_ENABLED', 'true').lower() == 'true',
            port=os.getenv('FAST_REACTION_SERIAL_PORT', SerialConfig.port),
            baudrate=int(os.getenv('FAST_REACTION_SERIAL_BAUDRATE', SerialConfig.baudrate)),
            timeout=int(os.getenv('FAST_REACTION_SERIAL_TIMEOUT', SerialConfig.timeout)),
            auto_reconnect=os.getenv('FAST_REACTION_SERIAL_AUTO_RECONNECT', 'true').lower() == 'true',
            reconnect_interval=int(os.getenv('FAST_REACTION_SERIAL_RECONNECT_INTERVAL', SerialConfig.reconnect_interval)),
            max_reconnect_attempts=int(os.getenv('FAST_REACTION_SERIAL_MAX_RECONNECT_ATTEMPTS', SerialConfig.max_reconnect_attempts)),
        )

        # Load MQTT settings
        mqtt_config = MQTTConfig(
            broker=os.getenv('FAST_REACTION_MQTT_BROKER', MQTTConfig.broker),
            port=int(os.getenv('FAST_REACTION_MQTT_PORT', MQTTConfig.port)),
        )

        return cls(
            api=api_config,
            game=game_config,
            ui=ui_config,
            serial=serial_config,
            mqtt=mqtt_config
        )


# Global settings instance
settings = Settings.load()


# Backwards compatibility
class Config:
    """Legacy config class for backwards compatibility"""
    
    @property
    def settings(self):
        return settings


config = Config()