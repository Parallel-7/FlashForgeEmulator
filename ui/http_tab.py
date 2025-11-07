"""
HTTP API Control Tab for FlashForge Emulator
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import threading
import requests
from datetime import datetime
import config

class HttpTab:
    """HTTP API control and monitoring interface"""

    def __init__(self, parent, emulator):
        self.parent = parent
        self.emulator = emulator
        # Don't create separate http_server - use emulator's instance
        self.test_credentials = {
            'serialNumber': '',
            'checkCode': ''
        }

        # Request statistics
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0

        # Initialize all widgets first
        self.create_widgets()
        self.setup_layout()
        self.update_ui_state()

        # Start periodic UI updates
        self.update_server_status()

    def create_widgets(self):
        """Create all UI widgets"""
        # HTTP Server Status (SIMPLIFIED - controls moved to Main tab)
        self.server_frame = ttk.LabelFrame(self.parent, text="HTTP Server Status", padding=10)

        # Current mode display
        mode_frame = ttk.Frame(self.server_frame)
        mode_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(mode_frame, text="Current Mode:").pack(side="left")
        self.current_mode_label = ttk.Label(mode_frame, text="AD5X", font=("Arial", 10, "bold"), foreground="blue")
        self.current_mode_label.pack(side="left", padx=(10, 0))

        # Server status display
        status_frame = ttk.Frame(self.server_frame)
        status_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(status_frame, text="HTTP Server:").pack(side="left")
        self.http_status = ttk.Label(status_frame, text="Stopped", foreground="red", font=("Arial", 10, "bold"))
        self.http_status.pack(side="left", padx=(10, 0))

        # Note about main tab controls
        note_label = ttk.Label(self.server_frame, text="Use the Main tab to start/stop servers and change modes",
                              font=("Arial", 9), foreground="gray")
        note_label.pack(pady=(10, 0))

        # Authentication Section
        self.auth_frame = ttk.LabelFrame(self.parent, text="Authentication", padding=10)

        ttk.Label(self.auth_frame, text="Serial Number:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.serial_number = tk.StringVar(value=self.emulator.config.get('serial_number', ''))
        serial_entry = ttk.Entry(self.auth_frame, textvariable=self.serial_number, width=20)
        serial_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(self.auth_frame, text="Check Code:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.check_code = tk.StringVar(value=self.emulator.config.get('check_code', config.HTTP_CONFIG['check_code']))
        check_entry = ttk.Entry(self.auth_frame, textvariable=self.check_code, width=20)
        check_entry.grid(row=1, column=1, sticky="ew")

        self.update_auth_btn = ttk.Button(self.auth_frame, text="Update Config", command=self.update_authentication)
        self.update_auth_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        self.test_auth_btn = ttk.Button(self.auth_frame, text="Test Auth", command=self.test_authentication)
        self.test_auth_btn.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky="ew")

        # Request Monitoring Section
        self.monitor_frame = ttk.LabelFrame(self.parent, text="Request Monitoring", padding=10)

        # Statistics
        stats_frame = ttk.Frame(self.monitor_frame)
        stats_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(stats_frame, text="Total Requests:").pack(side="left")
        self.total_requests_label = ttk.Label(stats_frame, text="0")
        self.total_requests_label.pack(side="left", padx=(5, 20))

        ttk.Label(stats_frame, text="Success:").pack(side="left")
        self.success_label = ttk.Label(stats_frame, text="0", foreground="green")
        self.success_label.pack(side="left", padx=(5, 20))

        ttk.Label(stats_frame, text="Errors:").pack(side="left")
        self.error_label = ttk.Label(stats_frame, text="0", foreground="red")
        self.error_label.pack(side="left", padx=(5, 20))

        self.clear_stats_btn = ttk.Button(stats_frame, text="Clear Stats", command=self.clear_statistics)
        self.clear_stats_btn.pack(side="right")

        # Log area
        self.log_area = scrolledtext.ScrolledText(self.monitor_frame, height=10, wrap=tk.WORD)
        self.log_area.pack(fill="both", expand=True)

        # Quick Testing Section
        self.test_frame = ttk.LabelFrame(self.parent, text="Quick Testing", padding=10)

        # Endpoint test buttons
        button_frame = ttk.Frame(self.test_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        self.test_product_btn = ttk.Button(button_frame, text="/product", command=lambda: self.test_endpoint('/product'))
        self.test_product_btn.pack(side="left", padx=(0, 5))

        self.test_detail_btn = ttk.Button(button_frame, text="/detail", command=lambda: self.test_endpoint('/detail'))
        self.test_detail_btn.pack(side="left", padx=(0, 5))

        self.test_files_btn = ttk.Button(button_frame, text="/gcodeList", command=lambda: self.test_endpoint('/gcodeList'))
        self.test_files_btn.pack(side="left", padx=(0, 5))

        self.test_led_btn = ttk.Button(button_frame, text="LED Toggle", command=self.test_led_control)
        self.test_led_btn.pack(side="left", padx=(0, 5))

        # Material Station Controls (AD5X only)
        self.matl_frame = ttk.LabelFrame(self.test_frame, text="Material Station (AD5X)", padding=10)

        matl_control_frame = ttk.Frame(self.matl_frame)
        matl_control_frame.pack(fill="x")

        ttk.Label(matl_control_frame, text="Slot:").pack(side="left")
        self.slot_selector = ttk.Combobox(matl_control_frame, values=["1", "2", "3", "4"], state="readonly", width=5)
        self.slot_selector.set("1")
        self.slot_selector.pack(side="left", padx=(5, 10))

        ttk.Label(matl_control_frame, text="Material:").pack(side="left")
        self.material_name = tk.StringVar(value="PLA")
        ttk.Entry(matl_control_frame, textvariable=self.material_name, width=8).pack(side="left", padx=(5, 10))

        ttk.Label(matl_control_frame, text="Color:").pack(side="left")
        self.material_color = tk.StringVar(value="#FF0000")
        ttk.Entry(matl_control_frame, textvariable=self.material_color, width=8).pack(side="left", padx=(5, 10))

        self.update_slot_btn = ttk.Button(matl_control_frame, text="Update Slot", command=self.update_material_slot)
        self.update_slot_btn.pack(side="left", padx=(10, 0))

        # File Upload Testing Section
        self.upload_frame = ttk.LabelFrame(self.parent, text="File Upload Testing", padding=10)

        file_frame = ttk.Frame(self.upload_frame)
        file_frame.pack(fill="x", pady=(0, 10))

        self.selected_file = tk.StringVar(value="No file selected")
        ttk.Label(file_frame, textvariable=self.selected_file).pack(side="left", fill="x", expand=True)

        self.browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side="right")

        # Upload options
        options_frame = ttk.Frame(self.upload_frame)
        options_frame.pack(fill="x", pady=(0, 10))

        self.print_now = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Start Print", variable=self.print_now).pack(side="left", padx=(0, 10))

        self.leveling = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Auto Level", variable=self.leveling).pack(side="left", padx=(0, 10))

        self.use_matl_station = tk.BooleanVar()
        self.matl_check = ttk.Checkbutton(options_frame, text="Use Material Station", variable=self.use_matl_station)
        self.matl_check.pack(side="left")

        self.upload_btn = ttk.Button(self.upload_frame, text="Upload File", command=self.upload_file)
        self.upload_btn.pack(pady=(10, 0), fill="x")

    def setup_layout(self):
        """Setup the layout of all widgets"""
        # Pack all frames in order
        self.server_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.auth_frame.pack(fill="x", padx=10, pady=5)
        self.test_frame.pack(fill="x", padx=10, pady=5)
        self.monitor_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.upload_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Configure grid weights for internal frames
        self.server_frame.grid_columnconfigure(1, weight=1)
        self.auth_frame.grid_columnconfigure(1, weight=1)

    def update_ui_state(self):
        """Update UI state based on current configuration"""
        # Update current mode display
        current_mode = self.emulator.config.get('printer_mode', 'AD5X')
        self.current_mode_label.config(text=current_mode)

        # Show/hide material station controls based on printer mode
        if current_mode == 'AD5X':
            self.matl_frame.pack(fill="x", pady=(10, 0))
        else:
            self.matl_frame.pack_forget()

    def refresh_mode_display(self):
        """Refresh the current mode display (called from main tab)"""
        current_mode = self.emulator.config.get('printer_mode', 'AD5X')
        self.current_mode_label.config(text=current_mode)
        self.update_ui_state()

    def update_server_status(self):
        """Update server status display (called periodically)"""
        if hasattr(self.emulator, 'http_server') and self.emulator.http_server:
            if self.emulator.http_server.is_running:
                self.http_status.config(text="Running", foreground="green")
            else:
                state = self.emulator.http_server.get_state()
                if state == "error":
                    self.http_status.config(text="Error", foreground="orange")
                else:
                    self.http_status.config(text="Stopped", foreground="red")
        else:
            self.http_status.config(text="Stopped", foreground="red")

        # Schedule next update
        self.parent.after(500, self.update_server_status)

    def update_authentication(self):
        """Update authentication configuration"""
        self.emulator.config['serial_number'] = self.serial_number.get()
        self.emulator.config['check_code'] = self.check_code.get()
        # Auto-save configuration
        self.emulator.save_config_to_json()
        self.log_message("Authentication configuration updated")

    def test_authentication(self):
        """Test authentication with current credentials"""
        if not hasattr(self.emulator, 'http_server') or not self.emulator.http_server or not self.emulator.http_server.is_running:
            messagebox.showwarning("Warning", "HTTP server is not running")
            return

        threading.Thread(target=self._test_auth_thread, daemon=True).start()

    def _test_auth_thread(self):
        """Test authentication in background thread"""
        try:
            port = config.HTTP_PORT
            url = f"http://localhost:{port}/product"

            payload = {
                "serialNumber": self.serial_number.get(),
                "checkCode": self.check_code.get()
            }

            response = requests.post(url, json=payload, timeout=5)
            result = response.json()

            if result.get('code') == 0:
                self.log_message("✓ Authentication test PASSED")
            else:
                self.log_message(f"✗ Authentication test FAILED: {result.get('message', 'Unknown error')}")

        except Exception as e:
            self.log_message(f"✗ Authentication test ERROR: {str(e)}")

    def test_endpoint(self, endpoint):
        """Test a specific endpoint"""
        if not hasattr(self.emulator, 'http_server') or not self.emulator.http_server or not self.emulator.http_server.is_running:
            messagebox.showwarning("Warning", "HTTP server is not running")
            return

        threading.Thread(target=self._test_endpoint_thread, args=(endpoint,), daemon=True).start()

    def _test_endpoint_thread(self, endpoint):
        """Test endpoint in background thread"""
        try:
            port = config.HTTP_PORT
            url = f"http://localhost:{port}{endpoint}"

            payload = {
                "serialNumber": self.serial_number.get(),
                "checkCode": self.check_code.get()
            }

            response = requests.post(url, json=payload, timeout=5)
            result = response.json()

            self.request_count += 1
            if result.get('code') == 0:
                self.success_count += 1
                self.log_message(f"✓ {endpoint} - Success")
            else:
                self.error_count += 1
                self.log_message(f"✗ {endpoint} - Error: {result.get('message', 'Unknown error')}")

            self._update_statistics()

        except Exception as e:
            self.error_count += 1
            self.log_message(f"✗ {endpoint} - Exception: {str(e)}")
            self._update_statistics()

    def test_led_control(self):
        """Test LED control command"""
        if not hasattr(self.emulator, 'http_server') or not self.emulator.http_server or not self.emulator.http_server.is_running:
            messagebox.showwarning("Warning", "HTTP server is not running")
            return

        # Toggle LED state
        current_state = self.emulator.config.get('led_on', False)
        new_status = "close" if current_state else "open"

        threading.Thread(target=self._test_led_control_thread, args=(new_status,), daemon=True).start()

    def _test_led_control_thread(self, status):
        """Test LED control in background thread"""
        try:
            port = config.HTTP_PORT
            url = f"http://localhost:{port}/control"

            payload = {
                "serialNumber": self.serial_number.get(),
                "checkCode": self.check_code.get(),
                "payload": {
                    "cmd": "lightControl_cmd",
                    "args": {"status": status}
                }
            }

            response = requests.post(url, json=payload, timeout=5)
            result = response.json()

            self.request_count += 1
            if result.get('code') == 0:
                self.success_count += 1
                self.log_message(f"✓ LED Control - Set to {status}")
            else:
                self.error_count += 1
                self.log_message(f"✗ LED Control - Error: {result.get('message', 'Unknown error')}")

            self._update_statistics()

        except Exception as e:
            self.error_count += 1
            self.log_message(f"✗ LED Control - Exception: {str(e)}")
            self._update_statistics()

    def update_material_slot(self):
        """Update material station slot"""
        if not hasattr(self.emulator, 'material_station') or not self.emulator.material_station:
            messagebox.showwarning("Warning", "Material station not available in current mode")
            return

        try:
            slot_id = int(self.slot_selector.get())
            material = self.material_name.get()
            color = self.material_color.get()

            self.emulator.material_station.update_slot(
                slot_id,
                has_filament=bool(material),
                material_name=material,
                material_color=color
            )

            self.log_message(f"Updated slot {slot_id}: {material} ({color})")

        except Exception as e:
            messagebox.showerror("Error", f"Error updating material slot: {str(e)}")

    def browse_file(self):
        """Browse for file to upload"""
        filename = filedialog.askopenfilename(
            title="Select G-code or 3MF file",
            filetypes=[
                ("3D Print Files", "*.gcode *.3mf *.gx"),
                ("G-code Files", "*.gcode *.gx"),
                ("3MF Files", "*.3mf"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            self.selected_file.set(filename)

    def upload_file(self):
        """Upload selected file"""
        filename = self.selected_file.get()
        if filename == "No file selected":
            messagebox.showwarning("Warning", "Please select a file first")
            return

        if not hasattr(self.emulator, 'http_server') or not self.emulator.http_server or not self.emulator.http_server.is_running:
            messagebox.showwarning("Warning", "HTTP server is not running")
            return

        threading.Thread(target=self._upload_file_thread, args=(filename,), daemon=True).start()

    def _upload_file_thread(self, filepath):
        """Upload file in background thread"""
        try:
            port = config.HTTP_PORT
            url = f"http://localhost:{port}/uploadGcode"

            # Read file
            with open(filepath, 'rb') as f:
                file_data = f.read()

            # Prepare headers
            headers = {
                'serialNumber': self.serial_number.get(),
                'checkCode': self.check_code.get(),
                'fileSize': str(len(file_data)),
                'printNow': str(self.print_now.get()).lower(),
                'levelingBeforePrint': str(self.leveling.get()).lower()
            }

            # Add AD5X headers if material station is used
            if self.use_matl_station.get() and self.emulator.config.get('printer_mode') == 'AD5X':
                headers.update({
                    'useMatlStation': 'true',
                    'gcodeToolCnt': '2',
                    'materialMappings': 'W3sidG9vbElkIjowLCJzbG90SWQiOjEsIm1hdGVyaWFsTmFtZSI6IlBMQSIsInRvb2xNYXRlcmlhbENvbG9yIjoiI0ZGMDAwMCIsInNsb3RNYXRlcmlhbENvbG9yIjoiI0ZGMDAwMCJ9XQ=='  # Base64 encoded sample mapping
                })

            # Prepare multipart form data
            files = {'gcodeFile': (filepath.split('/')[-1], file_data, 'application/octet-stream')}

            response = requests.post(url, files=files, headers=headers, timeout=30)
            result = response.json()

            self.request_count += 1
            if result.get('code') == 0:
                self.success_count += 1
                self.log_message(f"✓ File upload successful: {filepath.split('/')[-1]}")
            else:
                self.error_count += 1
                self.log_message(f"✗ File upload failed: {result.get('message', 'Unknown error')}")

            self._update_statistics()

        except Exception as e:
            self.error_count += 1
            self.log_message(f"✗ File upload exception: {str(e)}")
            self._update_statistics()

    def clear_statistics(self):
        """Clear request statistics"""
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self._update_statistics()
        self.log_message("Statistics cleared")

    def _update_statistics(self):
        """Update statistics display"""
        self.total_requests_label.config(text=str(self.request_count))
        self.success_label.config(text=str(self.success_count))
        self.error_label.config(text=str(self.error_count))

    def log_message(self, message):
        """Log message to the log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        # Thread-safe UI update
        self.parent.after(0, lambda: self._append_log(log_entry))

    def log_http_request(self, method, path, client_ip, status_code, request_body=None, response_body=None):
        """Log detailed HTTP request information and update statistics"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Build detailed log entry
        log_parts = [f"[{timestamp}] {method} {path}"]
        log_parts.append(f"  Client: {client_ip}")
        log_parts.append(f"  Status: {status_code}")

        if request_body:
            # Truncate long request bodies
            body_str = str(request_body)[:200]
            if len(str(request_body)) > 200:
                body_str += "..."
            log_parts.append(f"  Request: {body_str}")

        if response_body and status_code != 200:
            # Log response body only for errors
            body_str = str(response_body)[:200]
            if len(str(response_body)) > 200:
                body_str += "..."
            log_parts.append(f"  Response: {body_str}")

        log_entry = "\n".join(log_parts) + "\n\n"

        # Update statistics
        self.request_count += 1
        if 200 <= status_code < 300:
            self.success_count += 1
        else:
            self.error_count += 1

        # Thread-safe UI updates
        self.parent.after(0, lambda: self._append_log(log_entry))
        self.parent.after(0, self._update_statistics)

    def _append_log(self, log_entry):
        """Append log entry to log area (must be called from main thread)"""
        self.log_area.insert(tk.END, log_entry)
        self.log_area.see(tk.END)

        # Keep log size manageable
        lines = int(self.log_area.index(tk.END).split('.')[0])
        if lines > 1000:
            self.log_area.delete('1.0', '500.0')

    # Logger interface for HTTP server (legacy - for simple messages)
    def info(self, message):
        """Logger interface - info level"""
        self.log_message(f"INFO: {message}")

    def error(self, message):
        """Logger interface - error level"""
        self.log_message(f"ERROR: {message}")

    def warning(self, message):
        """Logger interface - warning level"""
        self.log_message(f"WARNING: {message}")

    def cleanup(self):
        """Cleanup resources"""
        # No cleanup needed - server is managed by emulator
        pass