"""
Printer Details tab UI for FlashForge Emulator
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class PrinterDetailsTab:
    """Printer Details tab UI component"""
    
    def __init__(self, parent, emulator, on_update_callback=None):
        self.parent = parent
        self.emulator = emulator
        self.on_update_callback = on_update_callback
        
        # Debounce timer for config changes
        self.restart_timer = None
        
        # Create the UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the printer details tab UI"""
        # Main config frame
        config_frame = ttk.LabelFrame(self.parent, text="Printer Configuration")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create a grid layout for printer config
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Row 0: Printer Name
        ttk.Label(config_grid, text="Printer Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.printer_name_var = tk.StringVar(value=self.emulator.config["printer_name"])
        ttk.Entry(config_grid, textvariable=self.printer_name_var, width=30).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)

        # Row 1: Machine Type
        ttk.Label(config_grid, text="Machine Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.machine_type_var = tk.StringVar(value=self.emulator.config["machine_type"])
        ttk.Entry(config_grid, textvariable=self.machine_type_var, width=30).grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)

        # Row 2: Serial Number
        ttk.Label(config_grid, text="Serial Number:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.serial_number_var = tk.StringVar(value=self.emulator.config["serial_number"])
        ttk.Entry(config_grid, textvariable=self.serial_number_var, width=30).grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)

        # Row 3: Firmware Version
        ttk.Label(config_grid, text="Firmware Version:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.firmware_version_var = tk.StringVar(value=self.emulator.config["firmware_version"])
        ttk.Entry(config_grid, textvariable=self.firmware_version_var, width=30).grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Row 4: Printer Dimensions section header
        ttk.Label(config_grid, text="Printer Dimensions:", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(15, 5))
        
        # Row 5: X, Y, Z Dimensions
        dimensions_frame = ttk.Frame(config_grid)
        dimensions_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Add X dimension
        ttk.Label(dimensions_frame, text="X:").pack(side=tk.LEFT, padx=(0, 5))
        self.x_dimension_var = tk.StringVar(value=str(self.emulator.config.get("x_dimension", 200)))
        ttk.Entry(dimensions_frame, textvariable=self.x_dimension_var, width=5).pack(side=tk.LEFT, padx=(0, 10))

        # Add Y dimension
        ttk.Label(dimensions_frame, text="Y:").pack(side=tk.LEFT, padx=(10, 5))
        self.y_dimension_var = tk.StringVar(value=str(self.emulator.config.get("y_dimension", 200)))
        ttk.Entry(dimensions_frame, textvariable=self.y_dimension_var, width=5).pack(side=tk.LEFT, padx=(0, 10))

        # Add Z dimension
        ttk.Label(dimensions_frame, text="Z:").pack(side=tk.LEFT, padx=(10, 5))
        self.z_dimension_var = tk.StringVar(value=str(self.emulator.config.get("z_dimension", 200)))
        ttk.Entry(dimensions_frame, textvariable=self.z_dimension_var, width=5).pack(side=tk.LEFT)
        
        # Row 6: Tool Count
        ttk.Label(config_grid, text="Tool Count:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.tool_count_var = tk.StringVar(value=str(self.emulator.config.get("tool_count", 1)))
        ttk.Spinbox(config_grid, textvariable=self.tool_count_var, from_=1, to=4, width=5).grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Apply button at the bottom
        apply_frame = ttk.Frame(config_frame)
        apply_frame.pack(fill=tk.X, pady=10, padx=10)
        ttk.Button(apply_frame, text="Apply Changes", style="primary.TButton", 
                   command=self.apply_changes).pack(side=tk.RIGHT)
        
        # Configure grid columns
        config_grid.columnconfigure(1, weight=1)
    
    def update_ui(self):
        """Update UI elements from emulator state"""
        # No dynamic updates needed for this tab
        pass
    
    def update_config_field(self, field, value):
        """Update a specific configuration field with debouncing"""
        if field in self.emulator.config:
            old_value = self.emulator.config[field]
            if old_value != value:  # Only update if changed
                self.emulator.config[field] = value
                
                if self.on_update_callback:
                    self.on_update_callback(f"Updated {field} to: {value}")
    
    def apply_changes(self):
        """Apply all changes to the emulator configuration"""
        # Update all text fields
        try:
            # Update basic info fields
            self.emulator.config['printer_name'] = self.printer_name_var.get()
            self.emulator.config['machine_type'] = self.machine_type_var.get()
            self.emulator.config['serial_number'] = self.serial_number_var.get()
            self.emulator.config['firmware_version'] = self.firmware_version_var.get()

            # Update dimensions and tool count
            x = int(self.x_dimension_var.get())
            y = int(self.y_dimension_var.get())
            z = int(self.z_dimension_var.get())
            tool_count = int(self.tool_count_var.get())

            self.emulator.config['x_dimension'] = x
            self.emulator.config['y_dimension'] = y
            self.emulator.config['z_dimension'] = z
            self.emulator.config['tool_count'] = tool_count

            # Auto-save configuration
            self.emulator.save_config_to_json()

            if self.on_update_callback:
                self.on_update_callback("Printer details updated and saved")

            # Restart the server if running to apply changes
            if self.emulator.server.is_running:
                self.schedule_server_restart()

        except ValueError:
            # Handle invalid input
            if self.on_update_callback:
                self.on_update_callback("Error: Please enter valid numbers for dimensions and tool count")
    
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
        self.emulator.restart_server()
