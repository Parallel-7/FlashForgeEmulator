"""
Filesystem tab UI for FlashForge Emulator
"""
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class FilesystemTab:
    """Filesystem tab UI component"""
    
    def __init__(self, parent, emulator, on_update_callback=None):
        self.parent = parent
        self.emulator = emulator
        self.on_update_callback = on_update_callback
        
        # Create the UI elements
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the filesystem tab UI"""
        # Virtual Files Frame
        file_frame = ttk.LabelFrame(self.parent, text="Emulated Files")
        file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Intro text
        intro_text = "The emulator simulates a printer filesystem with virtual files that appear in client applications."
        ttk.Label(file_frame, text=intro_text, wraplength=500).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Files list with scrollbar
        files_frame = ttk.Frame(file_frame)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.files_listbox = tk.Listbox(files_frame, height=12, selectmode=tk.SINGLE)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(files_frame, command=self.files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate the listbox with initial files
        for file in self.emulator.virtual_files:
            self.files_listbox.insert(tk.END, file)
        
        # Add/Delete buttons and file entry
        file_control_frame = ttk.Frame(file_frame)
        file_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
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
        
        # Help section at the bottom
        help_frame = ttk.LabelFrame(self.parent, text="File Types")
        help_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        help_text = """
        Supported file extensions:
        - .3mf
        - .gcode
        - .gx: FlashForge G-code file
        
        If no extension is provided, .3mf will be added automatically.
        """
        ttk.Label(help_frame, text=help_text, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=10)
    
    def update_ui(self):
        """Update UI elements from emulator state"""
        # Usually not needed as virtual files list doesn't change externally
        pass
    
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
