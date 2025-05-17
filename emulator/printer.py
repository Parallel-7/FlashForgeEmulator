import random
import time
import os
from .server import EmulatorServer
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
        
        # Initialize virtual files
        self.virtual_files = config.DEFAULT_VIRTUAL_FILES.copy()
        
        # Thumbnail path
        self.thumbnail_path = None
        
        # Printer configuration
        self.config = {
            "printer_name": config.DEFAULT_PRINTER_NAME,
            "serial_number": config.DEFAULT_SERIAL_NUMBER,
            "machine_type": config.DEFAULT_MACHINE_TYPE,
            "firmware_version": config.DEFAULT_FIRMWARE_VERSION,
            "ip_address": primary_ip,
            "led_state": False,
            "hotend_temp": self.idle_hotend_temp,
            "bed_temp": self.idle_bed_temp,
            "target_hotend": 0.0,
            "target_bed": 0.0,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "print_status": "idle",  # idle, printing, paused, completed, failed
            "print_progress": 0,     # 0-100
            "filament_runout_sensor": True,
            "current_file": "sample_model.3mf",  # Currently printing file name
            "x_dimension": 200,  # Printer dimensions in mm
            "y_dimension": 200,
            "z_dimension": 200,
            "tool_count": 1,      # Number of print heads
            "discovery_enabled": True  # Enable/disable the discovery service
        }
        
        # Initialize server
        self.server = EmulatorServer(self.config, self.virtual_files, self.thumbnail_path, self.log)
    
    @property
    def log(self):
        return self._logger
        
    @log.setter
    def log(self, logger):
        self._logger = logger
        # When the logger changes, update the server's logger too
        if hasattr(self, 'server'):
            self.server.log = logger
    
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
        """Update print status (idle, printing, paused, completed, failed)"""
        if status.lower() not in ["idle", "printing", "paused", "completed", "failed"]:
            self.log(f"Invalid print status: {status}")
            return False
            
        old_status = self.config['print_status']
        self.config['print_status'] = status.lower()
        
        # Reset progress if switching to idle
        if status.lower() == "idle" and old_status != "idle":
            self.config['print_progress'] = 0
            
        self.log(f"Print status updated from {old_status} to {status.lower()}")
        return True
    
    def start_server(self):
        """Start the emulator server"""
        if self.server.is_running:
            self.log("Server is already running")
            return False
            
        return self.server.start()
    
    def stop_server(self):
        """Stop the emulator server"""
        if not self.server.is_running:
            self.log("Server is not running")
            return False
            
        return self.server.stop()
    
    def restart_server(self):
        """Restart the emulator server"""
        self.stop_server()
        time.sleep(0.5)  # Small delay to ensure ports are freed
        return self.start_server()
