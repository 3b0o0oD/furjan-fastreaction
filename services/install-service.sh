#!/bin/bash

# Fast Reaction Game Service Installation Script
# This script installs and manages the Fast Reaction Game systemd service

SERVICE_NAME="fastreaction"
SERVICE_FILE="${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root directly."
        print_status "Use: sudo $0 [command]"
        exit 1
    fi
}

install_service() {
    print_status "Installing Fast Reaction Game service..."
    
    # Check if service file exists
    if [[ ! -f "$CURRENT_DIR/$SERVICE_FILE" ]]; then
        print_error "Service file $SERVICE_FILE not found in $CURRENT_DIR"
        exit 1
    fi
    
    # Copy service file
    print_status "Copying service file to $SYSTEMD_DIR..."
    sudo cp "$CURRENT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/"
    
    if [[ $? -ne 0 ]]; then
        print_error "Failed to copy service file"
        exit 1
    fi
    
    # Reload systemd
    print_status "Reloading systemd daemon..."
    sudo systemctl daemon-reload
    
    # Set appropriate permissions
    sudo chmod 644 "$SYSTEMD_DIR/$SERVICE_FILE"
    
    print_success "Service installed successfully!"
    print_status "You can now use: sudo systemctl start $SERVICE_NAME"
}

enable_service() {
    print_status "Enabling $SERVICE_NAME service to start on boot..."
    sudo systemctl enable "$SERVICE_NAME"
    
    if [[ $? -eq 0 ]]; then
        print_success "Service enabled successfully!"
    else
        print_error "Failed to enable service"
        exit 1
    fi
}

disable_service() {
    print_status "Disabling $SERVICE_NAME service from starting on boot..."
    sudo systemctl disable "$SERVICE_NAME"
    
    if [[ $? -eq 0 ]]; then
        print_success "Service disabled successfully!"
    else
        print_error "Failed to disable service"
        exit 1
    fi
}

start_service() {
    print_status "Starting $SERVICE_NAME service..."
    sudo systemctl start "$SERVICE_NAME"
    
    if [[ $? -eq 0 ]]; then
        print_success "Service started successfully!"
        sleep 2
        service_status
    else
        print_error "Failed to start service"
        print_status "Check logs with: sudo journalctl -u $SERVICE_NAME -xe"
        exit 1
    fi
}

stop_service() {
    print_status "Stopping $SERVICE_NAME service..."
    sudo systemctl stop "$SERVICE_NAME"
    
    if [[ $? -eq 0 ]]; then
        print_success "Service stopped successfully!"
    else
        print_error "Failed to stop service"
        exit 1
    fi
}

restart_service() {
    print_status "Restarting $SERVICE_NAME service..."
    sudo systemctl restart "$SERVICE_NAME"
    
    if [[ $? -eq 0 ]]; then
        print_success "Service restarted successfully!"
        sleep 2
        service_status
    else
        print_error "Failed to restart service"
        print_status "Check logs with: sudo journalctl -u $SERVICE_NAME -xe"
        exit 1
    fi
}

service_status() {
    print_status "Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager
}

service_logs() {
    print_status "Recent service logs:"
    sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
}

follow_logs() {
    print_status "Following service logs (Ctrl+C to stop):"
    sudo journalctl -u "$SERVICE_NAME" -f
}

uninstall_service() {
    print_status "Uninstalling $SERVICE_NAME service..."
    
    # Stop service if running
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null
    
    # Disable service
    sudo systemctl disable "$SERVICE_NAME" 2>/dev/null
    
    # Remove service file
    sudo rm -f "$SYSTEMD_DIR/$SERVICE_FILE"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    print_success "Service uninstalled successfully!"
}

check_dependencies() {
    print_status "Checking system dependencies..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        return 1
    else
        print_success "Python 3 found: $(python3 --version)"
    fi
    
    # Check PyQt5
    if ! python3 -c "import PyQt5" 2>/dev/null; then
        print_warning "PyQt5 not found. Install with: pip3 install PyQt5"
    else
        print_success "PyQt5 found"
    fi
    
    # Check PySerial
    if ! python3 -c "import serial" 2>/dev/null; then
        print_warning "PySerial not found. Install with: pip3 install pyserial"
    else
        print_success "PySerial found"
    fi
    
    # Check QML modules
    if command -v qmlscene &> /dev/null; then
        print_success "QML tools found"
    else
        print_warning "QML tools not found. Install with: sudo apt install qt5-qmltooling-plugins"
    fi
    
    # Check serial devices
    serial_devices=$(ls /dev/tty{USB,ACM,S}* 2>/dev/null | head -5)
    if [[ -n "$serial_devices" ]]; then
        print_success "Serial devices found:"
        echo "$serial_devices" | while read device; do
            echo "  - $device"
        done
    else
        print_warning "No serial devices found. Connect your serial device or use PTY."
    fi
    
    # Check PTY devices
    pty_devices=$(ls /dev/pts/[0-9]* 2>/dev/null | head -5)
    if [[ -n "$pty_devices" ]]; then
        print_success "PTY devices available:"
        echo "$pty_devices" | while read device; do
            echo "  - $device"
        done
    fi
    
    # Check dialout group membership
    if groups $USER | grep -q dialout; then
        print_success "User $USER is in dialout group"
    else
        print_warning "User $USER not in dialout group. Add with: sudo usermod -a -G dialout $USER"
    fi
    
    # Check X11 display
    if [[ -n "$DISPLAY" ]]; then
        print_success "X11 Display found: $DISPLAY"
    else
        print_warning "No X11 display set. Set DISPLAY environment variable."
    fi
    
    # Check PulseAudio
    if command -v pulseaudio &> /dev/null; then
        print_success "PulseAudio found"
    else
        print_warning "PulseAudio not found. Install with: sudo apt install pulseaudio"
    fi
}

setup_serial_permissions() {
    print_status "Setting up serial device permissions..."
    
    # Add user to dialout group
    print_status "Adding user $USER to dialout group..."
    sudo usermod -a -G dialout $USER
    
    if [[ $? -eq 0 ]]; then
        print_success "User added to dialout group"
        print_warning "You may need to log out and back in for group changes to take effect"
    else
        print_error "Failed to add user to dialout group"
    fi
    
    # Set permissions for common serial devices
    for device in /dev/ttyUSB* /dev/ttyACM*; do
        if [[ -e "$device" ]]; then
            print_status "Setting permissions for $device..."
            sudo chmod 666 "$device"
            print_success "Permissions set for $device"
        fi
    done
}

test_serial_controller() {
    print_status "Starting serial test controller..."
    print_status "This will help you test serial communication with the game"
    
    cd "$(dirname "$CURRENT_DIR")"
    
    if [[ -f "serial_test_controller.py" ]]; then
        print_success "Found serial test controller"
        print_status "Starting controller in background..."
        python3 serial_test_controller.py &
        CONTROLLER_PID=$!
        print_success "Serial test controller started (PID: $CONTROLLER_PID)"
        print_status "Check the controller window for connection instructions"
    else
        print_error "Serial test controller not found at serial_test_controller.py"
    fi
}

set_serial_port() {
    if [[ -z "$1" ]]; then
        print_error "No serial port specified"
        print_status "Usage: $0 set-port /dev/ttyUSB0"
        return 1
    fi
    
    SERIAL_PORT="$1"
    print_status "Setting serial port to: $SERIAL_PORT"
    
    # Update environment in service file
    sudo systemctl edit --full "$SERVICE_NAME" 2>/dev/null || {
        print_error "Service not installed. Install first with: $0 install"
        return 1
    }
    
    print_success "Service editor opened. Add or modify the environment line:"
    print_status "Environment=FAST_REACTION_SERIAL_PORT=$SERIAL_PORT"
}

show_usage() {
    echo "Fast Reaction Game Service Management Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  install           Install the service"
    echo "  uninstall         Remove the service"
    echo "  enable            Enable service to start on boot"
    echo "  disable           Disable service from starting on boot"
    echo "  start             Start the service"
    echo "  stop              Stop the service"
    echo "  restart           Restart the service"
    echo "  status            Show service status"
    echo "  logs              Show recent logs"
    echo "  follow            Follow logs in real-time"
    echo "  check-deps        Check system dependencies"
    echo "  setup-serial      Setup serial device permissions"
    echo "  test-controller   Start serial test controller"
    echo "  set-port <port>   Set custom serial port"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install              # Install the service"
    echo "  $0 check-deps           # Check dependencies"
    echo "  $0 setup-serial         # Setup serial permissions"
    echo "  $0 set-port /dev/ttyUSB0 # Set serial port"
    echo "  $0 start                # Start the service"
    echo "  $0 enable               # Enable auto-start on boot"
    echo "  $0 status               # Check if service is running"
    echo "  $0 test-controller      # Test serial communication"
    echo "  $0 logs                 # View recent logs"
    echo ""
    echo "Quick Setup:"
    echo "  $0 install && $0 setup-serial && $0 enable && $0 start"
    echo ""
    echo "Serial Communication:"
    echo "  Default port: /dev/pts/12"
    echo "  Custom port: $0 set-port /dev/ttyUSB0"
    echo "  Test mode: $0 test-controller"
}

# Main script logic
check_root

case "${1:-help}" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        service_status
        ;;
    logs)
        service_logs
        ;;
    follow)
        follow_logs
        ;;
    check-deps)
        check_dependencies
        ;;
    setup-serial)
        setup_serial_permissions
        ;;
    test-controller)
        test_serial_controller
        ;;
    set-port)
        set_serial_port "$2"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
