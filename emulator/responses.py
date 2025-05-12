"""
Response generators for G-Code commands
"""
import binascii
import os

def get_printer_info_response(config):
    """Generate printer info response (M115)"""
    firmware = config['firmware_version']
    machine_type = config['machine_type']
    response = (
        f"CMD M115 Received.\n"
        f"Machine Type: {machine_type}\n"
        f"Machine Name: {config['printer_name']}\n"
        f"Firmware: {firmware}\n"
        f"SN: {config['serial_number']}\n"
        f"X: 200 Y: 200 Z: 200\n"
        f"Tool Count: 1\n"
        f"ok\n"
    )
    return response

def get_temperature_response(config):
    """Generate temperature response (M105)"""
    hotend_temp = config['hotend_temp']
    hotend_target = config['target_hotend']
    bed_temp = config['bed_temp']
    bed_target = config['target_bed']
    
    response = (
        f"CMD M105 Received.\n"
        f"T0:{hotend_temp:.1f}/{hotend_target:.1f} T1:0.0/0.0 B:{bed_temp:.1f}/{bed_target:.1f}\n"
        f"ok\n"
    )
    return response

def get_endstop_response(config):
    """Generate endstop status response (M119)"""
    
    # Set machine status based on print state
    machine_status = "READY"
    move_mode = "READY"
    status_map = {
        "printing": ("BUILDING_FROM_SD", "MOVING"),
        "paused": ("PAUSED", "PAUSED"),
        "completed": ("BUILDING_COMPLETED", "READY"),
        "failed": ("READY", "READY"), # todo this should be an actual error state
        "idle": ("READY", "READY")
    }
    
    if config['print_status'].lower() in status_map:
        machine_status, move_mode = status_map[config['print_status'].lower()]
    
    # Current file - only include if printing/paused/completed
    current_file = ""
    if config['print_status'].lower() in ["printing", "paused", "completed"]:
        current_file = config['current_file']
    
    response = (
        f"CMD M119 Received.\n"
        f"Endstop: X-min: 0 Y-min: 0 Z-min: 0\n"
        f"MachineStatus: {machine_status}\n"
        f"MoveMode: {move_mode}\n"
        f"Status: S:0 L:0 J:0 F:0\n"
        f"LED: {1 if config['led_state'] else 0}\n"
        f"CurrentFile: {current_file}\n"
        f"ok\n"
    )
    return response

def get_print_status_response(config):
    """Generate print status response (M27)"""
    status_code = {"idle": 0, "printing": 1, "paused": 2, "completed": 3, "failed": 4}
    status = status_code.get(config['print_status'].lower(), 0)
    progress = config['print_progress']
    
    # Calculate layer information based on progress
    # When progress is 0, make sure we report layer 0
    total_layers = 100
    if progress == 0:
        current_layer = 0
    else:
        current_layer = max(1, int(progress * total_layers / 100))
    
    response = (
        f"CMD M27 Received.\n"
        f"SD printing byte {progress}/100\n"
        f"Layer: {current_layer}/{total_layers}\n"
        f"Status: S:{status} L:0 J:0 F:0\n"
        f"ok\n"
    )
    return response

def get_position_response(config):
    """Generate position response (M114)"""
    x = config['position']['x']
    y = config['position']['y']
    z = config['position']['z']
    
    response = (
        f"CMD M114 Received.\n"
        f"X:{x} Y:{y} Z:{z} A:0 B:0\n"
        f"ok\n"
    )
    return response

def get_file_list_response(virtual_files, logger=None):
    """Generate file list response for M661 matching actual response format"""

    header = "CMD M661 Received.\nok\n" # First, create the text header in ASCII
    response = header.encode('ascii') # Convert the header to bytes
    response += b'D\xcc\xd1D\xcc' # Start with "D" and then the specific sequence seen in the real printer response
    
    for filename in virtual_files: # Add files from the virtual files list
        file_entry = f"::\xcc\xd1/data/{filename}::"
        response += file_entry.encode('utf-8', errors='replace')
    
    #if logger:
    #    hex_dump = binascii.hexlify(response[:50]).decode('ascii')
    #    logger(f"M661 response hex dump (first 50 bytes): {hex_dump}")
    #    logger(f"M661 response includes {len(virtual_files)} files")
    
    return response

def get_thumbnail_response(thumbnail_path, file_path, virtual_files, logger=None):
    """Generate thumbnail response (M662) - binary response"""
    try:
        # Check if we have a valid thumbnail path
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            if logger:
                logger("Warning: No thumbnail file available")
            return f"CMD M662 Received.\nok\n".encode('ascii')
        
        # Log the file path being requested
        if logger:
            logger(f"Thumbnail requested for: {file_path}")
        
        # Check if the requested filename is in our virtual files list
        # Extract just the filename from the full path if needed
        requested_filename = os.path.basename(file_path)
        if file_path.startswith('/data/'):
            requested_filename = file_path[6:]  # Remove '/data/' prefix
        
        # Check if the file exists in our virtual files
        file_found = False
        for vfile in virtual_files:
            if vfile == requested_filename or f"/data/{vfile}" == file_path:
                file_found = True
                break
        
        if not file_found and logger:
            logger(f"Warning: Requested file {requested_filename} not in virtual files list")
            # Still return the thumbnail even if file not found for compatibility
        
        # Read the thumbnail file
        with open(thumbnail_path, 'rb') as f:
            png_data = f.read()
        
        # Response format: text header + PNG data
        header = f"CMD M662 Received.\nok\n".encode('ascii')
        
        # Combine header and PNG data
        response = bytearray()
        response.extend(header)
        response.extend(png_data)
        
        if logger:
            logger(f"Sending thumbnail response ({len(response)} bytes)")
        return response
    except Exception as e:
        if logger:
            logger(f"Error preparing thumbnail: {str(e)}")
        return f"CMD M662 Received.\nError: {str(e)}\nok\n".encode('ascii')
