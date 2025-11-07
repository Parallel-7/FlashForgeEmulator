"""
Main window UI for FlashForge Emulator
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import config

from .main_tab import MainTab
from .printer_details_tab import PrinterDetailsTab
from .printer_state_tab import PrinterStateTab
from .filesystem_tab import FilesystemTab
from .network_tab import NetworkTab
from .http_tab import HttpTab

class MainWindow:
    """Main UI Window"""
    
    def __init__(self, root, emulator):
        self.root = root
        self.emulator = emulator
        
        # Initialize window
        self.root.title("FlashForge API Emulator")
        self.root.geometry(f"{config.UI_WINDOW_WIDTH}x{config.UI_WINDOW_HEIGHT}")
        
        # Set up the UI
        self.main_tab = None
        self.printer_details_tab = None
        self.printer_state_tab = None
        self.filesystem_tab = None
        self.network_tab = None
        self.http_tab = None
        self.setup_ui()
        
        # Setup periodic updates
        self.update_ui()
        
        # Initial log message
        self.log("FlashForge API Emulator started")
    
    def setup_ui(self):
        """Set up the main window UI"""
        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Create tab frames
        main_tab_frame = ttk.Frame(self.notebook)
        printer_details_tab_frame = ttk.Frame(self.notebook)
        printer_state_tab_frame = ttk.Frame(self.notebook)
        filesystem_tab_frame = ttk.Frame(self.notebook)
        network_tab_frame = ttk.Frame(self.notebook)
        http_tab_frame = ttk.Frame(self.notebook)

        self.notebook.add(main_tab_frame, text="Main")
        self.notebook.add(printer_details_tab_frame, text="Printer Details")
        self.notebook.add(printer_state_tab_frame, text="Printer State")
        self.notebook.add(filesystem_tab_frame, text="Filesystem")
        self.notebook.add(network_tab_frame, text="Network")
        self.notebook.add(http_tab_frame, text="HTTP API")
        
        # Initialize tabs
        self.main_tab = MainTab(main_tab_frame, self.emulator, self.log)
        self.printer_details_tab = PrinterDetailsTab(printer_details_tab_frame, self.emulator, self.log)
        self.printer_state_tab = PrinterStateTab(printer_state_tab_frame, self.emulator, self.log)
        self.filesystem_tab = FilesystemTab(filesystem_tab_frame, self.emulator, self.log)
        self.network_tab = NetworkTab(network_tab_frame, self.emulator, self.log)
        self.http_tab = HttpTab(http_tab_frame, self.emulator)

        # Set up cross-tab references
        self.main_tab.set_http_tab_reference(self.http_tab)
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def log(self, message):
        """Log a message to the main tab"""
        if self.main_tab:
            return self.main_tab.log(message)
        return message
    
    def update_ui(self):
        """Periodically update the UI from emulator state"""
        # Update temperature and status displays
        self.emulator.simulate_temperatures()

        # Simulate print progress
        self.emulator.simulate_print_progress()

        # Update progress if printing
        if hasattr(self.emulator, 'update_progress') and self.emulator.update_progress():
            pass  # Progress was updated
        
        # Update UI in each tab
        if self.main_tab:
            self.main_tab.update_ui()
        
        if self.printer_details_tab:
            self.printer_details_tab.update_ui()
        
        if self.printer_state_tab:
            self.printer_state_tab.update_ui()
        
        if self.filesystem_tab:
            self.filesystem_tab.update_ui()
        
        if self.network_tab:
            self.network_tab.update_ui()

        # HTTP tab doesn't need regular updates - it's event-driven

        # Schedule next update
        self.root.after(1000, self.update_ui)
    
    def on_close(self):
        """Handle window close event"""
        # Save configuration before closing
        self.emulator.save_config_to_json()

        # Stop both TCP and HTTP servers
        self.emulator.stop_server()
        self.emulator.stop_http_server()

        # Cleanup HTTP tab
        if self.http_tab:
            self.http_tab.cleanup()

        self.root.destroy()
