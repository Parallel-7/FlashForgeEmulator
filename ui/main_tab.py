"""
Main tab UI for FlashForge Emulator
"""
import tkinter as tk
from tkinter import scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime

class MainTab:
    """Main tab UI component with logs and server controls"""
    
    def __init__(self, parent, emulator, on_update_callback=None):
        self.parent = parent
        self.emulator = emulator
        self.on_update_callback = on_update_callback
        
        # Debounce timer for config changes
        self.restart_timer = None
        
        # Create the UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main tab UI"""
        # Log Frame
        log_frame = ttk.LabelFrame(self.parent, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create log display
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=18)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Control buttons for log
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(log_control_frame, text="Clear Logs", style="secondary.TButton", 
                   command=self.clear_logs).pack(side=tk.RIGHT, padx=5)
        
        # Server control frame
        server_frame = ttk.LabelFrame(self.parent, text="Server Settings")
        server_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Network interface selection
        network_frame = ttk.Frame(server_frame)
        network_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Label(network_frame, text="Network Interface:").pack(side=tk.LEFT, padx=(5, 5))
        self.ip_address_var = tk.StringVar(value=self.emulator.config["ip_address"])
        ip_combo = ttk.Combobox(network_frame, textvariable=self.ip_address_var, width=25)
        ip_combo['values'] = [ip for _, ip in self.emulator.network_interfaces]
        ip_combo.pack(side=tk.LEFT, padx=5)
        ip_combo.bind('<<ComboboxSelected>>', lambda e: self.update_config_from_ui())
        
        # Discovery service option
        self.discovery_enabled_var = tk.BooleanVar(value=self.emulator.config.get("discovery_enabled", True))
        discovery_check = ttk.Checkbutton(network_frame, text="Enable Discovery Service", 
                                          variable=self.discovery_enabled_var, 
                                          command=self.update_config_from_ui)
        discovery_check.pack(side=tk.LEFT, padx=10)
        
        # Server status and buttons
        server_info_frame = ttk.Frame(server_frame)
        server_info_frame.pack(fill=tk.X, expand=True, pady=5, padx=5)
        
        self.server_status_var = tk.StringVar(value="Server Status: Stopped")
        status_label = ttk.Label(server_info_frame, textvariable=self.server_status_var, font=("Segoe UI", 10, "bold"))
        status_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Button frame on the right
        button_container = ttk.Frame(server_info_frame)
        button_container.pack(side=tk.RIGHT, padx=5)
        
        self.stop_button = ttk.Button(button_container, text="Stop Server", style="danger.TButton", 
                                     command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5)
        
        self.start_button = ttk.Button(button_container, text="Start Server", style="success.TButton", 
                                      command=self.start_server)
        self.start_button.pack(side=tk.RIGHT, padx=5)
    
    def log(self, message):
        """Add a timestamped entry to the log display"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Return the log entry for potential additional handling
        return log_entry
    
    def clear_logs(self):
        """Clear all log entries"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_ui(self):
        """Update UI elements from emulator state"""
        # Update server status based on emulator state
        if self.emulator.server.is_running:
            # Set status text including discovery service state
            discovery_status = "Discovery: On" if self.emulator.config.get('discovery_enabled', True) else "Discovery: Off"
            self.server_status_var.set(f"Server Status: Running ({discovery_status})")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.server_status_var.set("Server Status: Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
        # Update discovery checkbox state
        self.discovery_enabled_var.set(self.emulator.config.get('discovery_enabled', True))
    
    def update_config_from_ui(self):
        """Update emulator configuration from UI elements"""
        # Check if IP or discovery settings changed
        ip_changed = self.emulator.config['ip_address'] != self.ip_address_var.get()
        discovery_changed = self.emulator.config.get('discovery_enabled', True) != self.discovery_enabled_var.get()
        
        # Update the configuration
        self.emulator.config['ip_address'] = self.ip_address_var.get()
        self.emulator.config['discovery_enabled'] = self.discovery_enabled_var.get()
        
        # Call the update callback if provided
        message = "Network settings updated"
        if discovery_changed:
            state = "enabled" if self.discovery_enabled_var.get() else "disabled"
            message = f"Discovery service {state}"
        
        if self.on_update_callback:
            self.on_update_callback(message)
        
        # Update emulator server if running and settings changed
        if self.emulator.server.is_running and (ip_changed or discovery_changed):
            self.schedule_server_restart()
    
    def start_server(self):
        """Start the emulator servers"""
        if self.emulator.start_server():
            self.server_status_var.set("Server Status: Running")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
    
    def stop_server(self):
        """Stop the emulator servers"""
        if self.emulator.stop_server():
            self.server_status_var.set("Server Status: Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def schedule_server_restart(self):
        """Schedule a server restart with debouncing (1 second delay)"""
        # Cancel any pending restart
        if self.restart_timer:
            self.parent.after_cancel(self.restart_timer)
            self.restart_timer = None
            
        # Schedule a new restart after 1 second of inactivity
        self.restart_timer = self.parent.after(1000, self.restart_server)
    
    def restart_server(self):
        """Restart the emulator server after debounce delay"""
        self.restart_timer = None
        if self.on_update_callback:
            self.on_update_callback("Restarting emulator services to apply configuration changes...")
        
        if self.emulator.restart_server():
            self.server_status_var.set("Server Status: Running")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
