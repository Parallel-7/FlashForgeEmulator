import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import socket
import threading
import json
import os
import time
import binascii
import random
import re
from datetime import datetime
from PIL import Image, ImageDraw

# First, create a standard thumbnail image
def create_standard_thumbnail():
    """Create a standard thumbnail image for the emulator"""
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "standard_thumbnail.png")
    
    # If the thumbnail already exists, don't recreate it
    if os.path.exists(output_path):
        return output_path
    
    try:
        # Create a new image with a blue background
        size = (200, 200)
        background_color = (0, 100, 200)
        img = Image.new('RGB', size, background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes to make it recognizable
        width, height = size
        
        # Draw border
        border_color = (255, 255, 255)
        border_width = 10
        draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=border_width)
        
        # Draw diagonal lines
        draw.line([(0, 0), (width, height)], fill=(255, 0, 0), width=5)
        draw.line([(0, height), (width, 0)], fill=(255, 0, 0), width=5)
        
        # Draw center circle
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], outline=(0, 255, 0), width=5)
        
        # Save the image
        img.save(output_path, 'PNG')
        print(f"Standard thumbnail created at: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error creating thumbnail: {str(e)}")
        return None

class FlashForgeEmulator:
    """
    FlashForge 3D Printer Emulator
    
    Emulates network protocol of FlashForge printers to allow testing
    of client applications.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("FlashForge Printer Emulator")
        self.root.geometry("700x500")
        
        # Create standard thumbnail
        self.thumbnail_path = create_standard_thumbnail()
        
        # Detect IP addresses
        self.network_interfaces = self.get_network_interfaces()
        primary_ip = self.get_primary_ip()
        
        # Printer configuration
        self.config = {
            "printer_name": "FlashForge Emulator",
            "serial_number": "FF3DP123456789",
            "machine_type": "Adventurer 4",
            "firmware_version": "v2.14.5",
            "ip_address": primary_ip,
            "led_state": False,
            "hotend_temp": 25.0,
            "bed_temp": 25.0,
            "target_hotend": 0.0,
            "target_bed": 0.0,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "print_status": "idle",  # idle, printing, paused, completed, failed
            "print_progress": 52,     # 0-100
            "filament_runout_sensor": True,
            "current_file": "sample_model.3mf"  # Currently printing file name
        }
        
        # File list for M661 command
        self.virtual_files = [
            "sample_model.3mf",
            "test_print.gcode",
            "calibration_cube.gx"
        ]
        
        # Setup UI
        self.setup_ui()
        
        # Start servers
        self.discovery_server = None
        self.tcp_server = None
        self.tcp_clients = []
        self.start_servers()
        
        # Setup periodic updates
        self.update_ui()

    def get_network_interfaces(self):
        """Get all network interfaces with their IP addresses"""
        interfaces = []
        try:
            # Get all network interfaces using socket.if_nameindex()
            for iface_name in socket.if_nameindex():
                try:
                    ip = socket.gethostbyname(socket.gethostname())
                    interfaces.append((iface_name[1], ip))
                except:
                    pass
        except:
            # Alternative method for Windows
            try:
                # Try to get all IP addresses
                ips = socket.getaddrinfo(socket.gethostname(), None)
                for ip_info in ips:
                    if ip_info[0] == socket.AF_INET:  # IPv4 only
                        ip = ip_info[4][0]
                        if not ip.startswith('127.'):  # Skip loopback
                            interfaces.append(("eth", ip))
            except:
                # Fallback: just use the primary IP
                interfaces.append(("eth0", socket.gethostbyname(socket.gethostname())))
        
        # Also explicitly try common IP patterns
        for ip_prefix in ['192.168.', '10.', '172.']:
            for i in range(254):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    # This doesn't send any packets but allows us to see what IP would be used
                    s.connect((f"{ip_prefix}1.1", 1))
                    local_ip = s.getsockname()[0]
                    s.close()
                    if local_ip.startswith(ip_prefix) and local_ip not in [i[1] for i in interfaces]:
                        interfaces.append(("eth", local_ip))
                    break
                except:
                    pass
        
        return interfaces

    def get_primary_ip(self):
        """Get the primary IP address (non-loopback)"""
        # Try common network ranges first
        for prefix in ['192.168.', '10.', '172.']:
            for iface, ip in self.network_interfaces:
                if ip.startswith(prefix):
                    return ip
        
        # If no common network ranges, return the first non-loopback IP
        for iface, ip in self.network_interfaces:
            if not ip.startswith('127.'):
                return ip
                
        # Last resort: return localhost
        return '127.0.0.1'

    def setup_ui(self):
        # Create notebook with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        config_tab = ttk.Frame(notebook)
        logs_tab = ttk.Frame(notebook)
        
        notebook.add(config_tab, text="Configuration")
        notebook.add(logs_tab, text="Logs")
        
        # Configuration tab
        self.setup_config_tab(config_tab)
        
        # Logs tab
        self.setup_logs_tab(logs_tab)

    def setup_config_tab(self, parent):
        # Configuration Frame
        config_frame = ttk.LabelFrame(parent, text="Printer Configuration")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        row = 0
        # Printer info
        ttk.Label(config_frame, text="Printer Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.printer_name_var = tk.StringVar(value=self.config["printer_name"])
        ttk.Entry(config_frame, textvariable=self.printer_name_var, width=25).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Label(config_frame, text="Serial Number:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.serial_number_var = tk.StringVar(value=self.config["serial_number"])
        ttk.Entry(config_frame, textvariable=self.serial_number_var, width=25).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Label(config_frame, text="Machine Type:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.machine_type_var = tk.StringVar(value=self.config["machine_type"])
        ttk.Entry(config_frame, textvariable=self.machine_type_var, width=25).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Label(config_frame, text="Firmware Version:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.firmware_version_var = tk.StringVar(value=self.config["firmware_version"])
        ttk.Entry(config_frame, textvariable=self.firmware_version_var, width=25).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        # IP address selection
        ttk.Label(config_frame, text="Network Interface:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.ip_address_var = tk.StringVar(value=self.config["ip_address"])
        ip_combo = ttk.Combobox(config_frame, textvariable=self.ip_address_var, width=25)
        ip_combo['values'] = [ip for _, ip in self.network_interfaces]
        ip_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        ip_combo.bind('<<ComboboxSelected>>', lambda e: self.update_config_from_ui())
        row += 1
        
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Printer Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        row = 0
        # Temperature controls
        ttk.Label(status_frame, text="Hotend Temperature:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.hotend_temp_var = tk.StringVar(value=f"{self.config['hotend_temp']:.1f}°C / {self.config['target_hotend']:.1f}°C")
        ttk.Label(status_frame, textvariable=self.hotend_temp_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Button(status_frame, text="Set", command=lambda: self.show_temp_dialog('hotend')).grid(row=row, column=2, padx=5, pady=2)
        row += 1
        
        ttk.Label(status_frame, text="Bed Temperature:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.bed_temp_var = tk.StringVar(value=f"{self.config['bed_temp']:.1f}°C / {self.config['target_bed']:.1f}°C")
        ttk.Label(status_frame, textvariable=self.bed_temp_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Button(status_frame, text="Set", command=lambda: self.show_temp_dialog('bed')).grid(row=row, column=2, padx=5, pady=2)
        row += 1
        
        # Current file being printed
        ttk.Label(status_frame, text="Current File:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.current_file_var = tk.StringVar(value=self.config["current_file"])
        file_entry = ttk.Entry(status_frame, textvariable=self.current_file_var, width=25)
        file_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        file_entry.bind("<Return>", lambda e: self.update_config_from_ui())
        row += 1
        
        # Print status
        ttk.Label(status_frame, text="Print Status:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.print_status_var = tk.StringVar(value=self.config["print_status"].capitalize())
        status_combo = ttk.Combobox(status_frame, textvariable=self.print_status_var, width=15)
        status_combo['values'] = ('Idle', 'Printing', 'Paused', 'Completed', 'Failed')
        status_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.update_config_from_ui())
        row += 1
        
        ttk.Label(status_frame, text="Print Progress:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.progress_var = tk.IntVar(value=self.config["print_progress"])
        progress_scale = ttk.Scale(status_frame, from_=0, to=100, variable=self.progress_var, orient=tk.HORIZONTAL, length=150)
        progress_scale.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        progress_scale.bind("<ButtonRelease-1>", lambda e: self.update_config_from_ui())
        self.progress_label = ttk.Label(status_frame, text=f"{self.config['print_progress']}%")
        self.progress_label.grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        # LED state
        ttk.Label(status_frame, text="LED State:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.led_var = tk.BooleanVar(value=self.config["led_state"])
        ttk.Checkbutton(status_frame, variable=self.led_var, command=self.update_config_from_ui).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        # Filament sensor
        ttk.Label(status_frame, text="Filament Sensor:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.filament_sensor_var = tk.BooleanVar(value=self.config["filament_runout_sensor"])
        ttk.Checkbutton(status_frame, variable=self.filament_sensor_var, command=self.update_config_from_ui).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        # Thumbnail selection
        thumbnail_frame = ttk.LabelFrame(parent, text="File Emulation")
        thumbnail_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(thumbnail_frame, text="Thumbnail File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.thumbnail_path_var = tk.StringVar(value=os.path.basename(self.thumbnail_path) if self.thumbnail_path else "No file selected")
        ttk.Label(thumbnail_frame, textvariable=self.thumbnail_path_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Button(thumbnail_frame, text="Browse...", command=self.browse_thumbnail).grid(row=0, column=2, padx=5, pady=2)
        
        # Server control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.server_status_var = tk.StringVar(value="Server Status: Stopped")
        ttk.Label(control_frame, textvariable=self.server_status_var).pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Server", command=self.start_servers)
        self.start_button.pack(side=tk.RIGHT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Server", command=self.stop_servers, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5)

    def setup_logs_tab(self, parent):
        # Log Frame
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create log display
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.RIGHT, padx=5)

    def log(self, message):
        """Add a timestamped entry to the log display"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Update UI (in a thread-safe way)
        self.root.after(0, self._update_log, log_entry)
    
    def _update_log(self, log_entry):
        """Update log display (called from main thread)"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """Clear all log entries"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_ui(self):
        """Periodic UI updates"""
        # Update the temperature to simulate real printer behavior
        self.simulate_temperatures()
        
        # Update progress if printing
        if self.config['print_status'].lower() == 'printing':
            progress = self.config['print_progress']
            if progress < 100:
                self.config['print_progress'] = min(100, progress + 1)
                self.progress_var.set(self.config['print_progress'])
                self.progress_label.config(text=f"{self.config['print_progress']}%")
        
        # Update temperature display
        self.hotend_temp_var.set(f"{self.config['hotend_temp']:.1f}°C / {self.config['target_hotend']:.1f}°C")
        self.bed_temp_var.set(f"{self.config['bed_temp']:.1f}°C / {self.config['target_bed']:.1f}°C")
        
        # Make sure initial temperature values are reasonable
        if self.config['hotend_temp'] <= 0:
            self.config['hotend_temp'] = 22.0 + random.uniform(-1.0, 1.0)  # Room temperature
        
        if self.config['bed_temp'] <= 0:
            self.config['bed_temp'] = 22.0 + random.uniform(-1.0, 1.0)  # Room temperature
        
        # Schedule next update
        self.root.after(1000, self.update_ui)
    
    def simulate_temperatures(self):
        """Simulate temperature changes based on targets"""
        # Hotend temperature simulation
        if abs(self.config['hotend_temp'] - self.config['target_hotend']) > 0.5:
            if self.config['hotend_temp'] < self.config['target_hotend']:
                # Heating up (faster)
                self.config['hotend_temp'] += min(5.0, self.config['target_hotend'] - self.config['hotend_temp'])
            else:
                # Cooling down (slower)
                self.config['hotend_temp'] -= min(2.0, self.config['hotend_temp'] - self.config['target_hotend'])
        
        # Add some temperature jitter for realism
        self.config['hotend_temp'] += random.uniform(-0.3, 0.3)
        
        # Bed temperature simulation (slower changes)
        if abs(self.config['bed_temp'] - self.config['target_bed']) > 0.5:
            if self.config['bed_temp'] < self.config['target_bed']:
                # Heating up (slower)
                self.config['bed_temp'] += min(2.0, self.config['target_bed'] - self.config['bed_temp'])
            else:
                # Cooling down (much slower)
                self.config['bed_temp'] -= min(1.0, self.config['bed_temp'] - self.config['target_bed'])
        
        # Add some temperature jitter for realism
        self.config['bed_temp'] += random.uniform(-0.1, 0.1)
    
    def update_config_from_ui(self):
        """Update configuration from UI elements"""
        self.config['printer_name'] = self.printer_name_var.get()
        self.config['serial_number'] = self.serial_number_var.get()
        self.config['machine_type'] = self.machine_type_var.get()
        self.config['firmware_version'] = self.firmware_version_var.get()
        self.config['ip_address'] = self.ip_address_var.get()
        self.config['print_status'] = self.print_status_var.get().lower()
        self.config['print_progress'] = int(self.progress_var.get())
        self.config['led_state'] = self.led_var.get()
        self.config['filament_runout_sensor'] = self.filament_sensor_var.get()
        self.config['current_file'] = self.current_file_var.get()
        
        # Update progress label
        self.progress_label.config(text=f"{self.config['print_progress']}%")
        
        # Update emulator server if IP address changed
        if self.discovery_server or self.tcp_server:
            self.stop_servers()
            self.start_servers()
    
    def show_temp_dialog(self, heater_type):
        """Show dialog to set temperature targets"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Set {heater_type.capitalize()} Temperature")
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Target Temperature (°C):").pack(pady=(10, 5))
        
        temp_var = tk.StringVar(value=str(int(self.config[f'target_{heater_type}'])))
        temp_entry = ttk.Entry(dialog, textvariable=temp_var, width=10)
        temp_entry.pack(pady=5)
        temp_entry.select_range(0, tk.END)
        temp_entry.focus()
        
        def on_ok():
            try:
                new_temp = float(temp_var.get())
                if 0 <= new_temp <= 300:  # Safe temperature range
                    self.config[f'target_{heater_type}'] = new_temp
                    dialog.destroy()
                else:
                    messagebox.showerror("Invalid Temperature", "Temperature must be between 0°C and 300°C.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")
        
        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        
        # Bind Enter key to OK button
        dialog.bind("<Return>", lambda e: on_ok())
    
    def browse_thumbnail(self):
        """Browse for thumbnail image file"""
        file_path = filedialog.askopenfilename(
            title="Select Thumbnail Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.thumbnail_path = file_path
            self.thumbnail_path_var.set(os.path.basename(file_path))
            self.log(f"Thumbnail file set to: {file_path}")
    
    def start_servers(self):
        """Start the discovery and TCP command servers"""
        try:
            # Update UI
            self.server_status_var.set("Server Status: Starting...")
            self.start_button.config(state=tk.DISABLED)
            
            # Start discovery server (UDP)
            self.discovery_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_server.bind(('0.0.0.0', 48899))
            threading.Thread(target=self.handle_discovery, daemon=True).start()
            
            # Start TCP command server
            self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_server.bind(('0.0.0.0', 8899))
            self.tcp_server.listen(5)
            threading.Thread(target=self.handle_tcp_connections, daemon=True).start()
            
            # Update UI
            self.server_status_var.set("Server Status: Running")
            self.stop_button.config(state=tk.NORMAL)
            
            self.log(f"Emulator services started on {self.config['ip_address']}")
            self.log(f"Discovery service running on UDP port 48899")
            self.log(f"TCP API service running on port 8899")
        except Exception as e:
            self.log(f"Error starting servers: {str(e)}")
            self.server_status_var.set(f"Server Status: Error - {str(e)}")
            self.start_button.config(state=tk.NORMAL)
    
    def stop_servers(self):
        """Stop all server threads"""
        try:
            # Stop discovery server
            if self.discovery_server:
                self.discovery_server.close()
                self.discovery_server = None
            
            # Close all client connections
            for client in self.tcp_clients:
                try:
                    client.close()
                except:
                    pass
            self.tcp_clients = []
            
            # Stop TCP server
            if self.tcp_server:
                self.tcp_server.close()
                self.tcp_server = None
            
            # Update UI
            self.server_status_var.set("Server Status: Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            self.log("Emulator services stopped")
        except Exception as e:
            self.log(f"Error stopping servers: {str(e)}")
    
    def handle_discovery(self):
        """Handle printer discovery UDP requests"""
        self.log("Discovery service started")
        
        # Get the primary network interface IP - our emulated printer will only be available on this IP
        emulator_ip = self.config['ip_address']
        self.log(f"Emulator will be discoverable only at IP: {emulator_ip}")
        
        try:
            while self.discovery_server:
                try:
                    # Wait for an incoming discovery packet
                    data, addr = self.discovery_server.recvfrom(1024)
                    
                    # Check if this is the expected discovery packet format
                    if not data.startswith(b'www.usr'):
                        continue
                    
                    # Log the discovery request
                    discovery_hex = binascii.hexlify(data).decode('ascii')
                    self.log(f"Discovery request from {addr[0]}:{addr[1]} - Data: {discovery_hex}")
                    
                    # Only respond from the primary network interface
                    # Determine the local IP we would use to reach this address
                    local_ip = None
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect((addr[0], 1))
                        local_ip = s.getsockname()[0]
                        s.close()
                    except:
                        pass
                    
                    # If we're responding with an IP different from our configured one, skip it
                    if local_ip and local_ip != emulator_ip:
                        self.log(f"Skipping response from {local_ip} (not our primary emulator IP {emulator_ip})")
                        continue
                    
                    # Create the discovery response packet
                    # Based on the FlashForgePrinterDiscovery.parsePrinterResponse method
                    response = bytearray(0xC4)  # Response length 196 bytes
                    
                    # Set printer name at offset 0x00 (32 bytes)
                    name_bytes = self.config['printer_name'].encode('ascii')
                    response[0:len(name_bytes)] = name_bytes
                    
                    # Set serial number at offset 0x92 (32 bytes)
                    serial_bytes = self.config['serial_number'].encode('ascii')
                    response[0x92:0x92+len(serial_bytes)] = serial_bytes
                    
                    # Send the response back
                    self.discovery_server.sendto(response, addr)
                    self.log(f"Sent discovery response to {addr[0]}:{addr[1]} from {emulator_ip}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.discovery_server:  # Only log if still running
                        self.log(f"Discovery error: {str(e)}")
        except Exception as e:
            self.log(f"Discovery service error: {str(e)}")
        
        self.log("Discovery service stopped")
    
    def handle_tcp_connections(self):
        """Accept and handle TCP connections for printer commands"""
        self.log("TCP server started")
        
        try:
            while self.tcp_server:
                try:
                    # Accept a new connection
                    client_socket, addr = self.tcp_server.accept()
                    client_socket.settimeout(60)  # 60 second timeout
                    self.tcp_clients.append(client_socket)
                    
                    # Start a new thread to handle this client
                    threading.Thread(
                        target=self.handle_client_commands,
                        args=(client_socket, addr),
                        daemon=True
                    ).start()
                    
                    self.log(f"New client connected: {addr[0]}:{addr[1]}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.tcp_server:  # Only log if still running
                        self.log(f"TCP server error: {str(e)}")
        except Exception as e:
            self.log(f"TCP server error: {str(e)}")
        
        self.log("TCP server stopped")
    
    def handle_client_commands(self, client_socket, addr):
        """Handle commands from a specific client"""
        try:
            while True:
                # Receive command
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Parse command
                command = data.decode('ascii', errors='replace').strip()
                self.log(f"Received command from {addr[0]}: {command}")
                
                # Process command and get response
                response = self.process_command(command)
                
                # Send response
                if isinstance(response, str):
                    client_socket.sendall(response.encode('ascii'))
                else:
                    # Binary response
                    client_socket.sendall(response)
                
                if isinstance(response, str):
                    self.log(f"Sent response: {response[:100]}")
                else:
                    self.log(f"Sent binary response: {len(response)} bytes")
        except Exception as e:
            self.log(f"Error handling client {addr[0]}: {str(e)}")
        finally:
            # Clean up
            try:
                client_socket.close()
                if client_socket in self.tcp_clients:
                    self.tcp_clients.remove(client_socket)
            except:
                pass
            
            self.log(f"Client disconnected: {addr[0]}:{addr[1]}")
    
    def process_command(self, command):
        """Process a command and return the appropriate response"""
        # Handle login/logout
        if command == "~M601 S1":  # Login
            return "CMD M601 Received.\nControl Success.\nok\n"
        
        if command == "~M602":  # Logout
            return "CMD M602 Received.\nControl Release.\nok\n"
        
        # Status commands
        if command == "~M115":  # Info Status
            return self.get_printer_info_response()
        
        if command == "~M105":  # Temperature
            return self.get_temperature_response()
        
        if command == "~M119":  # Endstop status
            return self.get_endstop_response()
        
        if command == "~M27":  # Print status
            return self.get_print_status_response()
        
        if command == "~M114":  # Position
            return self.get_position_response()
        
        # LED control
        if command.startswith("~M146"):  # LED control
            if "r255 g255 b255" in command:
                self.config['led_state'] = True
            elif "r0 g0 b0" in command:
                self.config['led_state'] = False
            return "CMD M146 Received.\nok\n"
        
        # Filament runout sensor
        if command == "~M405":  # Runout sensor on
            self.config['filament_runout_sensor'] = True
            return "CMD M405 Received.\nok\n"
        
        if command == "~M406":  # Runout sensor off
            self.config['filament_runout_sensor'] = False
            return "CMD M406 Received.\nok\n"
        
        # Home axes
        if command == "~G28":  # Home axes
            # Reset position
            self.config['position'] = {"x": 0.0, "y": 0.0, "z": 0.0}
            return "CMD G28 Received.\nok\n"
        
        # Print control
        if command == "~M24":  # Resume print
            if self.config['print_status'] == 'paused':
                self.config['print_status'] = 'printing'
            return "CMD M24 Received.\nok\n"
        
        if command == "~M25":  # Pause print
            if self.config['print_status'] == 'printing':
                self.config['print_status'] = 'paused'
            return "CMD M25 Received.\nok\n"
        
        if command == "~M26":  # Stop print
            if self.config['print_status'] in ['printing', 'paused']:
                self.config['print_status'] = 'idle'
                self.config['print_progress'] = 0
            return "CMD M26 Received.\nok\n"
        
        # Temperature settings
        if command.startswith("~M104"):  # Set extruder temp
            parts = command.split()
            if len(parts) > 1 and parts[1].startswith("S"):
                try:
                    temp = float(parts[1][1:])
                    self.config['target_hotend'] = temp
                except ValueError:
                    pass
            return "CMD M104 Received.\nok\n"
        
        if command.startswith("~M140"):  # Set bed temp
            parts = command.split()
            if len(parts) > 1 and parts[1].startswith("S"):
                try:
                    temp = float(parts[1][1:])
                    self.config['target_bed'] = temp
                except ValueError:
                    pass
            return "CMD M140 Received.\nok\n"
        
        if command.startswith("~M109"):  # Wait for extruder temp
            parts = command.split()
            if len(parts) > 1 and parts[1].startswith("S"):
                try:
                    temp = float(parts[1][1:])
                    self.config['target_hotend'] = temp
                    self.config['hotend_temp'] = temp  # Immediately set temp for testing
                except ValueError:
                    pass
            return "CMD M109 Received.\nok\n"
        
        if command.startswith("~M190"):  # Wait for bed temp
            parts = command.split()
            if len(parts) > 1 and parts[1].startswith("S"):
                try:
                    temp = float(parts[1][1:])
                    self.config['target_bed'] = temp
                    self.config['bed_temp'] = temp  # Immediately set temp for testing
                except ValueError:
                    pass
            return "CMD M190 Received.\nok\n"
        
        # File listing
        if command == "~M661":  # List files
            return self.get_file_list_response()
        
        # Thumbnail
        if command.startswith("~M662"):  # Get thumbnail
            # Extract the filename from the command if present
            file_path = ""
            parts = command.split()
            if len(parts) > 1:
                file_path = parts[1]
            
            return self.get_thumbnail_response(file_path)
        
        # Movement
        if command.startswith("~G1"):  # Move
            # Parse X, Y, Z coordinates if present
            position = self.config['position'].copy()
            for axis in ['X', 'Y', 'Z']:
                match = re.search(f"{axis}([-+]?[0-9]*\.?[0-9]+)", command)
                if match:
                    position[axis.lower()] = float(match.group(1))
            self.config['position'] = position
            return "CMD G1 Received.\nok\n"
        
        # Default response for unhandled commands
        return f"CMD {command[1:]} Received.\nok\n"
    
    def get_printer_info_response(self):
        """Generate printer info response (M115)"""
        firmware = self.config['firmware_version']
        machine_type = self.config['machine_type']
        # Format matches the FlashForge protocol
        response = (
            f"CMD M115 Received.\n"
            f"Machine Type: {machine_type}\n"
            f"Machine Name: {self.config['printer_name']}\n"
            f"Firmware: {firmware}\n"
            f"SN: {self.config['serial_number']}\n"
            f"X: 200 Y: 200 Z: 200\n"
            f"Tool Count: 1\n"
            f"ok\n"
        )
        return response
    
    def get_temperature_response(self):
        """Generate temperature response (M105)"""
        hotend_temp = self.config['hotend_temp']
        hotend_target = self.config['target_hotend']
        bed_temp = self.config['bed_temp']
        bed_target = self.config['target_bed']
        
        response = (
            f"CMD M105 Received.\n"
            f"T0:{hotend_temp:.1f}/{hotend_target:.1f} T1:0.0/0.0 B:{bed_temp:.1f}/{bed_target:.1f}\n"
            f"ok\n"
        )
        return response
    
    def get_endstop_response(self):
        """Generate endstop status response (M119)"""
        # Set machine status based on print state
        machine_status = "READY"  # Default
        move_mode = "READY"      # Default
        
        # Map printer status to machine status and move mode
        status_map = {
            "printing": ("BUILDING_FROM_SD", "MOVING"),
            "paused": ("PAUSED", "PAUSED"),
            "completed": ("BUILDING_COMPLETED", "READY"),
            "failed": ("READY", "READY"),
            "idle": ("READY", "READY")
        }
        
        if self.config['print_status'].lower() in status_map:
            machine_status, move_mode = status_map[self.config['print_status'].lower()]
        
        # Current file - only include if printing/paused/completed
        current_file = ""
        if self.config['print_status'].lower() in ["printing", "paused", "completed"]:
            current_file = self.config['current_file']
        
        # All endstops open in normal operation
        response = (
            f"CMD M119 Received.\n"
            f"Endstop: X-min: 0 Y-min: 0 Z-min: 0\n"
            f"MachineStatus: {machine_status}\n"
            f"MoveMode: {move_mode}\n"
            f"Status: S:0 L:0 J:0 F:0\n"
            f"LED: {1 if self.config['led_state'] else 0}\n"
            f"CurrentFile: {current_file}\n"
            f"ok\n"
        )
        return response
    
    def get_print_status_response(self):
        """Generate print status response (M27)"""
        status_code = {"idle": 0, "printing": 1, "paused": 2, "completed": 3, "failed": 4}
        status = status_code.get(self.config['print_status'].lower(), 0)
        progress = self.config['print_progress']
        
        # Calculate layer information based on progress
        # Use a reasonable total layer count (e.g., 100 for a typical print)
        total_layers = 100
        current_layer = max(1, int(progress * total_layers / 100))
        
        response = (
            f"CMD M27 Received.\n"
            f"SD printing byte {progress}/100\n"
            f"Layer: {current_layer}/{total_layers}\n"
            f"Status: S:{status} L:0 J:0 F:0\n"
            f"ok\n"
        )
        return response
    
    def get_position_response(self):
        """Generate position response (M114)"""
        x = self.config['position']['x']
        y = self.config['position']['y']
        z = self.config['position']['z']
        
        response = (
            f"CMD M114 Received.\n"
            f"X:{x} Y:{y} Z:{z} A:0 B:0\n"
            f"ok\n"
        )
        return response
    
    def get_file_list_response(self):
        """Generate file list response (M661)"""
        file_list = "\n".join([f"/data/{filename}" for filename in self.virtual_files])
        response = (
            f"CMD M661 Received.\n"
            f"D{{::{file_list}::\n"
            f"ok\n"
        )
        return response
    
    def get_thumbnail_response(self, file_path=""):
        """Generate thumbnail response (M662) - binary response"""
        try:
            # Check if we have a valid thumbnail path
            if not self.thumbnail_path or not os.path.exists(self.thumbnail_path):
                self.log("Warning: No thumbnail file available")
                return f"CMD M662 Received.\nok\n".encode('ascii')
            
            # Only provide thumbnail if we're in printing/paused/completed state
            if self.config['print_status'].lower() not in ['printing', 'paused', 'completed']:
                self.log("Not in printing state - no thumbnail available")
                return f"CMD M662 Received.\nok\n".encode('ascii')
            
            # Log the file path being requested
            self.log(f"Thumbnail requested for: {file_path}")
            
            # Read the thumbnail file
            with open(self.thumbnail_path, 'rb') as f:
                png_data = f.read()
            
            # Very simple response format: text header + PNG data
            header = f"CMD M662 Received.\nok\n".encode('ascii')
            
            # Combine header and PNG data
            response = bytearray()
            response.extend(header)
            response.extend(png_data)
            
            self.log(f"Sending thumbnail response ({len(response)} bytes)")
            return response
        except Exception as e:
            self.log(f"Error preparing thumbnail: {str(e)}")
            return f"CMD M662 Received.\nError: {str(e)}\nok\n".encode('ascii')

def main():
    # Create the standard thumbnail first
    create_standard_thumbnail()
    
    # Start the UI
    root = tk.Tk()
    app = FlashForgeEmulator(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_servers(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()
