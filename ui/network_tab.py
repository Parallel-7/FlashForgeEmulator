"""
Network tab UI for FlashForge Emulator
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import random

class NetworkTab:
    """Network tab UI component with latency and failure simulation settings"""
    
    def __init__(self, parent, emulator, on_update_callback=None):
        self.parent = parent
        self.emulator = emulator
        self.on_update_callback = on_update_callback
        
        # Initialize network simulation settings if not present
        if 'network_simulation' not in self.emulator.config:
            self.emulator.config['network_simulation'] = {
                'latency': 0,           # Delay in milliseconds
                'latency_enabled': False,
                'failure_rate': 0,      # Percentage chance of failure (0-100)
                'failures_enabled': False,
                'failure_type': 'drop'  # 'drop', 'timeout', 'error'
            }
        
        # Create the UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the network tab UI"""
        # Latency Simulation Frame
        latency_frame = ttk.LabelFrame(self.parent, text="Response Latency Simulation")
        latency_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        # Enable latency simulation
        latency_enable_frame = ttk.Frame(latency_frame)
        latency_enable_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.latency_enabled_var = tk.BooleanVar(value=self.emulator.config['network_simulation']['latency_enabled'])
        ttk.Checkbutton(latency_enable_frame, text="Enable Latency Simulation", 
                       variable=self.latency_enabled_var, 
                       command=self.update_latency_settings).pack(side=tk.LEFT)
        
        # Latency slider
        latency_slider_frame = ttk.Frame(latency_frame)
        latency_slider_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(latency_slider_frame, text="Latency:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.latency_var = tk.IntVar(value=self.emulator.config['network_simulation']['latency'])
        latency_slider = ttk.Scale(latency_slider_frame, from_=0, to=5000, 
                                  variable=self.latency_var, orient=tk.HORIZONTAL,
                                  command=lambda e: self.update_latency_value())
        latency_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.latency_label = ttk.Label(latency_slider_frame, text=f"{self.latency_var.get()} ms", width=8)
        self.latency_label.pack(side=tk.LEFT)
        
        # Apply button for latency
        ttk.Button(latency_frame, text="Apply Latency Settings", 
                  command=self.update_latency_settings).pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Connection Failures Frame
        failures_frame = ttk.LabelFrame(self.parent, text="Connection Failures Simulation")
        failures_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        # Enable failures
        failures_enable_frame = ttk.Frame(failures_frame)
        failures_enable_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.failures_enabled_var = tk.BooleanVar(value=self.emulator.config['network_simulation']['failures_enabled'])
        ttk.Checkbutton(failures_enable_frame, text="Enable Connection Failures", 
                       variable=self.failures_enabled_var, 
                       command=self.update_failure_settings).pack(side=tk.LEFT)
        
        # Failure type
        failure_type_frame = ttk.Frame(failures_frame)
        failure_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(failure_type_frame, text="Failure Type:").pack(side=tk.LEFT, padx=(0, 10))
        self.failure_type_var = tk.StringVar(value=self.emulator.config['network_simulation']['failure_type'])
        failure_type_combo = ttk.Combobox(failure_type_frame, textvariable=self.failure_type_var, width=15)
        failure_type_combo['values'] = ('drop', 'timeout', 'error')
        failure_type_combo.pack(side=tk.LEFT, padx=5)
        failure_type_combo.bind('<<ComboboxSelected>>', lambda e: self.update_failure_type())
        
        # Explain the failure types
        failure_desc_frame = ttk.Frame(failures_frame)
        failure_desc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        failure_descriptions = (
            "drop: Close the connection without response\n"
            "timeout: Start sending data but never finish\n"
            "error: Return an error response"
        )
        ttk.Label(failure_desc_frame, text=failure_descriptions, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Failure rate slider
        failure_slider_frame = ttk.Frame(failures_frame)
        failure_slider_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(failure_slider_frame, text="Failure Rate:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.failure_rate_var = tk.IntVar(value=self.emulator.config['network_simulation']['failure_rate'])
        failure_slider = ttk.Scale(failure_slider_frame, from_=0, to=100, 
                                  variable=self.failure_rate_var, orient=tk.HORIZONTAL,
                                  command=lambda e: self.update_failure_value())
        failure_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.failure_label = ttk.Label(failure_slider_frame, text=f"{self.failure_rate_var.get()}%", width=8)
        self.failure_label.pack(side=tk.LEFT)
        
        # Apply button for failures
        ttk.Button(failures_frame, text="Apply Failure Settings", 
                  command=self.update_failure_settings).pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Network Simulation Status
        status_frame = ttk.LabelFrame(self.parent, text="Simulation Status")
        status_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        status_info_frame = ttk.Frame(status_frame)
        status_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(status_info_frame, text="Current Network Simulation:").pack(side=tk.LEFT, padx=(0, 10))
        self.status_var = tk.StringVar(value=self.get_simulation_status())
        ttk.Label(status_info_frame, textvariable=self.status_var, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        
        # Help text
        help_frame = ttk.Frame(self.parent)
        help_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        help_text = (
            "These settings allow you to simulate network conditions for testing client applications. "
            "Changes will apply to new connections after the server is restarted."
        )
        ttk.Label(help_frame, text=help_text, wraplength=500, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Needs server restart note
        restart_note = "Note: Server must be restarted for changes to take effect"
        ttk.Label(help_frame, text=restart_note, font=("Segoe UI", 9, "italic"), 
                 foreground="red").pack(anchor=tk.W, pady=(5, 0))
        
        # Test button
        test_button_frame = ttk.Frame(help_frame)
        test_button_frame.pack(anchor=tk.E, pady=10)
        ttk.Button(test_button_frame, text="Disable All Simulations", 
                  command=self.disable_all_simulations, style="secondary.TButton").pack(side=tk.LEFT, padx=5)
    
    def update_ui(self):
        """Update UI elements based on current configuration"""
        # Update latency controls
        self.latency_enabled_var.set(self.emulator.config['network_simulation']['latency_enabled'])
        self.latency_var.set(self.emulator.config['network_simulation']['latency'])
        self.update_latency_label()
        
        # Update failure controls
        self.failures_enabled_var.set(self.emulator.config['network_simulation']['failures_enabled'])
        self.failure_type_var.set(self.emulator.config['network_simulation']['failure_type'])
        self.failure_rate_var.set(self.emulator.config['network_simulation']['failure_rate'])
        self.update_failure_label()
        
        # Update simulation status text
        self.status_var.set(self.get_simulation_status())
    
    def update_latency_label(self):
        """Update the latency value label"""
        self.latency_label.config(text=f"{self.latency_var.get()} ms")
    
    def update_failure_label(self):
        """Update the failure rate value label"""
        self.failure_label.config(text=f"{self.failure_rate_var.get()}%")
        
    def update_latency_value(self):
        """Update the latency value and label when slider is moved"""
        latency_value = self.latency_var.get()
        self.emulator.config['network_simulation']['latency'] = latency_value
        self.latency_label.config(text=f"{latency_value} ms")
    
    def update_failure_value(self):
        """Update the failure rate value and label when slider is moved"""
        failure_rate = self.failure_rate_var.get()
        self.emulator.config['network_simulation']['failure_rate'] = failure_rate
        self.failure_label.config(text=f"{failure_rate}%")
    
    def update_failure_type(self):
        """Update the failure type when combobox selection changes"""
        failure_type = self.failure_type_var.get()
        self.emulator.config['network_simulation']['failure_type'] = failure_type
        # Optionally log the change
        if self.on_update_callback:
            self.on_update_callback(f"Failure type changed to: {failure_type}")
    
    def update_latency_settings(self):
        """Apply the latency simulation settings"""
        self.emulator.config['network_simulation']['latency_enabled'] = self.latency_enabled_var.get()
        self.emulator.config['network_simulation']['latency'] = self.latency_var.get()
        
        # Update status
        self.status_var.set(self.get_simulation_status())
        
        # Notify about changes
        if self.on_update_callback:
            if self.latency_enabled_var.get():
                self.on_update_callback(f"Latency simulation enabled with {self.latency_var.get()} ms delay")
            else:
                self.on_update_callback("Latency simulation disabled")
    
    def update_failure_settings(self):
        """Apply the connection failure simulation settings"""
        self.emulator.config['network_simulation']['failures_enabled'] = self.failures_enabled_var.get()
        self.emulator.config['network_simulation']['failure_rate'] = self.failure_rate_var.get()
        self.emulator.config['network_simulation']['failure_type'] = self.failure_type_var.get()
        
        # Update status
        self.status_var.set(self.get_simulation_status())
        
        # Notify about changes
        if self.on_update_callback:
            if self.failures_enabled_var.get():
                self.on_update_callback(
                    f"Connection failures simulation enabled - "
                    f"Type: {self.failure_type_var.get()}, Rate: {self.failure_rate_var.get()}%"
                )
            else:
                self.on_update_callback("Connection failures simulation disabled")
    
    def disable_all_simulations(self):
        """Disable all network simulations"""
        self.latency_enabled_var.set(False)
        self.failures_enabled_var.set(False)
        self.update_latency_settings()
        self.update_failure_settings()
        
        if self.on_update_callback:
            self.on_update_callback("All network simulations disabled")
    
    def get_simulation_status(self):
        """Get a text description of the current simulation status"""
        sim_config = self.emulator.config['network_simulation']
        status_parts = []
        
        if sim_config['latency_enabled']:
            status_parts.append(f"Latency: {sim_config['latency']} ms")
        
        if sim_config['failures_enabled']:
            status_parts.append(f"Failures: {sim_config['failure_type']} at {sim_config['failure_rate']}%")
        
        if not status_parts:
            return "No simulations active"
        
        return ", ".join(status_parts)
