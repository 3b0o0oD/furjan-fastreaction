# Fast Reaction Game Service

This directory contains the systemd service file for running the Fast Reaction Game application as a Linux service.

## Service File

**fastreaction.service** - Service for `Fast_Reaction_QML_sound.py`

## Prerequisites

- Ensure Python 3 is installed on the target system
- Install required Python packages:
  ```bash
  pip3 install PyQt5 numpy requests paho-mqtt pyserial
  ```
- Ensure the following system packages are installed:
  ```bash
  sudo apt update
  sudo apt install python3-pyqt5 python3-pyqt5.qtquick python3-pyqt5.qtmultimedia
  sudo apt install qt5-qmltooling-plugins qml-module-qtquick-controls2
  sudo apt install pulseaudio alsa-utils python3-serial
  ```
- Update the paths in the service file if they differ on your target system
- Ensure X11 display is available for GUI application
- For serial communication, ensure proper permissions for serial devices

## Installation Instructions

### 1. Copy service file to systemd directory:
```bash
sudo cp fastreaction.service /etc/systemd/system/
```

### 2. Reload systemd to recognize new service:
```bash
sudo systemctl daemon-reload
```

### 3. Enable service to start on boot (optional):
```bash
sudo systemctl enable fastreaction.service
```

## Service Management

### Start service:
```bash
sudo systemctl start fastreaction.service
```

### Stop service:
```bash
sudo systemctl stop fastreaction.service
```

### Restart service:
```bash
sudo systemctl restart fastreaction.service
```

### Check service status:
```bash
sudo systemctl status fastreaction.service
```

### View service logs:
```bash
# View recent logs
sudo journalctl -u fastreaction.service -n 50

# Follow logs in real-time
sudo journalctl -u fastreaction.service -f

# View logs from specific time
sudo journalctl -u fastreaction.service --since "1 hour ago"
```

### Disable service (stop auto-start on boot):
```bash
sudo systemctl disable fastreaction.service
```

## Configuration Details

- **User/Group**: Service runs as user `mostafa`. Update this in the service file if needed.
- **Working Directory**: Service uses the `/home/mostafa/UXE/games_UXE_2025/game3` directory.
- **Python Path**: Service uses `/usr/bin/python3`. Update if Python is installed elsewhere.
- **Display**: Service includes GUI environment variables for X11 display (`DISPLAY=:0`).
- **QML**: Service includes Qt5 QML environment variables for proper QML widget functionality.
- **Audio**: Service includes PulseAudio environment variables for sound support.
- **Serial**: Service includes default serial port configuration (`FAST_REACTION_SERIAL_PORT=/dev/pts/12`).

## Environment Variables

The service includes these environment variables for proper operation:

- `DISPLAY=:0` - X11 display for GUI
- `XDG_RUNTIME_DIR=/run/user/1000` - Runtime directory for user session
- `PULSE_RUNTIME_PATH=/run/user/1000/pulse` - PulseAudio runtime path
- `QT_QPA_PLATFORM=xcb` - Qt platform abstraction for X11
- `QML_IMPORT_PATH=/usr/lib/x86_64-linux-gnu/qt5/qml` - QML module path
- `XAUTHORITY=/home/mostafa/.Xauthority` - X authorization file
- `FAST_REACTION_SERIAL_PORT=/dev/pts/12` - Default serial port for communication

## Serial Communication Setup

The Fast Reaction game supports serial communication for external device integration:

### Default Configuration:
- **Port**: `/dev/pts/12` (can be overridden with environment variable)
- **Baudrate**: 9600
- **Communication Flow**: 
  1. Game sends "Start" → Device responds "OK"
  2. Game sends "Stop" → Device responds "OK"
  3. Game receives scores and events from device

### Using Custom Serial Port:
```bash
# Method 1: Environment variable
sudo systemctl edit fastreaction.service
# Add: Environment=FAST_REACTION_SERIAL_PORT=/dev/ttyUSB0

# Method 2: Update service file directly
sudo nano /etc/systemd/system/fastreaction.service
# Modify: Environment=FAST_REACTION_SERIAL_PORT=/your/custom/port

# Method 3: Runtime override
sudo systemctl set-environment FAST_REACTION_SERIAL_PORT=/dev/ttyUSB0
sudo systemctl restart fastreaction.service
```

### Serial Device Permissions:
```bash
# Add user to dialout group for serial access
sudo usermod -a -G dialout mostafa

# Set permissions for specific device
sudo chmod 666 /dev/ttyUSB0

# For persistent permissions, create udev rule:
sudo nano /etc/udev/rules.d/99-serial-permissions.rules
# Add: SUBSYSTEM=="tty", ATTRS{idVendor}=="YOUR_VENDOR_ID", MODE="0666"
```

## Key Commands Reference

### Start Services:
```bash
sudo systemctl start fastreaction.service
```

### Enable at Boot:
```bash
sudo systemctl enable fastreaction.service
```

### Restart Services:
```bash
sudo systemctl restart fastreaction.service
```

### Check Status:
```bash
sudo systemctl status fastreaction.service
```

### View Logs:
```bash
sudo journalctl -u fastreaction.service -f
```

## Troubleshooting

### Common Issues:

1. **Service fails to start:**
   ```bash
   # Check detailed logs
   sudo journalctl -u fastreaction.service -xe
   ```

2. **Python import errors:**
   ```bash
   # Install missing packages
   pip3 install [missing-package]
   
   # Or use system packages
   sudo apt install python3-[package-name]
   ```

3. **Display/GUI issues:**
   ```bash
   # Check X11 access
   echo $DISPLAY
   xhost +local:
   
   # Check X authority
   ls -la ~/.Xauthority
   
   # For remote systems, enable X11 forwarding
   ssh -X user@hostname
   ```

4. **Audio issues:**
   ```bash
   # Check PulseAudio
   pulseaudio --check
   pactl info
   
   # Restart PulseAudio if needed
   pulseaudio -k
   pulseaudio --start
   ```

5. **QML issues:**
   ```bash
   # Check QML modules
   qmlscene --list-modules
   
   # Install missing QML modules
   sudo apt install qml-module-qtquick-controls2
   sudo apt install qml-module-qtmultimedia
   ```

6. **Serial communication issues:**
   ```bash
   # Check serial device
   ls -la /dev/tty* | grep -E "(USB|ACM|pts)"
   
   # Test serial device
   sudo minicom -D /dev/ttyUSB0
   
   # Check permissions
   groups $USER | grep dialout
   
   # Monitor serial activity
   sudo journalctl -u fastreaction.service | grep -i serial
   ```

7. **Permission issues:**
   - Ensure the user `mostafa` exists and has proper permissions
   - Check file permissions in the game directory
   - Verify group membership:
     ```bash
     sudo usermod -a -G audio,video,dialout mostafa
     ```

### Debug Mode:

To run the game manually for debugging:
```bash
cd /home/mostafa/UXE/games_UXE_2025/game3
python3 Fast_Reaction_QML_sound.py
```

To test with custom serial port:
```bash
cd /home/mostafa/UXE/games_UXE_2025/game3
FAST_REACTION_SERIAL_PORT=/dev/ttyUSB0 python3 Fast_Reaction_QML_sound.py
```

### Serial Test Controller:

The game includes a serial test controller for development:
```bash
cd /home/mostafa/UXE/games_UXE_2025/game3
python3 serial_test_controller.py
```

### Update Service:

When updating the game code:
1. Stop the service: `sudo systemctl stop fastreaction.service`
2. Update your code
3. Restart the service: `sudo systemctl start fastreaction.service`

### Logs Location:

Service logs are stored in the systemd journal. Use `journalctl` commands above to view them, or check:
- `/var/log/syslog` - General system logs
- Application logs may be written to the game's `logs/` directory if configured

## Security Notes

The service includes basic security settings:
- `NoNewPrivileges=true` - Prevents privilege escalation
- `PrivateTmp=true` - Provides private /tmp directory
- User-level permissions for serial and audio devices

For production deployments, consider additional security measures based on your environment requirements.

## Game Features

The Fast Reaction game includes:
- **QML-based UI**: Modern Qt Quick interface
- **Sound Support**: Audio feedback and music
- **Serial Communication**: External device integration
- **Reaction Time Measurement**: Precise timing metrics
- **Score Tracking**: Performance monitoring
- **Multiple Game Modes**: Various difficulty levels

## Quick Setup Commands

```bash
# Full installation sequence
sudo cp fastreaction.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fastreaction.service
sudo systemctl start fastreaction.service
sudo systemctl status fastreaction.service

# With serial device setup
sudo usermod -a -G dialout mostafa
sudo systemctl restart fastreaction.service
```
