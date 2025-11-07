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

        # Protocol Mode Selection (NEW)
        protocol_frame = ttk.Frame(server_frame)
        protocol_frame.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(protocol_frame, text="Protocol Mode:").pack(side=tk.LEFT, padx=(5, 5))
        self.protocol_mode_var = tk.StringVar(value="Dual_Mode")
        protocol_combo = ttk.Combobox(protocol_frame, textvariable=self.protocol_mode_var,
                                     values=["TCP_Only", "HTTP_Only", "Dual_Mode"],
                                     state="readonly", width=15)
        protocol_combo.pack(side=tk.LEFT, padx=5)
        protocol_combo.bind('<<ComboboxSelected>>', self.on_protocol_mode_changed)

        ttk.Label(protocol_frame, text="Printer Mode:").pack(side=tk.LEFT, padx=(20, 5))
        self.printer_mode_var = tk.StringVar(value="AD5X")
        printer_combo = ttk.Combobox(protocol_frame, textvariable=self.printer_mode_var,
                                   values=["5M", "5M_Pro", "AD5X"],
                                   state="readonly", width=12)
        printer_combo.pack(side=tk.LEFT, padx=5)
        printer_combo.bind('<<ComboboxSelected>>', self.on_printer_mode_changed)
        
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
        
        # Server status and buttons (ENHANCED)
        server_info_frame = ttk.Frame(server_frame)
        server_info_frame.pack(fill=tk.X, expand=True, pady=5, padx=5)

        # Status display
        status_frame = ttk.Frame(server_info_frame)
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.tcp_status_var = tk.StringVar(value="TCP Server: Stopped")
        tcp_status = ttk.Label(status_frame, textvariable=self.tcp_status_var, font=("Segoe UI", 9, "bold"))
        tcp_status.pack(anchor=tk.W)

        self.http_status_var = tk.StringVar(value="HTTP Server: Stopped")
        http_status = ttk.Label(status_frame, textvariable=self.http_status_var, font=("Segoe UI", 9, "bold"))
        http_status.pack(anchor=tk.W)

        # Button frame on the right
        button_container = ttk.Frame(server_info_frame)
        button_container.pack(side=tk.RIGHT, padx=5)

        # Individual server controls
        tcp_btn_frame = ttk.Frame(button_container)
        tcp_btn_frame.pack(side=tk.TOP, pady=2)

        self.start_tcp_button = ttk.Button(tcp_btn_frame, text="Start TCP", style="success.TButton",
                                          command=self.start_tcp_server, width=12)
        self.start_tcp_button.pack(side=tk.LEFT, padx=2)

        self.stop_tcp_button = ttk.Button(tcp_btn_frame, text="Stop TCP", style="danger.TButton",
                                         command=self.stop_tcp_server, state=tk.DISABLED, width=12)
        self.stop_tcp_button.pack(side=tk.LEFT, padx=2)

        http_btn_frame = ttk.Frame(button_container)
        http_btn_frame.pack(side=tk.TOP, pady=2)

        self.start_http_button = ttk.Button(http_btn_frame, text="Start HTTP", style="info.TButton",
                                           command=self.start_http_server, width=12)
        self.start_http_button.pack(side=tk.LEFT, padx=2)

        self.stop_http_button = ttk.Button(http_btn_frame, text="Stop HTTP", style="warning.TButton",
                                          command=self.stop_http_server, state=tk.DISABLED, width=12)
        self.stop_http_button.pack(side=tk.LEFT, padx=2)
    
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
        # Update TCP server status
        if self.emulator.server.is_running:
            self.tcp_status_var.set("TCP Server: Running (8899)")
            self.start_tcp_button.config(state=tk.DISABLED)
            self.stop_tcp_button.config(state=tk.NORMAL)
        else:
            self.tcp_status_var.set("TCP Server: Stopped")
            self.start_tcp_button.config(state=tk.NORMAL)
            self.stop_tcp_button.config(state=tk.DISABLED)

        # Update HTTP server status (instant startup with async server)
        if hasattr(self.emulator, 'http_server') and self.emulator.http_server:
            if self.emulator.http_server.is_running:
                self.http_status_var.set("HTTP Server: Running (8898)")
                self.start_http_button.config(state=tk.DISABLED)
                self.stop_http_button.config(state=tk.NORMAL)
            else:
                state = self.emulator.http_server.get_state()
                if state == "error":
                    self.http_status_var.set("HTTP Server: Error")
                else:
                    self.http_status_var.set("HTTP Server: Stopped")
                self.start_http_button.config(state=tk.NORMAL)
                self.stop_http_button.config(state=tk.DISABLED)
        else:
            self.http_status_var.set("HTTP Server: Stopped")
            self.start_http_button.config(state=tk.NORMAL)
            self.stop_http_button.config(state=tk.DISABLED)

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

        # Auto-save configuration
        if ip_changed or discovery_changed:
            self.emulator.save_config_to_json()

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
        """Start the emulator servers (legacy method - use individual server methods)"""
        # This method is kept for compatibility but individual server methods should be used
        pass

    def stop_server(self):
        """Stop the emulator servers (legacy method - use individual server methods)"""
        # This method is kept for compatibility but individual server methods should be used
        pass
    
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
            # Update UI will be handled by the periodic update_ui() call
            pass

    # NEW ENHANCED SERVER METHODS
    def start_tcp_server(self):
        """Start the TCP emulator server (also starts HTTP server automatically)"""
        if self.emulator.start_server():
            self.tcp_status_var.set("TCP Server: Running (8899)")
            self.start_tcp_button.config(state=tk.DISABLED)
            self.stop_tcp_button.config(state=tk.NORMAL)
            if self.on_update_callback:
                self.on_update_callback("TCP and HTTP servers started successfully")
        else:
            if self.on_update_callback:
                self.on_update_callback("Failed to start TCP server")

    def stop_tcp_server(self):
        """Stop the TCP emulator server (also stops HTTP server automatically)"""
        if self.emulator.stop_server():
            self.tcp_status_var.set("TCP Server: Stopped")
            self.start_tcp_button.config(state=tk.NORMAL)
            self.stop_tcp_button.config(state=tk.DISABLED)
            if self.on_update_callback:
                self.on_update_callback("TCP and HTTP servers stopped")
        else:
            if self.on_update_callback:
                self.on_update_callback("Failed to stop TCP server")

    def start_http_server(self):
        """Start the HTTP API server"""
        # Pass http_tab logger if available
        http_logger = self._http_tab_ref if hasattr(self, '_http_tab_ref') else None
        if self.emulator.start_http_server(http_logger=http_logger):
            self.http_status_var.set("HTTP Server: Running (8898)")
            self.start_http_button.config(state=tk.DISABLED)
            self.stop_http_button.config(state=tk.NORMAL)
            if self.on_update_callback:
                self.on_update_callback("HTTP server started successfully")
        else:
            if self.on_update_callback:
                self.on_update_callback("Failed to start HTTP server")

    def stop_http_server(self):
        """Stop the HTTP API server"""
        if self.emulator.stop_http_server():
            self.http_status_var.set("HTTP Server: Stopped")
            self.start_http_button.config(state=tk.NORMAL)
            self.stop_http_button.config(state=tk.DISABLED)
            if self.on_update_callback:
                self.on_update_callback("HTTP server stopped")
        else:
            if self.on_update_callback:
                self.on_update_callback("Failed to stop HTTP server")

    def on_protocol_mode_changed(self, event=None):
        """Handle protocol mode change"""
        mode = self.protocol_mode_var.get()
        if self.on_update_callback:
            self.on_update_callback(f"Protocol mode changed to: {mode}")

        # Update UI based on mode
        if mode == "TCP_Only":
            self.start_http_button.config(state=tk.DISABLED)
            self.stop_http_button.config(state=tk.DISABLED)
        elif mode == "HTTP_Only":
            self.start_tcp_button.config(state=tk.DISABLED)
            self.stop_tcp_button.config(state=tk.DISABLED)
        else:  # Dual_Mode
            self.start_tcp_button.config(state=tk.NORMAL)
            self.start_http_button.config(state=tk.NORMAL)

    def on_printer_mode_changed(self, event=None):
        """Handle printer mode change"""
        mode = self.printer_mode_var.get()
        self.emulator.update_printer_mode(mode)

        # Auto-save configuration
        self.emulator.save_config_to_json()

        # Notify HTTP tab to refresh its display
        if hasattr(self, '_http_tab_ref') and self._http_tab_ref:
            self._http_tab_ref.refresh_mode_display()

        if self.on_update_callback:
            self.on_update_callback(f"Printer mode changed to: {mode}")

    def set_http_tab_reference(self, http_tab):
        """Set reference to HTTP tab for mode updates"""
        self._http_tab_ref = http_tab
