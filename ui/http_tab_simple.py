"""
Simplified HTTP API Tab that definitely works
"""
import tkinter as tk
from tkinter import ttk

class HttpTabSimple:
    """Simplified HTTP API interface"""

    def __init__(self, parent, emulator):
        self.parent = parent
        self.emulator = emulator

        # Create a simple label to test
        test_label = ttk.Label(self.parent, text="HTTP API Tab - Working!", font=("Arial", 16))
        test_label.pack(pady=20)

        # Server control frame
        server_frame = ttk.LabelFrame(self.parent, text="HTTP Server Control")
        server_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(server_frame, text="HTTP Status:").pack(pady=5)
        self.status_label = ttk.Label(server_frame, text="Stopped", foreground="red")
        self.status_label.pack(pady=5)

        # Start/Stop buttons
        button_frame = ttk.Frame(server_frame)
        button_frame.pack(pady=10)

        self.start_btn = ttk.Button(button_frame, text="Start HTTP Server", command=self.start_server)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop HTTP Server", command=self.stop_server)
        self.stop_btn.pack(side="left", padx=5)

        # Test buttons
        test_frame = ttk.LabelFrame(self.parent, text="Quick Tests")
        test_frame.pack(fill="x", padx=10, pady=10)

        test_button_frame = ttk.Frame(test_frame)
        test_button_frame.pack(pady=10)

        ttk.Button(test_button_frame, text="Test /product", command=self.test_product).pack(side="left", padx=5)
        ttk.Button(test_button_frame, text="Test /detail", command=self.test_detail).pack(side="left", padx=5)
        ttk.Button(test_button_frame, text="Test LED", command=self.test_led).pack(side="left", padx=5)

        # Log area
        log_frame = ttk.LabelFrame(self.parent, text="Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initialize with message
        self.log("HTTP API Tab loaded successfully")

    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def start_server(self):
        """Start HTTP server"""
        try:
            if self.emulator.start_http_server():
                self.status_label.config(text="Running", foreground="green")
                self.log("HTTP server started on port 8898")
            else:
                self.log("Failed to start HTTP server")
        except Exception as e:
            self.log(f"Error starting server: {e}")

    def stop_server(self):
        """Stop HTTP server"""
        try:
            if self.emulator.stop_http_server():
                self.status_label.config(text="Stopped", foreground="red")
                self.log("HTTP server stopped")
            else:
                self.log("Failed to stop HTTP server")
        except Exception as e:
            self.log(f"Error stopping server: {e}")

    def test_product(self):
        """Test product endpoint"""
        self.log("Testing /product endpoint...")
        # Add actual test logic here

    def test_detail(self):
        """Test detail endpoint"""
        self.log("Testing /detail endpoint...")
        # Add actual test logic here

    def test_led(self):
        """Test LED control"""
        self.log("Testing LED control...")
        # Add actual test logic here

    def cleanup(self):
        """Cleanup when closing"""
        pass