import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import config

from .logs_tab import LogsTab
from .config_tab import ConfigTab

class MainWindow:
    """Main UI Window"""
    
    def __init__(self, root, emulator):
        self.root = root
        self.emulator = emulator
        
        # Initialize window
        self.root.title("FlashForge API Emulator")
        self.root.geometry(f"{config.UI_WINDOW_WIDTH}x{config.UI_WINDOW_HEIGHT}")
        
        # Set up the UI
        self.logs_tab = None
        self.config_tab = None
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
        config_tab_frame = ttk.Frame(self.notebook)
        logs_tab_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(config_tab_frame, text="Configuration")
        self.notebook.add(logs_tab_frame, text="Logs")
        
        # Initialize tabs
        self.config_tab = ConfigTab(config_tab_frame, self.emulator, self.log)
        self.logs_tab = LogsTab(logs_tab_frame)
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def log(self, message):
        """Log a message to the logs tab"""
        if self.logs_tab:
            self.logs_tab.log(message)
        return message
    
    def update_ui(self):
        """Periodically update the UI from emulator state"""
        # Update temperature and status displays
        self.emulator.simulate_temperatures()
        
        # Update progress if printing
        if self.emulator.update_progress():
            pass  # Progress was updated
        
        # Update UI
        if self.config_tab:
            self.config_tab.update_ui()
        
        # Schedule next update
        self.root.after(1000, self.update_ui)
    
    def on_close(self):
        """Handle window close event"""
        self.emulator.stop_server()
        self.root.destroy()
