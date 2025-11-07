# Configuration File
CONFIG_FILE = "emulator_config.json"

# Network Ports
DISCOVERY_PORT = 48899
COMMAND_PORT = 8899
HTTP_PORT = 8898

# Default Printer Info
DEFAULT_PRINTER_NAME = "FlashForge Adventurer 4"
DEFAULT_SERIAL_NUMBER = "FF3DP123456789"
DEFAULT_MACHINE_TYPE = "Adventurer 4"
DEFAULT_FIRMWARE_VERSION = "1.2.3"

# Default Idle Temps
DEFAULT_IDLE_HOTEND_TEMP = 23.0
DEFAULT_IDLE_BED_TEMP = 30.0

# Default Cumulative Statistics
DEFAULT_CUMULATIVE_PRINT_TIME = 0  # Total print time in minutes
DEFAULT_CUMULATIVE_FILAMENT = 0.0  # Total filament used in meters

# Default files
DEFAULT_VIRTUAL_FILES = [
    "test.3mf",
    "test2.gcode",
    "test3.gcode.gx",
    "test_multicolor.3mf"
]

# UI dimensions
UI_WINDOW_WIDTH = 700
UI_WINDOW_HEIGHT = 750

# HTTP API Configuration
HTTP_CONFIG = {
    'port': HTTP_PORT,
    'enabled': True,
    'printer_mode': 'AD5X',  # Default mode: 5M, 5M_Pro, AD5X
    'check_code': '0e35a229',  # Default check code
    'material_station': {
        'slot_count': 4,
        'default_slots': [
            {'slotId': 1, 'hasFilament': True, 'materialName': 'PLA', 'materialColor': '#FF0000'},
            {'slotId': 2, 'hasFilament': True, 'materialName': 'PLA', 'materialColor': '#00FF00'},
            {'slotId': 3, 'hasFilament': False, 'materialName': '', 'materialColor': ''},
            {'slotId': 4, 'hasFilament': False, 'materialName': '', 'materialColor': ''}
        ]
    }
}

# Protocol Modes
class ProtocolMode:
    TCP_ONLY = "TCP_Only"
    HTTP_ONLY = "HTTP_Only"
    DUAL_MODE = "Dual_Mode"

# Printer Modes
class PrinterMode:
    STANDARD_5M = "5M"
    PRO_5M = "5M_Pro"
    AD5X = "AD5X"
