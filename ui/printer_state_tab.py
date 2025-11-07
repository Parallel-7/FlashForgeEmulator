"""
Printer State tab UI for FlashForge Emulator
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class PrinterStateTab:
    """Printer State tab UI component"""
    
    def __init__(self, parent, emulator, on_update_callback=None):
        self.parent = parent
        self.emulator = emulator
        self.on_update_callback = on_update_callback
        
        # Create the UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the printer state tab UI"""
        # Temperature Frame
        temp_frame = ttk.LabelFrame(self.parent, text="Temperature Control")
        temp_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        # Create a grid for the temperature controls
        temp_grid = ttk.Frame(temp_frame)
        temp_grid.pack(fill=tk.X, expand=True, padx=10, pady=10)
        
        # Row 0: Idle hotend temperature
        ttk.Label(temp_grid, text="Idle Hotend Temp:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        idle_hotend_frame = ttk.Frame(temp_grid)
        idle_hotend_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.idle_hotend_var = tk.DoubleVar(value=self.emulator.idle_hotend_temp)
        idle_hotend_spin = ttk.Spinbox(idle_hotend_frame, from_=15, to=40, increment=0.5, width=5, textvariable=self.idle_hotend_var)
        idle_hotend_spin.pack(side=tk.LEFT, padx=2)
        ttk.Label(idle_hotend_frame, text="°C").pack(side=tk.LEFT)
        
        # Row 1: Current hotend temperature display
        ttk.Label(temp_grid, text="Hotend Temperature:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        hotend_display_frame = ttk.Frame(temp_grid)
        hotend_display_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.hotend_temp_var = tk.StringVar(value=f"{self.emulator.config['hotend_temp']:.1f}°C / {self.emulator.config['target_hotend']:.1f}°C")
        ttk.Label(hotend_display_frame, textvariable=self.hotend_temp_var).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(hotend_display_frame, text="Set", command=lambda: self.show_temp_dialog('hotend')).pack(side=tk.LEFT, padx=2)
        ttk.Button(hotend_display_frame, text="Reset", command=lambda: self.reset_temp('hotend'), style="warning.TButton").pack(side=tk.LEFT, padx=2)
        
        # Row 2: Idle bed temperature
        ttk.Label(temp_grid, text="Idle Bed Temp:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        idle_bed_frame = ttk.Frame(temp_grid)
        idle_bed_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.idle_bed_var = tk.DoubleVar(value=self.emulator.idle_bed_temp)
        idle_bed_spin = ttk.Spinbox(idle_bed_frame, from_=20, to=50, increment=0.5, width=5, textvariable=self.idle_bed_var)
        idle_bed_spin.pack(side=tk.LEFT, padx=2)
        ttk.Label(idle_bed_frame, text="°C").pack(side=tk.LEFT)
        
        # Row 3: Current bed temperature display
        ttk.Label(temp_grid, text="Bed Temperature:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        bed_display_frame = ttk.Frame(temp_grid)
        bed_display_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.bed_temp_var = tk.StringVar(value=f"{self.emulator.config['bed_temp']:.1f}°C / {self.emulator.config['target_bed']:.1f}°C")
        ttk.Label(bed_display_frame, textvariable=self.bed_temp_var).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(bed_display_frame, text="Set", command=lambda: self.show_temp_dialog('bed')).pack(side=tk.LEFT, padx=2)
        ttk.Button(bed_display_frame, text="Reset", command=lambda: self.reset_temp('bed'), style="warning.TButton").pack(side=tk.LEFT, padx=2)
        
        # Apply button for idle temperatures
        apply_frame = ttk.Frame(temp_frame)
        apply_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        ttk.Button(apply_frame, text="Apply Idle Temperatures", style="primary.TButton", 
                   command=self.update_idle_temps).pack(side=tk.RIGHT)
        
        # Print Status Frame
        status_frame = ttk.LabelFrame(self.parent, text="Print Status")
        status_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        # Create a grid for print status
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X, expand=True, padx=10, pady=10)
        
        # Row 0: Current file
        ttk.Label(status_grid, text="Current File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.current_file_var = tk.StringVar(value=self.emulator.config["current_file"])
        file_entry = ttk.Entry(status_grid, textvariable=self.current_file_var, width=30)
        file_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        file_entry.bind("<Return>", lambda e: self.update_config_from_ui())
        
        # Row 1: Print status
        ttk.Label(status_grid, text="Print Status:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.print_status_var = tk.StringVar(value=self.emulator.config["print_status"].capitalize())
        status_combo = ttk.Combobox(status_grid, textvariable=self.print_status_var, width=15)
        status_combo['values'] = ('Ready', 'Busy', 'Calibrating', 'Error', 'Heating', 'Printing', 'Pausing', 'Paused', 'Cancelled', 'Completed', 'Unknown')
        status_combo.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.update_config_from_ui())
        
        # Row 2: Print progress
        ttk.Label(status_grid, text="Print Progress:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        progress_frame = ttk.Frame(status_grid)
        progress_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)

        self.progress_var = tk.IntVar(value=self.emulator.config["print_progress"])
        progress_scale = ttk.Scale(progress_frame, from_=0, to=100, variable=self.progress_var, orient=tk.HORIZONTAL)
        progress_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        progress_scale.bind("<ButtonRelease-1>", lambda e: self.update_config_from_ui())
        self.progress_label = ttk.Label(progress_frame, text=f"{self.emulator.config['print_progress']}%", width=4)
        self.progress_label.pack(side=tk.LEFT)

        # Row 3: Estimated Filament Length
        ttk.Label(status_grid, text="Est. Filament (m):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.filament_length_var = tk.DoubleVar(value=self.emulator.config.get("estimated_right_len", 0.0))
        self.filament_length_entry = ttk.Entry(status_grid, textvariable=self.filament_length_var, width=15)
        self.filament_length_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.filament_length_entry.bind("<Return>", lambda e: self.update_config_from_ui())
        self.filament_length_entry.bind("<FocusOut>", lambda e: self.update_config_from_ui())

        # Row 4: Estimated Filament Weight
        ttk.Label(status_grid, text="Est. Filament (g):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.filament_weight_var = tk.DoubleVar(value=self.emulator.config.get("estimated_right_weight", 0.0))
        self.filament_weight_entry = ttk.Entry(status_grid, textvariable=self.filament_weight_var, width=15)
        self.filament_weight_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.filament_weight_entry.bind("<Return>", lambda e: self.update_config_from_ui())
        self.filament_weight_entry.bind("<FocusOut>", lambda e: self.update_config_from_ui())

        # Row 5: Thumbnail
        ttk.Label(status_grid, text="Thumbnail File:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        thumbnail_frame = ttk.Frame(status_grid)
        thumbnail_frame.grid(row=5, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.thumbnail_path_var = tk.StringVar(value=os.path.basename(self.emulator.thumbnail_path) if self.emulator.thumbnail_path else "No file selected")
        ttk.Label(thumbnail_frame, textvariable=self.thumbnail_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(thumbnail_frame, text="Browse...", style="info.TButton", command=self.browse_thumbnail).pack(side=tk.RIGHT)
        
        # Configure status grid
        status_grid.columnconfigure(1, weight=1)
        
        # LED and Sensor Frame
        state_frame = ttk.LabelFrame(self.parent, text="Hardware State")
        state_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        # Create a frame for LED and filament sensor
        state_grid = ttk.Frame(state_frame)
        state_grid.pack(fill=tk.X, expand=True, padx=10, pady=10)
        
        # Row 0: LED State
        ttk.Label(state_grid, text="LED State:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        led_frame = ttk.Frame(state_grid)
        led_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.led_var = tk.BooleanVar(value=self.emulator.config["led_state"])
        led_check = ttk.Checkbutton(led_frame, variable=self.led_var, command=self.update_config_from_ui)
        led_check.pack(side=tk.LEFT)
        
        # Row 1: Filament Sensor
        ttk.Label(state_grid, text="Filament Sensor:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        filament_frame = ttk.Frame(state_grid)
        filament_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.filament_sensor_var = tk.BooleanVar(value=self.emulator.config["filament_runout_sensor"])
        filament_check = ttk.Checkbutton(filament_frame, variable=self.filament_sensor_var, command=self.update_config_from_ui)
        filament_check.pack(side=tk.LEFT)
        
        # Configure state grid columns
        state_grid.columnconfigure(1, weight=1)
    
    def update_ui(self):
        """Update UI elements from emulator state"""
        # Update temperature display
        self.hotend_temp_var.set(f"{self.emulator.config['hotend_temp']:.1f}°C / {self.emulator.config['target_hotend']:.1f}°C")
        self.bed_temp_var.set(f"{self.emulator.config['bed_temp']:.1f}°C / {self.emulator.config['target_bed']:.1f}°C")

        # Update print progress display
        self.progress_var.set(self.emulator.config['print_progress'])
        self.progress_label.config(text=f"{self.emulator.config['print_progress']}%")

        # Update print status
        self.print_status_var.set(self.emulator.config['print_status'].capitalize())

        # Update current file
        self.current_file_var.set(self.emulator.config['current_file'])

        # Update filament estimates ONLY if the user is not actively editing them
        # This prevents the feedback loop where updating the DoubleVar corrupts user input
        config_len = self.emulator.config.get('estimated_right_len', 0.0)
        config_weight = self.emulator.config.get('estimated_right_weight', 0.0)

        # DEBUG: Log what we're reading from config every 10 seconds to avoid spam
        import time
        if not hasattr(self, '_last_debug_time'):
            self._last_debug_time = 0
        if time.time() - self._last_debug_time > 10:
            if self.on_update_callback:
                self.on_update_callback(f"[DEBUG] Config->UI: Reading length={config_len}m, weight={config_weight}g")
            self._last_debug_time = time.time()

        # Only update the Entry widgets if they don't have focus (user isn't editing them)
        try:
            focused_widget = self.parent.focus_get()

            # Update length only if user isn't editing it
            if focused_widget != self.filament_length_entry:
                # Only update if value has actually changed (avoids unnecessary updates)
                current_val = self.filament_length_var.get()
                if abs(current_val - config_len) > 0.001:  # Small tolerance for float comparison
                    if time.time() - self._last_debug_time > 10:
                        if self.on_update_callback:
                            self.on_update_callback(f"[DEBUG] Updating length UI: {current_val} -> {config_len}")
                    self.filament_length_var.set(config_len)
            else:
                if time.time() - self._last_debug_time > 10:
                    if self.on_update_callback:
                        self.on_update_callback(f"[DEBUG] Skipping length update - user is editing")

            # Update weight only if user isn't editing it
            if focused_widget != self.filament_weight_entry:
                # Only update if value has actually changed
                current_val = self.filament_weight_var.get()
                if abs(current_val - config_weight) > 0.001:  # Small tolerance for float comparison
                    if time.time() - self._last_debug_time > 10:
                        if self.on_update_callback:
                            self.on_update_callback(f"[DEBUG] Updating weight UI: {current_val} -> {config_weight}")
                    self.filament_weight_var.set(config_weight)
            else:
                if time.time() - self._last_debug_time > 10:
                    if self.on_update_callback:
                        self.on_update_callback(f"[DEBUG] Skipping weight update - user is editing")
        except Exception as e:
            # Fallback: if we can't check focus, just update the values
            if self.on_update_callback:
                self.on_update_callback(f"[DEBUG] Focus check failed: {e}, updating values anyway")
            self.filament_length_var.set(config_len)
            self.filament_weight_var.set(config_weight)

        # Update LED and filament sensor
        self.led_var.set(self.emulator.config['led_state'])
        self.filament_sensor_var.set(self.emulator.config['filament_runout_sensor'])
    
    def update_config_from_ui(self):
        """Update emulator configuration from UI elements"""
        self.emulator.config['print_status'] = self.print_status_var.get().lower()
        self.emulator.config['print_progress'] = int(self.progress_var.get())
        self.emulator.config['led_state'] = self.led_var.get()
        self.emulator.config['filament_runout_sensor'] = self.filament_sensor_var.get()
        self.emulator.config['current_file'] = self.current_file_var.get()

        # Update filament estimates (apply to both left and right)
        try:
            filament_length = float(self.filament_length_var.get())
            filament_weight = float(self.filament_weight_var.get())

            # DEBUG LOGGING
            if self.on_update_callback:
                self.on_update_callback(f"[DEBUG] UI->Config: Setting length={filament_length}m, weight={filament_weight}g")

            self.emulator.config['estimated_right_len'] = filament_length
            self.emulator.config['estimated_left_len'] = filament_length
            self.emulator.config['estimated_right_weight'] = filament_weight
            self.emulator.config['estimated_left_weight'] = filament_weight

            # DEBUG: Verify what was stored
            if self.on_update_callback:
                stored_len = self.emulator.config.get('estimated_right_len')
                stored_weight = self.emulator.config.get('estimated_right_weight')
                self.on_update_callback(f"[DEBUG] Config stored: length={stored_len}m, weight={stored_weight}g")
        except ValueError:
            pass  # Ignore invalid input

        # Update progress label
        self.progress_label.config(text=f"{self.emulator.config['print_progress']}%")

        # Call the update callback if provided
        if self.on_update_callback:
            self.on_update_callback("Printer state updated from UI")
    
    def update_idle_temps(self):
        """Update idle temperature settings from UI"""
        if self.emulator.update_idle_temps(self.idle_hotend_var.get(), self.idle_bed_var.get()):
            if self.on_update_callback:
                self.on_update_callback(f"Idle temperatures updated - Hotend: {self.idle_hotend_var.get()}°C, Bed: {self.idle_bed_var.get()}°C")
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
