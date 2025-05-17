"""
Process G-code command responses
"""
import re
from .responses import (
    get_printer_info_response,
    get_temperature_response,
    get_endstop_response,
    get_print_status_response,
    get_position_response,
    get_file_list_response,
    get_thumbnail_response
)

def process_command(command, config, thumbnail_path, virtual_files, logger=None):
    """Process a command and return the appropriate response"""
    # Handle login/logout
    if command == "~M601 S1":  # Login
        return "CMD M601 Received.\nControl Success v2.1.\nok\n"
    
    if command == "~M602":  # Logout
        return "CMD M602 Received.\nControl Release.\nok\n"
    
    # Status commands
    if command == "~M115":  # Info Status
        return get_printer_info_response(config)
    
    if command == "~M105":  # Temperature
        return get_temperature_response(config)
    
    if command == "~M119":  # Endstop status
        return get_endstop_response(config)
    
    if command == "~M27":  # Print status
        return get_print_status_response(config)
    
    if command == "~M114":  # Position
        return get_position_response(config)
    
    # LED control
    if command.startswith("~M146"):  # LED control
        led_state_changed = False
        if "r255 g255 b255" in command.lower():
            if not config['led_state']:
                config['led_state'] = True
                led_state_changed = True
                if logger:
                    logger("LED turned ON")
        elif "r0 g0 b0" in command.lower():
            if config['led_state']:
                config['led_state'] = False
                led_state_changed = True
                if logger:
                    logger("LED turned OFF")
                    
        return "CMD M146 Received.\nok\n"
    
    # Filament runout sensor
    if command == "~M405":  # Runout sensor on
        old_state = config['filament_runout_sensor']
        config['filament_runout_sensor'] = True
        if not old_state and logger:
            logger("Filament sensor enabled")
        return "CMD M405 Received.\nok\n"
    
    if command == "~M406":  # Runout sensor off
        old_state = config['filament_runout_sensor']
        config['filament_runout_sensor'] = False
        if old_state and logger:
            logger("Filament sensor disabled")
        return "CMD M406 Received.\nok\n"
    
    # Home axes
    if command == "~G28":  # Home axes
        # Reset position
        config['position'] = {"x": 0.0, "y": 0.0, "z": 0.0}
        return "CMD G28 Received.\nok\n"
    
    # Print control
    if command == "~M24":  # Resume print
        if config['print_status'] == 'paused':
            config['print_status'] = 'printing'
            if logger:
                logger("Print resumed")
        return "CMD M24 Received.\nok\n"
    
    if command == "~M25":  # Pause print
        if config['print_status'] == 'printing':
            config['print_status'] = 'paused'
            if logger:
                logger("Print paused")
        return "CMD M25 Received.\nok\n"
    
    if command == "~M26":  # Stop print
        if config['print_status'] in ['printing', 'paused']:
            config['print_status'] = 'idle'
            config['print_progress'] = 0
            if logger:
                logger("Print stopped")
        return "CMD M26 Received.\nok\n"
    
    # Temperature settings
    if command.startswith("~M104"):  # Set extruder temp
        parts = command.split()
        if len(parts) > 1 and parts[1].startswith("S"):
            try:
                temp = float(parts[1][1:])
                config['target_hotend'] = temp
                if logger:
                    logger(f"Hotend target temperature set to {temp}°C")
            except ValueError:
                pass
        return "CMD M104 Received.\nok\n"
    
    if command.startswith("~M140"):  # Set bed temp
        parts = command.split()
        if len(parts) > 1 and parts[1].startswith("S"):
            try:
                temp = float(parts[1][1:])
                config['target_bed'] = temp
                if logger:
                    logger(f"Bed target temperature set to {temp}°C")
            except ValueError:
                pass
        return "CMD M140 Received.\nok\n"
    
    if command.startswith("~M109"):  # Wait for extruder temp
        parts = command.split()
        if len(parts) > 1 and parts[1].startswith("S"):
            try:
                temp = float(parts[1][1:])
                config['target_hotend'] = temp
                config['hotend_temp'] = temp  # Immediately set temp for testing
                if logger:
                    logger(f"Hotend temperature set to {temp}°C (wait)")
            except ValueError:
                pass
        return "CMD M109 Received.\nok\n"
    
    if command.startswith("~M190"):  # Wait for bed temp
        parts = command.split()
        if len(parts) > 1 and parts[1].startswith("S"):
            try:
                temp = float(parts[1][1:])
                config['target_bed'] = temp
                config['bed_temp'] = temp  # Immediately set temp for testing
                if logger:
                    logger(f"Bed temperature set to {temp}°C (wait)")
            except ValueError:
                pass
        return "CMD M190 Received.\nok\n"
    
    # File listing
    if command == "~M661":  # List files
        return get_file_list_response(virtual_files, logger)
    
    # Thumbnail
    if command.startswith("~M662"):
        # Extract the filename from the command if present
        file_path = ""
        if len(command) > 5:
            # Get everything after ~M662 (excluding the space)
            file_path = command[6:].strip()
        
        if logger:
            logger(f"Processing thumbnail request for: {file_path}")
        return get_thumbnail_response(thumbnail_path, file_path, virtual_files, logger)
    
    # Movement
    if command.startswith("~G1"):  # Move
        # Parse X, Y, Z coordinates if present
        position = config['position'].copy()
        for axis in ['X', 'Y', 'Z']:
            match = re.search(f"{axis}([-+]?[0-9]*\.?[0-9]+)", command)
            if match:
                position[axis.lower()] = float(match.group(1))
        config['position'] = position
        return "CMD G1 Received.\nok\n"
    
    # Default response for unhandled commands
    return f"CMD {command[1:]} Received.\nok\n"
