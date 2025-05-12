"""
Configuration tab UI for FlashForge Emulator
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class ConfigTab:
    """Configuration tab UI component"""
    
    def __init__(self, parent, emulator, on_update_callback=None):
        self.parent = parent
        self.emulator = emulator
        self.on_update_callback = on_update_callback
        
        # Debounce timer for config changes
        self.restart_timer = None
        self.config_changes = []
        
        # Create the UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the configuration tab UI"""
        # Configuration Frame
        config_frame = ttk.LabelFrame(self.parent, text="Printer Configuration")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)
        
        # Create a 2-column grid layout for printer config
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left column
        left_frame = ttk.Frame(config_grid)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        
        # Printer Name
        name_frame = ttk.Frame(left_frame)
        name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(name_frame, text="Printer Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.printer_name_var = tk.StringVar(value=self.emulator.config["printer_name"])
        self.printer_name_var.trace_add("write", lambda *args: self.update_config_field("printer_name", self.printer_name_var.get()))
        ttk.Entry(name_frame, textvariable=self.printer_name_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Machine Type
        machine_frame = ttk.Frame(left_frame)
        machine_frame.pack(fill=tk.X, pady=2)
        ttk.Label(machine_frame, text="Machine Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.machine_type_var = tk.StringVar(value=self.emulator.config["machine_type"])
        self.machine_type_var.trace_add("write", lambda *args: self.update_config_field("machine_type", self.machine_type_var.get()))
        ttk.Entry(machine_frame, textvariable=self.machine_type_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Right column
        right_frame = ttk.Frame(config_grid)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Serial Number
        serial_frame = ttk.Frame(right_frame)
        serial_frame.pack(fill=tk.X, pady=2)
        ttk.Label(serial_frame, text="Serial Number:").pack(side=tk.LEFT, padx=(0, 5))
        self.serial_number_var = tk.StringVar(value=self.emulator.config["serial_number"])
        self.serial_number_var.trace_add("write", lambda *args: self.update_config_field("serial_number", self.serial_number_var.get()))
        ttk.Entry(serial_frame, textvariable=self.serial_number_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Firmware Version
        firmware_frame = ttk.Frame(right_frame)
        firmware_frame.pack(fill=tk.X, pady=2)
        ttk.Label(firmware_frame, text="Firmware Version:").pack(side=tk.LEFT, padx=(0, 5))
        self.firmware_version_var = tk.StringVar(value=self.emulator.config["firmware_version"])
        self.firmware_version_var.trace_add("write", lambda *args: self.update_config_field("firmware_version", self.firmware_version_var.get()))
        ttk.Entry(firmware_frame, textvariable=self.firmware_version_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure grid to expand columns evenly
        config_grid.columnconfigure(0, weight=1)
        config_grid.columnconfigure(1, weight=1)
        
        # Network interface at the bottom
        network_frame = ttk.Frame(config_frame)
        network_frame.pack(fill=tk.X, pady=5)
        ttk.Label(network_frame, text="Network Interface:").pack(side=tk.LEFT, padx=(5, 5))
        self.ip_address_var = tk.StringVar(value=self.emulator.config["ip_address"])
        ip_combo = ttk.Combobox(network_frame, textvariable=self.ip_address_var, width=25)
        ip_combo['values'] = [ip for _, ip in self.emulator.network_interfaces]
        ip_combo.pack(side=tk.LEFT, padx=5)
        ip_combo.bind('<<ComboboxSelected>>', lambda e: self.update_config_from_ui())
        
        # Status frame
        status_frame = ttk.LabelFrame(self.parent, text="Printer Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)
        
        # Create grid layout for status
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid columns
        status_grid.columnconfigure(0, weight=1)
        status_grid.columnconfigure(1, weight=1)
        
        # Temperature section - left column
        temp_frame = ttk.Frame(status_grid)
        temp_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        
        # Hotend Temperature
        hotend_frame = ttk.Frame(temp_frame)
        hotend_frame.pack(fill=tk.X, pady=2)
        
        # Idle hotend temp control first (at the top)
        idle_hotend_frame = ttk.Frame(hotend_frame)
        idle_hotend_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E, padx=2, pady=2)
        ttk.Label(idle_hotend_frame, text="Idle Hotend Temp:").pack(side=tk.LEFT, padx=2)
        self.idle_hotend_var = tk.DoubleVar(value=self.emulator.idle_hotend_temp)
        idle_hotend_spin = ttk.Spinbox(idle_hotend_frame, from_=15, to=40, increment=0.5, width=5, textvariable=self.idle_hotend_var)
        idle_hotend_spin.pack(side=tk.LEFT, padx=2)
        ttk.Label(idle_hotend_frame, text="°C").pack(side=tk.LEFT)
        ttk.Button(idle_hotend_frame, text="Apply", command=self.update_idle_temps).pack(side=tk.LEFT, padx=5)
        
        # Current temperature display below idle temp
        ttk.Label(hotend_frame, text="Hotend Temperature:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.hotend_temp_var = tk.StringVar(value=f"{self.emulator.config['hotend_temp']:.1f}°C / {self.emulator.config['target_hotend']:.1f}°C")
        ttk.Label(hotend_frame, textvariable=self.hotend_temp_var).grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        
        # Hotend control buttons
        button_frame = ttk.Frame(hotend_frame)
        button_frame.grid(row=1, column=2, sticky=tk.E, padx=2, pady=2)
        ttk.Button(button_frame, text="Set", command=lambda: self.show_temp_dialog('hotend')).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset", command=lambda: self.reset_temp('hotend'), style="warning.TButton").pack(side=tk.LEFT, padx=2)
        
        # Bed Temperature - in same left column below hotend
        bed_frame = ttk.Frame(temp_frame)
        bed_frame.pack(fill=tk.X, pady=(5, 2))
        
        # Idle bed temp control first (at the top)
        idle_bed_frame = ttk.Frame(bed_frame)
        idle_bed_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E, padx=2, pady=2)
        ttk.Label(idle_bed_frame, text="Idle Bed Temp:").pack(side=tk.LEFT, padx=2)
        self.idle_bed_var = tk.DoubleVar(value=self.emulator.idle_bed_temp)
        idle_bed_spin = ttk.Spinbox(idle_bed_frame, from_=20, to=50, increment=0.5, width=5, textvariable=self.idle_bed_var)
        idle_bed_spin.pack(side=tk.LEFT, padx=2)
        ttk.Label(idle_bed_frame, text="°C").pack(side=tk.LEFT)
        ttk.Button(idle_bed_frame, text="Apply", command=self.update_idle_temps).pack(side=tk.LEFT, padx=5)
        
        # Current bed temperature display below idle temp
        ttk.Label(bed_frame, text="Bed Temperature:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.bed_temp_var = tk.StringVar(value=f"{self.emulator.config['bed_temp']:.1f}°C / {self.emulator.config['target_bed']:.1f}°C")
        ttk.Label(bed_frame, textvariable=self.bed_temp_var).grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        
        # Bed control buttons
        button_frame2 = ttk.Frame(bed_frame)
        button_frame2.grid(row=1, column=2, sticky=tk.E, padx=2, pady=2)
        ttk.Button(button_frame2, text="Set", command=lambda: self.show_temp_dialog('bed')).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame2, text="Reset", command=lambda: self.reset_temp('bed'), style="warning.TButton").pack(side=tk.LEFT, padx=2)
        
        # Print status section - right column
        print_frame = ttk.Frame(status_grid)
        print_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=2)
        
        # Current file
        file_frame = ttk.Frame(print_frame)
        file_frame.pack(fill=tk.X, pady=2)
        ttk.Label(file_frame, text="Current File:").pack(side=tk.LEFT, padx=(0, 5))
        self.current_file_var = tk.StringVar(value=self.emulator.config["current_file"])
        file_entry = ttk.Entry(file_frame, textvariable=self.current_file_var, width=25)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        file_entry.bind("<Return>", lambda e: self.update_config_from_ui())
        
        # Print status
        status_combo_frame = ttk.Frame(print_frame)
        status_combo_frame.pack(fill=tk.X, pady=2)
        ttk.Label(status_combo_frame, text="Print Status:").pack(side=tk.LEFT, padx=(0, 5))
        self.print_status_var = tk.StringVar(value=self.emulator.config["print_status"].capitalize())
        status_combo = ttk.Combobox(status_combo_frame, textvariable=self.print_status_var, width=15)
        status_combo['values'] = ('Idle', 'Printing', 'Paused', 'Completed', 'Failed')
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.update_config_from_ui())
        
        # Print progress
        progress_frame = ttk.Frame(print_frame)
        progress_frame.pack(fill=tk.X, pady=2)
        ttk.Label(progress_frame, text="Print Progress:").pack(side=tk.LEFT, padx=(0, 5))
        self.progress_var = tk.IntVar(value=self.emulator.config["print_progress"])
        progress_scale = ttk.Scale(progress_frame, from_=0, to=100, variable=self.progress_var, orient=tk.HORIZONTAL, length=150)
        progress_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        progress_scale.bind("<ButtonRelease-1>", lambda e: self.update_config_from_ui())
        self.progress_label = ttk.Label(progress_frame, text=f"{self.emulator.config['print_progress']}%", width=4)
        self.progress_label.pack(side=tk.LEFT)
        
        # Additional controls - in a horizontal frame at the bottom of print_frame
        controls_frame = ttk.Frame(print_frame)
        controls_frame.pack(fill=tk.X, pady=(5, 2))
        
        # LED State and Filament Sensor in a row
        led_frame = ttk.Frame(controls_frame)
        led_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(led_frame, text="LED State:").pack(side=tk.LEFT, padx=(0, 5))
        self.led_var = tk.BooleanVar(value=self.emulator.config["led_state"])
        ttk.Checkbutton(led_frame, variable=self.led_var, command=self.update_config_from_ui).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(led_frame, text="Filament Sensor:").pack(side=tk.LEFT, padx=(0, 5))
        self.filament_sensor_var = tk.BooleanVar(value=self.emulator.config["filament_runout_sensor"])
        ttk.Checkbutton(led_frame, variable=self.filament_sensor_var, command=self.update_config_from_ui).pack(side=tk.LEFT)
        
        # File Emulation frame
        file_emulation_frame = ttk.LabelFrame(self.parent, text="File Emulation")
        file_emulation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        
        # Thumbnail selection
        thumbnail_frame = ttk.Frame(file_emulation_frame)
        thumbnail_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Use horizontal layout with label, filename and button
        ttk.Label(thumbnail_frame, text="Thumbnail File:", width=15).pack(side=tk.LEFT, padx=(5, 5))
        self.thumbnail_path_var = tk.StringVar(value=os.path.basename(self.emulator.thumbnail_path) if self.emulator.thumbnail_path else "No file selected")
        ttk.Label(thumbnail_frame, textvariable=self.thumbnail_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(thumbnail_frame, text="Browse...", style="info.TButton", command=self.browse_thumbnail).pack(side=tk.RIGHT, padx=5)
        
        # Virtual Files section
        virtual_files_frame = ttk.Frame(file_emulation_frame)
        virtual_files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Label for section
        ttk.Label(virtual_files_frame, text="Emulated Files:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(5, 2))
        
        # Files list with scrollbar
        files_frame = ttk.Frame(virtual_files_frame)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        self.files_listbox = tk.Listbox(files_frame, height=8, selectmode=tk.SINGLE)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(files_frame, command=self.files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate the listbox with initial files
        for file in self.emulator.virtual_files:
            self.files_listbox.insert(tk.END, file)
        
        # Add/Delete buttons and file entry
        file_control_frame = ttk.Frame(virtual_files_frame)
        file_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.new_file_var = tk.StringVar()
        new_file_entry = ttk.Entry(file_control_frame, textvariable=self.new_file_var, width=30)
        new_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Bind Enter key to add file
        new_file_entry.bind("<Return>", lambda e: self.add_virtual_file())
        
        # Bind double-click on list item to delete
        self.files_listbox.bind("<Double-Button-1>", lambda e: self.delete_virtual_file())
        
        add_button = ttk.Button(file_control_frame, text="Add File", command=self.add_virtual_file)
        add_button.pack(side=tk.LEFT, padx=2)
        
        delete_button = ttk.Button(file_control_frame, text="Delete", style="danger.TButton", command=self.delete_virtual_file)
        delete_button.pack(side=tk.LEFT, padx=2)
        
        # Button to load default files (useful for restoring originals)
        ttk.Button(file_control_frame, text="Restore Defaults", style="secondary.TButton", 
                 command=self.restore_default_files).pack(side=tk.LEFT, padx=2)
        
        # Server control buttons
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Server status and buttons - use full width
        server_info_frame = ttk.Frame(control_frame)
        server_info_frame.pack(fill=tk.X, expand=True)
        
        self.server_status_var = tk.StringVar(value="Server Status: Stopped")
        status_label = ttk.Label(server_info_frame, textvariable=self.server_status_var, font=("Segoe UI", 10, "bold"))
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Button frame on the right
        button_container = ttk.Frame(server_info_frame)
        button_container.pack(side=tk.RIGHT, padx=10)
        
        self.stop_button = ttk.Button(button_container, text="Stop Server", style="danger.TButton", 
                                     command=self.stop_servers, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5)
        
        self.start_button = ttk.Button(button_container, text="Start Server", style="success.TButton", 
                                      command=self.start_servers)
        self.start_button.pack(side=tk.RIGHT, padx=5)
    
    def update_ui(self):
        """Update UI elements from emulator state"""
        # Update temperature display
        self.hotend_temp_var.set(f"{self.emulator.config['hotend_temp']:.1f}°C / {self.emulator.config['target_hotend']:.1f}°C")
        self.bed_temp_var.set(f"{self.emulator.config['bed_temp']:.1f}°C / {self.emulator.config['target_bed']:.1f}°C")
        
        # Update print progress display
        self.progress_var.set(self.emulator.config['print_progress'])
        self.progress_label.config(text=f"{self.emulator.config['print_progress']}%")
        
        # Update server status based on emulator state
        if self.emulator.server.is_running:
            self.server_status_var.set("Server Status: Running")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.server_status_var.set("Server Status: Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def update_config_from_ui(self):
        """Update emulator configuration from UI elements"""
        self.emulator.config['printer_name'] = self.printer_name_var.get()
        self.emulator.config['serial_number'] = self.serial_number_var.get()
        self.emulator.config['machine_type'] = self.machine_type_var.get()
        self.emulator.config['firmware_version'] = self.firmware_version_var.get()
        self.emulator.config['ip_address'] = self.ip_address_var.get()
        self.emulator.config['print_status'] = self.print_status_var.get().lower()
        self.emulator.config['print_progress'] = int(self.progress_var.get())
        self.emulator.config['led_state'] = self.led_var.get()
        self.emulator.config['filament_runout_sensor'] = self.filament_sensor_var.get()
        self.emulator.config['current_file'] = self.current_file_var.get()
        
        # Update progress label
        self.progress_label.config(text=f"{self.emulator.config['print_progress']}%")
        
        # Call the update callback if provided
        if self.on_update_callback:
            self.on_update_callback("Configuration updated from UI")
        
        # Update emulator server if IP address changed
        if self.emulator.server.is_running:
            self.schedule_server_restart()
    
    def update_config_field(self, field, value):
        """Update a specific configuration field with debouncing"""
        if field in self.emulator.config:
            old_value = self.emulator.config[field]
            if old_value != value:  # Only update if changed
                self.emulator.config[field] = value
                
                if self.on_update_callback:
                    self.on_update_callback(f"Updated {field} to: {value}")
                
                # If field affects server, schedule a debounced restart
                if field in ['printer_name', 'serial_number', 'machine_type', 'firmware_version', 'ip_address']:
                    if self.emulator.server.is_running:
                        self.schedule_server_restart()
    
    def update_idle_temps(self):
        """Update idle temperature settings from UI"""
        if self.emulator.update_idle_temps(self.idle_hotend_var.get(), self.idle_bed_var.get()):
            # Success - no additional action needed
            pass
        else:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for idle temperatures.")
    
    def reset_temp(self, heater_type):
        """Reset temperature target to 0 (off)"""
        if self.emulator.reset_temp(heater_type):
            if self.on_update_callback:
                self.on_update_callback(f"{heater_type.capitalize()} temperature target reset to 0°C")
        
    def show_temp_dialog(self, heater_type):
        """Show dialog to set temperature targets"""
        dialog = ttk.Toplevel(self.parent)
        dialog.title(f"Set {heater_type.capitalize()} Temperature")
        dialog.geometry("300x130")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Target Temperature (°C):").pack(pady=(10, 5))
        
        temp_var = tk.StringVar(value=str(int(self.emulator.config[f'target_{heater_type}'])))
        temp_entry = ttk.Entry(dialog, textvariable=temp_var, width=10)
        temp_entry.pack(pady=5)
        temp_entry.select_range(0, tk.END)
        temp_entry.focus()
        
        def on_ok():
            try:
                new_temp = float(temp_var.get())
                if self.emulator.set_temp(heater_type, new_temp):
                    dialog.destroy()
                else:
                    messagebox.showerror("Invalid Temperature", "Temperature must be between 0°C and 300°C.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", style="success.TButton", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", style="secondary.TButton", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to OK button
        dialog.bind("<Return>", lambda e: on_ok())
    
    def browse_thumbnail(self):
        """Browse for thumbnail image file"""
        file_path = filedialog.askopenfilename(
            title="Select Thumbnail Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            if self.emulator.set_thumbnail(file_path):
                self.thumbnail_path_var.set(os.path.basename(file_path))
                if self.on_update_callback:
                    self.on_update_callback(f"Thumbnail file set to: {file_path}")
    
    def add_virtual_file(self):
        """Add a new file to the virtual files list"""
        new_file = self.new_file_var.get().strip()
        
        # Validate file name
        if not new_file:
            messagebox.showwarning("Invalid File", "Please enter a file name")
            return
        
        if self.emulator.add_virtual_file(new_file):
            # Add to UI
            self.files_listbox.insert(tk.END, new_file)
            
            # Clear the entry field
            self.new_file_var.set("")
            
            if self.on_update_callback:
                self.on_update_callback(f"Added virtual file: {new_file}")
        else:
            messagebox.showwarning("Duplicate File", f"The file '{new_file}' is already in the list.")
    
    def delete_virtual_file(self):
        """Delete the selected file from the virtual files list"""
        # Get selected index
        selected_idx = self.files_listbox.curselection()
        
        if not selected_idx:
            messagebox.showwarning("No Selection", "Please select a file to delete.")
            return
        
        # Get file name from the selected index
        idx = selected_idx[0]
        filename = self.files_listbox.get(idx)
        
        if self.emulator.delete_virtual_file(filename):
            # Remove from UI
            self.files_listbox.delete(idx)
            
            if self.on_update_callback:
                self.on_update_callback(f"Deleted virtual file: {filename}")
    
    def restore_default_files(self):
        """Restore the default list of virtual files"""
        # Ask for confirmation if there are existing files
        if self.files_listbox.size() > 0:
            confirm = messagebox.askyesno("Confirm Restore", 
                                         "This will replace all current files with the default list. Continue?")
            if not confirm:
                return
        
        if self.emulator.restore_default_files():
            # Clear and repopulate the UI
            self.files_listbox.delete(0, tk.END)
            
            # Add default files
            for file in self.emulator.virtual_files:
                self.files_listbox.insert(tk.END, file)
            
            if self.on_update_callback:
                self.on_update_callback(f"Restored {len(self.emulator.virtual_files)} default virtual files")
    
    def start_servers(self):
        """Start the emulator servers"""
        if self.emulator.start_server():
            self.server_status_var.set("Server Status: Running")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
    
    def stop_servers(self):
        """Stop the emulator servers"""
        if self.emulator.stop_server():
            self.server_status_var.set("Server Status: Stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def restart_servers(self):
        """Restart the emulator servers"""
        if self.emulator.restart_server():
            self.server_status_var.set("Server Status: Running")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
    def schedule_server_restart(self):
        """Schedule a server restart with debouncing (1 second delay)"""
        # Cancel any pending restart
        if self.restart_timer:
            self.parent.after_cancel(self.restart_timer)
            self.restart_timer = None
            
        # Schedule a new restart after 1 second of inactivity
        self.restart_timer = self.parent.after(1000, self.perform_server_restart)
    
    def perform_server_restart(self):
        """Actually perform the server restart after debounce delay"""
        self.restart_timer = None
        if self.on_update_callback:
            self.on_update_callback("Restarting emulator services to apply configuration changes...")
        self.restart_servers()
