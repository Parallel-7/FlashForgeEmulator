"""
HTTP response generators for FlashForge API endpoints
"""
import json
import base64
from datetime import datetime
from typing import Dict, Any, List
from .printer_modes import ModeFeatures, get_printer_name_for_mode, get_machine_type_for_mode
import config

def create_error_response(code: int = 1, message: str = "Error") -> Dict[str, Any]:
    """Create standard error response"""
    return {
        "code": code,
        "message": message
    }

def create_success_response(data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standard success response"""
    response = {
        "code": 0,
        "message": "Success"  # CRITICAL: FlashForgeUI requires "Success" for validation
    }
    if data:
        response.update(data)
    return response

def generate_product_response(printer_config: Dict[str, Any], mode_features: ModeFeatures) -> Dict[str, Any]:
    """Generate /product endpoint response"""
    control_states = mode_features.get_product_control_states()

    return create_success_response({
        "product": control_states
    })

def generate_detail_response(printer_config: Dict[str, Any], mode: str, material_station=None) -> Dict[str, Any]:
    """Generate /detail endpoint response with comprehensive printer status"""

    # Get mode-specific printer info
    printer_name = get_printer_name_for_mode(mode, printer_config.get('printer_name', 'FlashForge Adventurer'))
    machine_type = get_machine_type_for_mode(mode)

    # Get current temperatures and status
    hotend_temp = printer_config.get('hotend_temp', 23.0)
    target_hotend = printer_config.get('target_hotend', 0.0)
    bed_temp = printer_config.get('bed_temp', 30.0)
    target_bed = printer_config.get('target_bed', 0.0)
    chamber_temp = printer_config.get('chamber_temp', 25.0)

    # Get print status
    print_status = printer_config.get('print_status', 'ready')
    progress = printer_config.get('print_progress', 0.0)
    current_file = printer_config.get('current_file', '')
    print_layer = printer_config.get('current_layer', 0)
    total_layers = printer_config.get('total_layers', 0)
    print_duration = printer_config.get('print_duration', 0)
    remaining_time = printer_config.get('remaining_time', 0)

    # Base detail object
    detail = {
        "name": printer_name,
        "firmwareVersion": printer_config.get('firmware_version', '1.0.0'),
        "macAddr": printer_config.get('mac_address', 'AA:BB:CC:DD:EE:FF'),
        "ipAddr": printer_config.get('ip_address', '192.168.1.100'),
        "status": print_status,

        # Cumulative statistics (CRITICAL for FiveMClient initialization)
        "cumulativePrintTime": printer_config.get('cumulative_print_time', 0),  # in minutes
        "cumulativeFilament": printer_config.get('cumulative_filament', 0.0),   # in meters

        # Temperatures
        "rightTemp": hotend_temp,
        "rightTargetTemp": target_hotend,
        "platTemp": bed_temp,
        "platTargetTemp": target_bed,
        "chamberTemp": chamber_temp,
        "chamberTargetTemp": 0.0,

        # Fan speeds
        "coolingFanSpeed": printer_config.get('cooling_fan_speed', 0),
        "chamberFanSpeed": printer_config.get('chamber_fan_speed', 0),

        # Control states
        "lightStatus": "open" if printer_config.get('led_on', False) else "close",
        "doorStatus": "close",  # Always closed for emulation
        "autoShutdown": "close",
        "autoShutdownTime": 0,

        # Print job info
        "printFileName": current_file,
        "printProgress": progress,
        "printLayer": print_layer,
        "targetPrintLayer": total_layers,
        "printDuration": print_duration,
        "estimatedTime": remaining_time,

        # Filament info
        "rightFilamentType": "PLA",
        "hasRightFilament": True,
        "leftFilamentType": "",
        "hasLeftFilament": False,

        # Other status
        "errorCode": "",
        "measure": "metric",
        "nozzleCnt": 1,
        "nozzleModel": "0.4mm",
        "currentPrintSpeed": 100,
        "printSpeedAdjust": 100,
        "zAxisCompensation": 0.0,
        "tvoc": 0,

        # Storage
        "remainingDiskSpace": 1024,  # MB

        # File estimates (read from config, updated via UI)
        # These represent TOTAL job filament, not consumed
        # DO NOT multiply by progress - return the raw values
        "estimatedRightLen": printer_config.get('estimated_right_len', 0.0),
        "estimatedRightWeight": printer_config.get('estimated_right_weight', 0.0),
        "estimatedLeftLen": printer_config.get('estimated_left_len', 0.0),
        "estimatedLeftWeight": printer_config.get('estimated_left_weight', 0.0),

        # Cloud codes
        "flashRegisterCode": "",
        "polarRegisterCode": ""
    }

    # Add mode-specific fields
    mode_features = ModeFeatures(mode)

    if mode_features.has_filtration:
        detail.update({
            "externalFanStatus": "close",
            "internalFanStatus": "close"
        })

    if mode_features.has_camera:
        detail["cameraStreamUrl"] = f"http://{printer_config.get('ip_address', '192.168.1.100')}:8080/stream"

    # Add AD5X specific fields
    if mode_features.has_material_station and material_station:
        detail.update({
            "hasMatlStation": True,
            "matlStationInfo": material_station.get_status()
        })

        # For single extruder with material station
        if material_station.current_slot > 0:
            current_slot_info = None
            for slot in material_station.slots:
                if slot['slotId'] == material_station.current_slot:
                    current_slot_info = slot
                    break

            if current_slot_info and current_slot_info['hasFilament']:
                detail.update({
                    "indepMatlInfo": {
                        "materialColor": current_slot_info['materialColor'],
                        "materialName": current_slot_info['materialName'],
                        "stateAction": 0,
                        "stateStep": 0
                    }
                })
    else:
        detail["hasMatlStation"] = False

    # Add dual extruder fields for Pro models
    if mode_features.has_camera:  # Use camera as proxy for Pro features
        detail.update({
            "leftTemp": 0.0,
            "leftTargetTemp": 0.0,
            "coolingFanLeftSpeed": 0
        })

    return create_success_response({"detail": detail})

def generate_gcode_list_response(file_manager, printer_mode: str = "5M") -> Dict[str, Any]:
    """Generate /gcodeList endpoint response"""
    file_list = file_manager.get_recent_file_list(printer_mode)

    if printer_mode == "AD5X":
        # Return detailed format with gcodeListDetail
        return create_success_response({
            "gcodeList": [],  # Keep empty for compatibility
            "gcodeListDetail": file_list
        })
    else:
        # Return simple format
        return create_success_response({
            "gcodeList": file_list
        })

def generate_thumbnail_response(file_manager, filename: str) -> Dict[str, Any]:
    """Generate /gcodeThumb endpoint response"""
    thumbnail_data = file_manager.get_file_thumbnail(filename)

    if thumbnail_data:
        return create_success_response({
            "imageData": thumbnail_data
        })
    else:
        return create_error_response(1, "Thumbnail not found")

def generate_upload_response(success: bool = True, message: str = "") -> Dict[str, Any]:
    """Generate /uploadGcode endpoint response"""
    if success:
        return create_success_response()
    else:
        return create_error_response(1, message or "Upload failed")

def generate_print_gcode_response(success: bool = True, message: str = "") -> Dict[str, Any]:
    """Generate /printGcode endpoint response"""
    if success:
        return create_success_response()
    else:
        return create_error_response(1, message or "Print start failed")

def generate_control_response(success: bool = True, message: str = "") -> Dict[str, Any]:
    """Generate /control endpoint response"""
    if success:
        return create_success_response()
    else:
        return create_error_response(1, message or "Control command failed")

# Command-specific response handlers
def handle_light_control(printer_config: Dict[str, Any], args: Dict[str, Any]) -> bool:
    """Handle lightControl_cmd command"""
    status = args.get('status', 'close')
    printer_config['led_on'] = (status == 'open')
    return True

def handle_printer_control(printer_config: Dict[str, Any], args: Dict[str, Any]) -> bool:
    """Handle printerCtl_cmd command"""
    # Update printer settings during print
    if args.get('speed'):
        printer_config['print_speed_adjust'] = args['speed']
    if args.get('zAxisCompensation') is not None:
        printer_config['z_axis_compensation'] = args['zAxisCompensation']
    if args.get('chamberFan'):
        printer_config['chamber_fan_speed'] = args['chamberFan']
    if args.get('coolingFan'):
        printer_config['cooling_fan_speed'] = args['coolingFan']
    return True

def handle_job_control(printer_config: Dict[str, Any], args: Dict[str, Any]) -> bool:
    """Handle jobCtl_cmd command"""
    action = args.get('action', '')

    if action == 'pause':
        if printer_config.get('print_status') == 'printing':
            printer_config['print_status'] = 'paused'
            return True
    elif action == 'continue':
        if printer_config.get('print_status') == 'paused':
            printer_config['print_status'] = 'printing'
            return True
    elif action == 'cancel':
        if printer_config.get('print_status') in ['printing', 'paused']:
            printer_config['print_status'] = 'ready'
            printer_config['print_progress'] = 0.0
            printer_config['current_file'] = ''
            printer_config['current_layer'] = 0
            printer_config['print_duration'] = 0
            return True

    return False

def handle_circulation_control(printer_config: Dict[str, Any], args: Dict[str, Any]) -> bool:
    """Handle circulateCtl_cmd command (filtration)"""
    internal = args.get('internal', 'close')
    external = args.get('external', 'close')

    printer_config['internal_fan_on'] = (internal == 'open')
    printer_config['external_fan_on'] = (external == 'open')
    return True

def handle_camera_control(printer_config: Dict[str, Any], args: Dict[str, Any]) -> bool:
    """Handle streamCtrl_cmd command (camera)"""
    action = args.get('action', 'close')
    printer_config['camera_on'] = (action == 'open')
    return True

def handle_temperature_control(printer_config: Dict[str, Any], args: Dict[str, Any]) -> bool:
    """Handle temperatureCtl_cmd command"""
    if 'extruderTemp' in args:
        printer_config['target_hotend'] = float(args['extruderTemp'])
    if 'bedTemp' in args:
        printer_config['target_bed'] = float(args['bedTemp'])
    if 'chamberTemp' in args:
        printer_config['target_chamber'] = float(args['chamberTemp'])
    return True

# Command dispatcher
COMMAND_HANDLERS = {
    "lightControl_cmd": handle_light_control,
    "printerCtl_cmd": handle_printer_control,
    "jobCtl_cmd": handle_job_control,
    "circulateCtl_cmd": handle_circulation_control,
    "streamCtrl_cmd": handle_camera_control,
    "temperatureCtl_cmd": handle_temperature_control
}

def process_control_command(printer_config: Dict[str, Any], command: str, args: Dict[str, Any]) -> bool:
    """Process a control command and update printer state"""
    handler = COMMAND_HANDLERS.get(command)
    if handler:
        return handler(printer_config, args)
    return False