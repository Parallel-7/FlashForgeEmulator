import random
import time
import os
import json
from .server import EmulatorServer
from .file_manager import EnhancedFileManager
from .printer_modes import MaterialStationEmulator
import config
from utils.network import get_network_interfaces, get_primary_ip

class PrinterEmulator:
    """Core printer emulator class"""
    
    def __init__(self, logger=None):
        self._logger = logger if logger else print
        
        # Track idle temperature settings
        self.idle_hotend_temp = config.DEFAULT_IDLE_HOTEND_TEMP
        self.idle_bed_temp = config.DEFAULT_IDLE_BED_TEMP
        
        # Find network interfaces
        self.network_interfaces = get_network_interfaces()
        primary_ip = get_primary_ip(self.network_interfaces)
        
        # Initialize virtual files and enhanced file manager
        self.virtual_files = config.DEFAULT_VIRTUAL_FILES.copy()
        self.thumbnail_path = None
        self.file_manager = EnhancedFileManager(self.virtual_files, self.thumbnail_path)
        
        # Printer configuration
        self.config = {
            "printer_name": config.DEFAULT_PRINTER_NAME,
            "serial_number": config.DEFAULT_SERIAL_NUMBER,
            "machine_type": config.DEFAULT_MACHINE_TYPE,
            "firmware_version": config.DEFAULT_FIRMWARE_VERSION,
            "ip_address": primary_ip,
            "mac_address": "AA:BB:CC:DD:EE:FF",  # HTTP API requires MAC address
            "led_state": False,
            "hotend_temp": self.idle_hotend_temp,
            "bed_temp": self.idle_bed_temp,
            "target_hotend": 0.0,
            "target_bed": 0.0,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "print_status": "ready",  # ready, busy, printing, paused, completed, cancelled, error
            "print_progress": 0,     # 0-100
            "filament_runout_sensor": True,
            "current_file": "sample_model.3mf",  # Currently printing file name
            "x_dimension": 200,  # Printer dimensions in mm
            "y_dimension": 200,
            "z_dimension": 200,
            "tool_count": 1,      # Number of print heads
            "discovery_enabled": True,  # Enable/disable the discovery service
            "printer_mode": config.HTTP_CONFIG['printer_mode'],  # HTTP API printer mode
            "check_code": config.HTTP_CONFIG['check_code'],      # HTTP API check code
            # HTTP API specific config
            "led_on": False,
            "cooling_fan_speed": 0,
            "chamber_fan_speed": 0,
            "chamber_temp": 25.0,
            "target_chamber": 0.0,
            "print_duration": 0,
            "remaining_time": 0,
            "estimated_print_time": 3600,  # Total estimated time for current print (seconds)
            "current_layer": 0,
            "total_layers": 0,
            "camera_on": False,
            "internal_fan_on": False,
            "external_fan_on": False,
            "print_speed_adjust": 100,
            "z_axis_compensation": 0.0,
            # Cumulative statistics
            "cumulative_print_time": config.DEFAULT_CUMULATIVE_PRINT_TIME,  # Total lifetime print time (minutes)
            "cumulative_filament": config.DEFAULT_CUMULATIVE_FILAMENT,   # Total lifetime filament used (meters)
            # Per-print filament estimates
            "estimated_right_len": 0.0,  # Meters of filament for this print (right extruder)
            "estimated_right_weight": 0.0,  # Grams of filament for this print (right extruder)
            "estimated_left_len": 0.0,  # Meters of filament for this print (left extruder)
            "estimated_left_weight": 0.0   # Grams of filament for this print (left extruder)
        }

        # Initialize Material Station for AD5X mode
        self.material_station = None
        if self.config['printer_mode'] == config.PrinterMode.AD5X:
            self.material_station = MaterialStationEmulator(config.HTTP_CONFIG['material_station']['default_slots'])

        # Initialize servers
        self.server = EmulatorServer(self.config, self.virtual_files, self.thumbnail_path, self.log)
        self.http_server = None  # Will be created when start_http_server() is called
    
    @property
    def log(self):
        return self._logger
        
    @log.setter
    def log(self, logger):
        self._logger = logger
        # When the logger changes, update the server's logger too
        if hasattr(self, 'server'):
            self.server.log = logger

    def save_config_to_json(self, filepath=None):
        """Save current configuration to JSON file"""
        if filepath is None:
            filepath = config.CONFIG_FILE

        try:
            config_data = {
                "printer_name": self.config["printer_name"],
                "serial_number": self.config["serial_number"],
                "machine_type": self.config["machine_type"],
                "firmware_version": self.config["firmware_version"],
                "ip_address": self.config["ip_address"],
                "discovery_enabled": self.config["discovery_enabled"],
                "printer_mode": self.config["printer_mode"],
                "check_code": self.config["check_code"],
                "idle_hotend_temp": self.idle_hotend_temp,
                "idle_bed_temp": self.idle_bed_temp,
                "virtual_files": self.virtual_files,
                "thumbnail_path": self.thumbnail_path,
                "cumulative_print_time": self.config["cumulative_print_time"],
                "cumulative_filament": self.config["cumulative_filament"]
            }

            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)

            self.log(f"Configuration saved to {filepath}")
            return True
        except Exception as e:
            self.log(f"Error saving configuration: {e}")
            return False

    def load_config_from_json(self, filepath=None):
        """Load configuration from JSON file"""
        if filepath is None:
            filepath = config.CONFIG_FILE

        if not os.path.exists(filepath):
            self.log(f"No saved configuration found at {filepath}, using defaults")
            return False

        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)

            # Update printer config
            if "printer_name" in config_data:
                self.config["printer_name"] = config_data["printer_name"]
            if "serial_number" in config_data:
                self.config["serial_number"] = config_data["serial_number"]
            if "machine_type" in config_data:
                self.config["machine_type"] = config_data["machine_type"]
            if "firmware_version" in config_data:
                self.config["firmware_version"] = config_data["firmware_version"]
            if "ip_address" in config_data:
                self.config["ip_address"] = config_data["ip_address"]
            if "discovery_enabled" in config_data:
                self.config["discovery_enabled"] = config_data["discovery_enabled"]
            if "printer_mode" in config_data:
                self.config["printer_mode"] = config_data["printer_mode"]
            if "check_code" in config_data:
                self.config["check_code"] = config_data["check_code"]

            # Update idle temperatures
            if "idle_hotend_temp" in config_data:
                self.idle_hotend_temp = config_data["idle_hotend_temp"]
                self.config["hotend_temp"] = self.idle_hotend_temp
            if "idle_bed_temp" in config_data:
                self.idle_bed_temp = config_data["idle_bed_temp"]
                self.config["bed_temp"] = self.idle_bed_temp

            # Update virtual files
            if "virtual_files" in config_data:
                self.virtual_files = config_data["virtual_files"]
                self.file_manager.virtual_files = self.virtual_files

            # Update thumbnail path
            if "thumbnail_path" in config_data and config_data["thumbnail_path"]:
                self.thumbnail_path = config_data["thumbnail_path"]
                if hasattr(self, 'server'):
                    self.server.thumbnail_path = self.thumbnail_path

            # Update cumulative statistics
            if "cumulative_print_time" in config_data:
                self.config["cumulative_print_time"] = config_data["cumulative_print_time"]
            if "cumulative_filament" in config_data:
                self.config["cumulative_filament"] = config_data["cumulative_filament"]

            # Reinitialize material station if mode changed
            if self.config['printer_mode'] == config.PrinterMode.AD5X:
                if not self.material_station:
                    self.material_station = MaterialStationEmulator(config.HTTP_CONFIG['material_station']['default_slots'])
            else:
                self.material_station = None

            self.log(f"Configuration loaded from {filepath}")
            return True
        except Exception as e:
            self.log(f"Error loading configuration: {e}")
            return False

    def update_idle_temps(self, hotend_temp, bed_temp):
        """Update idle temperature settings"""
        try:
            self.idle_hotend_temp = float(hotend_temp)
            self.idle_bed_temp = float(bed_temp)
            self.log(f"Idle temperatures updated - Hotend: {self.idle_hotend_temp:.1f}°C, Bed: {self.idle_bed_temp:.1f}°C")
            
            # If no target is set, immediately start moving toward new idle temps
            if self.config['target_hotend'] <= 0:
                # Small immediate bump to show change is happening
                if self.config['hotend_temp'] < self.idle_hotend_temp:
                    self.config['hotend_temp'] += min(0.5, self.idle_hotend_temp - self.config['hotend_temp'])
                elif self.config['hotend_temp'] > self.idle_hotend_temp:
                    self.config['hotend_temp'] -= min(0.5, self.config['hotend_temp'] - self.idle_hotend_temp)
            
            if self.config['target_bed'] <= 0:
                # Small immediate bump to show change is happening
                if self.config['bed_temp'] < self.idle_bed_temp:
                    self.config['bed_temp'] += min(0.3, self.idle_bed_temp - self.config['bed_temp'])
                elif self.config['bed_temp'] > self.idle_bed_temp:
                    self.config['bed_temp'] -= min(0.3, self.config['bed_temp'] - self.idle_bed_temp)
            
            return True
        except ValueError:
            self.log("Invalid input for idle temperatures")
            return False
    
    def reset_temp(self, heater_type):
        """Reset temperature target to 0 (off)"""
        if heater_type not in ["hotend", "bed"]:
            return False
            
        self.config[f'target_{heater_type}'] = 0.0
        self.log(f"{heater_type.capitalize()} temperature target reset to 0°C")
        return True
        
    def set_temp(self, heater_type, temp):
        """Set temperature target for a heater"""
        if heater_type not in ["hotend", "bed"]:
            return False
            
        try:
            new_temp = float(temp)
            if 0 <= new_temp <= 300:  # Safe temperature range
                self.config[f'target_{heater_type}'] = new_temp
                self.log(f"{heater_type.capitalize()} temperature target set to {new_temp}°C")
                return True
            else:
                self.log(f"Invalid temperature: {temp} - must be between 0°C and 300°C")
                return False
        except ValueError:
            self.log(f"Invalid temperature value: {temp}")
            return False
    
    def set_thumbnail(self, file_path):
        """Set the thumbnail file path"""
        if not file_path or not os.path.exists(file_path):
            self.log("Invalid thumbnail file path")
            return False
            
        self.thumbnail_path = file_path
        self.server.thumbnail_path = file_path
        self.log(f"Thumbnail file set to: {file_path}")
        return True
    
    def add_virtual_file(self, filename):
        """Add a new file to the virtual files list"""
        if not filename:
            self.log("Invalid file name")
            return False
            
        # Auto-add .3mf extension if no extension is provided
        if '.' not in filename:
            filename += ".3mf"
        
        # Check if the file is already in the list
        if filename in self.virtual_files:
            self.log(f"File '{filename}' already exists in virtual files")
            return False
        
        # Add to data model
        self.virtual_files.append(filename)
        self.log(f"Added virtual file: {filename}")
        return True
    
    def delete_virtual_file(self, filename):
        """Delete a file from the virtual files list"""
        if filename not in self.virtual_files:
            self.log(f"File '{filename}' not found in virtual files")
            return False
            
        self.virtual_files.remove(filename)
        self.log(f"Deleted virtual file: {filename}")
        return True
    
    def restore_default_files(self):
        """Restore the default list of virtual files"""
        self.virtual_files = config.DEFAULT_VIRTUAL_FILES.copy()
        self.log(f"Restored {len(self.virtual_files)} default virtual files")
        return True
    
    def simulate_temperatures(self):
        """Simulate temperature changes based on targets"""
        # Hotend temperature simulation
        if self.config['target_hotend'] > 0:
            # Active heating/cooling toward target
            if abs(self.config['hotend_temp'] - self.config['target_hotend']) > 0.5:
                if self.config['hotend_temp'] < self.config['target_hotend']:
                    # Heating up (faster)
                    self.config['hotend_temp'] += min(5.0, self.config['target_hotend'] - self.config['hotend_temp'])
                else:
                    # Cooling down (slower)
                    self.config['hotend_temp'] -= min(2.0, self.config['hotend_temp'] - self.config['target_hotend'])
            
            # Add some temperature jitter for realism
            self.config['hotend_temp'] += random.uniform(-0.3, 0.3)
        else:
            # No target set, move gradually toward idle temperature
            if abs(self.config['hotend_temp'] - self.idle_hotend_temp) > 0.5:
                if self.config['hotend_temp'] > self.idle_hotend_temp:
                    # Cooling down to idle
                    self.config['hotend_temp'] -= min(1.0, self.config['hotend_temp'] - self.idle_hotend_temp)
                else:
                    # Warming to idle
                    self.config['hotend_temp'] += min(0.5, self.idle_hotend_temp - self.config['hotend_temp'])
            
            # Smaller jitter when idling
            self.config['hotend_temp'] += random.uniform(-0.1, 0.1)
        
        # Bed temperature simulation (slower changes)
        if self.config['target_bed'] > 0:
            # Active heating/cooling toward target
            if abs(self.config['bed_temp'] - self.config['target_bed']) > 0.5:
                if self.config['bed_temp'] < self.config['target_bed']:
                    # Heating up (slower)
                    self.config['bed_temp'] += min(2.0, self.config['target_bed'] - self.config['bed_temp'])
                else:
                    # Cooling down (much slower)
                    self.config['bed_temp'] -= min(1.0, self.config['bed_temp'] - self.config['target_bed'])
            
            # Add some temperature jitter for realism
            self.config['bed_temp'] += random.uniform(-0.1, 0.1)
        else:
            # No target set, move gradually toward idle temperature
            if abs(self.config['bed_temp'] - self.idle_bed_temp) > 0.5:
                if self.config['bed_temp'] > self.idle_bed_temp:
                    # Cooling down to idle
                    self.config['bed_temp'] -= min(0.8, self.config['bed_temp'] - self.idle_bed_temp)
                else:
                    # Warming to idle
                    self.config['bed_temp'] += min(0.3, self.idle_bed_temp - self.config['bed_temp'])
            
            # Smaller jitter when idling
            self.config['bed_temp'] += random.uniform(-0.05, 0.05)
    
    def update_progress(self):
        """Update print progress if in printing state"""
        if self.config['print_status'].lower() == 'printing':
            progress = self.config['print_progress']
            if progress < 100:
                self.config['print_progress'] = min(100, progress + 1)
                return True
        return False
    
    def update_print_status(self, status):
        """Update print status (ready, busy, printing, paused, completed, cancelled, error)"""
        valid_statuses = ["ready", "busy", "calibrating", "error", "heating", "printing", "pausing", "paused", "cancelled", "completed", "unknown"]
        if status.lower() not in valid_statuses:
            self.log(f"Invalid print status: {status}")
            return False

        old_status = self.config['print_status']
        self.config['print_status'] = status.lower()

        # Reset progress if switching to ready/completed/cancelled
        if status.lower() in ["ready", "completed", "cancelled"] and old_status not in ["ready", "completed", "cancelled"]:
            self.config['print_progress'] = 0

        self.log(f"Print status updated from {old_status} to {status.lower()}")
        return True
    
    def start_server(self):
        """Start the emulator server (TCP + HTTP)"""
        if self.server.is_running:
            self.log("Server is already running")
            return False

        # Start TCP server
        tcp_started = self.server.start()

        # Auto-start HTTP server for 5M family printers
        if tcp_started and config.HTTP_CONFIG.get('enabled', True):
            http_started = self.start_http_server()
            if not http_started:
                self.log("Warning: TCP server started but HTTP server failed to start")

        return tcp_started
    
    def stop_server(self):
        """Stop the emulator server (TCP + HTTP)"""
        if not self.server.is_running:
            self.log("Server is not running")
            return False

        # Stop HTTP server first
        if self.http_server and self.http_server.is_running:
            self.stop_http_server()

        # Then stop TCP server
        return self.server.stop()
    
    def restart_server(self):
        """Restart the emulator server"""
        self.stop_server()
        time.sleep(0.5)  # Small delay to ensure ports are freed
        return self.start_server()

    def start_http_server(self, port=None, http_logger=None):
        """Start the HTTP API server (async, instant startup)"""
        if self.http_server and self.http_server.is_running:
            self.log("HTTP server is already running")
            return True

        try:
            # Use fast async HTTP server
            from .http_server_async import FlashForgeHTTPServerAsync
            # Pass http_logger if provided, otherwise use main logger
            logger = http_logger if http_logger else self.log
            self.http_server = FlashForgeHTTPServerAsync(self, self.file_manager, logger, http_logger)

            success = self.http_server.start(port)
            if not success:
                self.log("Failed to start HTTP API server")
            return success
        except Exception as e:
            self.log(f"Error starting HTTP server: {e}")
            return False

    def stop_http_server(self):
        """Stop the HTTP API server"""
        if not self.http_server or not self.http_server.is_running:
            self.log("HTTP server is not running")
            return True

        try:
            success = self.http_server.stop()
            if success:
                self.log("HTTP API server stopped")
                self.http_server = None
            else:
                self.log("Failed to stop HTTP API server")
            return success
        except Exception as e:
            self.log(f"Error stopping HTTP server: {e}")
            return False

    def start_print(self, filename):
        """Start printing a file (emulation)"""
        if not self.file_manager.file_exists(filename):
            self.log(f"Cannot start print: file '{filename}' not found")
            return False

        # Update print status
        self.config['current_file'] = filename
        self.config['print_status'] = 'printing'
        self.config['print_progress'] = 0.0
        self.config['current_layer'] = 0
        self.config['print_duration'] = 0

        # Get file metadata for print simulation
        metadata = self.file_manager.get_file_metadata(filename)
        if metadata:
            self.config['total_layers'] = metadata.get('totalLayers', 100)
            self.config['remaining_time'] = metadata.get('printingTime', 3600)

        self.log(f"Started printing: {filename}")
        return True

    def pause_print(self):
        """Pause current print"""
        if self.config.get('print_status') == 'printing':
            self.config['print_status'] = 'paused'
            self.log("Print paused")
            return True
        return False

    def resume_print(self):
        """Resume paused print"""
        if self.config.get('print_status') == 'paused':
            self.config['print_status'] = 'printing'
            self.log("Print resumed")
            return True
        return False

    def cancel_print(self):
        """Cancel current print"""
        if self.config.get('print_status') in ['printing', 'paused']:
            self.config['print_status'] = 'ready'
            self.config['print_progress'] = 0.0
            self.config['current_file'] = ''
            self.config['current_layer'] = 0
            self.config['print_duration'] = 0
            self.config['remaining_time'] = 0
            self.log("Print cancelled")
            return True
        return False

    def simulate_print_progress(self):
        """Simulate print progress during active printing"""
        if self.config.get('print_status') != 'printing':
            return

        # Simulate progress increment (very slow for realism)
        progress_increment = random.uniform(0.01, 0.05)  # 0.01% to 0.05% per call
        new_progress = min(100.0, self.config['print_progress'] + progress_increment)
        self.config['print_progress'] = new_progress

        # Update layer count proportionally
        total_layers = self.config.get('total_layers', 100)
        new_layer = int((new_progress / 100.0) * total_layers)
        self.config['current_layer'] = new_layer

        # Update print duration
        self.config['print_duration'] += 1  # 1 second per simulation tick

        # Update remaining time (simple linear estimation)
        if new_progress > 0:
            estimated_total_time = (self.config['print_duration'] * 100) / new_progress
            self.config['remaining_time'] = max(0, estimated_total_time - self.config['print_duration'])

        # Complete print when reaching 100%
        if new_progress >= 100.0:
            self.config['print_status'] = 'completed'
            self.config['remaining_time'] = 0
            self.log(f"Print completed: {self.config.get('current_file', 'unknown')}")

    def update_printer_mode(self, mode):
        """Update printer mode and reinitialize components if needed"""
        if mode not in [config.PrinterMode.STANDARD_5M, config.PrinterMode.PRO_5M, config.PrinterMode.AD5X]:
            return False

        old_mode = self.config.get('printer_mode')
        self.config['printer_mode'] = mode

        # Update material station based on mode
        if mode == config.PrinterMode.AD5X:
            if not self.material_station:
                self.material_station = MaterialStationEmulator(config.HTTP_CONFIG['material_station']['default_slots'])
        else:
            self.material_station = None

        # Update printer name based on mode
        from .printer_modes import get_printer_name_for_mode
        base_name = "FlashForge Adventurer"
        self.config['printer_name'] = get_printer_name_for_mode(mode, base_name)

        self.log(f"Printer mode changed from {old_mode} to {mode}")
        return True
