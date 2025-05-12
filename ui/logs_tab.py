"""
Logs tab UI for FlashForge Emulator
"""
import tkinter as tk
from tkinter import scrolledtext
import ttkbootstrap as ttk
from datetime import datetime

class LogsTab:
    """Logs tab UI component"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the logs tab UI"""
        # Log Frame
        log_frame = ttk.Frame(self.parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create log display
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=24)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Clear Logs", style="secondary.TButton", 
                   command=self.clear_logs).pack(side=tk.RIGHT, padx=5)
    
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
